"""Contact sheet of an object's geometry (green, its earliest or a given period) over a registered base-map scan, in
windows of ±HALF m every STEP m along the line, with a 100 m grid; other catalogue roads open in YEAR in red.
Usage: along.py OBJECT_ID SHEET_ID YEAR OUT.jpg [GEOMETRY_PERIOD_INDEX] [RANGES_JSON]
With RANGES_JSON (a list per path of [a, b] metres), matched ranges are drawn green and the rest magenta."""
import sys, json, gzip, math
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, box
from PIL import Image, ImageDraw
import os
HALF, STEP, SIZE = 350, 600, int(os.environ.get('SIZE', 520))
COLS = int(os.environ.get('COLS', 4))
oid, sid, year, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
pi = int(sys.argv[5]) if len(sys.argv) > 5 else -1
RANGES = json.loads(sys.argv[6]) if len(sys.argv) > 6 else None
from shapely.ops import substring
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
o = O[oid]; g = G[o['geometryPeriods'][pi]['geometryId']]
mine = [LineString([TO_METRIC(*q) for q in p]) for p in g['paths'] if len(p) > 1]
others = []
for x in cat['objects']:
    if x.get('kind') != 'roadSegment' or x['id'] == oid: continue
    st = next((s for s in x['states'] if s['from'] <= year < (s['to'] or 9999)), None); gp = next((q for q in x['geometryPeriods'] if q['from'] <= year < (q['to'] or 9999)), None)
    if st and st['state'] == 'open' and gp: others += [LineString([TO_METRIC(*q) for q in p]) for p in G[gp['geometryId']]['paths'] if len(p) > 1]
centres = []
for l in mine:
    d = 0
    while d <= l.length: centres.append(l.interpolate(d).coords[0]); d += STEP
    if l.length - (d - STEP) > STEP / 3: centres.append(l.coords[-1])
from shapely.geometry import Point as _P, Polygon as _Poly
from pyproj import Transformer as _T
def _frame(s_):
    r = s_['registration']; t = _T.from_crs(r['crs'], 'EPSG:3874', always_xy=True).transform
    return _Poly([t(*q) for q in r['metricFrame']])
SIDS = sid.split(',')                      # several sheets: each tile is read on the first whose frame contains it
FR = {x: _frame(maps.SHEETS[x]) for x in SIDS if 'metricFrame' in maps.SHEETS[x].get('registration', {})}
tiles = []
for cx, cy in centres:
    use = next((x for x in SIDS if x in FR and FR[x].contains(_P(cx, cy))), SIDS[0])
    try: im, f = maps.scan_window(use, cx, cy, HALF, SIZE)
    except Exception: continue
    dr = ImageDraw.Draw(im); B = box(cx - HALF, cy - HALF, cx + HALF, cy + HALF)
    for E in range(int(cx - HALF) // 100 * 100, int(cx + HALF) + 100, 100): dr.line([f(E, cy - HALF), f(E, cy + HALF)], fill=(0, 120, 255)); dr.text((f(E, cy + HALF)[0] + 2, 2), str(E)[-4:], fill=(0, 0, 200))
    for N in range(int(cy - HALF) // 100 * 100, int(cy + HALF) + 100, 100): dr.line([f(cx - HALF, N), f(cx + HALF, N)], fill=(0, 120, 255)); dr.text((2, f(cx - HALF, N)[1] + 2), str(N)[-4:], fill=(0, 0, 200))
    for l in others:
        if l.intersects(B): dr.line([f(*c) for c in l.coords], fill=(220, 0, 0), width=1)
    for k, l in enumerate(mine):
        if not l.intersects(B): continue
        if RANGES is None: dr.line([f(*c) for c in l.coords], fill=(0, 170, 0), width=2); continue
        dr.line([f(*c) for c in l.coords], fill=(230, 0, 230), width=2)
        for a, b in RANGES[k]:
            part = substring(l, a, b)
            if part.length > 0: dr.line([f(*c) for c in part.coords], fill=(0, 170, 0), width=3)
    tiles.append(im)
cols = COLS; rows = (len(tiles) + cols - 1) // cols
sheet = Image.new('RGB', (cols * SIZE, rows * SIZE), 'white')
for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * SIZE, (i // cols) * SIZE))
sheet.save(out, quality=85); print(out, len(tiles), 'tiles', round(sum(l.length for l in mine)), 'm')
