"""Kyrkoby–Storby along the Marsund connection: the parish maps 1021 01 Mörby 1929 and its Bovik edition 1946, the
1968 base map (sheet 101203) and OSM 2026, with the connection (red, distances from Frebbenby).
Usage: storby_windows.py CENTER_D HALF SIZE OUT.jpg"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
import maps
from maps import tile_window, scan_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, box
from PIL import Image, ImageDraw
for k, v in {'eckero-1929': 'map-39091228', 'sandgrunden-1928': 'map-39091224', 'morby-1929': 'map-38157016', 'bovik-1946': 'map-38157019'}.items():
    maps.MAPS[k] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{v}/{{z}}/{{x}}/{{y}}.png'}
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
L = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
d, h, S, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
cx, cy = L.interpolate(d).coords[0]
mod = [g for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features'] if g.get('kind') == 'road' and g.get('class') not in ('footway', 'path', 'cycleway', 'steps')]
sheet = Image.new('RGB', (S * 2, S * 2), 'white')
for i, (n, key, osm) in enumerate([('Mörby 1929', 'morby-1929', False), ('Bovik 1946', 'bovik-1946', False), ('base map 1968', 'nls:101203:1968', False), ('Mörby 1929 + OSM', 'morby-1929', True)]):
    try:
        im, f = scan_window(key, cx, cy, h, S) if key.startswith('nls:') else tile_window(key, 15, cx, cy, h, S)
    except Exception as e:
        print(n, 'unavailable', type(e).__name__); continue
    dr = ImageDraw.Draw(im)
    if osm:
        for g in mod:
            for p in g['paths']:
                l = LineString([TO_METRIC(*q) for q in p])
                if l.intersects(box(cx - h, cy - h, cx + h, cy + h)):
                    pts = [f(*q) for q in l.coords]; dr.line(pts, fill=(0, 150, 0), width=2); x, y = pts[len(pts) // 2]; dr.text((x + 3, y), g['id'][4:] + ' ' + (g.get('name') or '')[:14], fill=(0, 80, 0))
    else:
        dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=1)
    for k in range(int(d - h) // 100 * 100, int(d + h), 100):
        if 0 <= k <= L.length:
            x, y = f(*L.interpolate(k).coords[0]); dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 0, 0)); dr.text((x + 4, y - 12), str(k), fill=(255, 0, 0))
    dr.rectangle((0, 0, 170, 12), fill='black'); dr.text((2, 0), n, fill='yellow'); sheet.paste(im, ((i % 2) * S, (i // 2) * S))
sheet.save(out, quality=85); print(out)
