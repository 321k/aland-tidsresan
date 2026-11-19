"""The named buildings of the 1860 town plan, shown as planned in 1860.

`data/plan-1860-buildings.json` holds each building's outline as traced on G. Th. Chiewitz's plan
(dist/assets/mariehamn-plan-1860.png), in the pixel space of the plan's street traces
(data/mariehamn-city-traces.json, set plan-1860). The 1860 map does not show the plan at its raw georeference:
`planned_city_streets.py` draws it on the reconstructed 1861 grid. So the outlines are placed at build time through
that grid, not through the plan's three anchors:

* every crossing of a plan east–west street with a plan north–south street (pixels) is paired with the crossing of the
  same streets as the 1860 stage draws them (resolved through their objects where linked);
* crossings the stage lacks are filled from a distance-weighted affine fit of the nearest paired crossings;
* each outline is mapped through the bilinear cell of the four crossings around its centre, so a building stays in the
  same block as on the plan. Buildings outside the grid extrapolate from the nearest cell, at most
  `maxExtrapolationCells` cells.

The plan's pink house rows along the block streets (`houseRows`, one per block side) are placed the same way as
`buildingGroup` objects; the plot lines inside a row are not separate objects.

Each building becomes one object with a single `planned` state 1860–1861 and `constructionYear: null`: the plan is not
evidence that it was built. Everything is validated before the catalogue changes.
"""
from copy import deepcopy
import numpy as np
from shapely.geometry import LineString, Polygon
from pyproj import Transformer

TO_M = Transformer.from_crs(4326, 3874, always_xy=True).transform
TO_G = Transformer.from_crs(3874, 4326, always_xy=True).transform


def _extend(coords, d):
    c = np.array(coords, float)
    a = c[0] + (c[0] - c[1]) / np.linalg.norm(c[0] - c[1]) * d
    b = c[-1] + (c[-1] - c[-2]) / np.linalg.norm(c[-1] - c[-2]) * d
    return LineString([a, *c, b])


def _cross(g1, g2):
    i = g1.intersection(g2)
    pts = [g for g in getattr(i, 'geoms', [i]) if not g.is_empty and g.geom_type == 'Point']
    return np.array([np.mean([p.x for p in pts]), np.mean([p.y for p in pts])]) if pts else None


def apply_plan_1860_buildings(read, catalog):
    review = read('data/plan-1860-buildings.json')
    traces = next(s for s in read('data/mariehamn-city-traces.json')['sets'] if s['id'] == review['planDatasetId'])
    objects = {o['id']: o for o in catalog['objects']}
    geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}
    stage = next((s for s in catalog['cityStages'] if s['id'] == 'city-reconstruction-1860'), None)
    items = [(b, 'building') for b in review['buildings']] + [(h, 'buildingGroup') for h in review.get('houseRows', [])]
    ids = ['building:plan-1860:' + b['key'] for b, _ in items]
    if (review['schemaVersion'] != 1 or review['source']['id'] in sources or review['planDatasetId'] not in sources or stage is None
            or any(i in objects for i in ids) or len(set(ids)) != len(ids) or not review['basis']):
        raise ValueError('Plan building review already applied or missing its plan or stage')
    # Trace `pixels` are the drawn street centres. Two traces keep their first, house-row-edge line as
    # `registrationPixels`; that line places the plan on the map, not here (docs/plan-street-traces.md).
    if 'planLineCorrections' in review:
        raise ValueError('Plan line corrections belong in the traces (pixels / registrationPixels)')
    plan = {r['name']: r['pixels'] for r in traces['roads']}

    def stage_lines(names):
        out = []
        for f in stage['features']:
            if f['kind'] != 'street' or f.get('name') not in names:
                continue
            paths = f['paths']
            if f.get('objectId'):
                o = objects[f['objectId']]
                p = next((p for p in o['geometryPeriods'] if p['from'] <= 1860 and (p['to'] is None or 1860 < p['to'])), None)
                paths = geometries[p['geometryId']]['paths'] if p else []
            out += [_extend([TO_M(*q) for q in path], 60) for path in paths if len(path) > 1]
        if not out:
            raise ValueError('Control street missing from the 1860 stage: ' + ', '.join(names))
        return out

    ew, ns = review['controlStreets']['eastWest'], review['controlStreets']['northSouth']
    if any(name not in plan for name, _ in ew + ns):
        raise ValueError('Control street missing from the plan traces')
    lines = {name: stage_lines(names) for name, names in ew + ns}
    P, Q, known = {}, {}, []
    for i, (a, _) in enumerate(ew):
        for j, (b, _) in enumerate(ns):
            P[(i, j)] = _cross(_extend(plan[a], 400), _extend(plan[b], 400))
            hits = [x for la in lines[a] for lb in lines[b] if (x := _cross(la, lb)) is not None]
            if P[(i, j)] is None:
                raise ValueError(f'Plan streets do not cross: {a} / {b}')
            if hits:
                Q[(i, j)] = np.mean(hits, axis=0); known.append((i, j))
    if len(known) < 0.6 * len(P):
        raise ValueError('Too few control crossings on the 1860 stage')
    cp = np.array([P[k] for k in known]); cq = np.array([Q[k] for k in known])
    for k in P:
        if k not in Q:
            d = np.hypot(*(cp - P[k]).T); n = np.argsort(d)[:8]; w = np.sqrt(1 / (d[n] + 30) ** 2)
            m = np.linalg.lstsq(np.c_[cp[n], np.ones(len(n))] * w[:, None], cq[n] * w[:, None], rcond=None)[0]
            Q[k] = np.r_[P[k], 1] @ m

    def bil(D, i, j, u, v):
        return (1 - u) * (1 - v) * D[(i, j)] + u * (1 - v) * D[(i, j + 1)] + (1 - u) * v * D[(i + 1, j)] + u * v * D[(i + 1, j + 1)]

    def inverse(i, j, p):
        u = v = .5
        for _ in range(50):
            f = bil(P, i, j, u, v) - p; h = 1e-4
            J = np.c_[(bil(P, i, j, u + h, v) - bil(P, i, j, u, v)) / h, (bil(P, i, j, u, v + h) - bil(P, i, j, u, v)) / h]
            du, dv = np.linalg.solve(J, f); u -= du; v -= dv
        return u, v

    def cell(p):
        i = 0
        while i < len(ew) - 2 and _extend(plan[ew[i + 1][0]], 2000).intersects(LineString([p, p + [0, -1e4]])):
            i += 1
        j = 0
        while j < len(ns) - 2 and _extend(plan[ns[j + 1][0]], 2000).intersects(LineString([p, p + [-1e4, 0]])):
            j += 1
        return i, j

    plans = []
    for (b, kind), oid in zip(items, ids):
        px = np.array(b['pixels'], float)
        if len(px) < 4 or not Polygon(px).is_valid or not b['name'] or not b['planLabel'] or (kind == 'buildingGroup' and not b.get('location')):
            raise ValueError('Invalid traced outline ' + b['key'])
        i, j = cell(px.mean(axis=0)); far = 0; ring = []
        for p in px:
            u, v = inverse(i, j, p)
            far = max(far, max(0, -u, u - 1) + max(0, -v, v - 1))
            ring.append([round(c, 7) for c in TO_G(*bil(Q, i, j, u, v))])
        poly = Polygon([TO_M(*q) for q in ring])
        if far > review['maxExtrapolationCells'] or not poly.is_valid or not 50 < poly.area < 20000:
            raise ValueError(f'Placement failed for {b["key"]} (extrapolation {far:.2f}, area {poly.area:.0f} m²)')
        plans.append((b, kind, oid, ring + [ring[0]], round(far, 2), (ew[i][0], ew[i + 1][0], ns[j][0], ns[j + 1][0])))

    # All checks passed. Change the catalogue.
    source_id = review['source']['id']
    catalog['sources'].append(deepcopy(review['source']))
    for b, kind, oid, ring, far, cellnames in plans:
        gid = 'geometry:plan-1860-buildings:' + b['key']
        catalog['geometries'].append(dict(id=gid, paths=[ring], representation='outline', sourceIds=[review['planDatasetId']],
                                          note='Planens kontur förd till 1860 års tolkade gatunät; inte inmätt.'))
        eid = oid + ':plan-1860'
        note = review['basis'] + (' ' + b['note'] if b.get('note') else '') + (' ' + review['houseRowsNote'] if kind == 'buildingGroup' else '')
        catalog['objects'].append(dict(
            id=oid, kind=kind, name=b['name'], historicalBuilding=True, planLabel=b['planLabel'], **({'location': b['location']} if b.get('location') else {}),
            states=[dict(state='planned', **{'from': 1860, 'to': 1861}, evidenceIds=[eid], certainty='documented', note=note)],
            geometryPeriods=[dict(geometryId=gid, **{'from': 1860, 'to': 1861}, evidenceIds=[eid], certainty='inferred', basis=note)],
            evidence=[dict(id=eid, sourceId=review['planDatasetId'], describes={'from': 1860, 'to': 1861},
                           supports=['identity', 'state', 'geometry'], observationType='plan', outcome='planned', interpretation=True,
                           constructionYear=None, reviewId=source_id, planPixels=deepcopy(b['pixels']), planLabel=b['planLabel'],
                           placement=dict(method='bilinear-street-cell', cell=list(cellnames), extrapolationCells=far), note=note)],
            sourceLinks=[], planBuildingReview=dict(reviewedAt=review['reviewedAt'], constructionYear=None)))
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
