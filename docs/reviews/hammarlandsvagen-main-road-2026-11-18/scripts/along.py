"""Comparison sheets along today's Hammarlandsvägen (red): Senate atlas 1917, the parish map (1928 Hammarudda-Kungsö /
1929 Hammarby / 1929 Maarianhamina, whichever covers), the 1944 parish map, the first registered base map (1968, or
1978 where only that exists), the 1985 base map and a plain OSM 2026 panel. Optional traces (magenta) and extra lines.
Usage: along.py OUT_PREFIX D0 D1 STEP HALF_M [ROWS_PER_SHEET] [TRACES.json]"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from maps import tile_window, scan_window, inside, SHEETS, TO_GEO
from rural_registration import registration_pair
from pyproj import Transformer
from shapely.geometry import LineString
from PIL import Image, ImageDraw
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
ref = json.load(open(f'{R}/data/reference.json')); L = LineString(ref['metric'])
out, d0, d1, step, half = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
rows_per = int(sys.argv[6]) if len(sys.argv) > 6 else 6
traces = json.load(open(sys.argv[7])) if len(sys.argv) > 7 else {}
mod = [f for f in json.loads(gzip.decompress(open('dist/assets/modern.json.gz', 'rb').read()))['features'] if f.get('kind') == 'road']
from mariehamn_frame_1942 import TO_METRIC
P = 300
SENATE = '92062c61-d313-459a-be85-07f876826716'
PARISH = ['9c76c491-898b-4b0b-9331-7af223831264', '9c72eaa7-cd73-4f92-91b0-dc36524bef08', '9c76c492-0456-43c6-9478-b2aa0034b26c']
MID = ['9c72a692-458e-4804-af82-e6ac6dbf73fe', '9c72a692-bae4-473d-93bb-7bcdee1222e7', '9c72a694-1238-40a8-a8ca-33c754332810']


def sheet_for(E, N, years):
    for sid in [f'nls:{s}:{y}' for y in years for s in ('101206', '101205', '101208')]:
        s = SHEETS.get(sid)
        if not s: continue
        fwd, inv = registration_pair(s); x, y = inv(Transformer.from_crs(3874, s['registration']['crs'], always_xy=True).transform(E, N))
        fx = [q[0] for q in s['registration']['pixelFrame']]; fy = [q[1] for q in s['registration']['pixelFrame']]
        if min(fx) < x < max(fx) and min(fy) < y < max(fy): return sid      # inside the printed map frame, not the margin
    return None


def first_drawn(ids, labels, cx, cy, half):
    """The first map whose sheet actually has drawing at the window centre (sheet areas overlap; margins are blank)."""
    for m in ids:
        if not inside(m, cx, cy): continue
        win = tile_window(m, 15, cx, cy, half, P); c = win[0].crop((P // 2 - 20, P // 2 - 20, P // 2 + 20, P // 2 + 20)).convert('L')
        if min(c.getdata()) < 200: return (labels[m], win)
    return ('parish', None)


names = {m: json.load(open('data/historical-map-sources.json')) for m in []}
ds = []; d = d0
while d <= d1: ds.append(d); d += step
for k in range(0, len(ds), rows_per):
    chunk = ds[k:k + rows_per]; sheet = Image.new('RGB', (P * 6, P * len(chunk)), 'white')
    for i, dd in enumerate(chunk):
        cx, cy = L.interpolate(dd).coords[0]
        panels = []
        panels.append(('1917', tile_window(SENATE, 14, cx, cy, half, P) if inside(SENATE, cx, cy) else None))
        panels.append(first_drawn(PARISH, {PARISH[0]: '1928', PARISH[1]: '1929H', PARISH[2]: '1929M'}, cx, cy, half))
        panels.append(first_drawn(MID, {MID[0]: '1944K', MID[1]: '1944N', MID[2]: '1948M'}, cx, cy, half))
        s1 = sheet_for(cx, cy, [1968, 1978]); s2 = sheet_for(cx, cy, [1985])
        panels.append((s1[4:] if s1 else 'base', scan_window(s1, cx, cy, half, P) if s1 else None))
        panels.append((s2[4:] if s2 else 'base', scan_window(s2, cx, cy, half, P) if s2 else None))
        panels.append(('OSM', None))
        for j, (nm, win) in enumerate(panels):
            if j == 5:
                t = Image.new('RGB', (P, P), (245, 243, 236)); f = lambda E, N: ((E - cx + half) / (2 * half) * P, (cy + half - N) / (2 * half) * P)
                dr = ImageDraw.Draw(t)
                for g in mod:
                    for p in g['paths']:
                        if len(p) > 1: dr.line([f(*TO_METRIC(*q)) for q in p], fill=(150, 150, 150), width=1)
            elif win is None:
                t = Image.new('RGB', (P, P), (220, 220, 220)); f = None
            else:
                t, f = win
            dr = ImageDraw.Draw(t)
            if f:
                dr.line([f(*p) for p in L.coords if abs(p[0] - cx) < 3 * half and abs(p[1] - cy) < 3 * half], fill=(255, 0, 0), width=1)
                for tr in traces.values():
                    dr.line([f(*p) for p in tr if abs(p[0] - cx) < 3 * half and abs(p[1] - cy) < 3 * half], fill=(255, 0, 255), width=1)
            dr.rectangle((0, 0, 120, 12), fill='black'); dr.text((2, 0), f'{int(dd)} m {nm}', fill='yellow'); sheet.paste(t, (j * P, i * P))
    path = f'{out}-{int(chunk[0]):05d}.jpg'; sheet.save(path, quality=85); print(path)
