"""Survey: today's main roads (OSM primary, secondary, tertiary) against the catalogue's dated roads on the base maps.

For every 20 m piece of a main road, the registered base-map sheets (data/rural-map-review.json, by their metric
frame) whose frame contains it give the earliest edition year Y there. The piece is covered if a catalogue road open in
Y (any open period containing Y) lies within TOL m. Also reported: pieces no catalogue road covers today (2026).
Output: per road name and sheet, the uncovered length at the first edition and today. Usage: survey.py [OUT.json]"""
import sys, json, gzip, math, collections
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, Point, Polygon
from shapely.strtree import STRtree
from pyproj import Transformer

TOL, STEP = 25, 20
rev = json.load(open('data/rural-map-review.json'))
sheets = {}
for s in rev['sources']:
    r = s.get('registration') or {}
    if 'metricFrame' not in r: continue
    t = Transformer.from_crs(r['crs'], 'EPSG:3874', always_xy=True).transform
    poly = Polygon([t(*p) for p in r['metricFrame']])
    k = s['sheet']; y = s['year']
    if k not in sheets or y < sheets[k][1]: sheets[k] = (poly, y)
sheet_list = list(sheets.items()); stree = STRtree([p for _, (p, _) in sheet_list])
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}
lines_by_year = {}
def lines(year):
    if year not in lines_by_year:
        ls = []
        for o in cat['objects']:
            if o.get('kind') != 'roadSegment': continue
            st = next((s for s in o['states'] if s['from'] <= year < (s['to'] or 9999)), None)
            gp = next((g for g in o['geometryPeriods'] if g['from'] <= year < (g['to'] or 9999)), None)
            if not st or st['state'] != 'open' or not gp: continue
            for p in G[gp['geometryId']]['paths']:
                if len(p) > 1: ls.append(LineString([TO_METRIC(*q) for q in p]))
        lines_by_year[year] = (ls, STRtree(ls))
    return lines_by_year[year]
def covered(pt, year):
    ls, tree = lines(year)
    return any(ls[i].distance(pt) <= TOL for i in tree.query(pt.buffer(TOL)))
M = json.load(gzip.open('dist/assets/modern.json.gz'))['features']
agg = collections.defaultdict(lambda: dict(total=0, gapFirst=0, gapToday=0, ways=set(), years=set(), at=None))
for f in M:
    if f.get('kind') != 'road' or f.get('class') not in ('primary', 'secondary', 'tertiary'): continue
    for p in f['paths']:
        m = [TO_METRIC(*q) for q in p]
        for a, b in zip(m, m[1:]):
            n = max(1, int(math.dist(a, b) // STEP))
            for i in range(n):
                t = (i + .5) / n; pt = Point(a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])); seg = math.dist(a, b) / n
                hits = [sheet_list[j] for j in stree.query(pt) if sheet_list[j][1][0].contains(pt)]
                if not hits: continue
                sheet, (_, year) = min(hits, key=lambda h: h[1][1])
                key = (f.get('name') or '(namnlös)', sheet)
                r = agg[key]; r['total'] += seg; r['years'].add(year)
                if not covered(pt, year):
                    r['gapFirst'] += seg; r['ways'].add(f['id'])
                    if r['at'] is None: r['at'] = [round(v) for v in pt.coords[0]]
                    if not covered(pt, 2026): r['gapToday'] += seg
rows = sorted(({'name': k[0], 'sheet': k[1], 'firstYear': min(v['years']), 'totalM': round(v['total']), 'gapFirstM': round(v['gapFirst']), 'gapTodayM': round(v['gapToday']),
                'ways': sorted(v['ways'])[:20], 'at': v['at']} for k, v in agg.items()), key=lambda r: -r['gapFirstM'])
tot = sum(r['totalM'] for r in rows); gf = sum(r['gapFirstM'] for r in rows); gt = sum(r['gapTodayM'] for r in rows)
print(f'main roads on registered sheets: {tot/1000:.1f} km; not covered at the first edition: {gf/1000:.1f} km; not covered even today: {gt/1000:.1f} km')
for r in rows[:60]:
    if r['gapFirstM'] >= 100: print(f"  {r['gapFirstM']:6d} m  (today {r['gapTodayM']:5d})  {r['name'][:30]:30s} sheet {r['sheet']} {r['firstYear']}  at {r['at']}")
if len(sys.argv) > 1: json.dump(rows, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
