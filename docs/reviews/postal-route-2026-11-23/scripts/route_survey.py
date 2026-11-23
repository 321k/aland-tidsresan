"""Survey: how far the postal route's land legs can follow dated catalogue roads.
For a year, build a graph of the catalogue's road geometries open that year (vertices joined within SNAP m), and find
the shortest road path between the roads nearest two stops. Reports each leg: straight distance, road distance, the
stops' distance to the nearest road, the objects used (with first years) and, if the network breaks, how far apart
the two components come.  Usage: route_survey.py YEAR [YEAR ...]"""
import sys, json, gzip, heapq, math
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree

SNAP = 15
STOPS = [('Storby', 19.552652, 60.221273), ('Frebbenby', 19.7118011, 60.2193573), ('Emkarby', 19.8792041, 60.2110448), ('Haraldsby', 20.0201646, 60.240469), ('Kastelholm', 20.0818, 60.2323), ('Gamla Skarpans', 20.2110829, 60.2150034), ('Vargata', 20.3509256, 60.2463982)]
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}

def network(year):
    segs = []
    for o in cat['objects']:
        if o['kind'] != 'roadSegment': continue
        st = next((s for s in o['states'] if s['from'] <= year < (s['to'] or 9999)), None)
        gp = next((g for g in o['geometryPeriods'] if g['from'] <= year < (g['to'] or 9999)), None)
        if not st or st['state'] != 'open' or not gp: continue
        first = o['states'][0]['from']
        for p in G[gp['geometryId']]['paths']:
            m = [TO_METRIC(*q) for q in p]
            for a, b in zip(m, m[1:]):
                if a != b: segs.append((a, b, o['id'], o.get('name') or '', first))
    return segs

def key(p): return (round(p[0] / SNAP), round(p[1] / SNAP))

def build(segs):
    nodes, adj = {}, {}
    def node(p):
        k = key(p)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                kk = (k[0] + dx, k[1] + dy)
                if kk in nodes and math.dist(nodes[kk], p) <= SNAP: return kk
        nodes[k] = p; return k
    for a, b, oid, name, first in segs:
        ka, kb = node(a), node(b); d = math.dist(a, b)
        adj.setdefault(ka, []).append((kb, d, oid)); adj.setdefault(kb, []).append((ka, d, oid))
    return nodes, adj

def dijkstra(adj, src):
    dist, prev = {src: 0}, {}; h = [(0, src)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]: continue
        for v, w, oid in adj.get(u, []):
            if d + w < dist.get(v, 1e18): dist[v] = d + w; prev[v] = (u, oid); heapq.heappush(h, (d + w, v))
    return dist, prev

for year in map(int, sys.argv[1:]):
    segs = network(year); nodes, adj = build(segs)
    info = {}
    for a, b, oid, name, first in segs: info[oid] = (name, first)
    keys = list(nodes); pts = [Point(nodes[k]) for k in keys]; tree = STRtree(pts)
    def nearest(lon, lat):
        p = Point(TO_METRIC(lon, lat)); i = tree.nearest(p); return keys[i], p.distance(pts[i])
    print(f'== {year}: {len(segs)} road segments')
    for (n1, lo1, la1), (n2, lo2, la2) in zip(STOPS, STOPS[1:]):
        s, ds = nearest(lo1, la1); t, dt = nearest(lo2, la2)
        straight = math.dist(TO_METRIC(lo1, la1), TO_METRIC(lo2, la2))
        dist, prev = dijkstra(adj, s)
        if t in dist:
            used, u = [], t
            while u != s:
                u, oid = prev[u]
                if not used or used[-1] != oid: used.append(oid)
            used = used[::-1]
            firsts = sorted({info[o][1] for o in used})
            print(f'  {n1} → {n2}: straight {straight/1000:.1f} km, by road {dist[t]/1000:.1f} km; stops {ds:.0f} m / {dt:.0f} m off; {len(used)} objects, first years {firsts[:6]}{"…" if len(firsts)>6 else ""}; latest-dated {max([info[o][1] for o in used], default=None)}')
        else:
            reach = [k for k in dist]; rp = [Point(nodes[k]) for k in reach]
            dist2, _ = dijkstra(adj, t); other = [Point(nodes[k]) for k in dist2]
            from shapely.geometry import MultiPoint
            gap = MultiPoint(rp).distance(MultiPoint(other)) if rp and other else float('nan')
            print(f'  {n1} → {n2}: straight {straight/1000:.1f} km, NOT CONNECTED; the two road networks come within {gap:.0f} m; stops {ds:.0f} m / {dt:.0f} m off')
