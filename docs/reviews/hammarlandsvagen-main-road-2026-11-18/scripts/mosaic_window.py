"""Two parish-map tile sets combined (the second drawn where the first has no map), with a 50 m grid, the Marsund line
(red) and optionally OSM roads (green). Usage: mosaic_window.py KEY1 KEY2 E N HALF SIZE OUT.jpg [--osm]"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
import numpy as np, maps
from maps import tile_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, box
from PIL import Image, ImageDraw
for k, v in {'eckero-1929': 'map-39091228', 'eckero-1956': 'map-37971493', 'morby-1929': 'map-38157016', 'bovik-1946': 'map-38157019'}.items():
    maps.MAPS[k] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{v}/{{z}}/{{x}}/{{y}}.png'}
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
k1, k2, cx, cy, h, S, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
a, f = tile_window(k1, 15, cx, cy, h, S); b, _ = tile_window(k2, 15, cx, cy, h, S)
A, B = np.array(a), np.array(b); empty = (A.min(axis=2) > 245)
A[empty] = B[empty]; im = Image.fromarray(A); dr = ImageDraw.Draw(im)
for E in range(int(cx - h) // 50 * 50, int(cx + h) + 50, 50):
    dr.line([f(E, cy - h), f(E, cy + h)], fill=(0, 120, 255) if E % 100 else (0, 0, 200), width=1)
    if E % 100 == 0: x, _ = f(E, cy + h); dr.text((x + 2, 2), str(E)[-4:], fill=(0, 0, 200))
for N in range(int(cy - h) // 50 * 50, int(cy + h) + 50, 50):
    dr.line([f(cx - h, N), f(cx + h, N)], fill=(0, 120, 255) if N % 100 else (0, 0, 200), width=1)
    if N % 100 == 0: _, y = f(cx - h, N); dr.text((2, y + 2), str(N)[-4:], fill=(0, 0, 200))
L = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=1)
for k in range(0, int(L.length) + 1, 100):
    x, y = f(*L.interpolate(k).coords[0])
    if 0 <= x <= S and 0 <= y <= S: dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 0, 0)); dr.text((x + 4, y + 4), str(k), fill=(200, 0, 0))
if '--osm' in sys.argv:
    for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features']:
        if g.get('kind') != 'road' or g.get('class') in ('footway', 'path', 'cycleway', 'steps'): continue
        for p in g['paths']:
            l = LineString([TO_METRIC(*q) for q in p])
            if l.intersects(box(cx - h, cy - h, cx + h, cy + h)):
                pts = [f(*q) for q in l.coords]; dr.line(pts, fill=(0, 160, 0), width=1); x, y = pts[len(pts) // 2]
                dr.text((x + 3, y - 10), g['id'][4:] + ' ' + (g.get('name') or '')[:16] + ' ' + (g.get('class') or '')[:4], fill=(0, 90, 0))
im.save(out, quality=90); print(out)
