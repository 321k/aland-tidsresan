"""Trace a hand-waypointed road on a mosaic and report its distance profile to today's road.
Usage: trace_route.py MOSAIC.png ROUTE OUT_PREFIX [OBJECT_ID]  (waypoints from ../data/waypoints.json)"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import numpy as np
from trace import Mosaic, snap, smooth_metric, TO_M, TO_G
from shapely.geometry import LineString, Point
from PIL import Image, ImageDraw
png, route, out = sys.argv[1:4]; oid = sys.argv[4] if len(sys.argv) > 4 else 'road:qgis:mariehamn:lemlandsvagen-1-100km3'
here = __file__.rsplit('/', 2)[0]
wp = [(E0 + a, N0 + b) for E0, N0, pts in json.load(open(here + '/data/waypoints.json'))[route] for a, b in pts]
m = Mosaic(png)
geo = [snap(m, TO_G(*p), 3) for p in wp]
pts = smooth_metric(m.trace(geo), 13)
c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); G = {g['id']: g for g in c['geometries']}; O = {o['id']: o for o in c['objects']}
L = LineString([TO_M(*p) for p in G[O[oid]['geometryPeriods'][-1]['geometryId']]['paths'][0]])
T = LineString(pts); prof = []
for d in np.arange(0, T.length, 25):
    p = T.interpolate(d); prof.append((round(d), round(L.project(p)), round(L.distance(p), 1)))
json.dump(dict(route=route, mosaic=png.rsplit('/', 1)[-1], waypoints=wp, trace=[[round(x, 2), round(y, 2)] for x, y in T.simplify(1.0).coords], profile=prof), open(out + '.json', 'w'))
# overlay
img = Image.fromarray(m.rgb.astype('uint8')); xs = [m.px(*TO_G(*p)) for p in pts]
x0, y0 = min(p[0] for p in xs) - 30, min(p[1] for p in xs) - 30; x1, y1 = max(p[0] for p in xs) + 30, max(p[1] for p in xs) + 30
K = 3; im = img.crop((int(x0), int(y0), int(x1), int(y1))); im = im.resize((im.width * K, im.height * K), Image.LANCZOS); d = ImageDraw.Draw(im)
f = lambda q: ((q[0] - int(x0)) * K, (q[1] - int(y0)) * K)
d.line([f(m.px(*TO_G(*p))) for p in L.coords], fill=(255, 0, 0), width=1)
d.line([f(p) for p in xs], fill=(255, 0, 255), width=2)
for g in geo: x, y = f(m.px(*g)); d.ellipse((x - 3, y - 3, x + 3, y + 3), outline=(0, 0, 255))
im.save(out + '.jpg', quality=88)
print(len(pts), round(T.length), 'm'); print(' '.join(f'{a}:{b}:{c_}' for a, b, c_ in prof))
