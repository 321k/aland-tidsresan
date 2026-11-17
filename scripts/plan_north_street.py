"""Norra planerade tvärgatan in the interpreted 1860 plan and the 1861/1871 reconstructions.

The 1860 plan draws its northern cross street ("N o r r a … g a t a n" on the plan) one block row north of the street
that the plan streets were aligned to the real Norragatan by (`Norragatan i planen`, scripts/planned_city_streets.py).
The trace `plan-1860-trace-8` was never aligned with them: in the reconstructed grid it ran 75 m north of Norragatan in
the west and 26 m in the east, crossing the grid at an angle. `data/plan-north-street.json` records a visual review
(docs/reviews/norra-planerade-tvargatan-2026-11-17/): on the plan the block row between the two streets is 47 m deep
(measured 46.8–47.0 m through the plan's own registration).

In each listed stage the street is redrawn parallel to the stage's reconstructed Norragatan at that depth, from the
west shore street to Strandgatan. The plan-only streets that ended on it are cut or extended along their own direction
to meet it, and the one derived block bounded by it is recomputed with the same rule as the early-city stages. The raw
trace stays in the source dataset and on the feature as `sourcePaths`. Everything is validated before any stage changes.
"""
from copy import deepcopy
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import substring, unary_union
from mariehamn_frame_1942 import digest, TO_METRIC, TO_GEO
from postwar_city import geographic, parts
from city_continuity import shape as ring_shape  # even-odd rings, as the early-city blocks use


def _line(path):
    return LineString([TO_METRIC(*p) for p in path])


def _geo(coords):
    return [[round(v, 7) for v in TO_GEO(x, y)] for x, y in coords]


def _ray(a, b, length=400):
    """The line through b and a, extended `length` metres beyond a."""
    v = np.array(a) - np.array(b); v /= np.linalg.norm(v)
    return LineString([tuple(np.array(b) - v * length), tuple(np.array(a) + v * length)])


def _plan(review, stage):
    features = {f['id'].split(':', 1)[1]: f for f in stage['features']}
    street = features.get(review['featureId'])
    if street is None or street.get('traceId') != review['traceId'] or digest(street['paths']) != review['inputHash'] or street.get('alignment') or 'sourcePaths' in street:
        raise ValueError('Changed plan north street in ' + stage['id'])
    old = _line(street['paths'][0])
    ng = [f for f in stage['features'] if f['kind'] == 'street' and review['referenceName'] in (f.get('name') or '')]
    pts = np.array(sorted({TO_METRIC(*q) for f in ng for p in f['paths'] for q in p}))
    if len(ng) < 5:
        raise ValueError('Missing reconstructed Norragatan in ' + stage['id'])
    # The reconstructed Norragatan is straight to within a couple of metres; fit that line and offset it, so that short
    # end segments of the reconstruction do not bend the planned street.
    mid = pts.mean(0)
    direction = np.linalg.svd(pts - mid)[2][0]
    normal = np.array([-direction[1], direction[0]])
    if normal[1] < 0:
        normal = -normal
    if np.abs((pts - mid) @ normal).max() > review['straightnessMeters']:
        raise ValueError('Reconstructed Norragatan is not straight in ' + stage['id'])
    ref = LineString([tuple(mid - direction * 1500), tuple(mid + direction * 1500)])
    base = mid + normal * review['offsetMeters']
    long = LineString([tuple(base - direction * 1500), tuple(base + direction * 1500)])
    moves = {}
    for a in review['attached']:
        f = features.get(a['featureId'])
        if f is None or f.get('objectId') or digest(f['paths']) != a['inputHash'] or 'sourcePaths' in f or f.get('alignment'):
            raise ValueError('Changed attached plan street ' + a['featureId'])
        p = [TO_METRIC(*q) for q in f['paths'][0]]
        i = 0 if Point(p[0]).distance(old) < Point(p[-1]).distance(old) else len(p) - 1
        if Point(p[i]).distance(old) > 3:
            raise ValueError('Attached street does not end on the plan north street: ' + a['featureId'])
        hit = _ray(p[i], p[1] if i == 0 else p[-2]).intersection(long)
        if hit.geom_type != 'Point' or Point(p[i]).distance(hit) > review['maxMoveMeters']:
            raise ValueError('Attached street cannot meet the aligned street: ' + a['featureId'])
        moves[a['featureId']] = (i, hit)
    west = moves[review['westEndFeatureId']][1]
    east_feature = next((f for f in stage['features'] if f.get('objectId') == review['eastEndObjectId']), None)
    if east_feature is None:
        raise ValueError('Missing Strandgatan in ' + stage['id'])
    east = _line(east_feature['paths'][0]).intersection(long)
    if east.geom_type != 'Point':
        raise ValueError('The aligned street does not meet Strandgatan in ' + stage['id'])
    a, b = sorted([long.project(west), long.project(east)])
    new = substring(long, a, b)
    if abs(ref.distance(Point(new.coords[0])) - review['offsetMeters']) > 0.01 or abs(ref.distance(Point(new.coords[-1])) - review['offsetMeters']) > 0.01:
        raise ValueError('Aligned street is not parallel to Norragatan in ' + stage['id'])
    block = features.get(review['block']['featureId'])
    if block is None or block['kind'] != 'block' or digest(block['paths']) != review['block']['inputHash'] or 'sourcePaths' in block:
        raise ValueError('Changed block next to the plan north street in ' + stage['id'])
    return street, new, moves, block


def apply_plan_north_street(read, catalog):
    review = read('data/plan-north-street.json')
    sources = {s['id'] for s in catalog['sources']}
    stages = {s['id']: s for s in catalog['cityStages']}
    if review['schemaVersion'] != 1 or review['source']['id'] in sources or any(s not in stages for s in review['stages']) or not review['basis'] or not review['offsetMeters'] > 0:
        raise ValueError('Plan north street review already applied or missing a stage')
    plans = [(stages[s], _plan(review, stages[s])) for s in review['stages']]

    # Check the recomputed block before changing anything.
    rebuilt = []
    for stage, (street, new, moves, block) in plans:
        features = []
        for f in stage['features']:
            key = f['id'].split(':', 1)[1]
            if f is street:
                f = dict(f, paths=[_geo(new.coords)])
            elif key in moves:
                i, hit = moves[key]; p = deepcopy(f['paths'][0]); p[i] = _geo([hit.coords[0]])[0]
                f = dict(f, paths=[p])
            features.append(f)
        network = unary_union([_line(p) for f in features if f['kind'] == 'street' for p in f['paths'] if len(p) > 1])
        parks = unary_union([ring_shape(f) for f in features if f['kind'] == 'park'])
        seed = Polygon([TO_METRIC(*q) for q in block['paths'][0]]).representative_point()
        # The joints of the reconstructed grid can miss by under a metre, so find the enclosed street space with
        # 1 m tolerance rather than by exact noding; a cell that reaches the search window is not enclosed.
        window = seed.buffer(400)
        cell = next((q for q in parts(window.difference(network.buffer(1.0)), 'Polygon') if q.contains(seed)), None)
        if cell is None or not cell.within(window.buffer(-2)):
            raise ValueError('The block next to the plan north street is not enclosed in ' + stage['id'])
        polygon = cell.buffer(1.0)
        found = [q for q in parts(polygon.buffer(-4).difference(parks).difference(network.buffer(4)), 'Polygon') if q.area > 150]
        if len(found) != 1 or not review['block']['minArea'] < found[0].area < review['block']['maxArea']:
            raise ValueError('Unexpected recomputed block in ' + stage['id'])
        rebuilt.append(found[0])

    # All checks passed. Change the stages.
    catalog['sources'].append(deepcopy(review['source']))
    for (stage, (street, new, moves, block)), poly in zip(plans, rebuilt):
        street['sourcePaths'] = street['paths']
        street['paths'] = [_geo(new.coords)]
        street['alignment'] = dict(reviewId=review['source']['id'], reviewedAt=review['reviewedAt'], basis=review['basis'],
                                   offsetMeters=review['offsetMeters'], reference=review['referenceName'])
        for f in stage['features']:
            key = f['id'].split(':', 1)[1]
            if key in moves:
                i, hit = moves[key]
                f['sourcePaths'] = deepcopy(f['paths'])
                p = deepcopy(f['paths'][0]); p[i] = _geo([hit.coords[0]])[0]
                f['paths'] = [p] + deepcopy(f['paths'][1:])
                f['alignment'] = dict(reviewId=review['source']['id'], basis='Gatans norra ände möter Norra planerade tvärgatan i dess justerade läge.')
        block['sourcePaths'] = block['paths']
        block['paths'] = [geographic(poly.exterior.coords), *[geographic(r.coords) for r in poly.interiors]]
        block['alignment'] = dict(reviewId=review['source']['id'], basis='Kvarteret räknas om mellan gatorna efter justeringen.')
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
