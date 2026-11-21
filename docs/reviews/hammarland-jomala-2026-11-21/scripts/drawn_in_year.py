"""What the catalogue draws in a given year (magenta: road objects open with a geometry period that year) over a map
window along the reference line. Usage: drawn_in_year.py YEAR CENTER_D HALF SIZE MAP(tile key|nls:...) OUT.jpg"""
import sys, json, gzip
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from maps import tile_window, scan_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString
from PIL import ImageDraw
for k, v in {'saltvik-1929': 'map-38157483', 'tjudo-1927': 'map-38157484', 'geta-1927': 'map-38157399', 'saltvik-1944': 'map-38147682', 'daglosa-1941': 'map-38147690', 'geta-1941': 'map-38138095', 'stromma-1941': 'map-38138094'}.items():
    maps.MAPS[k] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{v}/{{z}}/{{x}}/{{y}}.png'}
maps.MAPS['senate-1917'] = maps.MAPS['92062c61-d68d-43ef-b581-e9bdcdc8e0ba']
D = 'docs/reviews/hammarland-jomala-2026-11-21'
year, d, half, size, mp, out = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
L = LineString(json.load(open(f'{D}/data/reference.json'))['metric']); cx, cy = L.interpolate(d).coords[0]
im, f = scan_window(mp, cx, cy, half, size) if mp.startswith('nls:') else tile_window(mp, 14 if half > 700 else 15, cx, cy, half, size)
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}
dr = ImageDraw.Draw(im); inside = lambda o, y: o['from'] <= y < (o['to'] or 9999)
for o in cat['objects']:
    if o['kind'] != 'roadSegment' or not any(inside(s, year) and s['state'] == 'open' for s in o['states']): continue
    for gp in o['geometryPeriods']:
        if inside(gp, year):
            for p in G[gp['geometryId']]['paths']:
                pts = [f(*TO_METRIC(*q)) for q in p]
                if any(-50 < x < size + 50 and -50 < y < size + 50 for x, y in pts):
                    dr.line(pts, fill=(255, 0, 255), width=3)
dr.rectangle((0, 0, 190, 12), fill='black'); dr.text((2, 0), f'drawn {year} on {mp}', fill='yellow'); im.save(out, quality=88); print(out)
