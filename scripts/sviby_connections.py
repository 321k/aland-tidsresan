"""The connections at Sviby (docs/sviby-connections.md): the roads that join Norra Svibyvägen to Kasbergsvägen, to
Norra Möckelövägen and to Svibyvägen.

Two review files, applied in order on one copy of the catalogue, which replaces it only if all pass:
- data/sviby-connections-early.json (_apply): Norra Möckelövägen from 1929, the road along the west shore of Svibyviken
  on the parish map 1012 08 (1929) and its 1948 edition;
- data/sviby-connections.json: new road objects made of OSM pieces that no object owns ('newRoads'), each dated by its
  maps and resting on the roads it joins; and the city-stage features they replace ('stageFeatures').

A new road's pieces may be whole ways or a way's first vertices up to where another object's ownership begins, so
ownership in each extract stays complete and without overlap. Map years are first evidence, not construction years.
"""
from copy import deepcopy
from shapely.geometry import Point
from hammarlandsvagen_main_road import _apply, metric, END_LIMIT, OVERLAP_BUFFER, OVERLAP_LIMIT, SNAPSHOTS
from mariehamn_frame_1942 import digest, TO_METRIC

EARLY, MAIN = 'data/sviby-connections-early.json', 'data/sviby-connections.json'


def _point(p, t):
    """The point at fractional vertex index t of path p."""
    k = int(t)
    if t == k:
        return list(p[k])
    f = t - k
    return [p[k][i] + f * (p[k + 1][i] - p[k][i]) for i in (0, 1)]


def _piece(p, a, b, reverse):
    ka, kb = int(-(-a // 1)), int(b // 1)
    pts = ([_point(p, a)] if a != ka else []) + [list(q) for q in p[ka:kb + 1]] + ([_point(p, b)] if b != kb else [])
    return pts[::-1] if reverse else pts


def _check(read, catalog, review):
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}; labels = review['maps']
    if review['schemaVersion'] != 1 or review['source']['id'] in sources:
        raise ValueError('Connections review already applied')
    if any(l['sourceId'] not in sources for l in labels.values()):
        raise ValueError('Unexpected map sources')
    files = {}
    def feature(ds, fid):
        file = SNAPSHOTS[ds][0]
        if file not in files:
            files[file] = {x['id']: x for x in read(file)['features']}
        return files[file].get(fid)
    owned = [(o['id'], l['datasetId'], l['featureId'], l.get('sourceVertexRange')) for o in catalog['objects'] for l in o.get('sourceLinks', [])]
    new_lines = {}
    for nr in review['newRoads']:
        if nr['id'] in objects or nr['id'] in new_lines or nr['surveySourceId'] in sources:
            raise ValueError('Duplicate new road ' + nr['id'])
        year = lambda k: labels[k]['year']
        present = [year(k) for k, v in nr['maps'].items() if v == 'present']
        # a map from before the first year may be marked absent (the road is not yet drawn); none after it
        if not set(nr['maps']) <= set(labels) or not present or min(present) != nr['firstYear'] \
                or any(v == 'absent' and year(k) >= nr['firstYear'] for k, v in nr['maps'].items()) or any(v not in ('present', 'absent') for v in nr['maps'].values()):
            raise ValueError('New road dates do not follow its maps: ' + nr['id'])
        # The OSM pieces: unchanged, single-path ways, not owned by any object. A piece that is not the whole way ends
        # (or begins) exactly where an object's ownership of the same way begins (or ends).
        for l in nr['sourceLinks']:
            f = feature(l['datasetId'], l['featureId']); a, b = l['sourceVertexRange']
            if not f or not l['featureId'].startswith(SNAPSHOTS[l['datasetId']][1]) or len(f['paths']) != 1 or digest(f['paths']) != l['input'] \
                    or l['sourceVertexCount'] != len(f['paths'][0]) or not 0 <= a < b <= len(f['paths'][0]) - 1:
                raise ValueError('Changed OSM source ' + l['featureId'])
            others = [r for _, ds, fid, r in owned if ds == l['datasetId'] and fid == l['featureId']]
            if any(r is None or max(a, r[0]) < min(b, r[1]) for r in others):
                raise ValueError('OSM source already owned: ' + l['featureId'])
            # 'partialBasis': a stated reason to own only part of a way whose rest stays unowned (an arc of a roundabout)
            if ((a != 0 and not any(r[1] == a for r in others)) or (b != len(f['paths'][0]) - 1 and not any(r[0] == b for r in others))) and not l.get('partialBasis'):
                raise ValueError('A partial piece does not abut the owned rest of its way: ' + l['featureId'])
            owned.append((nr['id'], l['datasetId'], l['featureId'], [a, b]))
        if not {l['datasetId'] for l in nr['sourceLinks']} <= set(SNAPSHOTS) or not any(l['datasetId'] == 'osm-2026' for l in nr['sourceLinks']):
            raise ValueError('The new road needs its 2026 pieces: ' + nr['id'])
        # The geometry: the 2026 pieces in the listed order and direction, consecutive pieces within 'joinMeters'.
        built = []
        for l in [x for x in nr['sourceLinks'] if x['datasetId'] == 'osm-2026']:
            part = _piece(feature('osm-2026', l['featureId'])['paths'][0], *l['sourceVertexRange'], l.get('reverse', False))
            if built and Point(TO_METRIC(*built[-1])).distance(Point(TO_METRIC(*part[0]))) > nr['joinMeters']:
                raise ValueError('The pieces do not follow each other: ' + l['featureId'])
            built += part[1:] if built and built[-1] == part[0] else part
        if [built] != nr['paths']:
            raise ValueError('The new road is not its OSM pieces: ' + nr['id'])
        line = metric(built)
        # Its ends rest (within 1 m) on the roads it joins, in every period of theirs from its first year on.
        for oid, i in ((nr['start'], 0), (nr['end'], -1)):
            e = Point(line.coords[i])
            if oid is None:                                         # a stated free end (a quay, a house the road leads to)
                if not nr.get('freeStartBasis' if i == 0 else 'freeEndBasis'):
                    raise ValueError('A free end needs a stated basis: ' + nr['id'])
                continue
            if oid in new_lines:                                    # another new road of this review, listed before
                if new_lines[oid].distance(e) > END_LIMIT:
                    raise ValueError(f"The new road does not join {oid}: {nr['id']}")
                continue
            o = objects.get(oid)
            periods = [gp for gp in o['geometryPeriods'] if (gp['to'] or 9999) > nr['firstYear']] if o else []
            if not periods or any(min(metric(p).distance(e) for p in geometries[gp['geometryId']]['paths'] if len(p) > 1) > END_LIMIT for gp in periods):
                raise ValueError(f"The new road does not join {oid}: {nr['id']}")
        for o in catalog['objects']:
            if o['kind'] != 'roadSegment': continue
            for gp in o['geometryPeriods']:
                if (gp['to'] or 9999) > nr['firstYear']:
                    for p in geometries[gp['geometryId']]['paths']:
                        hit = metric(p).intersection(line.buffer(OVERLAP_BUFFER)) if len(p) > 1 else None
                        if hit is not None and max([h.length for h in getattr(hit, 'geoms', [hit])] + [0]) > OVERLAP_LIMIT:
                            raise ValueError(f"The new road runs along {o['id']}: {nr['id']}")
        for other in new_lines.values():
            if line.intersection(other.buffer(OVERLAP_BUFFER)).length > OVERLAP_LIMIT:
                raise ValueError('Two new roads run together: ' + nr['id'])
        new_lines[nr['id']] = line
    # City-stage features a new road replaces: unchanged, in a stage from the road's first year on, and within
    # 'maxDistanceMeters' of the road along their whole length.
    stages = {s['id']: s for s in catalog['cityStages']}
    roads = {nr['id']: nr for nr in review['newRoads']}
    for x in review.get('stageFeatures', []):
        s = stages.get(x['stageId']); f = next((f for f in (s or {}).get('features', []) if f['id'] == x['featureId']), None)
        nr = roads.get(x['replacedBy'])
        if not f or digest(f) != x['featureHash'] or not nr or s['from'] < nr['firstYear'] or not x.get('basis') \
                or max(new_lines[nr['id']].distance(Point(TO_METRIC(*q))) for p in f['paths'] for q in p) > x['maxDistanceMeters']:
            raise ValueError('Changed or unmatched city-stage feature ' + x['featureId'])


def _add(catalog, review):
    labels = review['maps']; src = review['source']['id']
    stages = {s['id']: s for s in catalog['cityStages']}
    catalog['sources'] += [deepcopy(review['source'])] + [deepcopy(s) for s in review['surveySources']]
    for nr in review['newRoads']:
        gid = 'geometry:' + nr['id'].split(':', 1)[1]
        catalog['geometries'].append(dict(id=gid, representation='centerline', paths=deepcopy(nr['paths']), sourceIds=[nr['surveySourceId']], note=nr['geometryNote']))
        ev = []
        for k in sorted(nr['maps'], key=lambda k: (labels[k]['year'], k)):
            y = labels[k]['year']; outcome = nr['maps'][k]
            e = dict(id=f"{nr['id']}:map-{k}", sourceId=labels[k]['sourceId'], describes={'from': y, 'to': y + 1}, observationType=labels[k].get('observationType', 'printed-map-review'),
                     interpretation=True, outcome=outcome, supports=['geometry', 'identity', 'state'] if outcome == 'present' else ['state'], constructionYear=None, reviewId=src,
                     note=nr['basis'], **{x: labels[k][x] for x in ('observedAt', 'imageCoverage') if x in labels[k]})
            if outcome == 'present':
                e.update(matchedGeometryId=gid, coverage=nr.get('coverage', {}).get(k, 'full'), canonicalRange=nr.get('canonicalRanges', {}).get(k, [0, 1]))
            ev.append(e)
        first = [x['id'] for x in ev if x['describes']['from'] == nr['firstYear'] and x['outcome'] == 'present']
        links = [{k: v for k, v in l.items() if k not in ('input', 'reverse', 'partialBasis')} for l in nr['sourceLinks']]
        catalog['objects'].append(dict(
            id=nr['id'], name=nr['name'], kind='roadSegment', independentRoad=True, ruralRoad=True, modernRoadClass=nr['modernRoadClass'], roadWidth=nr['roadWidth'], routeId=nr['routeId'],
            states=[dict(state='open', **{'from': nr['firstYear'], 'to': None}, certainty='inferred', evidenceIds=first, note=nr['basis'])],
            geometryPeriods=[dict(geometryId=gid, **{'from': nr['firstYear'], 'to': None}, certainty='inferred', evidenceIds=first, coverage='full', canonicalRange=[0, 1], basis=nr['geometryNote'])],
            evidence=ev, sourceLinks=links,
            mainRoadReview=dict(reviewedAt=review['reviewedAt'], review=src, newFromOsm=True, constructionYear=None)))
    objects = {o['id']: o for o in catalog['objects']}
    for x in review.get('stageFeatures', []):
        stage = stages[x['stageId']]; o = objects[x['replacedBy']]
        i = next(i for i, f in enumerate(stage['features']) if f['id'] == x['featureId'])
        old = stage['features'][i]; fid = f"{x['stageId']}:{review.get('stagePrefix', 'sviby-connections')}:{o['id']}"
        stage['features'][i] = dict(id=fid, objectId=o['id'], name=o['name'], kind=old['kind'], width=8, sourceFeatureId=old['id'], paths=deepcopy(o_paths(catalog, o)))
        o['sourceLinks'].append(dict(datasetId=x['stageId'], featureId=fid))
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])


def o_paths(catalog, o):
    return next(g for g in catalog['geometries'] if g['id'] == o['geometryPeriods'][0]['geometryId'])['paths']


def apply_sviby_connections(read, catalog):
    apply_connections(read, catalog, EARLY, MAIN)


def apply_connections(read, catalog, early, main):
    """The step for any pair of review files of this form (docs/mockelo-road.md uses it too)."""
    trial = deepcopy(catalog)
    _apply(read, trial, early)
    review = read(main)
    _check(read, trial, review)
    _add(trial, review)
    catalog.clear(); catalog.update(trial)
