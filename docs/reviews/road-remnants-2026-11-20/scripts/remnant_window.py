"""A 1929 parish-map window around a heritage-register road remnant: its register outline (magenta, dashed area),
today's catalogue roads open in YEAR (green) and a 50 m grid. Usage: remnant_window.py CODE TILE_KEY HALF YEAR OUT.jpg"""
import sys, json, gzip
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from maps import tile_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import shape
from PIL import ImageDraw
TILES = {'lumparland-1929': 'map-39093010', 'eckero-1929': 'map-39091228', 'hammarby-1929': 'map-39092401', 'jomala-1928': 'map-39092821', 'flaka-1929': 'map-39093008', 'hammarby-1944': 'map-37946377'}
for k, v in TILES.items():
    maps.MAPS[k] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{v}/{{z}}/{{x}}/{{y}}.png'}
code, key, half, year, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
f = next(x for x in json.load(open('dist/assets/heritage-boundaries.geojson'))['features'] if x['properties']['code'] == code)
g = shape(f['geometry']); cx, cy = TO_METRIC(*g.centroid.coords[0])
im, fx = tile_window(key, 15, cx, cy, half, 1000); dr = ImageDraw.Draw(im)
for E in range(int(cx - half) // 50 * 50, int(cx + half) + 50, 50):
    dr.line([fx(E, cy - half), fx(E, cy + half)], fill=(0, 120, 255), width=1)
for N in range(int(cy - half) // 50 * 50, int(cy + half) + 50, 50):
    dr.line([fx(cx - half, N), fx(cx + half, N)], fill=(0, 120, 255), width=1)
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {x['id']: x for x in cat['geometries']}
for o in cat['objects']:
    if o['kind'] != 'roadSegment': continue
    for gp in o['geometryPeriods']:
        if gp['from'] <= year < (gp['to'] or 9999):
            for p in G[gp['geometryId']]['paths']:
                pts = [fx(*TO_METRIC(*q)) for q in p]
                if any(-50 < x < 1050 and -50 < y < 1050 for x, y in pts): dr.line(pts, fill=(0, 170, 0), width=3)
for poly in getattr(g, 'geoms', [g]):
    dr.line([fx(*TO_METRIC(*q)) for q in poly.exterior.coords], fill=(230, 0, 200), width=3)
dr.rectangle((0, 0, 260, 12), fill='black'); dr.text((2, 0), f'{code} on {key}; green = catalogue {year}', fill='yellow'); im.save(out, quality=88); print(out)
