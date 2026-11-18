"""A tile map window with every OSM 2026 road (green, ids written) and today's Hammarlandsvägen (red), for matching
old roads to today's ways. Usage: osm_on_map.py MAP_ID CENTER_D HALF SIZE OUT.jpg [ZOOM]"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
from maps import tile_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString
from PIL import ImageDraw
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
L = LineString(json.load(open(f'{R}/data/reference.json'))['metric'])
mid, d, half, size, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]; Z = int(sys.argv[6]) if len(sys.argv) > 6 else 15
cx, cy = L.interpolate(d).coords[0]; im, f = tile_window(mid, Z, cx, cy, half, size); dr = ImageDraw.Draw(im)
for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features']:
    if g.get('kind') != 'road' or g.get('class') in ('footway', 'path', 'steps', 'cycleway') or (len(sys.argv) > 6 and g.get('class') not in ('primary', 'secondary', 'tertiary', 'unclassified')): continue
    for p in g['paths']:
        pts = [f(*TO_METRIC(*q)) for q in p]
        if any(0 <= x <= size and 0 <= y <= size for x, y in pts):
            dr.line(pts, fill=(0, 160, 0), width=1); x, y = pts[len(pts) // 2]; dr.text((x + 3, y), g['id'][4:] + ' ' + (g.get('name') or '')[:14], fill=(0, 90, 0))
dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=1)
for k in range(int(d - half), int(d + half), 100):
    x, y = f(*L.interpolate(k).coords[0]); dr.text((x + 5, y - 5), str(k), fill=(255, 0, 0))
im.save(out, quality=90); print(out)
