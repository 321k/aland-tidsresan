"""Screen the survey's gaps on the first-edition scans: is the base map's red main-road symbol within RADIUS m of a gap
piece? For each 20 m gap piece (survey.py logic), the scan of the sheet's first edition is sampled in a square of
±RADIUS m and the share of strong red pixels (R > 170, G < 120, B < 120) is measured. A share of at least RED_SHARE
counts as "drawn as a main road" (a red fill crossing the square); thin red boundary lines and red text stay below it.
This is a screening for review, not evidence: every candidate is checked by eye on the map before it is dated.
Usage: screen_red.py OUT.json"""
import sys, json, gzip, math, collections
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import numpy as np
import maps
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, Point, Polygon
from shapely.strtree import STRtree
from pyproj import Transformer
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

TOL, STEP, RADIUS, RED_SHARE = 25, 20, 20, 0.06
rev = json.load(open('data/rural-map-review.json'))
sheets = {}
for s in rev['sources']:
    r = s.get('registration') or {}
    if 'metricFrame' not in r: continue
    t = Transformer.from_crs(r['crs'], 'EPSG:3874', always_xy=True).transform
    poly = Polygon([t(*p) for p in r['metricFrame']])
    if s['sheet'] not in sheets or s['year'] < sheets[s['sheet']][1]: sheets[s['sheet']] = (poly, s['year'], s['id'])
sheet_list = list(sheets.items()); stree = STRtree([p for _, (p, _, _) in sheet_list])
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}
cache = {}
def lines(year):
    if year not in cache:
        ls = []
        for o in cat['objects']:
            if o.get('kind') != 'roadSegment': continue
            st = next((s for s in o['states'] if s['from'] <= year < (s['to'] or 9999)), None)
            gp = next((g for g in o['geometryPeriods'] if g['from'] <= year < (g['to'] or 9999)), None)
            if not st or st['state'] != 'open' or not gp: continue
            for p in G[gp['geometryId']]['paths']:
                if len(p) > 1: ls.append(LineString([TO_METRIC(*q) for q in p]))
        cache[year] = (ls, STRtree(ls))
    return cache[year]
def covered(pt, year):
    ls, tree = lines(year); return any(ls[i].distance(pt) <= TOL for i in tree.query(pt.buffer(TOL)))
scans = {}
def red_share(sid, E, N):
    if sid not in scans:
        try: maps.scan_window(sid, E, N, 50, 10)
        except Exception: scans[sid] = None; return None
        img, px = maps._scans[sid]; scans[sid] = (np.asarray(img), px)
    if scans[sid] is None: return None
    a, px = scans[sid]
    pts = [px(E + dx, N + dy) for dx in (-RADIUS, RADIUS) for dy in (-RADIUS, RADIUS)]
    x0, y0 = int(min(p[0] for p in pts)), int(min(p[1] for p in pts)); x1, y1 = int(max(p[0] for p in pts)) + 1, int(max(p[1] for p in pts)) + 1
    w = a[max(0, y0):y1, max(0, x0):x1]
    if w.size == 0: return None
    r, g, b = w[..., 0].astype(int), w[..., 1].astype(int), w[..., 2].astype(int)
    return float(((r > 170) & (g < 120) & (b < 120)).mean())
M = json.load(gzip.open('dist/assets/modern.json.gz'))['features']
agg = collections.defaultdict(lambda: dict(total=0, gap=0, red=0, nored=0, unread=0, ways=set(), at=None, year=None, sid=None))
for f in M:
    if f.get('kind') != 'road' or f.get('class') not in ('primary', 'secondary', 'tertiary'): continue
    for p in f['paths']:
        m = [TO_METRIC(*q) for q in p]
        for a_, b_ in zip(m, m[1:]):
            n = max(1, int(math.dist(a_, b_) // STEP))
            for i in range(n):
                t = (i + .5) / n; pt = Point(a_[0] + t * (b_[0] - a_[0]), a_[1] + t * (b_[1] - a_[1])); seg = math.dist(a_, b_) / n
                hits = [sheet_list[j] for j in stree.query(pt) if sheet_list[j][1][0].contains(pt)]
                if not hits: continue
                sheet, (_, year, sid) = min(hits, key=lambda h: h[1][1])
                r = agg[(f.get('name') or '(namnlös)', sheet)]; r['total'] += seg; r['year'] = year; r['sid'] = sid
                if covered(pt, year): continue
                r['gap'] += seg; r['ways'].add(f['id'])
                share = red_share(sid, *pt.coords[0])
                if share is None: r['unread'] += seg
                elif share >= RED_SHARE:
                    r['red'] += seg
                    if r['at'] is None: r['at'] = [round(v) for v in pt.coords[0]]
                else: r['nored'] += seg
rows = sorted(({'name': k[0], 'sheet': k[1], 'firstEdition': v['sid'], 'totalM': round(v['total']), 'gapM': round(v['gap']), 'redM': round(v['red']), 'noRedM': round(v['nored']),
                'unreadM': round(v['unread']), 'ways': sorted(v['ways']), 'at': v['at']} for k, v in agg.items() if v['gap'] > 0), key=lambda r: -r['redM'])
g = sum(r['gapM'] for r in rows); red = sum(r['redM'] for r in rows); nr = sum(r['noRedM'] for r in rows); un = sum(r['unreadM'] for r in rows)
print(f'gaps {g/1000:.1f} km: red on the first edition {red/1000:.1f} km, not red {nr/1000:.1f} km, scan not readable {un/1000:.1f} km')
for r in rows[:45]:
    if r['redM'] >= 150: print(f"  red {r['redM']:6d} m of gap {r['gapM']:6d}  {r['name'][:28]:28s} {r['firstEdition']}  at {r['at']}")
json.dump(rows, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
