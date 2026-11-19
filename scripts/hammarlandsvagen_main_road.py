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
The same step applies the southern review (data/hammarlandsvagen-south.json) and the old road through Näfsby
(data/hammarlandsvagen-nafsby.json: the smaller roads it survives as, and its vanished pieces as one old-road object),
Kattby westwards (data/hammarlandsvagen-kattby.json) and the Marsund connection at Marby–Kyrkoby
(data/hammarlandsvagen-marsund.json).
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
    _apply(read, catalog, 'data/hammarlandsvagen-main-road.json')


def apply_hammarlandsvagen_south(read, catalog):
    """The southern half: older roads on the route Mariehamn–Söderby (see docs/hammarlandsvagen-south.md)."""
    _apply(read, catalog, 'data/hammarlandsvagen-south.json')


def apply_hammarlandsvagen_kattby(read, catalog):
    """West of Kattby: today's road is the road on the 1929 parish maps (docs/hammarlandsvagen-kattby.md)."""
    _apply(read, catalog, 'data/hammarlandsvagen-kattby.json')


def apply_hammarlandsvagen_nafsby(read, catalog):
    """The old road through Näfsby: the smaller roads it survives as, and the vanished link (docs/hammarlandsvagen-nafsby.md)."""
    _apply(read, catalog, 'data/hammarlandsvagen-nafsby.json')


def apply_hammarlandsvagen_marsund(read, catalog):
    """The Marsund connection, Marby–Kyrkoby in Eckerö: where today's road is the road on the 1929 parish map
    (docs/hammarlandsvagen-marsund.md)."""
    _apply(read, catalog, 'data/hammarlandsvagen-marsund.json')


def _path_cuts(e, o, g):
    """Cuts on a geometry of several paths. 'pathOrder' lists the paths in order along the road; each must start where
    the one before it ends. 'pathRanges' are [path, from, to] in metres along that path, in order along the road.
    Cuts that run on across a path boundary form one stretch; the stretches must be 'ranges' (metres along the whole
    object in path order). Each cut is at least 50 m, unless it is a whole path within a longer stretch."""
    order = e['pathOrder']; n = len(g['paths'])
    if sorted(order) != list(range(n)):
        raise ValueError('Invalid path order ' + e['objectId'])
    lines = {i: metric(g['paths'][i]) for i in order}
    for x, y in zip(order, order[1:]):
        if Point(lines[x].coords[-1]).distance(Point(lines[y].coords[0])) > SAME_ROAD_GAP:
            raise ValueError(f'Paths {x} and {y} do not follow each other: ' + e['objectId'])
    offset, at = {}, 0.0
    for i in order:
        offset[i] = at; at += lines[i].length
    parts, spans = [], []
    for i, a, b in e['pathRanges']:
        whole_path = i in lines and a == 0 and abs(b - lines[i].length) < 0.1
        if i not in lines or a < 0 or b > lines[i].length + 0.1 or (b - a < 50 and not whole_path):
            raise ValueError('Invalid path cut ' + e['objectId'])
        parts.append(cut(g['paths'][i], lines[i], a, b)); spans.append([offset[i] + a, offset[i] + min(b, lines[i].length)])
    stretches = []
    for a, b in spans:
        if stretches and a < stretches[-1][1] - 0.1:
            raise ValueError('Path cuts are not in order along the road ' + e['objectId'])
        if stretches and a - stretches[-1][1] < 0.1:
            stretches[-1][1] = b
        else:
            stretches.append([a, b])
    if len(stretches) != len(e['ranges']) or any(b - a < 50 for a, b in stretches) \
            or any(abs(s - r) > 0.5 for x, y in zip(stretches, e['ranges']) for s, r in zip(x, y)):
        raise ValueError('Path cuts do not make the reviewed ranges ' + e['objectId'])
    return (e, o, g, parts, False, [[round(a / at, 6), round(b / at, 6)] for a, b in stretches])


def _apply(read, catalog, path_):
    review = read(path_)
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}; src = review['source']['id']
    if review['schemaVersion'] != 1 or src in sources:
        raise ValueError('Hammarlandsvägen review already applied')
    # maps: label -> source id (the label is the year), or label -> {sourceId, year} when two sheets share a year.
    labels = {k: (v if isinstance(v, dict) else dict(sourceId=v, year=int(k))) for k, v in review['maps'].items()}
    if any(s['id'] in sources for s in review['sources']) or any(l['sourceId'] not in sources | {s['id'] for s in review['sources']} for l in labels.values()):
        raise ValueError('Unexpected map sources')
    maps = {int(k): l['sourceId'] for k, l in labels.items() if k.isdigit()}
    prefix = review.get('geometryPrefix', 'geometry:hammarlandsvagen-1929:')

    plans, stages = [], {}
    for e in review['early']:
        o = objects.get(e['objectId'])
        if not o or fingerprint(o) != e['inputHash']:
            raise ValueError('Changed Hammarlandsvägen input ' + e['objectId'])
        g = geometries[e['geometryId']]
        # The early period normally cuts the object's first geometry. 'laterGeometry': a later geometry of the same
        # object, where the old road is longer than what the first map after it draws (that map is then the gap below).
        own = [gp['geometryId'] for gp in o['geometryPeriods']] if e.get('laterGeometry') else [o['geometryPeriods'][0]['geometryId']]
        # A geometry of several paths is dated whole ('wholeGeometry'), on one of its paths ('pathIndex'), or by cuts
        # on its paths ('pathRanges', see _path_cuts).
        multi = len(g['paths']) != 1 and 'pathIndex' not in e; pi = e.get('pathIndex', 0)
        if digest(g) != e['geometryHash'] or g['id'] not in own or (multi and not (e.get('wholeGeometry') or 'pathRanges' in e)) or not 0 <= pi < len(g['paths']):
            raise ValueError('Changed Hammarlandsvägen geometry ' + e['objectId'])
        path = g['paths'][pi]; line = metric(path) if not multi else None
        length = sum(metric(p).length for p in g['paths']) if multi else line.length
        if abs(length - e['lengthMeters']) > 0.05:
            raise ValueError('Changed Hammarlandsvägen length ' + e['objectId'])
        first = o['states'][0]['from']
        # 'gapUntil': the old road is open until 'until'; between it and the object's first year no map secures it
        # ('unknown'). The gap must be marked on a map as neither present nor absent.
        gap = e.get('gapUntil')
        if (gap if gap else e['until']) != first or o['geometryPeriods'][0]['from'] != first or e['firstYear'] >= first:
            raise ValueError('The early period must end where the object now begins: ' + e['objectId'])
        if gap and not (e['firstYear'] < e['until'] < gap and any(v == 'unclear' and e['until'] <= labels[k]['year'] < gap for k, v in e['maps'].items() if k in labels)
                        and not any(v == 'absent' for v in e['maps'].values()) and review['gapBasis'].get(e['objectId'])):
            raise ValueError('Invalid gap before the object begins: ' + e['objectId'])
        if not set(e['maps']) <= set(labels) or min(labels[k]['year'] for k, v in e['maps'].items() if v == 'present') != e['firstYear']:
            raise ValueError('First year is not the first map marked present: ' + e['objectId'])
        rs = e['ranges']
        if multi and 'pathRanges' in e:
            plans.append(_path_cuts(e, o, g)); continue
        if multi:       # a geometry of several paths is dated whole, or by explicit cuts on its paths ('pathRanges')
            if rs != [[0.0, round(length, 1)]]:
                raise ValueError('Invalid same-road ranges ' + e['objectId'])
            plans.append((e, o, g, deepcopy(g['paths']), True, [[0, 1]])); continue
        whole = len(rs) == 1 and rs[0][0] == 0 and abs(rs[0][1] - line.length) < 0.1     # a short object may be dated whole
        if not rs or any(a < 0 or b > line.length + 0.1 or (b - a < 50 and not whole) for a, b in rs) or any(x[1] >= y[0] for x, y in zip(rs, rs[1:])):
            raise ValueError('Invalid same-road ranges ' + e['objectId'])
        parts = [cut(path, line, a, b) for a, b in rs]
        full = whole and len(g['paths']) == 1
        plans.append((e, o, g, parts, full, [[round(a / line.length, 6), round(min(b, line.length) / line.length, 6)] for a, b in rs]))
        # 'laterStage': from a later map the old road is longer on this object (it moved onto more of it). A second early
        # period from that map's year, with its own ranges, until the object's first year. That map must be marked present.
        st = e.get('laterStage')
        if st:
            r2 = st['ranges']; y2 = st['firstYear']
            if not (e['firstYear'] < y2 < e['until']) or e.get('gapUntil') or not any(labels[k]['year'] == y2 and v == 'present' for k, v in e['maps'].items() if k in labels) \
                    or not r2 or any(a < 0 or b > line.length + 0.1 or b - a < 50 for a, b in r2) or any(x[1] >= y[0] for x, y in zip(r2, r2[1:])) \
                    or not review['laterStageBasis'].get(e['objectId']):
                raise ValueError('Invalid later stage ' + e['objectId'])
            stages[e['objectId']] = ([cut(path, line, a, b) for a, b in r2], [[round(a / line.length, 6), round(min(b, line.length) / line.length, 6)] for a, b in r2])

    # The same-road objects follow each other along the road (the reference line) in the reviewed order.
    # Together the cuts cover each reviewed same-road interval of today's road exactly once, without gaps.
    ref = LineString(review['reference']) if 'sameRoad' in review else None
    for s, e in review.get('sameRoad', []):
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
    for prev, nxt in (zip(plans, plans[1:]) if ref is not None else []):
        if prev[5][-1][1] == 1 and nxt[5][0][0] == 0:        # a stretch runs on across the object boundary
            a, b = metric(prev[3][-1]), metric(nxt[3][0])
            if min(Point(a.coords[i]).distance(Point(b.coords[j])) for i in (0, -1) for j in (0, -1)) > SAME_ROAD_GAP:
                raise ValueError(f'Same-road stretch breaks between {prev[0]["objectId"]} and {nxt[0]["objectId"]}')

    # The old line (Smedens; at Näfsby its vanished pieces, 'paths'): ends on today's roads, not along any road open
    # while it is, and not surviving in OSM.
    od = review.get('oldRoad')
    if od and od['id'] in objects:
        raise ValueError('Duplicate old-road identity ' + od['id'])
    if od:
        od_paths = od['paths'] if 'paths' in od else [od['path']]
        olds = [metric(p) for p in od_paths]
        if abs(sum(o_.length for o_ in olds) - od['lengthMeters']) > 0.5 or max(od['endSnapMeters']) > od.get('endSnapLimit', 25) \
                or len(od['endSnapMeters']) != 2 * len(olds):
            raise ValueError('Changed old line ' + od['id'])
        year = lambda k: labels[k]['year'] if k in labels else int(k)
        present, absent = ([year(y) for y, v in od['maps'].items() if v == want] for want in ('present', 'absent'))
        if not all(k in labels or k.isdigit() for k in od['maps']) or not present or not absent or min(present) != od['firstYear'] or od['until'] != min(absent):
            raise ValueError('Old road dates do not follow its maps')
        today = [metric(p) for oid in od.get('endObjects', ['road:rural:hammarland-way-345142933', 'road:rural:hammarland-way-345143750'])
                 for p in geometries[objects[oid]['geometryPeriods'][0]['geometryId']]['paths']]
        # 'freeEnds': [path, 0 | -1] ends that are not on a road (a ferry pier), each with a stated reason.
        free = [tuple(x) for x in od.get('freeEnds', [])]
        if free and (not all(len(x) == 2 and 0 <= x[0] < len(olds) and x[1] in (0, -1) for x in free) or not od.get('freeEndBasis')):
            raise ValueError('Invalid free end ' + od['id'])
        for k, o_ in enumerate(olds):
            for i in (0, -1):
                if (k, i) not in free and min(t.distance(Point(o_.coords[i])) for t in today) > END_LIMIT:
                    raise ValueError('Old line does not end on today\'s road: ' + od['id'])
        early_lines = [metric(p) for pl in plans for p in pl[3]]
        for o in catalog['objects']:
            if o['kind'] != 'roadSegment': continue
            for gp in o['geometryPeriods']:
                if gp['from'] < od['until'] and od['firstYear'] < (gp['to'] or 9999):
                    for p in geometries[gp['geometryId']]['paths']:
                        for old in olds:
                            hit = metric(p).intersection(old.buffer(OVERLAP_BUFFER)) if len(p) > 1 else None
                            if hit is not None and max([h.length for h in getattr(hit, 'geoms', [hit])] + [0]) > OVERLAP_LIMIT:
                                raise ValueError('Old line runs along ' + o['id'])
        for p in early_lines:
            for old in olds:
                hit = p.intersection(old.buffer(OVERLAP_BUFFER))
                if max([h.length for h in getattr(hit, 'geoms', [hit])] + [0]) > OVERLAP_LIMIT:
                    raise ValueError('Old line repeats a same-road stretch')
        modern = read('dist/assets/modern.json.gz')['features']
        for f in modern:
            if f.get('kind') != 'road' or f.get('name') == 'Hammarlandsvägen' or f.get('class') in ('footway', 'path', 'cycleway', 'steps'):
                continue
            for p in f['paths']:
                if len(p) > 1 and any(metric(p).intersection(old.buffer(SURVIVOR_BUFFER)).length > SURVIVOR_LIMIT for old in olds):
                    raise ValueError('The old line survives as ' + f['id'] + '; reconcile it instead of adding a separate object')

    # 'route': the old road as a chain of the dated cuts (and the old line) in order along it. Consecutive pieces meet
    # within 'joinMeters', except at the reviewed gaps, whose length is stated. 'repeat': pieces of several paths that the
    # route passes more than once (the old line's vanished pieces).
    rt = review.get('route')
    if rt:
        pieces = {pl[0]['objectId']: [metric(p) for p in pl[3]] for pl in plans}
        if od: pieces[od['id']] = olds
        for oid in rt.get('endObjects', []):
            pieces[oid] = [metric(p) for p in geometries[objects[oid]['geometryPeriods'][0]['geometryId']]['paths']]
        inner = [x for x in rt['order'] if x not in rt.get('endObjects', []) + rt.get('repeat', [])] + [x for x in rt.get('repeat', []) if x in rt['order']]
        if len(inner) != len(set(inner)) or set(inner) != set(pieces) - set(rt.get('endObjects', [])) or not set(rt['order']) <= set(pieces):
            raise ValueError('The old-road route does not list each dated piece once')
        gaps = {tuple(gp['between']): gp['meters'] for gp in rt.get('gaps', [])}
        for a, b in zip(rt['order'], rt['order'][1:]):
            d = min(Point(x.coords[i]).distance(y) for x in pieces[a] for y in pieces[b] for i in (0, -1))
            d = min(d, min(Point(y.coords[i]).distance(x) for x in pieces[a] for y in pieces[b] for i in (0, -1)))
            want = gaps.get((a, b))
            if (want is None and d > rt['joinMeters']) or (want is not None and abs(d - want) > 2):
                raise ValueError(f'The old-road route breaks between {a} and {b} ({round(d, 1)} m)')

    # All checks passed. Change the catalogue.
    catalog['sources'] += [deepcopy(s) for s in review['sources']] + [deepcopy(review['source'])]

    def map_evidence(oid, outcomes, gid, note, coverage):
        ev = []
        for k in sorted(outcomes, key=lambda k: (labels[k]['year'] if k in labels else int(k), k)):
            outcome = outcomes[k]; y = labels[k]['year'] if k in labels else int(k)
            e = dict(id=f'{oid}:parish-map-{k}', sourceId=labels[k]['sourceId'] if k in labels else f'nls:101206:{y}', describes={'from': y, 'to': y + 1}, observationType='printed-map-review',
                     interpretation=True, outcome=outcome, supports=['geometry', 'identity', 'state'] if outcome == 'present' else ['state'], constructionYear=None, reviewId=src, note=note)
            if outcome == 'present':
                e.update(matchedGeometryId=gid, **coverage)
            ev.append(e)
        return ev

    for e, o, g, parts, full, ranges in plans:
        oid = e['objectId']; gid = prefix + oid.rsplit(':', 1)[1]
        cov = dict(coverage='full', canonicalRange=[0, 1]) if full else (dict(coverage='partial', canonicalRange=ranges[0]) if len(ranges) == 1 else dict(coverage='partial', canonicalRanges=ranges))
        catalog['geometries'].append(dict(id=gid, representation='centerline', paths=deepcopy(parts), sourceIds=deepcopy(g['sourceIds']),
                                          note=review.get('geometryNote', 'Del av objektets egen geometri (samma koordinater) där dagens väg är den väg sockenkartan 1929 ritar.')))
        basis = review['earlyBasis'][oid]
        ev = map_evidence(oid, e['maps'], gid, basis, cov)
        refs = [x['id'] for x in ev if x['outcome'] == 'present' and x['describes']['from'] == e['firstYear']]
        o['evidence'] += ev
        if oid in stages:
            parts2, ranges2 = stages[oid]; y2 = e['laterStage']['firstYear']; gid2 = f'{gid}:{y2}'; basis2 = review['laterStageBasis'][oid]
            cov2 = dict(coverage='partial', canonicalRange=ranges2[0]) if len(ranges2) == 1 else dict(coverage='partial', canonicalRanges=ranges2)
            catalog['geometries'].append(dict(id=gid2, representation='centerline', paths=deepcopy(parts2), sourceIds=deepcopy(g['sourceIds']), note=review['laterStageNote']))
            for x in ev:
                if x['outcome'] == 'present' and x['describes']['from'] >= y2:
                    x.update(matchedGeometryId=gid2, **cov2); x.pop('canonicalRange', None) if 'canonicalRanges' in cov2 else x.pop('canonicalRanges', None)
            refs2 = [x['id'] for x in ev if x['outcome'] == 'present' and x['describes']['from'] == y2]
            o['geometryPeriods'].insert(0, dict(geometryId=gid2, **{'from': y2, 'to': e['until']}, certainty='inferred', evidenceIds=refs2, basis=basis2, **cov2))
        if e.get('gapUntil'):
            gnote = review['gapBasis'][oid]
            gev = [x['id'] for x in ev if x['outcome'] == 'unclear']
            o['states'].insert(0, dict(state='unknown', **{'from': e['until'], 'to': e['gapUntil']}, certainty='inferred', evidenceIds=gev, note=gnote))
        o['states'].insert(0, dict(state='open', **{'from': e['firstYear'], 'to': e['until']}, certainty='inferred', evidenceIds=refs, note=basis))
        o['geometryPeriods'].insert(0, dict(geometryId=gid, **{'from': e['firstYear'], 'to': e['laterStage']['firstYear'] if oid in stages else e['until']}, certainty='inferred', evidenceIds=refs, basis=basis, **cov))
        o['hammarlandsvagenMainRoad'] = dict(reviewedAt=review['reviewedAt'], previousFirstYear=e.get('gapUntil', e['until']), ranges=e['ranges'], constructionYear=None,
                                             **({'pathIndex': e['pathIndex']} if 'pathIndex' in e else {}),
                                             **({'pathRanges': e['pathRanges']} if 'pathRanges' in e else {}),
                                             **({'laterStage': e['laterStage']} if oid in stages else {}),
                                             **({'unknownFrom': e['until']} if e.get('gapUntil') else {}),
                                             **({'review': src} if path_ != 'data/hammarlandsvagen-main-road.json' else {}))

    if od:
        oid = od['id']; gid = 'geometry:' + oid.split(':', 1)[1]
        catalog['geometries'].append(dict(id=gid, representation='centerline', paths=deepcopy(od_paths), sourceIds=[maps[1929]] if 1929 in maps else [labels[k]['sourceId'] for k, v in od['maps'].items() if v == 'present' and k in labels and labels[k]['year'] == od['firstYear']][:1], note=od['traceBasis']))
        ev = map_evidence(oid, od['maps'], gid, od['basis'], dict(coverage='full', canonicalRange=[0, 1]))
        refs = [x['id'] for x in ev if x['outcome'] == 'present']
        later = dict(id=oid + ':after-maps', sourceId=src, describes={'from': od['until'], 'to': None}, supports=['state'], observationType='interpretation', interpretation=True,
                     constructionYear=None, note=od.get('afterNote', 'Grundkartan 1968 ritar inte vägen, och den finns inte i OpenStreetMap. Exakt när den togs ur bruk är inte känt.'))
        ev.append(later)
        catalog['objects'].append(dict(
            id=oid, name=od['name'], kind='roadSegment', independentRoad=True, ruralRoad=True, modernRoadClass=od['modernRoadClass'], roadWidth=od['roadWidth'], routeId=od['routeId'],
            states=[dict(state='open', **{'from': od['firstYear'], 'to': od['until']}, certainty='inferred', evidenceIds=refs, note=od['basis']),
                    dict(state='unknown', **{'from': od['until'], 'to': None}, certainty='inferred', evidenceIds=[later['id']], note=later['note'])],
            geometryPeriods=[dict(geometryId=gid, **{'from': od['firstYear'], 'to': od['until']}, certainty='inferred', evidenceIds=refs, coverage='full', canonicalRange=[0, 1], basis=od['traceBasis'])],
            evidence=ev, sourceLinks=[],
            hammarlandsvagenMainRoad=dict(reviewedAt=review['reviewedAt'], oldRoad=True, referenceRange=od['referenceRange'], endSnapMeters=od['endSnapMeters'], constructionYear=None)))
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])


def apply_hammarlandsvagen_frebbenby(read, catalog):
    """Marsundsvägen from Frebbenby to the old ferry pier: the road to the Marsund ferry on the 1929 parish map
    (docs/hammarlandsvagen-frebbenby.md)."""
    _apply(read, catalog, 'data/hammarlandsvagen-frebbenby.json')


def apply_hammarlandsvagen_marby(read, catalog):
    """The old road on the Eckerö side of the ferry, Marby–Klemes–Nissas: Marbyvägen and the vanished link at Sundkvist
    (docs/hammarlandsvagen-ferry-west.md)."""
    _apply(read, catalog, 'data/hammarlandsvagen-marby.json')


def apply_hammarlandsvagen_shore(read, catalog):
    """The vanished shore road from the narrow sound south to Nissas, 1929–1956 (docs/hammarlandsvagen-ferry-west.md)."""
    _apply(read, catalog, 'data/hammarlandsvagen-shore.json')


def apply_hammarlandsvagen_overby(read, catalog):
    """The old road through Överby (docs/hammarlandsvagen-overby.md). The 1929 parish map and the base maps 1968 and
    1978 draw the main road north through the village; today's bypass is first a road on the 1985 base map (1978: an
    uncased overprint). Two changes, both checked before either is made:
    - 'bypass': the Marsund connection's period from 1959 is split. Until the first map that draws the bypass, it
      leaves out the bypass pieces of one of its paths (cuts of the same coordinates); from then on, as before.
    - 'oldRoad': a new object for the two loops of the old road, the main road until the bypass, with its own trace
      where nothing survives and the OSM coordinates of Gamla Landsvägen and Brinkbacken where they do. After the
      bypass it is only those surviving parts, the same coordinates, and owns them in OSM (partial source links)."""
    review = read('data/hammarlandsvagen-overby.json')
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}; src = review['source']['id']
    if review['schemaVersion'] != 1 or src in sources:
        raise ValueError('Överby review already applied')
    labels = review['maps']
    if any(l['sourceId'] not in sources for l in labels.values()) or any(x['id'] in sources for x in review['sources']) \
            or review['oldRoad']['surveySourceId'] not in {x['id'] for x in review['sources']}:
        raise ValueError('Unexpected map sources')
    year = lambda k: labels[k]['year']

    def follows(maps_, first, until, what):
        if not set(maps_) <= set(labels):
            raise ValueError('Unknown map in ' + what)
        present = [year(k) for k, v in maps_.items() if v == 'present']
        absent = [year(k) for k, v in maps_.items() if v == 'absent']
        return present, absent

    # The bypass split.
    bp = review['bypass']; m = objects.get(bp['objectId'])
    if not m or fingerprint(m) != bp['inputHash']:
        raise ValueError('Changed Marsund input ' + bp['objectId'])
    g = geometries.get(bp['geometryId']); period = next((gp for gp in m['geometryPeriods'] if gp['from'] == bp['from']), None)
    if not g or digest(g) != bp['geometryHash'] or not period or period['geometryId'] != g['id'] or period['to'] is not None:
        raise ValueError('Changed Marsund geometry ' + bp['objectId'])
    present, absent = follows(bp['maps'], bp['from'], bp['until'], 'bypass')
    if not present or min(present) != bp['until'] or not absent or not all(bp['from'] <= y < bp['until'] for y in absent) \
            or any(v == 'unclear' and not bp['from'] <= year(k) < bp['until'] for k, v in bp['maps'].items()) or not review['bypassBasis']:
        raise ValueError('Bypass dates do not follow its maps')
    order = bp['pathOrder']; pi = bp['pathIndex']
    if sorted(order) != list(range(len(g['paths']))) or pi not in order:
        raise ValueError('Invalid path order ' + bp['objectId'])
    lines = {i: metric(g['paths'][i]) for i in order}; line = lines[pi]
    if abs(line.length - bp['pathLength']) > 0.05:
        raise ValueError('Changed Marsund path length')
    keep = bp['keep']
    if keep[0][0] != 0 or abs(keep[-1][1] - line.length) > 0.1 or any(b <= a for a, b in keep) or any(x[1] + 50 > y[0] for x, y in zip(keep, keep[1:])):
        raise ValueError('Invalid kept ranges of the Marsund path')
    split_paths = []
    for i, p in enumerate(g['paths']):
        split_paths += [cut(p, line, a, b) for a, b in keep] if i == pi else [deepcopy(p)]
    offset, at = {}, 0.0
    for i in order:
        offset[i] = at; at += lines[i].length
    removed = [[offset[pi] + x[1], offset[pi] + y[0]] for x, y in zip(keep, keep[1:])]
    canon, start = [], 0.0
    for a, b in removed:
        canon.append([round(start / at, 6), round(a / at, 6)]); start = b
    canon.append([round(start / at, 6), 1])

    # The old road.
    od = review['oldRoad']
    if od['id'] in objects:
        raise ValueError('Duplicate old-road identity ' + od['id'])
    present, absent = follows(od['maps'], od['firstYear'], od['mainUntil'], 'old road')
    if not present or min(present) != od['firstYear'] or od['mainUntil'] != bp['until'] or absent:      # open from its first map to today
        raise ValueError('Old road dates do not follow its maps')
    early = m['geometryPeriods'][0]
    if early['from'] != od['firstYear'] or early['to'] != bp['from']:
        raise ValueError('The Marsund connection has no early period from ' + str(od['firstYear']))
    olds = [metric(p) for p in od['paths']]
    if abs(sum(l.length for l in olds) - od['lengthMeters']) > 0.5:
        raise ValueError('Changed old line ' + od['id'])
    ends = lambda paths: [Point(metric(p).coords[i]) for p in paths for i in (0, -1)]
    for name, paths in (('the 1929 stretches', geometries[early['geometryId']]['paths']), ('the connection without the bypass', split_paths)):
        targets = ends(paths)
        if any(min(t.distance(e) for t in targets) > END_LIMIT for e in ends(od['paths'])):
            raise ValueError(f'Old road does not join {name}: ' + od['id'])
    trace = LineString(od['trace'])
    modern = {f['id']: f for f in read('dist/assets/modern.json.gz')['features']}
    if len(od['laterPaths']) != len(od['sourceLinks']):
        raise ValueError('Each surviving part needs one source link')
    for later, link in zip(od['laterPaths'], od['sourceLinks']):
        f = modern.get(link['featureId']); a, b = link['sourceVertexRange']
        if not f or link['datasetId'] != 'osm-2026' or len(f['paths']) != 1 or link['sourceVertexCount'] != len(f['paths'][0]) \
                or not (type(a) is int and type(b) is int and 0 <= a < b < len(f['paths'][0])):
            raise ValueError('Invalid surviving part ' + link['featureId'])
        run = f['paths'][0][a:b + 1]
        if later not in (run, run[::-1]):
            raise ValueError('A surviving part is not its OSM way: ' + link['featureId'])
        if not any(later == p[k:k + len(later)] for p in od['paths'] for k in range(len(p) - len(later) + 1)):
            raise ValueError('A surviving part moves at the bypass: ' + link['featureId'])
        if max(trace.distance(Point(q)) for q in metric(later).coords) > od['sameRoadMeters']:
            raise ValueError('A surviving part is not on the 1929 road: ' + link['featureId'])
    for o in catalog['objects']:
        if o['kind'] != 'roadSegment' or o['id'] == m['id']: continue
        for gp in o['geometryPeriods']:
            if gp['from'] < od['mainUntil'] and od['firstYear'] < (gp['to'] or 9999):
                for p in geometries[gp['geometryId']]['paths']:
                    for old in olds:
                        hit = metric(p).intersection(old.buffer(OVERLAP_BUFFER)) if len(p) > 1 else None
                        if hit is not None and max([h.length for h in getattr(hit, 'geoms', [hit])] + [0]) > OVERLAP_LIMIT:
                            raise ValueError('Old line runs along ' + o['id'])
    for p in geometries[early['geometryId']]['paths'] + split_paths:
        for old in olds:
            hit = metric(p).intersection(old.buffer(OVERLAP_BUFFER))
            if max([h.length for h in getattr(hit, 'geoms', [hit])] + [0]) > OVERLAP_LIMIT:
                raise ValueError('Old line runs along the Marsund connection')

    # All checks passed. Change the catalogue.
    catalog['sources'] += [deepcopy(x) for x in review['sources']] + [deepcopy(review['source'])]

    def evidence(oid, maps_, gid, note):
        ev = []
        for k in sorted(maps_, key=lambda k: (year(k), k)):
            outcome = maps_[k]; y = year(k)
            e = dict(id=f'{oid}:overby-map-{k}', sourceId=labels[k]['sourceId'], describes={'from': y, 'to': y + 1}, observationType='printed-map-review',
                     interpretation=True, outcome=outcome, supports=['geometry', 'identity', 'state'] if outcome == 'present' else ['state'], constructionYear=None, reviewId=src, note=note)
            if outcome == 'present' and gid:
                e.update(matchedGeometryId=gid)
            ev.append(e)
        return ev

    gid = review['geometryPrefix'] + 'marsund-without-bypass'
    catalog['geometries'].append(dict(id=gid, representation='centerline', paths=split_paths, sourceIds=deepcopy(g['sourceIds']), note=review['bypassGeometryNote']))
    ev = evidence(m['id'], bp['maps'], None, review['bypassBasis'])
    m['evidence'] += ev
    refs = [x['id'] for x in ev if x['outcome'] == 'absent']
    period['from'] = bp['until']
    period['evidenceIds'] = list(period.get('evidenceIds', [])) + [x['id'] for x in ev if x['outcome'] == 'present']
    k = m['geometryPeriods'].index(period)
    m['geometryPeriods'].insert(k, dict(geometryId=gid, **{'from': bp['from'], 'to': bp['until']}, certainty='inferred', evidenceIds=refs,
                                        basis=review['bypassBasis'], coverage='partial', canonicalRanges=canon))
    m['overbyBypass'] = dict(review=src, reviewedAt=review['reviewedAt'], firstMapYear=bp['until'], previousFrom=bp['from'], pathIndex=pi, keep=keep, constructionYear=None)

    oid = od['id']; g1, g2 = 'geometry:' + oid.split(':', 1)[1], 'geometry:' + oid.split(':', 1)[1] + ':surviving'
    catalog['geometries'].append(dict(id=g1, representation='centerline', paths=deepcopy(od['paths']), sourceIds=[labels['1929-eckero']['sourceId']], note=od['traceBasis']))
    catalog['geometries'].append(dict(id=g2, representation='centerline', paths=deepcopy(od['laterPaths']), sourceIds=[od['surveySourceId']], note=od['laterBasis']))
    ev = evidence(oid, od['maps'], g1, od['basis'])
    main = [x['id'] for x in ev if x['outcome'] == 'present' and x['describes']['from'] < od['mainUntil']]
    after = [x['id'] for x in ev if x['describes']['from'] >= od['mainUntil']]
    catalog['objects'].append(dict(
        id=oid, name=od['name'], kind='roadSegment', independentRoad=True, ruralRoad=True, modernRoadClass=od['modernRoadClass'], roadWidth=od['roadWidth'], routeId=od['routeId'],
        states=[dict(state='open', **{'from': od['firstYear'], 'to': None}, certainty='inferred', evidenceIds=main, note=od['basis'])],
        geometryPeriods=[dict(geometryId=g1, **{'from': od['firstYear'], 'to': od['mainUntil']}, certainty='inferred', evidenceIds=main, coverage='full', canonicalRange=[0, 1], basis=od['traceBasis']),
                         dict(geometryId=g2, **{'from': od['mainUntil'], 'to': None}, certainty='inferred', evidenceIds=after, coverage='partial', canonicalRanges=od['laterCanonicalRanges'], basis=od['laterBasis'])],
        evidence=ev, sourceLinks=deepcopy(od['sourceLinks']),
        hammarlandsvagenMainRoad=dict(reviewedAt=review['reviewedAt'], oldRoad=True, review=src, mainRoadUntil=od['mainUntil'], constructionYear=None)))
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])


SNAPSHOTS = {'osm-2026': ('dist/assets/modern.json.gz', 'way/'), 'osm-2014': ('dist/assets/roads-2014.json.gz', 'road-2014-'),
             'osm-2021': ('dist/assets/roads-2021.json.gz', 'road-2021-'), 'osm-2025': ('dist/assets/roads-2025.json.gz', 'road-2025-')}


def apply_hammarlandsvagen_holmberg(read, catalog):
    """Holmberg (docs/hammarlandsvagen-holmberg.md): the 1929 road from the narrow sound straight across Holmberg to the
    ferry pier (an old-road object, through _apply), and Öravägen, the road to the later pier at Örliden, first on the
    1956 edition. Öravägen is a new object from its OSM way, which it owns in the 2014, 2021, 2025 and 2026 extracts.
    Öravägen's checks run first; then _apply checks the old road before anything changes."""
    path_ = 'data/hammarlandsvagen-holmberg.json'
    review = read(path_); nr = review['newRoad']
    objects = {o['id']: o for o in catalog['objects']}; sources = {s['id'] for s in catalog['sources']}
    labels = review['maps']
    if nr['id'] in objects or nr['surveySourceId'] in sources:
        raise ValueError('Duplicate new road ' + nr['id'])
    present = [labels[k]['year'] for k, v in nr['maps'].items() if v == 'present']
    if not set(nr['maps']) <= set(labels) or not present or min(present) != nr['firstYear'] or any(v == 'absent' for v in nr['maps'].values()):
        raise ValueError('New road dates do not follow its maps')
    owned = {(l['datasetId'], l['featureId']) for o in catalog['objects'] for l in o.get('sourceLinks', [])}
    if {l['datasetId'] for l in nr['sourceLinks']} != set(SNAPSHOTS):
        raise ValueError('The new road must be owned in every OSM extract')
    for l in nr['sourceLinks']:
        file, prefix = SNAPSHOTS[l['datasetId']]
        f = next((x for x in read(file)['features'] if x['id'] == l['featureId']), None)
        a, b = l['sourceVertexRange']
        if not f or not l['featureId'].startswith(prefix) or len(f['paths']) != 1 or digest(f['paths']) != l['input'] \
                or l['sourceVertexCount'] != len(f['paths'][0]) or [a, b] != [0, len(f['paths'][0]) - 1]:
            raise ValueError('Changed or partial OSM source ' + l['featureId'])
        if (l['datasetId'], l['featureId']) in owned:
            raise ValueError('OSM source already owned: ' + l['featureId'])
        if l['datasetId'] == 'osm-2026' and f['paths'] != nr['paths']:
            raise ValueError('The new road is not its OSM way')

    _apply(read, catalog, path_)

    gid = 'geometry:' + nr['id'].split(':', 1)[1]
    catalog['sources'].append(deepcopy(review['newRoadSource']))
    catalog['geometries'].append(dict(id=gid, representation='centerline', paths=deepcopy(nr['paths']), sourceIds=[nr['surveySourceId']], note=nr['geometryNote']))
    ev = []
    for k in sorted(nr['maps'], key=lambda k: labels[k]['year']):
        y = labels[k]['year']; outcome = nr['maps'][k]
        e = dict(id=f"{nr['id']}:map-{k}", sourceId=labels[k]['sourceId'], describes={'from': y, 'to': y + 1}, observationType='printed-map-review', interpretation=True,
                 outcome=outcome, supports=['geometry', 'identity', 'state'] if outcome == 'present' else ['state'], constructionYear=None, reviewId=review['source']['id'], note=nr['basis'])
        if outcome == 'present':
            e.update(matchedGeometryId=gid, coverage='full', canonicalRange=[0, 1])
        ev.append(e)
    first = [x['id'] for x in ev if x['describes']['from'] == nr['firstYear']]
    catalog['objects'].append(dict(
        id=nr['id'], name=nr['name'], kind='roadSegment', independentRoad=True, ruralRoad=True, modernRoadClass=nr['modernRoadClass'], roadWidth=nr['roadWidth'], routeId=nr['routeId'],
        states=[dict(state='open', **{'from': nr['firstYear'], 'to': None}, certainty='inferred', evidenceIds=first, note=nr['basis'])],
        geometryPeriods=[dict(geometryId=gid, **{'from': nr['firstYear'], 'to': None}, certainty='inferred', evidenceIds=first, coverage='full', canonicalRange=[0, 1], basis=nr['geometryNote'])],
        evidence=ev, sourceLinks=[{k: v for k, v in l.items() if k != 'input'} for l in nr['sourceLinks']],
        hammarlandsvagenMainRoad=dict(reviewedAt=review['reviewedAt'], review=review['source']['id'], newFromOsm=True, constructionYear=None)))
