"""Conservative cartographic reconciliation; never infer construction dates."""
from copy import deepcopy
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.ops import transform

project = Transformer.from_crs(4326, 3874, always_xy=True).transform


def shape(feature):
    # Even-odd rings, matching the canvas renderer (including courtyards).
    result = Polygon()
    for ring in feature['paths']:
        result = result.symmetric_difference(transform(project, Polygon(ring)).buffer(0))
    return result


def equivalent(a, b):
    """Same object, only a small survey correction; preserve substantial changes."""
    return (a.area > 0 and b.area > 0
            and .85 <= a.area / b.area <= 1.18
            and a.centroid.distance(b.centroid) <= 4
            and a.hausdorff_distance(b) <= 6
            and a.intersection(b).area / a.union(b).area >= .70)


def reconcile(snapshots):
    """Mutate chronological snapshots; the last snapshot is the current map.

    Keep one outline in runs of near-identical geometry for the same OSM ID.
    Bridge an absent intermediate record only when it reappears with equivalent
    geometry, and no other mapped building substantially occupies its footprint.
    Never carry an object beyond its last observation or before its first one.
    """
    indexes = [{f['id']: f for f in s['features']} for s in snapshots]
    geometries = [{k: shape(f) for k, f in index.items()} for index in indexes]
    corrections = gaps = 0
    for identity in sorted(set().union(*(index.keys() for index in indexes))):
        observed = [i for i, index in enumerate(indexes) if identity in index]
        for left, right in zip(observed, observed[1:]):
            a, b = geometries[left][identity], geometries[right][identity]
            if not equivalent(a, b):
                continue
            for i in range(left + 1, right):
                if any(a.intersection(other).area > a.area * .2 for other in geometries[i].values()):
                    continue
                f = deepcopy(indexes[left][identity])
                f['continuity'] = {'lastSeenYear': snapshots[left]['year'], 'nextSeenYear': snapshots[right]['year']}
                indexes[i][identity] = f
                geometries[i][identity] = a
                snapshots[i]['features'].append(f)
                gaps += 1
        run = []

        def normalize():
            nonlocal corrections
            if len(run) < 2:
                return
            canonical = indexes[run[-1]][identity]
            for i in run[:-1]:
                f = indexes[i][identity]
                if f['paths'] != canonical['paths']:
                    f['paths'] = deepcopy(canonical['paths'])
                    f['geometryYear'] = snapshots[run[-1]]['year']
                    corrections += 1

        for i in range(len(snapshots)):
            if identity not in indexes[i]:
                normalize()
                run = []
            else:
                # Every member must match the eventual canonical outline, so
                # repeated small edits cannot silently absorb a large extension.
                if any(not equivalent(geometries[j][identity], geometries[i][identity]) for j in run):
                    normalize()
                    run = []
                run.append(i)
        normalize()
    return {'minorGeometryCorrections': corrections, 'bridgedSnapshotGaps': gaps}
