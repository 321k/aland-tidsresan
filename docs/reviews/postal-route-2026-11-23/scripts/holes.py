"""For one postal-route leg, route on today's OSM roads (no footways/paths/cycleways/tracks) and list the stretches of
the route that no catalogue object open in YEAR covers (by OSM ownership in osm-2026, vertex ranges respected).
Uncovered segments weigh PENALTY times their length (env, default 5), so the route keeps to dated roads where it can.
Usage: holes.py YEAR LON1 LAT1 LON2 LAT2"""
import sys, json, gzip, heapq, math
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import Point
from shapely.strtree import STRtree
import os
year = int(sys.argv[1]); a1, b1, a2, b2 = map(float, sys.argv[2:6]); PEN = float(os.environ.get('PENALTY', 5))
M = json.load(gzip.open('dist/assets/modern.json.gz'))['features']
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz'))
own = {}
for o in cat['objects']:
    if o['kind'] != 'roadSegment': continue
    opn = any(s['state'] == 'open' and s['from'] <= year < (s['to'] or 9999) for s in o['states']) and any(g['from'] <= year < (g['to'] or 9999) for g in o['geometryPeriods'])
    for l in o.get('sourceLinks', []):
        if l['datasetId'] == 'osm-2026': own.setdefault(l['featureId'], []).append((o['id'], o['states'][0]['from'], l.get('sourceVertexRange'), opn))
nodes, adj, F = {}, {}, {}
def node(p):
    k = (round(p[0], 1), round(p[1], 1)); nodes[k] = p; return k
for f in M:
    if f.get('kind') != 'road' or f.get('class') in ('footway', 'path', 'steps', 'cycleway', 'track', 'bridleway'): continue
    F[f['id']] = f
    for p in f['paths']:
        m = [TO_METRIC(*q) for q in p]
        for i, (a, b) in enumerate(zip(m, m[1:])):
            ka, kb = node(a), node(b); d = math.dist(a, b)
            adj.setdefault(ka, []).append((kb, d, f['id'], i)); adj.setdefault(kb, []).append((ka, d, f['id'], i))
# Coverage by geometry: a segment is covered when a catalogue road drawn in YEAR lies within 4 m of both its ends and
# its midpoint (ownership alone is not enough: an owner's early periods may draw only part of its way).
from shapely.geometry import LineString as _LS
_G = {g['id']: g for g in cat['geometries']}; _lines = []
for o in cat['objects']:
    if o['kind'] != 'roadSegment' or not any(s['state'] == 'open' and s['from'] <= year < (s['to'] or 9999) for s in o['states']): continue
    for gp in o['geometryPeriods']:
        if gp['from'] <= year < (gp['to'] or 9999):
            _lines += [_LS([TO_METRIC(*q) for q in p]) for p in _G[gp['geometryId']]['paths'] if len(p) > 1]
_tree = STRtree(_lines); _cache = {}
def covered(fid, i):
    if (fid, i) not in _cache:
        m = [TO_METRIC(*q) for q in F[fid]['paths'][0]][i:i + 2]
        pts = [Point(m[0]), Point(m[1]), Point((m[0][0] + m[1][0]) / 2, (m[0][1] + m[1][1]) / 2)]
        _cache[(fid, i)] = all(any(_lines[j].distance(q) <= 4 for j in _tree.query(q.buffer(4))) for q in pts)
    return _cache[(fid, i)]
keys = list(nodes); tree = STRtree([Point(nodes[k]) for k in keys])
near = lambda lon, lat: keys[tree.nearest(Point(TO_METRIC(lon, lat)))]
s, t = near(a1, b1), near(a2, b2)
dist, prev = {s: 0}, {}; h = [(0, s)]
while h:
    d, u = heapq.heappop(h)
    if u == t: break
    if d > dist[u]: continue
    for v, w, fid, i in adj.get(u, []):
        w = w if covered(fid, i) else w * PEN
        if d + w < dist.get(v, 1e18): dist[v] = d + w; prev[v] = (u, fid, i); heapq.heappush(h, (d + w, v))
steps, u = [], t
while u != s:
    p, fid, i = prev[u]; steps.append((fid, i, math.dist(nodes[p], nodes[u]), nodes[p])); u = p
steps = steps[::-1]
print(f'route {sum(x[2] for x in steps)/1000:.2f} km; uncovered in {year}:')
run = None
total = 0
for fid, i, d, p in steps + [(None, 0, 0, None)]:
    bad = fid is not None and not covered(fid, i)
    if bad:
        if run and run[0] == fid: run[1] += d; run[3] = i
        else:
            if run: print(f'   {run[0]:16} {(F[run[0]].get("name") or "")[:24]:24} segs {run[2]}-{run[3]+1} {run[1]:6.0f} m at {[round(v) for v in run[4]]}  owners {[(o.split(":",1)[1][:38], y, r, op) for o, y, r, op in own.get(run[0], [])]}')
            run = [fid, d, i, i, p]
        total += d
    elif run:
        print(f'   {run[0]:16} {(F[run[0]].get("name") or "")[:24]:24} segs {run[2]}-{run[3]+1} {run[1]:6.0f} m at {[round(v) for v in run[4]]}  owners {[(o.split(":",1)[1][:38], y, r, op) for o, y, r, op in own.get(run[0], [])]}'); run = None
print(f'   total {total:.0f} m')
