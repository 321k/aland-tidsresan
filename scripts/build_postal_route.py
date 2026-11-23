"""The postal route across Åland on dated roads (docs/postal-route-roads.md).

For each land leg between two post stations (data/postal-route-stations.json), the route follows the catalogue's road
objects in the earliest year when they connect the two stations: the graph of every geometry the roads had while open
in a period beginning by that year (vertices joined within SNAP m), including old roads that closed before it, and the
shortest path between the road points nearest the stations.
A station must lie within STATION_LIMIT m of a road that year. Where a road ends within JOIN m of a vertex of another
road (a junction the maps draw, where one object follows today's road and the other the older line beside it), the
two are joined by a straight connector; each join used is listed with the leg. A ferry crossing in the stations file
('crossings') joins the roads nearest its two landings; the postal route (to 1911) is older than every bridge that
replaced a ferry ('until' is the bridge's year), so the ferry is used whatever year dates the roads. Among the roads open that
year, segments that are not on the object's geometry of any period beginning by 'preferEarlyRoads.until' cost 'factor'
times their length, so the line keeps to the roads of the parish maps where they connect. Candidate years are the years in which some road period
begins, from 1800 to 2026. The route itself is older (1638–1911); before the leg's year the line shows where the road
ran when it was first mapped, not a reconstruction. Sea legs stay schematic.

Writes dist/postal-route-roads.js (window.POSTAL_ROUTE_ROADS). Run after build_temporal_objects.py.
"""
import gzip, heapq, json, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from mariehamn_frame_1942 import TO_METRIC, TO_GEO

SNAP = 15
STATION_LIMIT = 150
JOIN = 40
MARGIN = 4000


def load():
    cat = json.load(gzip.open(ROOT / 'dist/assets/temporal-objects.json.gz'))
    stations = json.load(open(ROOT / 'data/postal-route-stations.json'))
    return cat, stations


def segments(cat, box, year, early_until=None):
    """(a, b, object id, early) for each segment of the roads open in year, and the paths' end points. 'early': the
    segment lies (within 3 m) on the object's geometry of some period beginning by early_until."""
    from shapely.geometry import LineString, Point
    G = {g['id']: g for g in cat['geometries']}
    x0, y0, x1, y1 = box
    out, ends = [], []
    for o in cat['objects']:
        if o.get('kind') != 'roadSegment':
            continue
        # Every geometry the object had while open, in any period beginning by this year: a road that closed before it
        # (the old road to a ferry pier) was still the road of the postal route.
        gps = [g for g in o['geometryPeriods'] if g['from'] <= year
               and next((s for s in o['states'] if s['from'] <= g['from'] < (s['to'] or 9999)), {}).get('state') == 'open']
        if not gps:
            continue
        olds = None
        paths = {}
        for g in gps:
            for i, p in enumerate(G[g['geometryId']]['paths']):
                paths.setdefault(json.dumps(p), p)
        for p in paths.values():
            m = [TO_METRIC(*q) for q in p]
            if not any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in m):
                continue
            if olds is None:
                olds = [LineString([TO_METRIC(*q) for q in pp]) for g in o['geometryPeriods'] if early_until and g['from'] <= early_until
                        and next((s for s in o['states'] if s['from'] <= g['from'] < (s['to'] or 9999)), {}).get('state') == 'open'
                        for pp in G[g['geometryId']]['paths'] if len(pp) > 1]
            for a, b in zip(m, m[1:]):
                if a != b:
                    out.append((a, b, o['id'], any(l.distance(Point(a)) < 3 and l.distance(Point(b)) < 3 for l in olds)))
            ends += [(m[0], o['id']), (m[-1], o['id'])]
    return out, ends


def route(network, s, t, crossings=(), prefer=None):
    """Shortest path on the snapped segment graph from the road point nearest s to the one nearest t."""
    segs, ends = network
    key = lambda p: (round(p[0] / SNAP), round(p[1] / SNAP))
    nodes, adj, owners = {}, {}, {}
    for a, b, oid, early in segs:
        owners.setdefault(key(a), set()).add(oid); owners.setdefault(key(b), set()).add(oid)
        ka, kb = key(a), key(b)
        nodes.setdefault(ka, a); nodes.setdefault(kb, b)
        if ka == kb:
            continue
        d = math.dist(a, b) * (prefer['factor'] if prefer and not early else 1)
        adj.setdefault(ka, []).append((kb, d, oid, a, b)); adj.setdefault(kb, []).append((ka, d, oid, b, a))
    if not nodes:
        return None
    # Joins: a road end to the nearest vertex of another road within JOIN m, if they are not already joined.
    from shapely.strtree import STRtree
    from shapely.geometry import Point
    vkeys = list(nodes); tree = STRtree([Point(nodes[k]) for k in vkeys])
    for e, oid in ends:
        ke = key(e)
        cands = [vkeys[i] for i in tree.query(Point(e).buffer(JOIN))]
        cands = [k for k in cands if k != ke and not (owners[k] & owners.get(ke, set())) and oid not in owners[k]
                 and not any(v == k for v, *_ in adj.get(ke, []))]
        if not cands:
            continue
        k = min(cands, key=lambda k: math.dist(nodes[k], e)); d = math.dist(nodes[k], e)
        if d <= JOIN:
            w = d * (prefer['factor'] if prefer else 1)     # a join is not a mapped road: it costs as a later piece does
            adj.setdefault(ke, []).append((k, w, 'join', e, nodes[k])); adj.setdefault(k, []).append((ke, w, 'join', nodes[k], e))
    near = lambda p: min(nodes, key=lambda k: math.dist(nodes[k], p))
    for c in crossings:                 # a ferry: the road points nearest its two landings, if both are near a road
        p, q = TO_METRIC(*c['from']), TO_METRIC(*c['to']); kp, kq = near(p), near(q)
        if math.dist(nodes[kp], p) <= STATION_LIMIT and math.dist(nodes[kq], q) <= STATION_LIMIT and kp != kq:
            d = math.dist(nodes[kp], nodes[kq])
            adj.setdefault(kp, []).append((kq, d, 'ferry:' + c['id'], nodes[kp], nodes[kq])); adj.setdefault(kq, []).append((kp, d, 'ferry:' + c['id'], nodes[kq], nodes[kp]))
    ks, kt = near(s), near(t)
    if math.dist(nodes[ks], s) > STATION_LIMIT or math.dist(nodes[kt], t) > STATION_LIMIT:
        return None
    dist, prev, heap = {ks: 0}, {}, [(0, ks)]
    while heap:
        d, u = heapq.heappop(heap)
        if u == kt:
            break
        if d > dist[u]:
            continue
        for v, w, oid, a, b in adj.get(u, []):
            if d + w < dist.get(v, 1e18):
                dist[v] = d + w; prev[v] = (u, oid, a, b); heapq.heappush(heap, (d + w, v))
    if kt not in dist:
        return None
    # The path is made of the traversed segments' own coordinates (consecutive segments meet within SNAP).
    pts, objs, joins, ferries, u, length = [], [], [], [], kt, 0
    while u != ks:
        u, oid, a, b = prev[u]
        length += math.dist(a, b)
        if not pts or pts[-1] != b:
            pts.append(b)
        pts.append(a)
        if oid == 'join':
            joins.append([round(math.dist(a, b), 1)] + [round(c, 6) for c in TO_GEO((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)]); continue
        if oid.startswith('ferry:'):
            ferries.append(oid[6:]); continue
        if not objs or objs[-1] != oid:
            objs.append(oid)
    return pts[::-1], objs[::-1], length, joins[::-1], ferries[::-1]


def road_part(cat, data, years, names, s, t, crossings):
    """The road between two points in the earliest year the roads connect them (see the module docstring)."""
    box = (min(s[0], t[0]) - MARGIN, min(s[1], t[1]) - MARGIN, max(s[0], t[0]) + MARGIN, max(s[1], t[1]) + MARGIN)
    prefer = data.get('preferEarlyRoads')
    for year in years:
        r = route(segments(cat, box, year, (prefer or {}).get('until')), s, t, crossings, prefer)
        if r:
            pts, objs, length, joins, ferries = r
            return dict(by='road', year=year, lengthMeters=round(length), objects=[dict(id=o, name=names[o]) for o in objs], joinsMeters=[j[0] for j in joins],
                        joinsAt=[j[1:] for j in joins], ferries=ferries,
                        path=[[round(c, 6) for c in TO_GEO(*s)]] + [[round(c, 6) for c in TO_GEO(*p)] for p in pts] + [[round(c, 6) for c in TO_GEO(*t)]])
    return dict(by='road', year=None, note='Inga daterade vägar förbinder punkterna.')


def build():
    """Each leg is valid for 'years' (the route's own period, 1638–1911) and may use only its listed ferry crossings.
    A boat leg is a road part from the station to its departure pier (when the pier is not the station itself), the
    boat line over 'water' and a road part from the landing to the next station."""
    cat, data = load()
    st = {s['id']: s for s in data['stations']}
    years = sorted({gp['from'] for o in cat['objects'] if o.get('kind') == 'roadSegment' for gp in o['geometryPeriods'] if 1800 <= gp['from'] <= 2026})
    names = {o['id']: o.get('name') or o['id'] for o in cat['objects']}
    crossings = {c['id']: c for c in data.get('crossings', [])}
    legs = []
    for leg in data['legs']:
        a, b = st[leg['from']], st[leg['to']]
        s, t = TO_METRIC(a['lon'], a['lat']), TO_METRIC(b['lon'], b['lat'])
        out = dict(**{'from': leg['from'], 'to': leg['to']}, by=leg['by'], years=leg['years'], note=leg.get('note', ''))
        if leg['by'] == 'road':
            out.update({k: v for k, v in road_part(cat, data, years, names, s, t, [crossings[c] for c in leg.get('crossings', [])]).items() if k != 'by'})
        else:
            parts = []
            dep = TO_METRIC(*leg['departure']) if leg.get('departure') else s
            if math.dist(dep, s) > 1:
                parts.append(road_part(cat, data, years, names, s, dep, []))
            parts.append(dict(by='boat', path=leg['water']))
            land = TO_METRIC(*leg['landing'])
            if math.dist(land, t) > 1:
                parts.append(road_part(cat, data, years, names, land, t, []))
            out.update(parts=parts)
        legs.append(out)
        print(leg['from'], '→', leg['to'], leg['years'], out.get('year'), out.get('lengthMeters'), len(out.get('objects', [])), 'objects, joins', out.get('joinsMeters'), 'ferries', out.get('ferries'),
              [(p['by'], p.get('year'), p.get('lengthMeters')) for p in out.get('parts', [])])
    js = ('/* Generated by scripts/build_postal_route.py from data/postal-route-stations.json and the road catalogue. */\n'
          'window.POSTAL_ROUTE_STATIONS=' + json.dumps(data['stations'], ensure_ascii=False, separators=(',', ':')) + ';\n'
          'window.POSTAL_ROUTE_ROADS=' + json.dumps(legs, ensure_ascii=False, separators=(',', ':')) + ';\n')
    (ROOT / 'dist/postal-route-roads.js').write_text(js)


if __name__ == '__main__':
    build()
