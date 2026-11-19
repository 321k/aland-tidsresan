"""Marsundsvägen (magenta, the catalogue object) on the base maps 1968, 1978, 1985 (sheets 101203 and 101206, whichever
covers it) and the 1956 parish map edition, with its distances from Frebbenby (red). Usage: marsundsvagen_base_maps.py OUT.jpg"""
import sys, json
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
sys.path.insert(0, R + '/scripts'); sys.path.insert(0, 'scripts')
import maps
from maps import scan_window, tile_window
from shapely.geometry import LineString
from PIL import Image, ImageDraw
maps.MAPS['eckero-1956'] = {'tiles_url': 'https://historicmaps2.vanhatkartat.fi/maps/mml/map-37971493/{z}/{x}/{y}.png'}
L = LineString(json.load(open(f'{R}/data/marsundsvagen-reference.json'))['metric'])
cx, cy = L.interpolate(560).coords[0]; h, S = 620, 700
panels = [('1956 parish map', 'eckero-1956')] + [(f'{y} base map {s}', f'nls:{s}:{y}') for y in (1968, 1978, 1985) for s in ('101203', '101206')]
sheet = Image.new('RGB', (S * 4, S * 2), 'white')
for i, (name, key) in enumerate(panels):
    try:
        im, f = tile_window(key, 15, cx, cy, h, S) if key.startswith('eckero') else scan_window(key, cx, cy, h, S)
    except Exception as e:
        print(name, 'unavailable', type(e).__name__); continue
    dr = ImageDraw.Draw(im); dr.line([f(*p) for p in L.coords], fill=(255, 0, 255), width=1)
    for k in range(0, int(L.length), 100):
        x, y = f(*L.interpolate(k).coords[0]); dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 0, 0)); dr.text((x + 3, y + 3), str(k), fill=(200, 0, 0))
    dr.rectangle((0, 0, 170, 12), fill='black'); dr.text((2, 0), name, fill='yellow'); sheet.paste(im, ((i % 4) * S, (i // 4) * S))
sheet.save(sys.argv[1], quality=85); print(sys.argv[1])
