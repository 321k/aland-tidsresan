"""A window of a tile map with a 50 m metric grid (EPSG:3874, labelled every 100 m), a reference line (red) and,
optionally, OSM 2026 roads (green, ids), for reading old-road waypoints by hand.
Usage: grid_window.py MAP_KEY CENTER_D HALF SIZE OUT.jpg [--osm]   (REF: reference line json, default the Marsund line)"""
import sys, os, json, gzip
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from maps import tile_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, box
from PIL import Image, ImageDraw
for k, v in {'saltvik-1929': 'map-38157483', 'tjudo-1927': 'map-38157484', 'geta-1927': 'map-38157399', 'saltvik-1944': 'map-38147682', 'daglosa-1941': 'map-38147690', 'geta-1941': 'map-38138095', 'stromma-1941': 'map-38138094'}.items():
    maps.MAPS[k] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{v}/{{z}}/{{x}}/{{y}}.png'}
R = 'docs/reviews/saltviksvagen-2026-11-21'
L = LineString(json.load(open(os.environ.get('REF', f'{R}/data/reference.json')))['metric'])
key, d, h, S, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
cx, cy = (tuple(float(v) for v in os.environ['CENTER'].split(',')) if os.environ.get('CENTER') else L.interpolate(d).coords[0])   # CENTER=E,N overrides
im, f = (maps.scan_window(key, cx, cy, h, S) if key.startswith("nls:") else tile_window(key, 15, cx, cy, h, S)); dr = ImageDraw.Draw(im)
for E in range(int(cx - h) // 50 * 50, int(cx + h) + 50, 50):
    dr.line([f(E, cy - h), f(E, cy + h)], fill=(0, 120, 255) if E % 100 else (0, 0, 200), width=1)
    if E % 100 == 0: x, _ = f(E, cy + h); dr.text((x + 2, 2), str(E)[-4:], fill=(0, 0, 200))
for N in range(int(cy - h) // 50 * 50, int(cy + h) + 50, 50):
    dr.line([f(cx - h, N), f(cx + h, N)], fill=(0, 120, 255) if N % 100 else (0, 0, 200), width=1)
    if N % 100 == 0: _, y = f(cx - h, N); dr.text((2, y + 2), str(N)[-4:], fill=(0, 0, 200))
dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=1)
for k in range(int(d - h) // 100 * 100, int(d + h), 100):
    if 0 <= k <= L.length:
        x, y = f(*L.interpolate(k).coords[0]); dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 0, 0)); dr.text((x + 4, y + 4), str(k), fill=(255, 0, 0))
if '--osm' in sys.argv:
    for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features']:
        if g.get('kind') != 'road': continue
        for p in g['paths']:
            l = LineString([TO_METRIC(*q) for q in p])
            if l.intersects(box(cx - h, cy - h, cx + h, cy + h)):
                pts = [f(*q) for q in l.coords]; dr.line(pts, fill=(0, 160, 0), width=2); x, y = pts[len(pts) // 2]
                dr.text((x + 3, y - 10), g['id'][4:] + ' ' + (g.get('name') or '')[:16], fill=(0, 90, 0))
im.save(out, quality=90); print(out, round(cx), round(cy))
