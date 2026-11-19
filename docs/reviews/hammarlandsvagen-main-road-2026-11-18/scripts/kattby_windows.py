"""Kattby westwards (17.2–18.6 km along today's Hammarlandsvägen) on the parish maps of sheet 1012 03 Eckerö (1929,
colour; 1956, black and white; vanhatkartat tiles of the funet scans, not yet in data/historical-map-sources.json) and
the 1929 Hammarby sheet, with today's road (red) and OSM 2026 roads (green, ids). Usage: kattby_windows.py CENTER_D HALF SIZE OUT.jpg [YEAR]"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
import maps
from maps import tile_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, box
from PIL import Image, ImageDraw
EXTRA = {'eckero-1929': 'map-39091228', 'eckero-1956': 'map-37971493'}
for k, v in EXTRA.items():
    maps.MAPS[k] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{v}/{{z}}/{{x}}/{{y}}.png'}
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
import os
L = LineString(json.load(open(os.environ.get('REF', f'{R}/data/reference.json')))['metric'])   # REF: another reference line
d, h, S, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
YEAR = int(sys.argv[5]) if len(sys.argv) > 5 else None   # optional: draw what the catalogue shows that year (magenta)
cx, cy = L.interpolate(d).coords[0]
mod = [g for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features'] if g.get('kind') == 'road' and g.get('class') not in ('footway', 'path', 'cycleway', 'steps')]
panels = [('Eckerö 1929', 'eckero-1929', False), ('Eckerö 1956', 'eckero-1956', False), ('Hammarby 1929', '9c72eaa7-cd73-4f92-91b0-dc36524bef08', False), ('Eckerö 1929 + OSM', 'eckero-1929', True)]
sheet = Image.new('RGB', (S * 2, S * 2), 'white')
for i, (n, m, osm) in enumerate(panels):
    im, f = tile_window(m, 15, cx, cy, h, S); dr = ImageDraw.Draw(im)
    if osm:
        for g in mod:
            for p in g['paths']:
                l = LineString([TO_METRIC(*q) for q in p])
                if l.intersects(box(cx - h, cy - h, cx + h, cy + h)):
                    pts = [f(*q) for q in l.coords]; dr.line(pts, fill=(0, 150, 0), width=2); x, y = pts[len(pts) // 2]; dr.text((x + 3, y), g['id'][4:] + ' ' + (g.get('name') or '')[:14], fill=(0, 80, 0))
    elif YEAR:
        cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {x['id']: x for x in cat['geometries']}; inn = lambda o_, y: o_['from'] <= y < (o_['to'] or 9999)
        for o_ in cat['objects']:
            if o_['kind'] == 'roadSegment' and any(inn(s_, YEAR) and s_['state'] == 'open' for s_ in o_['states']):
                for gp in o_['geometryPeriods']:
                    if inn(gp, YEAR):
                        for p in G[gp['geometryId']]['paths']:
                            pts = [f(*TO_METRIC(*q)) for q in p]
                            if any(-50 < x < S + 50 and -50 < y < S + 50 for x, y in pts): dr.line(pts, fill=(255, 0, 255), width=3)
    else:
        dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=1)
    for k in range(int(d - h) // 100 * 100, int(d + h), 100):
        if 0 <= k <= L.length:
            x, y = f(*L.interpolate(k).coords[0]); dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 0, 0)); dr.text((x + 4, y - 12), str(k), fill=(255, 0, 0))
    dr.rectangle((0, 0, 150, 12), fill='black'); dr.text((2, 0), n, fill='yellow'); sheet.paste(im, ((i % 2) * S, (i // 2) * S))
sheet.save(out, quality=88); print(out)
