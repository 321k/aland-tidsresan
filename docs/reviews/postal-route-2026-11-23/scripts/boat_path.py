"""The postal boat's line over water: the shortest path through water on a grid of today's OSM coastline
(dist/assets/coast.json.gz), keeping at least CLEAR m from land where the water allows it, simplified.
Usage: boat_path.py E1 N1 E2 N2   (landings in EPSG:3874; prints lon/lat waypoints as JSON)
The coastline is today's; the sea stood about 1–1.5 m higher in the 18th century, so channels were if anything wider."""
import sys, json, gzip, heapq, math
sys.path.insert(0, 'scripts')
import numpy as np
from mariehamn_frame_1942 import TO_METRIC, TO_GEO
from shapely.geometry import shape, box, LineString, Point
from shapely import prepared
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

CELL, CLEAR, MARGIN = 20, 60, 1500
e1, n1, e2, n2 = map(float, sys.argv[1:5])
x0, y0, x1, y1 = min(e1, e2) - MARGIN, min(n1, n2) - MARGIN, max(e1, e2) + MARGIN, max(n1, n2) + MARGIN
land = shape(json.load(gzip.open('dist/assets/coast.json.gz'))['geometry'])
lo0, la0 = TO_GEO(x0, y0); lo1, la1 = TO_GEO(x1, y1)
land = land.intersection(box(min(lo0, lo1) - .01, min(la0, la1) - .01, max(lo0, lo1) + .01, max(la0, la1) + .01))
W, H = int((x1 - x0) / CELL) + 1, int((y1 - y0) / CELL) + 1
im = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(im)
f = lambda E, N: ((E - x0) / CELL, (y1 - N) / CELL)
for poly in getattr(land, 'geoms', [land]):
    dr.polygon([f(*TO_METRIC(*q)) for q in poly.exterior.coords], fill=1)
    for r in poly.interiors: dr.polygon([f(*TO_METRIC(*q)) for q in r.coords], fill=0)
water = np.array(im) == 0
dist = distance_transform_edt(water) * CELL                     # metres to land
cell = lambda E, N: (int(round((y1 - N) / CELL)), int(round((E - x0) / CELL)))
def nearest_water(rc):
    r, c = rc; best = None
    for dr_ in range(-6, 7):
        for dc in range(-6, 7):
            rr, cc = r + dr_, c + dc
            if 0 <= rr < H and 0 <= cc < W and water[rr, cc] and (best is None or dr_ * dr_ + dc * dc < best[0]): best = (dr_ * dr_ + dc * dc, (rr, cc))
    return best[1]
s, t = nearest_water(cell(e1, n1)), nearest_water(cell(e2, n2))
g = {s: 0}; prev = {}; heap = [(0, s)]
while heap:
    d, u = heapq.heappop(heap)
    if u == t: break
    if d > g[u]: continue
    for dr_ in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if not dr_ and not dc: continue
            v = (u[0] + dr_, u[1] + dc)
            if not (0 <= v[0] < H and 0 <= v[1] < W) or not water[v]: continue
            w = math.hypot(dr_, dc) * CELL * (1 + 3 * max(0, CLEAR - dist[v]) / CLEAR)
            if d + w < g.get(v, 1e18): g[v] = d + w; prev[v] = u; heapq.heappush(heap, (d + w, v))
path, u = [t], t
while u != s: u = prev[u]; path.append(u)
pts = [(x0 + c * CELL, y1 - r * CELL) for r, c in path[::-1]]
line = LineString([(e1, n1)] + pts + [(e2, n2)]).simplify(30)
geo = [[round(v, 6) for v in TO_GEO(*p)] for p in line.coords]
crossing = LineString(geo).intersection(land)
ends = [Point(TO_GEO(e1, n1)), Point(TO_GEO(e2, n2))]
print(json.dumps(dict(meters=round(line.length), points=geo)))
