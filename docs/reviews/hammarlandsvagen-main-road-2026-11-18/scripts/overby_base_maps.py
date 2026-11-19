"""Överby (6.0–7.1 km along the Marsund connection) on the base maps 1968, 1978, 1985 (sheet 101203) and the 1956
parish map edition, with today's road (red) and the OSM ways along the old road (green). Usage: overby_base_maps.py OUT.jpg"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
import maps
from maps import tile_window, scan_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString
from PIL import Image, ImageDraw
maps.MAPS['eckero-1956'] = {'tiles_url': 'https://historicmaps2.vanhatkartat.fi/maps/mml/map-37971493/{z}/{x}/{y}.png'}
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
L = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
cx, cy = L.interpolate(6560).coords[0]; h, S = 600, 800
WAYS = {'way/641674806', 'way/1140848345', 'way/641674808', 'way/641674809', 'way/1479463187'}
osm = [(g['id'], [LineString([TO_METRIC(*q) for q in p]) for p in g['paths']]) for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features'] if g['id'] in WAYS]
sheet = Image.new('RGB', (2 * S, 2 * S), 'white')
for i, (name, key, scan) in enumerate([('base map 1968', 'nls:101203:1968', True), ('base map 1978', 'nls:101203:1978', True),
                                        ('base map 1985', 'nls:101203:1985', True), ('parish map 1956', 'eckero-1956', False)]):
    im, f = (scan_window(key, cx, cy, h, S) if scan else tile_window(key, 15, cx, cy, h, S)); dr = ImageDraw.Draw(im)
    dr.line([f(*p) for p in L.coords], fill=(255, 0, 0), width=1)
    for gid, ls in osm:
        for l in ls:
            pts = [f(*q) for q in l.coords]; dr.line(pts, fill=(0, 170, 0), width=1); x, y = pts[len(pts) // 2]; dr.text((x + 3, y - 12), gid[4:], fill=(0, 110, 0))
    dr.rectangle((0, 0, 150, 12), fill='black'); dr.text((2, 0), name, fill='yellow'); sheet.paste(im, ((i % 2) * S, (i // 2) * S))
sheet.save(sys.argv[1], quality=88); print(sys.argv[1])
