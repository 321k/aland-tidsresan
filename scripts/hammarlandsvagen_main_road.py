"""Hammarlandsvägen on the 1929 parish map, Söderby–Kattby: where today's road is the old road, it is drawn from 1929.

The visual review (docs/reviews/hammarlandsvagen-main-road-2026-11-18, data/hammarlandsvagen-main-road.json) compared
today's road with the 1929 Hammarby parish map, its 1944 black-and-white edition and the 1968–1995 base maps. Between
Söderby and the church in Hammarland, today's road follows the 1929 road except at three later bypasses (Drygsböle,
Smedens, Näfsby; first on the 1968 base map). Those stay as they are.

- Each object along a same-road stretch gets an earlier open state and geometry period from 1929 until its current
  first year, covering only the same-road ranges. A partial period gets its own cut of the object's geometry (same
  coordinates, so the road does not move when the sources change). Nothing else on the object changes.
- The old line at Smedens, 25–70 m west of today's bypass, becomes its own object (open 1929 until 1968, then
  'unknown': the 1968 map does not draw it, and nothing of it survives in OpenStreetMap).
All checks run before any change. Map years are first evidence, not construction years.
"""
from copy import deepcopy
from shapely.geometry import LineString, Point
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from lemlandsvagen_main_road import cut

SAME_ROAD_GAP = 1.0      # metres: consecutive objects along the road meet within this
END_LIMIT = 1.0          # metres: the old road's ends lie on today's road
OVERLAP_BUFFER, OVERLAP_LIMIT = 12, 80
SURVIVOR_BUFFER, SURVIVOR_LIMIT = 15, 60


def metric(path):
    return LineString([TO_METRIC(*p) for p in path])


def apply_hammarlandsvagen_main_road(read, catalog):
    review = read('data/hammarlandsvagen-main-road.json')
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}; src = review['source']['id']
    if review['schemaVersion'] != 1 or src in sources:
        raise ValueError('Hammarlandsvägen review already applied')
    if any(s['id'] in sources for s in review['sources']) or set(review['maps'].values()) != {s['id'] for s in review['sources']}:
        raise ValueError('Unexpected map sources')
    maps = {int(y): v for y, v in review['maps'].items()}

    plans = []
    for e in review['early']:
        o = objects.get(e['objectId'])
        if not o or fingerprint(o) != e['inputHash']:
            raise ValueError('Changed Hammarlandsvägen input ' + e['objectId'])
        g = geometries[e['geometryId']]
        if digest(g) != e['geometryHash'] or o['geometryPeriods'][0]['geometryId'] != g['id'] or len(g['paths']) != 1:
            raise ValueError('Changed Hammarlandsvägen geometry ' + e['objectId'])
        path = g['paths'][0]; line = metric(path)
        if abs(line.length - e['lengthMeters']) > 0.05:
            raise ValueError('Changed Hammarlandsvägen length ' + e['objectId'])
        first = o['states'][0]['from']
        if e['until'] != first or o['geometryPeriods'][0]['from'] != first or e['firstYear'] >= first:
            raise ValueError('The early period must end where the object now begins: ' + e['objectId'])
        if sorted(e['maps']) != sorted(review['maps']) or min(int(y) for y, v in e['maps'].items() if v == 'present') != e['firstYear']:
            raise ValueError('First year is not the first map marked present: ' + e['objectId'])
        rs = e['ranges']
        if not rs or any(a < 0 or b > line.length + 0.05 or b - a < 50 for a, b in rs) or any(x[1] >= y[0] for x, y in zip(rs, rs[1:])):
            raise ValueError('Invalid same-road ranges ' + e['objectId'])
        parts = [cut(path, line, a, b) for a, b in rs]
        full = len(rs) == 1 and rs[0][0] == 0 and abs(rs[0][1] - line.length) < 0.05
        plans.append((e, o, g, parts, full, [[round(a / line.length, 6), round(min(b, line.length) / line.length, 6)] for a, b in rs]))

    # The same-road objects follow each other along the road (the reference line) in the reviewed order.
    # Together the cuts cover each reviewed same-road interval of today's road exactly once, without gaps.
    ref = LineString(review['reference'])
    for s, e in review['sameRoad']:
        got = []
        for pl in plans:
            for part in pl[3]:
                m = metric(part); a, b = sorted([ref.project(Point(m.coords[0])), ref.project(Point(m.coords[-1]))])
                if b > s + SAME_ROAD_GAP and a < e - SAME_ROAD_GAP:
                    if a < s - 2 or b > e + 2 or ref.distance(Point(m.coords[len(m.coords) // 2])) > 2:
                        raise ValueError(f'Same-road cut runs outside the reviewed interval {s}-{e}')
                    got.append((a, b))
        got.sort(); at = s
        for a, b in got:
            if a > at + 2 or a < at - 2:
                raise ValueError(f'Same-road interval {s}-{e} has a gap or overlap at {round(at)}')
            at = b
        if abs(at - e) > 2:
            raise ValueError(f'Same-road interval {s}-{e} is not covered to its end')
    for prev, nxt in zip(plans, plans[1:]):
        if prev[5][-1][1] == 1 and nxt[5][0][0] == 0:        # a stretch runs on across the object boundary
            a, b = metric(prev[3][-1]), metric(nxt[3][0])
            if min(Point(a.coords[i]).distance(Point(b.coords[j])) for i in (0, -1) for j in (0, -1)) > SAME_ROAD_GAP:
                raise ValueError(f'Same-road stretch breaks between {prev[0]["objectId"]} and {nxt[0]["objectId"]}')

    # The old line at Smedens: ends on today's road, not along any road open while it is, and not surviving in OSM.
    od = review['oldRoad']
    if od['id'] in objects:
        raise ValueError('Duplicate old-road identity ' + od['id'])
    old = metric(od['path'])
    if abs(old.length - od['lengthMeters']) > 0.5 or max(od['endSnapMeters']) > 25:
        raise ValueError('Changed Smedens old line')
    if sorted(od['maps']) != sorted(set(od['maps'])) or min(int(y) for y, v in od['maps'].items() if v == 'present') != od['firstYear'] \
            or od['until'] != min(int(y) for y, v in od['maps'].items() if v == 'absent'):
        raise ValueError('Old road dates do not follow its maps')
    today = [metric(p) for oid in ('road:rural:hammarland-way-345142933', 'road:rural:hammarland-way-345143750')
             for p in geometries[objects[oid]['geometryPeriods'][0]['geometryId']]['paths']]
    for pt in (Point(old.coords[0]), Point(old.coords[-1])):
        if min(t.distance(pt) for t in today) > END_LIMIT:
            raise ValueError('Smedens old line does not end on today\'s road')
    early_lines = [metric(p) for pl in plans for p in pl[3]]
    for o in catalog['objects']:
        if o['kind'] != 'roadSegment': continue
        for gp in o['geometryPeriods']:
            if gp['from'] < od['until'] and od['firstYear'] < (gp['to'] or 9999):
                for p in geometries[gp['geometryId']]['paths']:
                    hit = metric(p).intersection(old.buffer(OVERLAP_BUFFER)) if len(p) > 1 else None
                    if hit is not None and max([h.length for h in getattr(hit, 'geoms', [hit])] + [0]) > OVERLAP_LIMIT:
                        raise ValueError('Smedens old line runs along ' + o['id'])
    for p in early_lines:
        hit = p.intersection(old.buffer(OVERLAP_BUFFER))
        if max([h.length for h in getattr(hit, 'geoms', [hit])] + [0]) > OVERLAP_LIMIT:
            raise ValueError('Smedens old line repeats a same-road stretch')
    modern = read('dist/assets/modern.json.gz')['features']
    for f in modern:
        if f.get('kind') != 'road' or f.get('name') == 'Hammarlandsvägen' or f.get('class') in ('footway', 'path', 'cycleway', 'steps'):
            continue
        for p in f['paths']:
            if len(p) > 1 and metric(p).intersection(old.buffer(SURVIVOR_BUFFER)).length > SURVIVOR_LIMIT:
                raise ValueError('The Smedens old line survives as ' + f['id'] + '; reconcile it instead of adding a separate object')

    # All checks passed. Change the catalogue.
    catalog['sources'] += [deepcopy(s) for s in review['sources']] + [deepcopy(review['source'])]

    def map_evidence(oid, outcomes, gid, note, coverage):
        ev = []
        for y in sorted(int(k) for k in outcomes):
            outcome = outcomes[str(y)]
            e = dict(id=f'{oid}:parish-map-{y}', sourceId=maps.get(y) or f'nls:101206:{y}', describes={'from': y, 'to': y + 1}, observationType='printed-map-review',
                     interpretation=True, outcome=outcome, supports=['geometry', 'identity', 'state'] if outcome == 'present' else ['state'], constructionYear=None, reviewId=src, note=note)
            if outcome == 'present':
                e.update(matchedGeometryId=gid, **coverage)
            ev.append(e)
        return ev

    for e, o, g, parts, full, ranges in plans:
        oid = e['objectId']; gid = 'geometry:hammarlandsvagen-1929:' + oid.rsplit(':', 1)[1]
        cov = dict(coverage='full', canonicalRange=[0, 1]) if full else (dict(coverage='partial', canonicalRange=ranges[0]) if len(ranges) == 1 else dict(coverage='partial', canonicalRanges=ranges))
        catalog['geometries'].append(dict(id=gid, representation='centerline', paths=deepcopy(parts), sourceIds=deepcopy(g['sourceIds']),
                                          note='Del av objektets egen geometri (samma koordinater) där dagens väg är den väg sockenkartan 1929 ritar.'))
        basis = review['earlyBasis'][oid]
        ev = map_evidence(oid, e['maps'], gid, basis, cov)
        refs = [x['id'] for x in ev if x['outcome'] == 'present' and x['describes']['from'] == e['firstYear']]
        o['evidence'] += ev
        o['states'].insert(0, dict(state='open', **{'from': e['firstYear'], 'to': e['until']}, certainty='inferred', evidenceIds=refs, note=basis))
        o['geometryPeriods'].insert(0, dict(geometryId=gid, **{'from': e['firstYear'], 'to': e['until']}, certainty='inferred', evidenceIds=refs, basis=basis, **cov))
        o['hammarlandsvagenMainRoad'] = dict(reviewedAt=review['reviewedAt'], previousFirstYear=e['until'], ranges=e['ranges'], constructionYear=None)

    oid = od['id']; gid = 'geometry:' + oid.split(':', 1)[1]
    catalog['geometries'].append(dict(id=gid, representation='centerline', paths=[deepcopy(od['path'])], sourceIds=[maps[1929]], note=od['traceBasis']))
    ev = map_evidence(oid, od['maps'], gid, od['basis'], dict(coverage='full', canonicalRange=[0, 1]))
    refs = [x['id'] for x in ev if x['outcome'] == 'present']
    later = dict(id=oid + ':after-maps', sourceId=src, describes={'from': od['until'], 'to': None}, supports=['state'], observationType='interpretation', interpretation=True,
                 constructionYear=None, note='Grundkartan 1968 ritar inte vägen, och den finns inte i OpenStreetMap. Exakt när den togs ur bruk är inte känt.')
    ev.append(later)
    catalog['objects'].append(dict(
        id=oid, name=od['name'], kind='roadSegment', independentRoad=True, ruralRoad=True, modernRoadClass=od['modernRoadClass'], roadWidth=od['roadWidth'], routeId=od['routeId'],
        states=[dict(state='open', **{'from': od['firstYear'], 'to': od['until']}, certainty='inferred', evidenceIds=refs, note=od['basis']),
                dict(state='unknown', **{'from': od['until'], 'to': None}, certainty='inferred', evidenceIds=[later['id']], note=later['note'])],
        geometryPeriods=[dict(geometryId=gid, **{'from': od['firstYear'], 'to': od['until']}, certainty='inferred', evidenceIds=refs, coverage='full', canonicalRange=[0, 1], basis=od['traceBasis'])],
        evidence=ev, sourceLinks=[],
        hammarlandsvagenMainRoad=dict(reviewedAt=review['reviewedAt'], oldRoad=True, referenceRange=od['referenceRange'], endSnapMeters=od['endSnapMeters'], constructionYear=None)))
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
