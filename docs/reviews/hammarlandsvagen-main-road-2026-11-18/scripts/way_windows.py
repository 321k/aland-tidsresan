"""Windows along given OSM 2026 ways (cyan) with today's Hammarlandsvägen (red): 1917, 1928, 1929H, 1944K, 1953K, the
1968/1978 and 1985 base maps (first registered sheet that covers). Usage: way_windows.py OUT.jpg STEP HALF WAY[,WAY...]"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
from maps import tile_window, scan_window, inside, SHEETS
from rural_registration import registration_pair
from pyproj import Transformer
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString
from shapely.ops import linemerge
from PIL import Image, ImageDraw
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
L = LineString(json.load(open(f'{R}/data/reference.json'))['metric'])
out, step, half, ways = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4].split(',')
mod = {f['id']: f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']}
W = linemerge([LineString([TO_METRIC(*q) for q in mod[w]['paths'][0]]) for w in ways])
WL = list(getattr(W, 'geoms', [W]))
TILES = [('1917', '92062c61-d313-459a-be85-07f876826716', 14), ('1928', '9c76c491-898b-4b0b-9331-7af223831264', 15), ('1929H', '9c72eaa7-cd73-4f92-91b0-dc36524bef08', 15),
         ('1929M', '9c76c492-0456-43c6-9478-b2aa0034b26c', 15), ('1944K', '9c72a692-458e-4804-af82-e6ac6dbf73fe', 15), ('1953K', '9c72a692-80ff-433c-950e-1cf484176101', 15),
         ('1955J', '9c72a694-4f10-4b9f-9c9e-2f3d2a7c8e3a', 15)]
import json as _j
ids = {m['id'][:13]: m['id'] for m in _j.load(open('data/historical-map-sources.json'))['maps']}
TILES = [(n, ids[m[:13]], z) for n, m, z in TILES if m[:13] in ids]


def sheet_for(E, N, years):
    for sid in [f'nls:{s}:{y}' for y in years for s in ('101206', '101205', '101208', '101209')]:
        s = SHEETS.get(sid)
        if not s: continue
        fwd, inv = registration_pair(s); x, y = inv(Transformer.from_crs(3874, s['registration']['crs'], always_xy=True).transform(E, N))
        fx = [q[0] for q in s['registration']['pixelFrame']]; fy = [q[1] for q in s['registration']['pixelFrame']]
        if min(fx) < x < max(fx) and min(fy) < y < max(fy): return sid


P = 280; rows = []
for line in WL:
    d = 0.0
    while d <= line.length:
        rows.append(line.interpolate(d).coords[0]); d += step
sheet = Image.new('RGB', (P * 9, P * len(rows)), 'white')
for i, (cx, cy) in enumerate(rows):
    panels = []
    for n, m, z in TILES:
        if inside(m, cx, cy):
            win = tile_window(m, z, cx, cy, half, P); c = win[0].crop((P // 2 - 15, P // 2 - 15, P // 2 + 15, P // 2 + 15)).convert('L')
            panels.append((n, win if min(c.getdata()) < 200 else None))
        else:
            panels.append((n, None))
    for yrs in ([1968], [1978], [1985]):
        s = sheet_for(cx, cy, yrs); panels.append((s[4:] if s else str(yrs[0]), scan_window(s, cx, cy, half, P) if s else None))
    panels = panels[:9]
    for j, (n, win) in enumerate(panels):
        t, f = win if win else (Image.new('RGB', (P, P), (220, 220, 220)), None)
        dr = ImageDraw.Draw(t)
        if f:
            dr.line([f(*p) for p in L.coords if abs(p[0] - cx) < 3 * half and abs(p[1] - cy) < 3 * half], fill=(255, 0, 0), width=1)
            for l in WL: dr.line([f(*p) for p in l.coords if abs(p[0] - cx) < 3 * half and abs(p[1] - cy) < 3 * half], fill=(0, 190, 230), width=1)
        dr.rectangle((0, 0, 130, 12), fill='black'); dr.text((2, 0), f'{i} {n}', fill='yellow'); sheet.paste(t, (j * P, i * P))
sheet.save(out, quality=85); print(out, len(rows))
