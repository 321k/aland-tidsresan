"""A window of a historical map (tile map by uuid, or a registered base-map scan 'nls:1012xx:YEAR') with a 100 m metric
grid (EPSG:3874), catalogue roads open in YEAR (red, names) and optionally OSM 2026 roads (green, ids).
Usage: window.py MAP CX CY HALF SIZE YEAR OUT.jpg [--osm] [--nocat]"""
import sys, json, gzip
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, box
from PIL import ImageDraw
import os as _os
if _os.environ.get('SHEETS_EXTRA'):                                # extra registered scans (a review's registrations file)
    maps.SHEETS.update({x['id']: x for x in json.load(open(_os.environ['SHEETS_EXTRA']))['sources']})
if sys.argv[1].startswith('map-'):                               # a paituli parish map by its map id (tile server)
    maps.MAPS[sys.argv[1]] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{sys.argv[1]}/{{z}}/{{x}}/{{y}}.png'}
key, cx, cy, h, S, year, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
im, f = (maps.scan_window(key, cx, cy, h, S) if key.startswith('nls:') else maps.tile_window(key, int(__import__('os').environ.get('Z', 15)), cx, cy, h, S)); dr = ImageDraw.Draw(im)
step = 100 if h <= 800 else 200
for E in range(int(cx - h) // step * step, int(cx + h) + step, step):
    dr.line([f(E, cy - h), f(E, cy + h)], fill=(0, 120, 255), width=1); x, _ = f(E, cy + h); dr.text((x + 2, 2), str(E)[-4:], fill=(0, 0, 200))
for N in range(int(cy - h) // step * step, int(cy + h) + step, step):
    dr.line([f(cx - h, N), f(cx + h, N)], fill=(0, 120, 255), width=1); _, y = f(cx - h, N); dr.text((2, y + 2), str(N)[-4:], fill=(0, 0, 200))
B = box(cx - h, cy - h, cx + h, cy + h)
if '--nocat' not in sys.argv:
    c = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in c['geometries']}
    for o in c['objects']:
        if not o['id'].startswith('road'): continue
        for gp in o['geometryPeriods']:
            if gp['from'] <= year < (gp['to'] or 9999):
                for p in G[gp['geometryId']]['paths']:
                    if len(p) < 2: continue
                    l = LineString([TO_METRIC(*q) for q in p])
                    if l.intersects(B):
                        pts = [f(*q) for q in l.coords]; dr.line(pts, fill=(230, 0, 0), width=1); x, y = pts[len(pts) // 2]
                        dr.text((x + 3, y + 2), (o.get('name') or '')[:22], fill=(200, 0, 0))
if '--osm' in sys.argv:
    for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features']:
        if g.get('kind') != 'road': continue
        for p in g['paths']:
            l = LineString([TO_METRIC(*q) for q in p])
            if l.intersects(B):
                pts = [f(*q) for q in l.coords]; dr.line(pts, fill=(0, 160, 0), width=1); x, y = pts[len(pts) // 2]
                dr.text((x + 3, y - 10), g['id'][4:], fill=(0, 90, 0))
im.save(out, quality=88); print(out)
