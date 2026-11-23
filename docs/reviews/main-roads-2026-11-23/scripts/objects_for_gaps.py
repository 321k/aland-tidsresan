"""For the red candidates of the screen on the given sheets: which catalogue object covers each gap piece today (within
25 m, the nearest road open in 2026), with the object's first year and earliest geometry. Aggregated by object.
Usage: objects_for_gaps.py OUT.json SHEET [SHEET ...]"""
import sys, json, gzip, math, collections
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
sys.argv, out, want = sys.argv[:1], sys.argv[1], set(sys.argv[2:])
import importlib.util
spec = importlib.util.spec_from_file_location('scr', 'docs/reviews/main-roads-2026-11-23/scripts/screen_red.py')
src = open('docs/reviews/main-roads-2026-11-23/scripts/screen_red.py').read().split('M = json.load(gzip.open')[0]
ns = {}; exec(src, ns)
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
from mariehamn_frame_1942 import TO_METRIC
cat, G = ns['cat'], ns['G']
objs = []
for o in cat['objects']:
    if o.get('kind') != 'roadSegment': continue
    st = next((s for s in o['states'] if s['from'] <= 2026 < (s['to'] or 9999)), None)
    gp = next((g for g in o['geometryPeriods'] if g['from'] <= 2026 < (g['to'] or 9999)), None)
    if not st or st['state'] != 'open' or not gp: continue
    for p in G[gp['geometryId']]['paths']:
        if len(p) > 1: objs.append((o, LineString([TO_METRIC(*q) for q in p])))
tree = STRtree([l for _, l in objs])
M = json.load(gzip.open('dist/assets/modern.json.gz'))['features']
agg = collections.defaultdict(lambda: dict(red=0, gap=0, roads=set(), sheets=set(), edition=None, unowned=0))
for f in M:
    if f.get('kind') != 'road' or f.get('class') not in ('primary', 'secondary', 'tertiary'): continue
    for p in f['paths']:
        m = [TO_METRIC(*q) for q in p]
        for a, b in zip(m, m[1:]):
            n = max(1, int(math.dist(a, b) // ns['STEP']))
            for i in range(n):
                t = (i + .5) / n; pt = Point(a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])); seg = math.dist(a, b) / n
                hits = [ns['sheet_list'][j] for j in ns['stree'].query(pt) if ns['sheet_list'][j][1][0].contains(pt)]
                if not hits: continue
                sheet, (_, year, sid) = min(hits, key=lambda h: h[1][1])
                if sheet not in want or ns['covered'](pt, year): continue
                share = ns['red_share'](sid, *pt.coords[0])
                if share is None or share < ns['RED_SHARE']: continue
                near = [(objs[j][1].distance(pt), objs[j][0]['id']) for j in tree.query(pt.buffer(25))]
                oid = min(near)[1] if near else '(no object today)'
                r = agg[oid]; r['red'] += seg; r['roads'].add(f.get('name') or '(namnlös)'); r['sheets'].add(sid)
O = {o['id']: o for o in cat['objects']}
rows = []
for oid, r in sorted(agg.items(), key=lambda kv: -kv[1]['red']):
    o = O.get(oid)
    rows.append(dict(objectId=oid, name=o.get('name') if o else None, firstYear=o['states'][0]['from'] if o else None,
                     periods=[(g['from'], g['to']) for g in o['geometryPeriods']] if o else None, redM=round(r['red']), roads=sorted(r['roads']), editions=sorted(r['sheets'])))
for r in rows: print(f"{r['redM']:6d} m  {r['objectId'][-45:]:45s} {str(r['name'])[:28]:28s} first {r['firstYear']} {r['periods']} {r['editions']}")
json.dump(rows, open(out, 'w'), ensure_ascii=False, indent=1)
