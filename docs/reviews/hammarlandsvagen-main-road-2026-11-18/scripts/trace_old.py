"""Trace an old road between hand-picked waypoints on a 1929 mosaic and report its distance profile to today's
Hammarlandsvägen (reference line). Usage: trace_old.py MOSAIC.png ROUTE OUT_PREFIX [--direct]  (--direct: the waypoints themselves, densified, no least-cost path)"""
import sys, json
sys.path.insert(0, 'docs/reviews/lemlandsvagen-main-road-2026-11-17/scripts')
import numpy as np
from trace import Mosaic, snap, smooth_metric, TO_M, TO_G
from shapely.geometry import LineString
from PIL import Image, ImageDraw
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
png, route, out = sys.argv[1:4]
wp = json.load(open(f'{R}/data/waypoints.json'))[route]
m = Mosaic(png); direct = '--direct' in sys.argv
geo = [TO_G(*p) for p in wp] if direct else [snap(m, TO_G(*p), 3) for p in wp]
pts = [tuple(p) for p in LineString(wp).segmentize(5).coords] if direct else smooth_metric(m.trace(geo), 13)
L = LineString(json.load(open(f'{R}/data/reference.json'))['metric']); T = LineString(pts)
prof = [(round(d), round(L.project(T.interpolate(d))), round(L.distance(T.interpolate(d)), 1)) for d in np.arange(0, T.length, 25)]
json.dump(dict(route=route, mosaic=png.rsplit('/', 1)[-1], waypoints=wp, trace=[[round(x, 2), round(y, 2)] for x, y in T.simplify(1.0).coords], profile=prof), open(out + '.json', 'w'))
img = Image.fromarray(m.rgb.astype('uint8')); xs = [m.px(*TO_G(*p)) for p in pts]
x0, y0 = min(p[0] for p in xs) - 40, min(p[1] for p in xs) - 40; x1, y1 = max(p[0] for p in xs) + 40, max(p[1] for p in xs) + 40
K = 3; im = img.crop((int(x0), int(y0), int(x1), int(y1))); im = im.resize((im.width * K, im.height * K), Image.LANCZOS); d = ImageDraw.Draw(im)
f = lambda q: ((q[0] - int(x0)) * K, (q[1] - int(y0)) * K)
d.line([f(m.px(*TO_G(*p))) for p in L.coords], fill=(255, 0, 0), width=1)
d.line([f(p) for p in xs], fill=(255, 0, 255), width=2)
for g in geo: x, y = f(m.px(*g)); d.ellipse((x - 3, y - 3, x + 3, y + 3), outline=(0, 0, 255))
im.save(out + '.jpg', quality=88)
print(len(pts), round(T.length), 'm'); print(' '.join(f'{a}:{b}:{c}' for a, b, c in prof))
