"""Overview windows along the reference line (red, km marks) on a tile map or a registered base-map scan.
Usage: overview.py MAP START_M END_M STEP HALF SIZE PREFIX   (MAP: tile key like flaka-1929 or a sheet id nls:101210:1968)"""
import sys, json
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from maps import tile_window, scan_window
from shapely.geometry import LineString
from PIL import ImageDraw
TILES = {'saltvik-1929': 'map-38157483', 'tjudo-1927': 'map-38157484', 'geta-1927': 'map-38157399', 'saltvik-1944': 'map-38147682', 'daglosa-1941': 'map-38147690', 'geta-1941': 'map-38138095', 'stromma-1941': 'map-38138094'}
for k, v in TILES.items():
    maps.MAPS[k] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{v}/{{z}}/{{x}}/{{y}}.png'}
D = 'docs/reviews/getavagen-2026-11-20'
L = LineString(json.load(open(f'{D}/data/reference.json'))['metric'])
maps.MAPS['senate-1917'] = maps.MAPS['92062c61-d68d-43ef-b581-e9bdcdc8e0ba']
key, a, b, step, h, S, prefix = sys.argv[1], *map(float, sys.argv[2:6]), int(sys.argv[6]), sys.argv[7]
d = a
while d <= b:
    cx, cy = L.interpolate(d).coords[0]
    im, f = (scan_window(key, cx, cy, h, S) if key.startswith('nls:') else tile_window(key, 14 if h > 700 else 15, cx, cy, h, S))
    dr = ImageDraw.Draw(im)
    dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=1)
    for k in range(0, int(L.length), 250):
        x, y = f(*L.interpolate(k).coords[0]); dr.ellipse((x - 3, y - 3, x + 3, y + 3), outline=(255, 0, 0)); dr.text((x + 5, y + 3), str(k), fill=(255, 0, 0))
    out = f'{prefix}-{int(d)}.jpg'; im.save(out, quality=88); print(out); d += step
