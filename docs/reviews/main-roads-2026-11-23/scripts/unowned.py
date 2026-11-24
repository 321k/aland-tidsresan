"""Main-road OSM ways (2026 extract; primary, secondary, tertiary) that no catalogue object owns and that no catalogue
road open in 2026 lies along (under half the way within 25 m), on a registered base-map sheet. Ways with the same name
that touch are grouped. Writes OUT.json (the groups) and OUT_CAT.json.gz: the catalogue with one candidate object per
group ('cand:<first way>', open from 2026, one path per way), for match_editions.py and along.py (env CAT).
Usage: unowned.py OUT.json OUT_CAT.json.gz"""
import sys, json, gzip, collections
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, Polygon
from shapely.strtree import STRtree
from shapely.ops import unary_union
from pyproj import Transformer

out, out_cat = sys.argv[1], sys.argv[2]
rev = json.load(open('data/rural-map-review.json'))
frames = {}
for s in rev['sources']:
    r = s.get('registration') or {}
    if 'metricFrame' not in r: continue
    t = Transformer.from_crs(r['crs'], 'EPSG:3874', always_xy=True).transform
    k = s['sheet']
    if k not in frames or s['year'] < frames[k][1]: frames[k] = (Polygon([t(*p) for p in r['metricFrame']]), s['year'], s['id'])
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}
owned = {l['featureId'] for o in cat['objects'] for l in o.get('sourceLinks', []) if l['datasetId'] == 'osm-2026'}
today = []
for o in cat['objects']:
    if o.get('kind') != 'roadSegment': continue
    st = next((s for s in o['states'] if s['from'] <= 2026 < (s['to'] or 9999)), None)
    gp = next((g for g in o['geometryPeriods'] if g['from'] <= 2026 < (g['to'] or 9999)), None)
    if st and st['state'] == 'open' and gp:
        today += [LineString([TO_METRIC(*q) for q in p]) for p in G[gp['geometryId']]['paths'] if len(p) > 1]
tree = STRtree(today)
ways = []
for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']:
    if f.get('kind') != 'road' or f.get('class') not in ('primary', 'secondary', 'tertiary') or f['id'] in owned: continue
    if len(f['paths']) != 1 or len(f['paths'][0]) < 2: continue
    l = LineString([TO_METRIC(*q) for q in f['paths'][0]])
    sh = [(k, v) for k, v in frames.items() if v[0].contains(l.centroid)]
    if not sh: continue
    near = l.intersection(unary_union([today[i] for i in tree.query(l.buffer(25))]).buffer(25)).length if len(tree.query(l.buffer(25))) else 0
    if near > 0.5 * l.length: continue
    k, (poly, year, sid) = min(sh, key=lambda x: x[1][1])
    ways.append(dict(id=f['id'], name=f.get('name') or '', cls=f['class'], line=l, path=f['paths'][0], sheet=k, year=year, near=round(near)))
# group: same name, ends within 1 m
parent = list(range(len(ways)))
def find(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
for i, a in enumerate(ways):
    for j in range(i):
        b = ways[j]
        if a['name'] == b['name'] and a['line'].distance(b['line']) < 1: parent[find(i)] = find(j)
groups = collections.defaultdict(list)
for i, w in enumerate(ways): groups[find(i)].append(w)
res = []
for g in groups.values():
    g.sort(key=lambda w: w['id'])
    cid = 'cand:' + g[0]['id']
    res.append(dict(id=cid, name=g[0]['name'], ways=[w['id'] for w in g], classes=sorted({w['cls'] for w in g}), sheets=sorted({w['sheet'] for w in g}),
                    firstYear=min(w['year'] for w in g), length=round(sum(w['line'].length for w in g)), nearToday=sum(w['near'] for w in g),
                    at=[round(c) for c in g[0]['line'].interpolate(0.5, normalized=True).coords[0]]))
    gid = 'geometry:' + cid
    cat['geometries'].append(dict(id=gid, representation='centerline', paths=[w['path'] for w in g], sourceIds=[]))
    cat['objects'].append(dict(id=cid, name=g[0]['name'], kind='roadSegment', states=[{'state': 'open', 'from': 2026, 'to': None}],
                               geometryPeriods=[{'geometryId': gid, 'from': 2026, 'to': None}], evidence=[], sourceLinks=[]))
res.sort(key=lambda r: -r['length'])
json.dump(res, open(out, 'w'), indent=1, ensure_ascii=False)
json.dump(cat, gzip.open(out_cat, 'wt'))
print(len(res), 'groups', sum(r['length'] for r in res), 'm')
for r in res: print(r['length'], r['id'], r['name'], r['sheets'], r['firstYear'], len(r['ways']), r['at'])
