"""The two Överby loops of the old road (magenta: the 1929 trace; green: Gamla Landsvägen and Brinkbacken in OSM) on
the 1956 parish map edition and the base maps 1968, 1978, 1985 (sheet 101203), with the Marsund line's distances (red).
Usage: overby_loops.py   (writes renders/overby-east-1956-1985.jpg and overby-west-1956-1985.jpg)"""
import sys, json, gzip
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
sys.path.insert(0, R + '/scripts'); sys.path.insert(0, 'scripts')
import maps
from maps import scan_window, tile_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString
from PIL import Image, ImageDraw
maps.MAPS['eckero-1956'] = {'tiles_url': 'https://historicmaps2.vanhatkartat.fi/maps/mml/map-37971493/{z}/{x}/{y}.png'}
L = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
T = json.load(open(f'{R}/data/trace-overby-1929.json'))['trace']
osm = [(g['id'], [[TO_METRIC(*q) for q in p] for p in g['paths']]) for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features'] if g['id'] in ('way/641674806', 'way/1140848345')]
for name, (d, h) in {'east': (6200, 230), 'west': (6760, 380)}.items():
    cx, cy = L.interpolate(d).coords[0]; S = 700
    sheet = Image.new('RGB', (2 * S, 2 * S), 'white')
    for i, (label, key) in enumerate([('1956', 'eckero-1956'), ('1968', 'nls:101203:1968'), ('1978', 'nls:101203:1978'), ('1985', 'nls:101203:1985')]):
        im, f = tile_window(key, 15, cx, cy, h, S) if key.startswith('eckero') else scan_window(key, cx, cy, h, S); dr = ImageDraw.Draw(im)
        dr.line([f(*p) for p in T], fill=(255, 0, 255), width=1)
        for gid, ps in osm:
            for p in ps: dr.line([f(*q) for q in p], fill=(0, 170, 0), width=1)
        for k in range(int(d - h) // 50 * 50, int(d + h), 50):
            x, y_ = f(*L.interpolate(k).coords[0]); dr.ellipse((x - 2, y_ - 2, x + 2, y_ + 2), fill=(255, 0, 0)); dr.text((x + 3, y_ + 3), str(k), fill=(200, 0, 0))
        dr.rectangle((0, 0, 120, 12), fill='black'); dr.text((2, 0), label, fill='yellow'); sheet.paste(im, ((i % 2) * S, (i // 2) * S))
    sheet.save(f'{R}/renders/overby-{name}-1956-1985.jpg', quality=88)
print('ok')
