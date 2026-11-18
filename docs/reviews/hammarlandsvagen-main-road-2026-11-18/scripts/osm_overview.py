"""OSM 2026 roads with names over the same window as overview.py, today's Hammarlandsvägen red.
Usage: osm_overview.py CENTER_D HALF_M SIZE OUT.jpg [MIN_CLASS_LIST]"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString
from PIL import Image, ImageDraw
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
L = LineString(json.load(open(f'{R}/data/reference.json'))['metric'])
d, half, size, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
cx, cy = L.interpolate(d).coords[0]; f = lambda E, N: ((E - cx + half) / (2 * half) * size, (cy + half - N) / (2 * half) * size)
im = Image.new('RGB', (size, size), (248, 246, 240)); dr = ImageDraw.Draw(im)
for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features']:
    if g.get('kind') != 'road' or g.get('class') in ('footway', 'path', 'steps', 'cycleway'): continue
    for p in g['paths']:
        pts = [f(*TO_METRIC(*q)) for q in p]
        if not any(0 <= x <= size and 0 <= y <= size for x, y in pts): continue
        w = 3 if g.get('class') in ('primary', 'secondary', 'tertiary') else 1
        dr.line(pts, fill=(90, 90, 90), width=w)
        if g.get('name') and g['name'] != 'Väg eller stig' and len(p) > 3:
            x, y = pts[len(pts) // 2]; dr.text((x + 2, y), g['name'] + ' ' + g['id'][4:], fill=(0, 0, 160))
dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=2)
for k in range(0, int(L.length), 500):
    x, y = f(*L.interpolate(k).coords[0]); dr.text((x + 4, y - 6), str(k), fill=(200, 0, 0))
im.save(out); print(out)
