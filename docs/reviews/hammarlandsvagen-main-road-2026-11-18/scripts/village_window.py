"""One area at several dates: the 1929H/1944N parish maps and the 1968/1985 base maps, with today's Hammarlandsvägen
(red), an old line read on the 1929 map (magenta, optional) and the catalogue's road objects near it (cyan with ids,
their 1968 geometry where they have one, else their first). Usage: village_window.py CENTER_D HALF SIZE OUT.jpg [TRACE.json|ROUTE] [OBJ_PREFIX,...]"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
from maps import tile_window, scan_window
from rural_registration import registration_pair
from pyproj import Transformer
from maps import SHEETS
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, box
from PIL import Image, ImageDraw
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
L = LineString(json.load(open(f'{R}/data/reference.json'))['metric'])
d, half, size, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
cx, cy = L.interpolate(d).coords[0]; area = box(cx - half, cy - half, cx + half, cy + half)
T = None
if len(sys.argv) > 5 and sys.argv[5] != '-':
    a = sys.argv[5]; T = json.load(open(a))['trace'] if a.endswith('.json') else json.load(open(f'{R}/data/waypoints.json'))[a]
def sheet_for(E, N, years):
    for sid in [f'nls:{s}:{y}' for y in years for s in ('101206', '101205', '101208', '101209')]:
        s = SHEETS.get(sid)
        if not s: continue
        fwd, inv = registration_pair(s); x, y = inv(Transformer.from_crs(3874, s['registration']['crs'], always_xy=True).transform(E, N))
        fx = [q[0] for q in s['registration']['pixelFrame']]; fy = [q[1] for q in s['registration']['pixelFrame']]
        if min(fx) < x < max(fx) and min(fy) < y < max(fy): return sid


cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}
objs = []
for o in cat['objects']:
    if not o['id'].startswith('road') or not o.get('geometryPeriods'): continue
    gps = o['geometryPeriods']; gp = next((p for p in gps if p.get('from') == 1968), gps[0])
    for path in G[gp['geometryId']]['paths']:
        l = LineString([TO_METRIC(*q) for q in path])
        if l.intersects(area): objs.append((o['id'].split(':')[-1], gp.get('from'), l))
panels = [('1929H', tile_window('9c72eaa7-cd73-4f92-91b0-dc36524bef08', 15, cx, cy, half, size)),
          ('1944N', tile_window('9c72a692-bae4-473d-93bb-7bcdee1222e7', 15, cx, cy, half, size))]
for y in (1968, 1985):
    s = sheet_for(cx, cy, [y]); panels.append((s, scan_window(s, cx, cy, half, size)))
sheet = Image.new('RGB', (size * 2, size * 2), 'white')
for i, (n, (im, f)) in enumerate(panels):
    dr = ImageDraw.Draw(im)
    dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=1)
    if T: dr.line([f(*p) for p in T], fill=(255, 0, 255), width=2)
    if i >= 2:
        for k, (oid, fy, l) in enumerate(objs):
            pts = [f(*p) for p in l.coords]; dr.line(pts, fill=(0, 170, 220), width=1)
            if i == 3: x, y = pts[len(pts) // 2]; dr.text((x + 3, y - 4), f'{oid[:28]} {fy}', fill=(0, 60, 140))
    dr.rectangle((0, 0, 160, 12), fill='black'); dr.text((2, 0), f'{d:.0f} {n}', fill='yellow'); sheet.paste(im, ((i % 2) * size, (i // 2) * size))
sheet.save(out, quality=88); print(out, len(objs))
