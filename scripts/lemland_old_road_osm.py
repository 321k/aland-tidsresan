"""Gamla Lemlandsvägen in today's road network: the old-road objects own the OpenStreetMap ways they survive as.

The early-map review (lemlandsvagen_main_road.py) added the old road between the canal and the church village as four
objects traced on the 1929 parish map, open 1917 until 1985/1995 and then 'unknown'. Much of it survives as local roads
(Knutsbodavägen, Kockobacka, Kommunrundan, Norra Söderbyvägen) that were drawn from the 2014 OSM snapshot on as
separate, unowned source lines: two identities for one road, and a 1929 line 3-30 m off where today's line is exact.

The review (data/lemland-old-road-osm.json) names, per object and phase, the OSM way ranges that are the old road and
where the 1929 trace has to fill a gap. This step builds each phase's line: OSM centre lines where the road survives,
and between them the 1929 trace moved linearly by the offset measured at the two OSM anchors (sheet error, not a road
move). The raw trace geometry is kept unchanged as evidence. From 1995 each object keeps only its surviving parts
(partial coverage) and owns those OSM ranges in every snapshot that has them; the rest is not reviewed after 1985.
Övre-Börs also gets the realignment the maps show: the 1929/1948 corner at Fridelund, the eased curve from 1968.
All checks run before any change. Map and snapshot years are first evidence, not construction years.
"""
from copy import deepcopy
from shapely.geometry import LineString, Point
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from mariehamn_lemlandsvagen_split import sub_path, fractional_index

YEARS = {'osm-2014': 2014, 'osm-2021': 2021, 'osm-2025': 2025, 'osm-2026': 2026}


def metric(path):
    return LineString([TO_METRIC(*p) for p in path])


def osm_piece(paths, piece):
    a, b = piece['range']; path = paths[piece['way']]
    if not (0 <= a < b <= len(path) - 1):
        raise ValueError('Invalid way range ' + piece['way'])
    part = sub_path(path, a, b)
    return part[::-1] if piece['reverse'] else part


def gap_piece(trace, start, end):
    """The 1929 trace between two anchors (geographic points or None for the trace ends), moved linearly from the
    offset at one anchor to the offset at the other."""
    T = metric(trace); L = T.length
    pa = Point(TO_METRIC(*start)) if start else Point(T.coords[0]); pb = Point(TO_METRIC(*end)) if end else Point(T.coords[-1])
    t1, t2 = (T.project(pa) if start else 0.0), (T.project(pb) if end else L)
    if t2 - t1 < 20:
        raise ValueError('Trace gap runs backwards or is empty')
    q1, q2 = T.interpolate(t1), T.interpolate(t2)
    d1, d2 = (pa.x - q1.x, pa.y - q1.y), (pb.x - q2.x, pb.y - q2.y)
    out = [list(start) if start else list(trace[0])]
    run = 0.0; coords = list(T.coords)
    for i in range(1, len(coords) - 1):
        run += Point(coords[i - 1]).distance(Point(coords[i]))
        if t1 < run < t2:
            f = (run - t1) / (t2 - t1); x, y = coords[i]
            out.append(list(TO_GEO(x + d1[0] + (d2[0] - d1[0]) * f, y + d1[1] + (d2[1] - d1[1]) * f)))
    out.append(list(end) if end else list(trace[-1]))
    return unloop(out), (t1, t2), (round(Point(d1).distance(Point(0, 0)), 1), round(Point(d2).distance(Point(0, 0)), 1))


def unloop(path, limit=30):
    """Cut small loops left by smoothing the trace (the line crossing itself), at the crossing point."""
    while True:
        m = [TO_METRIC(*p) for p in path]
        hit = next(((i, j) for i in range(len(m) - 1) for j in range(i + 2, len(m) - 1)
                    if LineString(m[i:i + 2]).crosses(LineString(m[j:j + 2]))), None)
        if not hit:
            return path
        i, j = hit
        if LineString(m[i + 1:j + 1]).length > limit:
            raise ValueError('The 1929 trace crosses itself over more than a small loop')
        x = LineString(m[i:i + 2]).intersection(LineString(m[j:j + 2]))
        path = path[:i + 1] + [list(TO_GEO(x.x, x.y))] + path[j + 1:]


def assemble(trace, paths, pieces, join):
    """One phase line, or (when it has no gaps and its OSM pieces do not touch) several."""
    built = [osm_piece(paths, p) if 'way' in p else None for p in pieces]
    lines, gaps, current = [], [], []
    for i, p in enumerate(pieces):
        if 'way' in p:
            part = built[i]
            if current and metric([current[-1], part[0]]).length > join:
                if pieces[i - 1].get('trace'):
                    raise ValueError('Gap does not end on its anchor')
                lines.append(current); current = []
            current = current + part[1:] if current else list(part)
        else:
            start = current[-1] if current else None
            end = built[i + 1][0] if i + 1 < len(pieces) else None
            part, span, offsets = gap_piece(trace, start, end)
            gaps.append(dict(traceRange=[round(span[0], 1), round(span[1], 1)], anchorOffsets=list(offsets)))
            current = current + part[1:] if current else part
    lines.append(current)
    return lines, gaps


def runs_along(path, lines, limit, step=2.0, shortest=25.0):
    """Fractional vertex ranges of path that lie within limit of one of lines, sampled every step metres."""
    segs = [metric(path[k:k + 2]).length for k in range(len(path) - 1)]
    samples = []
    for k, seg in enumerate(segs):
        n = max(1, int(seg // step))
        for i in range(n):
            samples.append(k + i / n)
    samples.append(float(len(path) - 1))
    near = []
    for t in samples:
        k = min(int(t), len(path) - 2); f = t - k
        x = Point(TO_METRIC(*[path[k][j] + (path[k + 1][j] - path[k][j]) * f for j in (0, 1)]))
        near.append(min(l.distance(x) for l in lines) <= limit)
    out, start = [], None
    for t, ok in zip(samples + [None], near + [False]):
        if ok and start is None:
            start = t
        elif not ok and start is not None:
            end = prev
            if end > start and metric(sub_path(path, start, end)).length >= shortest:
                out.append([round(start, 8), round(end, 8)])
            start = None
        prev = t
    return out


def apply_lemland_old_road_osm(read, catalog):
    review = read('data/lemland-old-road-osm.json'); lim = review['limits']
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}
    modern = {f['id']: f for f in read('dist/assets/modern.json.gz')['features']}
    snaps = {d: {f['id']: f for f in read(f'dist/assets/roads-{y}.json.gz')['features']} for d, y in YEARS.items() if y < 2026}
    if review['schemaVersion'] != 1 or review['source']['id'] in sources:
        raise ValueError('Old-road OSM review already applied')
    if any(s not in sources for s in review['snapshots'].values()):
        raise ValueError('Unknown snapshot source')
    paths = {}
    for w, h in review['wayHashes'].items():
        if w not in modern or digest(modern[w]['paths']) != h or len(modern[w]['paths']) != 1:
            raise ValueError('Changed OpenStreetMap way ' + w)
        paths[w] = modern[w]['paths'][0]
    for d, feats in review['snapshotHashes'].items():
        for fid, h in feats.items():
            if fid not in snaps[d] or digest(snaps[d][fid]['paths']) != h:
                raise ValueError('Changed snapshot feature ' + fid)
    for u in review['unchanged']:
        if fingerprint(objects[u['id']]) != u['inputHash']:
            raise ValueError('Changed old-road object ' + u['id'])

    owned = {}
    for o in catalog['objects']:
        for l in o.get('sourceLinks', []):
            owned.setdefault((l['datasetId'], l['featureId']), []).append(l.get('sourceVertexRange'))
    roads = [(o, gp, metric(p)) for o in catalog['objects'] if o['kind'] == 'roadSegment' and not o['id'].startswith('road:lemland:gamla-lemlandsvagen:')
             for gp in o['geometryPeriods'] for p in geometries[gp['geometryId']]['paths'] if len(p) > 1]
    # Ends may also rest on another old-road object (the old road continued where today's road did not yet run).
    anchor_roads = roads + [(o, gp, metric(p)) for o in catalog['objects'] if o['id'].startswith('road:lemland:gamla-lemlandsvagen:')
                            for gp in o['geometryPeriods'] for p in geometries[gp['geometryId']]['paths'] if len(p) > 1]

    def open_during(o, gp, a, b):
        return gp['from'] < (b or 9999) and a < (gp['to'] or 9999) and any(
            s['state'] == 'open' and s['from'] < (b or 9999) and a < (s['to'] or 9999) for s in o['states'])

    plans = []
    for spec in review['objects']:
        obj = objects.get(spec['id'])
        if not obj or fingerprint(obj) != spec['inputHash']:
            raise ValueError('Changed old-road object ' + spec['id'])
        tg = geometries[spec['traceGeometryId']]
        if digest(tg) != spec['traceGeometryHash'] or obj['geometryPeriods'][0]['geometryId'] != tg['id'] or len(obj['geometryPeriods']) != 1:
            raise ValueError('Changed old-road trace ' + spec['id'])
        trace = tg['paths'][0]; T = metric(trace); start, end = obj['states'][0]['from'], obj['states'][0]['to']
        phases = spec['phases']
        if phases[0]['from'] != start or phases[-1]['to'] is not None or any(a['to'] != b['from'] for a, b in zip(phases, phases[1:])):
            raise ValueError('Phases do not run from the first year without gaps')
        if phases[-1]['from'] != end or [s['state'] for s in obj['states']] != ['open', 'unknown']:
            raise ValueError('The surviving phase must begin where the reviewed maps end')
        built = []
        for k, ph in enumerate(phases):
            lines, gaps = assemble(trace, paths, ph['pieces'], lim['joinMeters'])
            last = k == len(phases) - 1
            if not last and (len(lines) != 1 or not metric(lines[0]).is_simple):
                raise ValueError(f'Phase {ph["from"]} of {spec["id"]} is not one simple line')
            if last and any(p.get('trace') for p in ph['pieces']):
                raise ValueError('The surviving phase may hold only OpenStreetMap ways')
            line = metric(lines[0]) if len(lines) == 1 else None
            if ph.get('traceCheck'):
                # Same road: the 1929 trace stays close along its whole length (sheet error 3-30 m, junction wobbles more).
                ds = sorted([line.distance(T.interpolate(x)) for x in range(0, int(T.length), 10)])
                far = max(max(T.distance(Point(c)) for c in line.coords), max(line.distance(Point(c)) for c in T.coords))
                if far > lim['traceMeters'] or ds[int(len(ds) * 0.9)] > lim['traceP90Meters']:
                    raise ValueError(f'Phase {ph["from"]} of {spec["id"]} leaves its 1929 trace ({far:.0f} m, 90 % within {ds[int(len(ds) * 0.9)]:.0f} m)')
            if not last:
                ends = [Point(line.coords[0]), Point(line.coords[-1])]; raw = [Point(T.coords[0]), Point(T.coords[-1])]
                for e, r in zip(ends, raw):
                    anchors = [l for o, gp, l in anchor_roads if o['id'] != spec['id'] and open_during(o, gp, ph['from'], ph['to']) and l.distance(r) < 1.0]
                    if not anchors or min(l.distance(e) for l in anchors) > lim['anchorMeters']:
                        raise ValueError(f'Phase {ph["from"]} of {spec["id"]} does not end on the road its trace ends on')
            for o, gp, other in roads:
                if open_during(o, gp, ph['from'], ph['to']):
                    # Longest continuous run beside another road; junctions and crossings give short contacts.
                    hits = [other.intersection(metric(p).buffer(lim['overlapBuffer'])) for p in lines]
                    run = max([g.length for h in hits for g in getattr(h, 'geoms', [h])] + [0])
                    if run > lim['overlapMeters']:
                        raise ValueError(f'Phase {ph["from"]} of {spec["id"]} runs {run:.0f} m along {o["id"]}')
            built.append(dict(lines=lines, gaps=gaps))
        survivors = [p for p in phases[-1]['pieces']]
        previous = built[-2]['lines'][0]; P = metric(previous)
        ranges = []
        for line in built[-1]['lines']:
            m = metric(line); a, b = P.project(Point(m.coords[0])), P.project(Point(m.coords[-1]))
            if b <= a or max(P.distance(Point(c)) for c in m.coords) > 0.05:
                raise ValueError('Surviving part is not part of the line before it')
            ranges.append([round(a / P.length, 6), round(b / P.length, 6)])
        ranges.sort()
        if any(x[1] > y[0] for x, y in zip(ranges, ranges[1:])):
            raise ValueError('Surviving parts overlap')
        # Source ownership. 2026: exactly the reviewed way ranges. Earlier snapshots split and drew the same OSM ways
        # differently, so each same-id snapshot feature owns the runs of it (sampled every 2 m, at least 25 m long)
        # that lie within the link limit of a surviving line; the rest of the feature stays unowned.
        links = []
        for p in survivors:
            path = paths[p['way']]; a, b = p['range']
            links.append(dict(datasetId='osm-2026', featureId=p['way'], sourceVertexRange=[a, b], sourceVertexCount=len(path), year=2026))
        ids = sorted({p['way'][4:] for p in survivors}); surv = [metric(line) for line in built[-1]['lines']]
        for d, y in YEARS.items():
            if y == 2026:
                continue
            missing = [f'road-{y}-{i}' for i in ids if f'road-{y}-{i}' in snaps[d] and f'road-{y}-{i}' not in review['snapshotHashes'][d]]
            if missing:
                raise ValueError('Snapshot features left out of the review: ' + ', '.join(missing))
            for fid in sorted(review['snapshotHashes'][d]):
                if fid.rsplit('-', 1)[1] not in ids:
                    continue
                f = snaps[d][fid]
                if len(f['paths']) != 1:
                    raise ValueError('Split snapshot feature ' + fid)
                for a, b in runs_along(f['paths'][0], surv, lim['linkMeters']):
                    links.append(dict(datasetId=d, featureId=fid, sourceVertexRange=[a, b], sourceVertexCount=len(f['paths'][0]), year=y))
        for l in links:
            for r in owned.get((l['datasetId'], l['featureId']), []):
                if r is None or max(r[0], l['sourceVertexRange'][0]) < min(r[1], l['sourceVertexRange'][1]) - 1e-8:
                    raise ValueError(f'{l["featureId"]} is already owned')
        plans.append((spec, obj, tg, built, ranges, links))

    # All checks passed. Change the catalogue.
    src = review['source']['id']; catalog['sources'].append(deepcopy(review['source']))
    for spec, obj, tg, built, ranges, links in plans:
        oid = spec['id']; base = 'geometry:' + oid.split(':', 1)[1]
        ev = [dict(id=oid + ':osm-review', sourceId=src, describes={'from': spec['phases'][0]['from'], 'to': None}, supports=['identity', 'geometry', 'state'],
                   observationType='interpretation', interpretation=True, constructionYear=None, originalGeometryId=tg['id'],
                   note='Den gamla vägen är samma väg som ' + ', '.join(spec['modernNames']) + ' i OpenStreetMap där den finns kvar. Linjen följer OpenStreetMap där; '
                        'sockenkartans förskjutning flyttar inte vägen. Det oflyttade spåret från 1929 finns kvar som källgeometri.')]
        for y in sorted({l['year'] for l in links}):
            d = next(k for k, v in YEARS.items() if v == y)
            ev.append(dict(id=f'{oid}:osm-{y}', sourceId=review['snapshots'][d], describes={'from': y, 'to': y + 1}, observationType='source-snapshot', interpretation=True,
                           outcome='present', supports=['geometry', 'identity', 'state'], coverage='partial', canonicalRanges=deepcopy(ranges) if len(ranges) > 1 else None,
                           canonicalRange=deepcopy(ranges[0]) if len(ranges) == 1 else None, matchedGeometryId=f'{base}:osm-survivor', constructionYear=None,
                           note=f'OpenStreetMap {y} har vägen här: ' + ', '.join(sorted({l["featureId"] for l in links if l["year"] == y})) + '. Kartläggningsår, inte byggår.'))
            if len(ranges) > 1: del ev[-1]['canonicalRange']
            else: del ev[-1]['canonicalRanges']
        early = [e['id'] for e in obj['evidence'] if e.get('outcome') == 'present']
        periods = []
        for k, (ph, b) in enumerate(zip(spec['phases'], built)):
            last = k == len(spec['phases']) - 1
            gid = f'{base}:osm-survivor' if last else f'{base}:phase-{ph["from"]}'
            catalog['geometries'].append(dict(id=gid, representation='centerline', paths=deepcopy(b['lines']), sourceIds=['city-2026'] if last else ['city-2026', tg['sourceIds'][0]],
                                              note='Kvarvarande delar i OpenStreetMap 2026.' if last else 'OpenStreetMap där vägen finns kvar; däremellan 1929 års spår flyttat med förskjutningen vid fästpunkterna.'))
            if last:
                refs = [oid + ':osm-review'] + [e['id'] for e in ev if e['id'].startswith(oid + ':osm-') and e['id'] != oid + ':osm-review']
                cov = dict(coverage='partial', canonicalRanges=deepcopy(ranges)) if len(ranges) > 1 else dict(coverage='partial', canonicalRange=deepcopy(ranges[0]))
            else:
                years = [y for y in (1917, 1929, 1948, 1968, 1978, 1985) if ph['from'] <= y < ph['to']]
                refs = [oid + ':osm-review'] + [e for e in early if int(e.rsplit('-', 1)[1]) in years]
                cov = dict(coverage='full', canonicalRange=[0, 1])
            periods.append(dict(geometryId=gid, **{'from': ph['from'], 'to': ph['to']}, certainty='inferred', evidenceIds=refs, basis=ph['basis'], **cov))
        if spec.get('realignment'):
            r = spec['realignment']
            ev.append(dict(id=f'{oid}:realigned-{r["year"]}', sourceId=src, describes={'from': r['year'], 'to': None}, supports=['geometry'],
                           observationType='interpretation', interpretation=True, constructionYear=None, note=r['note'] + f' Kartorna {r["previousMap"]} och {r["map"]} avgränsar ändringen; inget byggår antas.'))
            for p in periods:
                if p['from'] == r['year']:
                    p['evidenceIds'].append(f'{oid}:realigned-{r["year"]}')
        previous = dict(name=obj['name'], states=deepcopy(obj['states']), geometryPeriods=deepcopy(obj['geometryPeriods']))
        survivor = spec['phases'][-1]['basis']
        obj['name'] = spec['name']; obj['evidence'] += ev
        obj['states'] = [dict(state='open', **{'from': obj['states'][0]['from'], 'to': None}, certainty='inferred',
                              evidenceIds=deepcopy(obj['states'][0]['evidenceIds']) + [e['id'] for e in ev if e['id'] != oid + ':osm-review' and e.get('outcome') == 'present'],
                              note=obj['states'][0]['note'] + ' ' + survivor)]
        obj['geometryPeriods'] = periods
        obj['sourceLinks'] = [dict(datasetId=l['datasetId'], featureId=l['featureId'], sourceVertexRange=l['sourceVertexRange'], sourceVertexCount=l['sourceVertexCount'],
                                   basis='Den gamla Lemlandsvägen; endast den del av vägen som är den gamla sträckningen ägs. Anslutningar som byggts senare lämnas kvar.') for l in links]
        obj['lemlandOldRoadOsm'] = dict(reviewedAt=review['reviewedAt'], modernNames=spec['modernNames'], previous=previous, survivingRanges=ranges,
                                        gaps={str(ph['from']): b['gaps'] for ph, b in zip(spec['phases'], built) if b['gaps']},
                                        snapshotYears=sorted({l['year'] for l in links}), constructionYear=None)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
