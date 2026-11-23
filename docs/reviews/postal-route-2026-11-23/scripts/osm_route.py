"""Route each postal-route leg on today's OSM roads (dist/assets/modern.json.gz, no footways or paths) and list the OSM
ways on the route with the catalogue object that owns them (and its first year) or UNOWNED. Usage: osm_route.py"""
import sys, json, gzip, heapq, math
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import Point
from shapely.strtree import STRtree
STOPS = [('Storby', 19.552652, 60.221273), ('Frebbenby', 19.7118011, 60.2193573), ('Emkarby', 19.8792041, 60.2110448), ('Haraldsby', 20.0201646, 60.240469),
         ('Kastelholm', 20.0818, 60.2323), ('Gamla Skarpans', 20.2110829, 60.2150034), ('Vargata', 20.3509256, 60.2463982)]
M = json.load(gzip.open('dist/assets/modern.json.gz'))['features']
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz'))
owner = {}
for o in cat['objects']:
    for l in o.get('sourceLinks', []):
        if l['datasetId'] == 'osm-2026': owner.setdefault(l['featureId'], []).append((o['id'], o.get('name'), o['states'][0]['from'], l.get('sourceVertexRange')))
nodes, adj = {}, {}
def node(p):
    k = (round(p[0], 1), round(p[1], 1)); nodes[k] = p; return k
for f in M:
    if f.get('kind') != 'road' or f.get('class') in ('footway', 'path', 'steps', 'cycleway', 'track', 'bridleway'): continue
    for p in f['paths']:
        m = [TO_METRIC(*q) for q in p]
        for i, (a, b) in enumerate(zip(m, m[1:])):
            ka, kb = node(a), node(b); d = math.dist(a, b)
            adj.setdefault(ka, []).append((kb, d, f['id'], i)); adj.setdefault(kb, []).append((ka, d, f['id'], i))
keys = list(nodes); tree = STRtree([Point(nodes[k]) for k in keys])
names = {f['id']: (f.get('name'), f.get('class')) for f in M}
def near(lon, lat): return keys[tree.nearest(Point(TO_METRIC(lon, lat)))]
for (n1, a1, b1), (n2, a2, b2) in zip(STOPS, STOPS[1:]):
    s, t = near(a1, b1), near(a2, b2)
    dist, prev = {s: 0}, {}; h = [(0, s)]
    while h:
        d, u = heapq.heappop(h)
        if u == t: break
        if d > dist[u]: continue
        for v, w, fid, i in adj.get(u, []):
            if d + w < dist.get(v, 1e18): dist[v] = d + w; prev[v] = (u, fid, i); heapq.heappush(h, (d + w, v))
    if t not in dist:
        print(f'{n1} → {n2}: no OSM road route (a crossing by water)'); continue
    runs, u = [], t
    while u != s:
        u, fid, i = prev[u]
        if runs and runs[-1][0] == fid: runs[-1][1].add(i)
        else: runs.append([fid, {i}])
    runs = runs[::-1]
    print(f'{n1} → {n2}: {dist[t]/1000:.1f} km on {len(runs)} OSM ways')
    for fid, idx in runs:
        own = owner.get(fid)
        nm, cl = names[fid]
        lo, hi = min(idx), max(idx) + 1
        covered = own and any(r is None or (r[0] <= lo + 1e-6 and r[1] >= hi - 1e-6) for _, _, _, r in own)
        tag = 'UNOWNED' if not own else ('partly owned' if not covered else '')
        print(f'   {fid:16} {(nm or "")[:28]:28} {cl or "":12} seg {lo}-{hi} ' + ('; '.join(f"{oid.split(':',1)[-1][:40]} ({fy}) {r}" for oid, _, fy, r in (own or []))[:150]) + (' ' + tag if tag else ''))
