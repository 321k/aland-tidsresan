"""Shared by the old-road prepare scripts: find the OSM vertex runs along a 1929 trace and build the old line from the
trace and those runs (their exact coordinates), with its surviving extents. The same method as prepare_kyrkoby.py."""
import sys
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point

geo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
met = lambda p: LineString([TO_METRIC(*q) for q in p])


def survivor(T, f, limit=20, minimum=40):
    p = f['paths'][0]; ok = [T.distance(Point(TO_METRIC(*q))) <= limit for q in p]
    runs, s = [], None
    for i, v in enumerate(ok + [False]):
        if v and s is None: s = i
        if not v and s is not None: runs.append((s, i - 1)); s = None
    runs = [r for r in runs if r[1] > r[0]]
    if not runs: return None
    a, b = max(runs, key=lambda r: met(p[r[0]:r[1] + 1]).length)
    run = p[a:b + 1]; L = met(run).length
    print(' ', f['id'], f.get('name'), 'vertices', a, b, 'of', len(p), round(L), 'm, max off', round(max(T.distance(Point(TO_METRIC(*q))) for q in run), 1))
    return (f['id'], a, b, run, len(p)) if L >= minimum else None


def old_line(start, end, T, feats, gap=10):
    """start → trace → each surviving run (in trace order) → … → end. Trace waypoints within `gap` m of a join are left out."""
    pos = lambda q: T.project(Point(TO_METRIC(*q)))
    surv = []
    for f in feats:
        s = survivor(T, f)
        if s:
            fid, a, b, run, n = s
            surv.append((fid, a, b, run if pos(run[0]) < pos(run[-1]) else run[::-1], n))
    surv.sort(key=lambda s: pos(s[3][0]))
    keep, last = [], -1
    for fid, a, b, run, n in surv:      # a run that starts behind the previous one loses those leading vertices
        k = 0
        while k < len(run) and pos(run[k]) < last + 1: k += 1
        rest = run[k:]
        if len(rest) < 2 or met(rest).length < 40: continue
        if k:
            full = next(f for f in feats if f['id'] == fid)['paths'][0]
            i = next(j for j in range(len(full)) if full[j] == rest[0]); i2 = next(j for j in range(len(full)) if full[j] == rest[-1])
            a, b = min(i, i2), max(i, i2)
            print('  trimmed', fid, 'to vertices', a, b)
        keep.append((fid, a, b, rest, n)); last = pos(rest[-1])
    path, t = [start], pos(start)
    for fid, a, b, run, n in keep:
        path += [geo(q) for q in T.coords if t + gap < T.project(Point(q)) < pos(run[0]) - gap] + run; t = pos(run[-1])
    path += [geo(q) for q in T.coords if t + gap < T.project(Point(q)) < pos(end) - gap] + [end]
    total = met(path).length; ranges = []
    for fid, a, b, run, n in keep:
        k = next(i for i in range(len(path)) if path[i:i + len(run)] == run)
        s0 = met(path[:k + 1]).length if k else 0.0
        ranges.append([round(s0 / total, 6), round((s0 + met(run).length) / total, 6)])
    merged = []
    for r in sorted(ranges):
        if merged and r[0] - merged[-1][1] < 1e-5: merged[-1][1] = r[1]
        else: merged.append(list(r))
    return path, keep, merged, total
