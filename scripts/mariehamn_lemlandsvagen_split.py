"""Split the rural Lemlandsvägen object at Strandnäs so its unchanged western corridor carries its 1968 evidence.

The existing object keeps its identity, its 1985 start, all earlier evidence and its original geometry
for the realigned eastern remainder. The western section and the roundabout lane become their own
persistent objects. Source ownership is re-partitioned exactly: every whole or partial vertex range the
original object owned ends up with exactly one of the three objects. All checks run before any change.
"""
import statistics
from copy import deepcopy
from shapely.geometry import LineString, Point
from mariehamn_south_streets import digest
from postwar_city import METRIC

BIN, MEDIAN_LIMIT, OTHER_SYMBOL = 150, 12, 40   # metres
LINK_LIMIT = {'west': 15, 'remainder': 15, 'approach': 25}


def metric(path):
    return LineString([METRIC(*p) for p in path])


def fractional_index(path, point):
    line = metric(path); d = line.project(Point(METRIC(*point))); run = 0
    for k in range(len(path) - 1):
        seg = metric(path[k:k + 2]).length
        if run + seg >= d:
            return round(k + (d - run) / seg, 8)
        run += seg
    return float(len(path) - 1)


def sub_path(path, a, b):
    """Source line between fractional vertex positions a and b."""
    at = lambda t: [path[int(min(t, len(path) - 2))][j] + (path[int(min(t, len(path) - 2)) + 1][j] - path[int(min(t, len(path) - 2))][j]) * (t - int(min(t, len(path) - 2))) for j in (0, 1)]
    return [at(a)] + [p for i, p in enumerate(path) if a < i < b] + [at(b)]


def key(link):
    return (link['datasetId'], link['featureId'], tuple(link['sourceVertexRange']), link['sourceVertexCount'])


def apply_lemlandsvagen_split(read, catalog):
    review = read('data/mariehamn-lemlandsvagen-split.json')
    first = read('data/mariehamn-major-roads.json')
    modern = {f['id']: f for f in read('dist/assets/modern.json.gz')['features']}
    stage_features = {(s['id'], f['id']): f for s in read('dist/assets/mariehamn-city-grid.json')['sets'] for f in s['features']}
    snapshots = {f'osm-{y}': {f['id']: f for f in read(f'dist/assets/roads-{y}.json.gz')['features']} for y in [2014, 2021, 2025]}
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}
    t = review['target']
    if review['schemaVersion'] != 1 or review['sheets'] != first['sheets'] or review['source']['id'] in sources:
        raise ValueError('Lemlandsvägen split already applied or uses unverified sheets')
    q2, q3 = objects.get(t['objectId']), objects.get(review['pairedLane']['objectId'])
    if not q2 or not q3 or digest(q2) != t['inputHash'] or digest(q3) != review['pairedLane']['inputHash']:
        raise ValueError('Changed rural Lemlandsvägen input')
    geo = geometries[t['geometryId']]
    if digest(geo) != t['geometryHash'] or len(q2['geometryPeriods']) != 1 or q2['geometryPeriods'][0]['geometryId'] != geo['id']:
        raise ValueError('Changed rural Lemlandsvägen geometry')
    path, seq = geo['paths'][0], []
    for w in t['ways']:
        if digest(modern[w]) != t['wayHashes'][w]:
            raise ValueError('Changed modern Lemlandsvägen way')
        p = modern[w]['paths'][0]; seq += p if not seq else p[1:]
    if seq != path or path[t['slices']['west'][1]] != t['splitPoint'] or modern[t['splitWay']]['paths'][0][t['splitVertex']] != t['splitPoint']:
        raise ValueError('Split point no longer on the rural geometry')
    s = t['slices']
    if s['approach'][0] != 0 or s['approach'][1] != s['west'][0] or s['west'][1] != s['remainder'][0] or s['remainder'][1] != len(path) - 1:
        raise ValueError('Split slices do not cover the road exactly once')
    parts = {k: path[a:b + 1] for k, (a, b) in s.items()}
    lines = {k: metric(p) for k, p in parts.items()}

    # Ownership: the three link sets rebuild the original ranges exactly, and each moved range lies on its new road.
    sets = {o['part']: o['sourceLinks'] for o in review['objects']}; sets['remainder'] = review['remainder']['sourceLinks']
    rebuilt = {}
    for part, links in sets.items():
        for l in links:
            k = (l['datasetId'], l['featureId'])
            source = modern[k[1]]['paths'][0] if k[0] == 'osm-2026' else snapshots[k[0]][k[1]]['paths'][0]
            if len(source) != l['sourceVertexCount']:
                raise ValueError('Changed source vertex count')
            if 'splitAt' in l and l['splitAt'] != (float(t['splitVertex']) if k[0] == 'osm-2026' else fractional_index(source, t['splitPoint'])):
                raise ValueError('Split position differs from the reviewed point')
            a, b = l['sourceVertexRange']
            piece = metric(sub_path(source, a, b))
            if max(lines[part].distance(Point(c)) for c in piece.coords) > LINK_LIMIT[part]:
                raise ValueError('Moved source range is not on its new road')
            rebuilt.setdefault(k, []).append((a, b, l['sourceVertexCount']))
    merged = {}
    for k, ranges in rebuilt.items():
        ranges.sort(); a, b, n = ranges[0]
        for a2, b2, n2 in ranges[1:]:
            if a2 != b or n2 != n:
                raise ValueError('Split ranges overlap or leave a gap')
            b = b2
        merged[k] = (a, b, n)
    if merged != {(l['datasetId'], l['featureId']): (*l['sourceVertexRange'], l['sourceVertexCount']) for l in q2['sourceLinks']}:
        raise ValueError('Split does not preserve the original source ownership')
    owned = {(l['datasetId'], l['featureId']) for o in objects.values() for l in o['sourceLinks']}
    stage = [l for o in review['objects'] for l in o['stageLinks']] + review['pairedLane']['stageLinks']
    if len({(l['datasetId'], l['featureId']) for l in stage}) != len(stage):
        raise ValueError('City-stage record linked twice')
    for l in stage:
        f = stage_features[(l['datasetId'], l['featureId'])]
        if (l['datasetId'], l['featureId']) in owned or digest(f) != l['inputHash'] or f['paths'] != modern[l['modernFeatureId']]['paths']:
            raise ValueError('City-stage record changed or already owned')

    # Map evidence for the western section: every 150 m bin passes numerically or has a recorded visual check.
    west, results = lines['west'], {}
    bins = int(west.length // BIN) + 1
    for year in ['1968', '1978', '1985', '1995']:
        trace = review['traces'][year]; got = {}
        for q in trace['points']:
            pt = Point(METRIC(*q)); along = west.project(pt); d = west.distance(pt)
            if 0 < along < west.length and d <= OTHER_SYMBOL:
                got.setdefault(int(along // BIN), []).append(d)
        medians = {b: round(statistics.median(v), 1) for b, v in got.items()}
        checked = {c['bin'] for c in review['visualChecks'] if str(c['year']) == year and c['outcome'] == 'same-corridor'}
        failing = {b for b in range(bins) if medians.get(b, 99) > MEDIAN_LIMIT}
        if failing - checked or checked - failing or trace['crops']['west']['sourceId'] != next(x['sourceId'] for x in review['sheets'] if str(x['year']) == year):
            raise ValueError('Western Lemlandsvägen is not the same corridor in ' + year)
        results[year] = dict(medians=[medians.get(b) for b in range(bins)], visualBins=sorted(checked), samples=sum(len(v) for v in got.values()))

    # Mutation starts here.
    basis = {(x['datasetId'], x['featureId']): x['basis'] for x in q2['sourceLinks']}
    clean = lambda l: {k: v for k, v in l.items() if k != 'splitAt'} | {'basis': basis[(l['datasetId'], l['featureId'])]}
    src = review['source']['id']; catalog['sources'].append(deepcopy(review['source']))
    sheet = {s_['year']: s_['sourceId'] for s_ in review['sheets']}
    new = {}
    for spec in review['objects']:
        oid, part = spec['id'], spec['part']
        if oid in objects:
            raise ValueError('Duplicate Lemlandsvägen identity')
        gid = f'geometry:lemlandsvagen-split:{part}'
        catalog['geometries'].append(dict(id=gid, representation='centerline', paths=[deepcopy(parts[part])], sourceIds=['city-2026'],
                                          note='Del av den granskade landsbygdsgeometrin (moderna vägar). Samma koordinater används genom alla källbyten.'))
        interp = oid + ':interpretation'
        ev = [dict(id=interp, sourceId=src, describes={'from': spec['firstYear'], 'to': None}, supports=['identity', 'state'], observationType='interpretation', interpretation=True, constructionYear=None, note=spec['basis']),
              dict(id=oid + ':split-from', sourceId=src, describes={'from': 2026, 'to': None}, supports=['identity'], observationType='identity-split', interpretation=True,
                   splitFrom=q2['id'], previousGeometryId=geo['id'], note=f'Avdelad från {q2["name"]} ({q2["id"]}). Dess tidigare belägg och geometri finns kvar på den enheten.')]
        for y in [1968, 1978, 1985, 1995]:
            present = y >= spec['firstYear']
            e = dict(id=f'{oid}:map-{y}', sourceId=sheet[y], describes={'from': y, 'to': y + 1}, observationType='printed-map-review', interpretation=True,
                     outcome='present' if present else 'absent', supports=['geometry', 'identity', 'state'] if present else ['state'])
            if present:
                e.update(coverage='full', canonicalRange=[0, 1], matchedGeometryId=gid)
            if part == 'west':
                r_ = results[str(y)]
                e.update(traceSamples=r_['samples'], binMediansMeters=r_['medians'], visualBins=r_['visualBins'],
                         note=f'Spårad mittlinje: medianavvikelse per {BIN}-metersavsnitt ' + ', '.join('–' if m is None else str(m) for m in r_['medians']) + ' m' + (f'; visuellt kontrollerade avsnitt {r_["visualBins"]}.' if r_['visualBins'] else '.'))
            else:
                e['note'] = spec['basis'] if present else 'Rak genomfart 1968; ingen rondelltillfart.'
            ev.append(e)
        refs = [interp, f'{oid}:map-{spec["firstYear"]}']
        obj = dict(id=oid, name=spec['name'], kind='roadSegment', independentRoad=True, ruralRoad=True, modernRoadClass=q2['modernRoadClass'], roadWidth=q2['roadWidth'], routeId=q2['routeId'],
                   states=[dict(state='open', **{'from': spec['firstYear'], 'to': None}, certainty='inferred', evidenceIds=refs, note=spec['basis'])],
                   geometryPeriods=[dict(geometryId=gid, **{'from': spec['firstYear'], 'to': None}, certainty='inferred', evidenceIds=refs, coverage='full', canonicalRange=[0, 1], basis=spec['basis'])],
                   evidence=ev, sourceLinks=[clean(l) for l in spec['sourceLinks']]
                   + [dict(datasetId=l['datasetId'], featureId=l['featureId']) for l in spec['stageLinks']],
                   lemlandsvagenSplit=dict(reviewedAt=review['reviewedAt'], part=part, splitFrom=q2['id'], constructionYear=None, lengthMeters=round(lines[part].length, 2)))
        catalog['objects'].append(obj); new[part] = obj
    # The original object keeps identity, dates and evidence; only its extent and ownership shrink.
    rgid = 'geometry:lemlandsvagen-split:remainder'
    catalog['geometries'].append(dict(id=rgid, representation='centerline', paths=[deepcopy(parts['remainder'])], sourceIds=['city-2026'], note='Återstående del efter delningen vid Södergård. Den ursprungliga geometrin finns kvar som belägg.'))
    previous = deepcopy(q2['geometryPeriods'])
    q2['geometryPeriods'][0]['geometryId'] = rgid
    q2['sourceLinks'] = [clean(l) for l in review['remainder']['sourceLinks']]
    q2['evidence'].append(dict(id=q2['id'] + ':strandnas-split', sourceId=src, describes={'from': 2026, 'to': None}, supports=['identity'], observationType='identity-split', interpretation=True,
                               originalGeometryId=geo['id'], splitInto=[new['west']['id'], new['approach']['id']], note=review['remainder']['basis']))
    for y in [1968, 1978]:
        q2['evidence'].append(dict(id=f'{q2["id"]}:solstrand-{y}', sourceId=sheet[y], describes={'from': y, 'to': y + 1}, supports=['state'], observationType='printed-map-review', interpretation=True,
                                   outcome='absent', note='Dagens sträckning öster om Södergård saknas; vägen går i en äldre båge 12–31 m söder om den. ' + review['curveDeviation']['note']))
    q2['strandnasSplit'] = dict(reviewedAt=review['reviewedAt'], previousGeometryPeriods=previous, splitInto=[new['west']['id'], new['approach']['id']])
    # The roundabout's second eastern lane starts with the ring in 1978; its 1985 phase is untouched.
    pl = review['pairedLane']; eid = q3['id'] + ':map-1978-ring'
    q3['evidence'].append(dict(id=eid, sourceId=sheet[1978], describes={'from': 1978, 'to': 1979}, supports=['geometry', 'identity', 'state'], observationType='printed-map-review', interpretation=True,
                               outcome='present', coverage='full', canonicalRange=[0, 1], matchedGeometryId=q3['geometryPeriods'][0]['geometryId'], note=pl['basis']))
    if q3['states'][0]['from'] != 1985 or q3['geometryPeriods'][0]['from'] != 1985:
        raise ValueError('Paired lane already starts earlier')
    q3['states'].insert(0, dict(state='open', **{'from': pl['firstYear'], 'to': 1985}, certainty='inferred', evidenceIds=[eid], note=pl['basis']))
    q3['geometryPeriods'].insert(0, dict(geometryId=q3['geometryPeriods'][0]['geometryId'], **{'from': pl['firstYear'], 'to': 1985}, certainty='inferred', evidenceIds=[eid], coverage='full', canonicalRange=[0, 1], basis=pl['basis']))
    q3['sourceLinks'] += [dict(datasetId=l['datasetId'], featureId=l['featureId']) for l in pl['stageLinks']]
    q3['strandnasSplit'] = dict(reviewedAt=review['reviewedAt'], previousFirstYear=1985)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
