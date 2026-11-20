"""Candidate catalogue roads (today's geometry, coloured) over a parish-map window along the reference line.
Usage: candidates.py MAP CENTER_D HALF SIZE OUT.jpg id=colour ..."""
import sys, json, gzip
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from maps import tile_window, scan_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString
from PIL import ImageDraw
for k, v in {'saltvik-1929': 'map-38157483', 'tjudo-1927': 'map-38157484', 'geta-1927': 'map-38157399', 'saltvik-1944': 'map-38147682', 'daglosa-1941': 'map-38147690', 'geta-1941': 'map-38138095'}.items():
    maps.MAPS[k] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{v}/{{z}}/{{x}}/{{y}}.png'}
mp, d, half, S, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
want = dict(a.split('=') for a in sys.argv[6:])
L = LineString(json.load(open('docs/reviews/getavagen-2026-11-20/data/reference.json'))['metric']); cx, cy = L.interpolate(d).coords[0]
im, f = scan_window(mp, cx, cy, half, S) if mp.startswith('nls:') else tile_window(mp, 14 if half > 700 else 15, cx, cy, half, S)
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
dr = ImageDraw.Draw(im); y = 4
for oid, col in want.items():
    for p in G[O[oid]['geometryPeriods'][-1]['geometryId']]['paths']:
        dr.line([f(*TO_METRIC(*q)) for q in p], fill=col, width=3)
    dr.rectangle((0, y - 2, 330, y + 11), fill='black'); dr.text((3, y), O[oid].get('name', oid)[:45], fill=col); y += 14
for k in range(0, int(L.length), 500):
    x, yy = f(*L.interpolate(k).coords[0]); dr.text((x + 5, yy), str(k), fill=(160, 0, 160))
im.save(out, quality=88); print(out)
