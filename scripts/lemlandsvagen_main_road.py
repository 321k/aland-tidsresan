"""Lemlandsvägen del 1 on the early maps: split today's road where it was rebuilt, and add the old road (1917–1985).

The visual review (docs/reviews/lemlandsvagen-main-road-2026-11-17, data/lemlandsvagen-main-road.json) compared today's
road with the 1917 Senate atlas, the 1929 and 1948 parish maps and the 1968, 1978 and 1985 base maps. Where the old and
new roads are the same, today's road gets its first map year (1917); where today's road is a later bypass, it gets the
first map that draws it, and the old road, traced on the 1929 map, becomes its own object.

- The original object keeps its identity, its 1985 start, all evidence and its original geometry (as evidence) for the
  Knutsboda–Dragsvik bypass (section E). Seven new section objects take the rest. Source ownership is re-partitioned
  exactly: every source range of the original ends up with exactly one section, and each piece lies on its section.
- Four old-road objects carry the 1929 trace, open from 1917 until the edition after the last base map that draws them,
  then 'unknown' (not reviewed later; much of the line survives as local roads in OpenStreetMap, not yet reconciled).
- Långskata del 2's first 300 m are the old road: it gets a partial 1917–1985 period, as other partial streets do.
All checks run before any change. Map years are first evidence, not construction years.
"""
from copy import deepcopy
from shapely.geometry import LineString, Point
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from mariehamn_lemlandsvagen_split import sub_path

LINK_LIMIT = 25        # metres: a moved source range must lie this close to its section
OVERLAP_BUFFER, OVERLAP_LIMIT = 12, 80   # metres: an old-road object may run this long beside another road (junctions, crossings)
MAP_YEARS = [1917, 1929, 1948, 1968, 1978, 1985]
PRESENT = {'present', 'absent', 'unclear'}


def metric(path):
    return LineString([TO_METRIC(*p) for p in path])


def cut(path, line, a, b):
    """The original path between distances a and b along it, keeping its own vertices."""
    run, idx = 0.0, []
    for k in range(len(path) - 1):
        seg = metric(path[k:k + 2]).length; idx.append((run, k, seg)); run += seg
    def pos(d):
        if d >= run: return float(len(path) - 1)
        r, k, seg = next(x for x in idx if x[0] <= d < x[0] + x[2])
        return k + (d - r) / seg
    return sub_path(path, pos(a), pos(b))


def apply_lemlandsvagen_main_road(read, catalog):
    review = read('data/lemlandsvagen-main-road.json')
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}
    modern = {f['id']: f for f in read('dist/assets/modern.json.gz')['features']}
    snapshots = {f'osm-{y}': {f['id']: f for f in read(f'dist/assets/roads-{y}.json.gz')['features']} for y in [2014, 2021, 2025]}
    t = review['target']; src = review['source']['id']
    if review['schemaVersion'] != 1 or src in sources:
        raise ValueError('Lemlandsvägen main-road review already applied')
    q = objects.get(t['objectId']); lg = objects.get(review['langskata']['objectId'])
    if not q or fingerprint(q) != t['inputHash'] or not lg or fingerprint(lg) != review['langskata']['inputHash']:
        raise ValueError('Changed Lemlandsvägen or Långskata input')
    geo = geometries[t['geometryId']]
    if digest(geo) != t['geometryHash'] or len(q['geometryPeriods']) != 1 or q['geometryPeriods'][0]['geometryId'] != geo['id']:
        raise ValueError('Changed Lemlandsvägen geometry')
    path = geo['paths'][0]; L = metric(path)
    if abs(L.length - t['lengthMeters']) > 0.05:
        raise ValueError('Changed Lemlandsvägen length')
    if any(s['id'] not in sources for s in []) or any(v not in sources and v != review['sources'][0]['id'] for v in review['maps'].values()):
        raise ValueError('Unknown map source')

    # Sections cover the road exactly once.
    specs = review['sections'] + [dict(review['remainder'], id=q['id'])]
    specs.sort(key=lambda s: s['range'][0])
    if specs[0]['range'][0] != 0 or abs(specs[-1]['range'][1] - L.length) > 0.05 or any(a['range'][1] != b['range'][0] for a, b in zip(specs, specs[1:])):
        raise ValueError('Sections do not cover Lemlandsvägen exactly once')
    for s in specs:
        if sorted(s['maps']) != [str(y) for y in MAP_YEARS] or set(s['maps'].values()) - PRESENT:
            raise ValueError('Incomplete map review for section ' + s['part'])
        if min(int(y) for y, v in s['maps'].items() if v == 'present') != s['firstYear'] or any(v == 'present' for y, v in s['maps'].items() if int(y) < s['firstYear']):
            raise ValueError('First year is not the first present map for section ' + s['part'])
        if s['id'] != q['id'] and s['id'] in objects:
            raise ValueError('Duplicate section identity ' + s['id'])
    if review['remainder']['firstYear'] != q['states'][0]['from']:
        raise ValueError('The kept object must keep its first year')
    parts = {s['part']: cut(path, L, *s['range']) for s in specs}; lines = {k: metric(p) for k, p in parts.items()}

    # Ownership: the section link sets rebuild the original ranges exactly, and each piece lies on its section.
    rebuilt = {}
    for part, links in review['sourceLinks'].items():
        for l in links:
            k = (l['datasetId'], l['featureId'])
            source = (modern[k[1]] if k[0] == 'osm-2026' else snapshots[k[0]][k[1]])['paths'][0]
            if len(source) != l['sourceVertexCount']:
                raise ValueError('Changed source vertex count')
            a, b = l['sourceVertexRange']; piece = metric(sub_path(source, a, b))
            if max(lines[part].distance(Point(c)) for c in piece.coords) > LINK_LIMIT:
                raise ValueError(f'Source range {k} is not on section {part}')
            rebuilt.setdefault(k, []).append((a, b, l['sourceVertexCount']))
    merged = {}
    for k, ranges in rebuilt.items():
        ranges.sort(); a, b, n = ranges[0]
        for a2, b2, n2 in ranges[1:]:
            if abs(a2 - b) > 1e-6 or n2 != n:
                raise ValueError('Section ranges overlap or leave a gap')
            b = b2
        merged[k] = (round(a, 6), round(b, 6), n)
    if merged != {(l['datasetId'], l['featureId']): (round(l['sourceVertexRange'][0], 6), round(l['sourceVertexRange'][1], 6), l['sourceVertexCount']) for l in q['sourceLinks']}:
        raise ValueError('Split does not preserve the original source ownership')

    # Old road: ends on today's road (or Långskata), no long overlap with another road open at the same time.
    old = review['oldRoad']; lg_geo = geometries[lg['geometryPeriods'][0]['geometryId']]; lg_line = metric(lg_geo['paths'][0])
    ends = {**{s['id']: lines[s['part']] for s in specs}}
    roads = [(o, metric(p)) for o in catalog['objects'] if o['kind'] == 'roadSegment' and o['id'] != q['id']
             for gp in o['geometryPeriods'] for p in geometries[gp['geometryId']]['paths'] if len(p) > 1]
    for spec in old['objects']:
        if spec['id'] in objects:
            raise ValueError('Duplicate old-road identity ' + spec['id'])
        line = metric(spec['path']); first, last = Point(line.coords[0]), Point(line.coords[-1])
        anchor = lg_line if spec['startsOn'] == review['langskata']['objectId'] else L
        if anchor.distance(first) > 0.5 or L.distance(last) > 0.5 or max(spec['endSnapMeters']) > 25:
            raise ValueError('Old road does not end on today\'s road: ' + spec['id'])
        until = spec['until']
        if spec['lastPresent'] != max(int(y) for y, v in spec['maps'].items() if v == 'present') or until <= spec['lastPresent']:
            raise ValueError('Old road end does not follow its last map: ' + spec['id'])
        for o, other in roads:
            if any(p['from'] < until and old['firstYear'] < (p['to'] or 9999) for p in o['states'] if p['state'] == 'open'):
                if other.intersection(line.buffer(OVERLAP_BUFFER)).length > OVERLAP_LIMIT and o['id'] != lg['id']:
                    raise ValueError(f'Old road {spec["id"]} runs along {o["id"]}')
            if o['id'] == lg['id']:
                seg = cut(lg_geo['paths'][0], lg_line, 0, lg_line.length * review['langskata']['canonicalRange'][1])
                if metric(seg).intersection(line.buffer(OVERLAP_BUFFER)).length > OVERLAP_LIMIT:
                    raise ValueError('Old road repeats the Långskata stretch')
    lr = review['langskata']
    if lg['states'][0]['from'] != lr['until'] or lg['geometryPeriods'][0]['from'] != lr['until'] or len(lg['geometryPeriods']) != 1:
        raise ValueError('Långskata del 2 already has an earlier period')

    basis = {(l['datasetId'], l['featureId']): l['basis'] for l in q['sourceLinks']}
    owned = lambda part: [dict(l, basis=basis[(l['datasetId'], l['featureId'])]) for l in review['sourceLinks'][part]]

    # All checks passed. Change the catalogue.
    for s_ in review['sources']:
        catalog['sources'].append(deepcopy(s_))
    catalog['sources'].append(deepcopy(review['source']))
    maps = {int(y): v for y, v in review['maps'].items()}

    def map_evidence(oid, outcomes, gid, note, years=MAP_YEARS, coverage=None):
        ev = []
        for y in years:
            outcome = outcomes[str(y)]
            e = dict(id=f'{oid}:early-map-{y}', sourceId=maps[y], describes={'from': y, 'to': y + 1}, observationType='printed-map-review', interpretation=True,
                     outcome=outcome, supports=['geometry', 'identity', 'state'] if outcome == 'present' else ['state'], constructionYear=None, reviewId=src, note=note)
            if outcome == 'present':
                e.update(coverage=coverage['coverage'] if coverage else 'full', canonicalRange=coverage['canonicalRange'] if coverage else [0, 1], matchedGeometryId=gid)
            ev.append(e)
        return ev

    new = {}
    for spec in review['sections']:
        oid, part = spec['id'], spec['part']; gid = f'geometry:lemlandsvagen-main:{part.lower()}'
        catalog['geometries'].append(dict(id=gid, representation='centerline', paths=[deepcopy(parts[part])], sourceIds=['city-2026'],
                                          note='Del av den granskade landsbygdsgeometrin (moderna vägar). Samma koordinater används genom alla källbyten.'))
        ev = [dict(id=oid + ':split-from', sourceId=src, describes={'from': 2026, 'to': None}, supports=['identity'], observationType='identity-split', interpretation=True,
                   splitFrom=q['id'], previousGeometryId=geo['id'], constructionYear=None, note=f'Avdelad från {q["name"]} ({q["id"]}). Dess tidigare belägg och geometri finns kvar på den enheten.')]
        ev += map_evidence(oid, spec['maps'], gid, spec['basis'])
        refs = [e['id'] for e in ev if e.get('outcome') == 'present' and e['describes']['from'] == spec['firstYear']]
        obj = dict(id=oid, name=spec['name'], kind='roadSegment', independentRoad=True, ruralRoad=True, modernRoadClass=q['modernRoadClass'], roadWidth=q['roadWidth'], routeId=q['routeId'],
                   states=[dict(state='open', **{'from': spec['firstYear'], 'to': None}, certainty='inferred', evidenceIds=refs, note=spec['basis'])],
                   geometryPeriods=[dict(geometryId=gid, **{'from': spec['firstYear'], 'to': None}, certainty='inferred', evidenceIds=refs, coverage='full', canonicalRange=[0, 1], basis=spec['basis'])],
                   evidence=ev, sourceLinks=owned(part),
                   lemlandsvagenMainRoad=dict(reviewedAt=review['reviewedAt'], part=part, splitFrom=q['id'], range=spec['range'], constructionYear=None, lengthMeters=round(lines[part].length, 2)))
        catalog['objects'].append(obj); new[part] = obj

    # The original keeps identity, 1985 start and evidence; only its extent, name and ownership shrink.
    rem = review['remainder']; gid = 'geometry:lemlandsvagen-main:e'
    catalog['geometries'].append(dict(id=gid, representation='centerline', paths=[deepcopy(parts['E'])], sourceIds=['city-2026'],
                                      note='Återstående del efter uppdelningen på de tidiga kartorna. Den ursprungliga geometrin finns kvar som belägg.'))
    previous = deepcopy(q['geometryPeriods']); previous_name = q['name']
    q['name'] = rem['name']; q['geometryPeriods'][0]['geometryId'] = gid
    q['sourceLinks'] = owned('E')
    q['evidence'].append(dict(id=q['id'] + ':early-map-split', sourceId=src, describes={'from': 2026, 'to': None}, supports=['identity'], observationType='identity-split', interpretation=True,
                              originalGeometryId=geo['id'], splitInto=[o['id'] for o in new.values()], constructionYear=None,
                              note=f'{previous_name} delades i åtta delar efter de tidiga kartorna; denna enhet behåller förbifarten Knutsboda–Dragsvik.'))
    q['evidence'] += map_evidence(q['id'], rem['maps'], gid, rem['basis'])
    q['lemlandsvagenMainRoad'] = dict(reviewedAt=review['reviewedAt'], part='E', previousName=previous_name, previousGeometryPeriods=previous,
                                      splitInto=[o['id'] for o in new.values()], range=rem['range'], constructionYear=None)

    # Old road objects.
    for spec in old['objects']:
        oid = spec['id']; gid = 'geometry:' + oid.split(':', 1)[1]
        catalog['geometries'].append(dict(id=gid, representation='centerline', paths=[deepcopy(spec['path'])], sourceIds=[maps[1929]], note=old['traceBasis']))
        ev = map_evidence(oid, spec['maps'], gid, spec['basis'])
        refs = [e['id'] for e in ev if e['outcome'] == 'present']
        later = dict(id=oid + ':after-maps', sourceId=src, describes={'from': spec['until'], 'to': None}, supports=['state'], observationType='interpretation', interpretation=True, constructionYear=None,
                     note='Inte granskad efter den sista grundkartan som ritar vägen. Det betyder inte att vägen försvann; delar finns kvar som lokala vägar.')
        ev.append(later)
        obj = dict(id=oid, name=spec['name'], kind='roadSegment', independentRoad=True, ruralRoad=True, modernRoadClass=old['modernRoadClass'], roadWidth=old['roadWidth'], routeId=old['routeId'],
                   states=[dict(state='open', **{'from': old['firstYear'], 'to': spec['until']}, certainty='inferred', evidenceIds=refs, note=spec['basis']),
                           dict(state='unknown', **{'from': spec['until'], 'to': None}, certainty='inferred', evidenceIds=[later['id']], note=later['note'])],
                   geometryPeriods=[dict(geometryId=gid, **{'from': old['firstYear'], 'to': spec['until']}, certainty='inferred', evidenceIds=refs, coverage='full', canonicalRange=[0, 1], basis=old['traceBasis'])],
                   evidence=ev, sourceLinks=[],
                   lemlandsvagenMainRoad=dict(reviewedAt=review['reviewedAt'], oldRoad=True, traceId=spec['traceId'], traceRange=spec['traceRange'], todayRange=spec['todayRange'],
                                              endSnapMeters=spec['endSnapMeters'], constructionYear=None))
        catalog['objects'].append(obj)

    # Långskata del 2: its first 300 m are the old road from 1917.
    cov = dict(coverage='partial', canonicalRange=lr['canonicalRange']); lgid = lg['geometryPeriods'][0]['geometryId']
    ev = map_evidence(lg['id'], lr['maps'], lgid, lr['basis'], years=[1917, 1929, 1948, 1968, 1978], coverage=cov)
    refs = [e['id'] for e in ev]
    lg['evidence'] += ev
    lg['states'].insert(0, dict(state='open', **{'from': lr['firstYear'], 'to': lr['until']}, certainty='inferred', evidenceIds=refs, note=lr['basis']))
    lg['geometryPeriods'].insert(0, dict(geometryId=lgid, **{'from': lr['firstYear'], 'to': lr['until']}, certainty='inferred', evidenceIds=refs, basis=lr['basis'], **cov))
    lg['lemlandsvagenMainRoad'] = dict(reviewedAt=review['reviewedAt'], previousFirstYear=lr['until'], earlyRange=lr['canonicalRange'], constructionYear=None)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
