"""Draw given catalogue geometries (green, 2 px) on a map window with a 100 m grid. Usage:
line_on_map.py MAP CX CY HALF SIZE OUT.jpg GEOMETRY_ID [GEOMETRY_ID ...]"""
import sys, json, gzip
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from mariehamn_frame_1942 import TO_METRIC
from PIL import ImageDraw
key, cx, cy, h, S, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
im, f = (maps.scan_window(key, cx, cy, h, S) if key.startswith('nls:') else maps.tile_window(key, 15, cx, cy, h, S)); dr = ImageDraw.Draw(im)
for E in range(int(cx - h) // 100 * 100, int(cx + h) + 100, 100):
    dr.line([f(E, cy - h), f(E, cy + h)], fill=(0, 120, 255), width=1); x, _ = f(E, cy + h); dr.text((x + 2, 2), str(E)[-4:], fill=(0, 0, 200))
for N in range(int(cy - h) // 100 * 100, int(cy + h) + 100, 100):
    dr.line([f(cx - h, N), f(cx + h, N)], fill=(0, 120, 255), width=1); _, y = f(cx - h, N); dr.text((2, y + 2), str(N)[-4:], fill=(0, 0, 200))
G = {g['id']: g for g in json.load(gzip.open('dist/assets/temporal-objects.json.gz'))['geometries']}
for gid in sys.argv[7:]:
    for p in G[gid]['paths']:
        dr.line([f(*TO_METRIC(*q)) for q in p], fill=(0, 170, 0), width=2)
im.save(out, quality=88); print(out)
