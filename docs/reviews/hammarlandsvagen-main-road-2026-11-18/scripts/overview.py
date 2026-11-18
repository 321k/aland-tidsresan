"""Wide overview windows of one tile map with today's Hammarlandsvägen (red) and optional traces (magenta).
Usage: overview.py MAP_ID ZOOM CENTER_D HALF_M SIZE OUT.jpg [TRACES.json]"""
import sys, json
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from maps import tile_window
from shapely.geometry import LineString
from PIL import ImageDraw
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
L = LineString(json.load(open(f'{R}/data/reference.json'))['metric'])
mid, z, d, half, size, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
traces = json.load(open(sys.argv[7])) if len(sys.argv) > 7 else {}
cx, cy = L.interpolate(d).coords[0]; im, f = tile_window(mid, z, cx, cy, half, size); dr = ImageDraw.Draw(im)
dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=2)
for k in range(0, int(L.length), 500):
    x, y = f(*L.interpolate(k).coords[0]); dr.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 0, 0)); dr.text((x + 4, y - 6), str(k), fill=(200, 0, 0))
for tr in traces.values(): dr.line([f(*p) for p in tr], fill=(255, 0, 255), width=2)
im.save(out, quality=88); print(out)
