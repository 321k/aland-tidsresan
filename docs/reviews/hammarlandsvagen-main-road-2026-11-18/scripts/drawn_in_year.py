"""What the catalogue draws in a given year (magenta: road objects open with a geometry period that year) over a map
window around today's Hammarlandsvägen. Usage: drawn_in_year.py YEAR CENTER_D HALF SIZE MAP(1929H|1944N|nls:...) OUT.jpg"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
from maps import tile_window, scan_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString
from PIL import ImageDraw
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
year, d, half, size, mp, out = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
L = LineString(json.load(open(f'{R}/data/reference.json'))['metric']); cx, cy = L.interpolate(d).coords[0]
TM = {'1929H': '9c72eaa7-cd73-4f92-91b0-dc36524bef08', '1944N': '9c72a692-bae4-473d-93bb-7bcdee1222e7'}
im, f = tile_window(TM[mp], 15, cx, cy, half, size) if mp in TM else scan_window(mp, cx, cy, half, size)
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
dr.rectangle((0, 0, 150, 12), fill='black'); dr.text((2, 0), f'drawn {year} on {mp}', fill='yellow'); im.save(out, quality=88); print(out)
