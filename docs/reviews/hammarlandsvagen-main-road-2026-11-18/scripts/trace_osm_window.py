"""A close window on a tile map or base-map scan with an old line (magenta, metres marked), today's OSM 2026 roads
(green, ids) and the catalogue objects' first geometry (cyan dashed by object, short ids). For matching an old road to
existing objects. Usage: trace_osm_window.py TRACE.json AT_M HALF SIZE OUT.jpg MAP(1929H|1944N|nls:101206:1968...)"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
from maps import tile_window, scan_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, box
from PIL import ImageDraw
T = LineString(json.load(open(sys.argv[1]))['trace']); at, half, size, out, mp = float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
cx, cy = T.interpolate(at).coords[0]; area = box(cx - half, cy - half, cx + half, cy + half)
TM = {'1929H': '9c72eaa7-cd73-4f92-91b0-dc36524bef08', '1944N': '9c72a692-bae4-473d-93bb-7bcdee1222e7'}
im, f = tile_window(TM[mp], 15, cx, cy, half, size) if mp in TM else scan_window(mp, cx, cy, half, size)
dr = ImageDraw.Draw(im)
for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features']:
    if g.get('kind') != 'road': continue
    for p in g['paths']:
        l = LineString([TO_METRIC(*q) for q in p])
        if l.intersects(area):
            pts = [f(*q) for q in l.coords]; dr.line(pts, fill=(0, 150, 0), width=1)
            m = l.intersection(area); m = getattr(m, 'geoms', [m])[0]; x, y = f(*m.interpolate(0.5, normalized=True).coords[0]); dr.text((x + 3, y + 2), g['id'][4:], fill=(0, 100, 0))
dr.line([f(*p) for p in T.coords], fill=(255, 0, 255), width=1)
for k in range(0, int(T.length), 25):
    x, y = f(*T.interpolate(k).coords[0]); dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 0, 255)); dr.text((x - 28, y - 4), str(k), fill=(160, 0, 160))
dr.rectangle((0, 0, 200, 12), fill='black'); dr.text((2, 0), f'{mp} trace {at:.0f} m', fill='yellow')
im.save(out, quality=90); print(out)
