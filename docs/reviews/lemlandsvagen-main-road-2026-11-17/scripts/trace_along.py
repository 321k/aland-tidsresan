"""Trace the drawn road along a stretch of today's road (waypoints = today's line every STEP m, snapped to the
nearest drawn band within SNAP px) and report 150 m bin medians of the distance to today's line.
Usage: trace_along.py MOSAIC.png FROM_M TO_M OUT_PREFIX [STEP] [SNAP]"""
import sys, json, gzip, statistics
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import numpy as np
from trace import Mosaic, snap, smooth_metric, TO_M, TO_G
from shapely.geometry import LineString, Point
png, a, b, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
step = float(sys.argv[5]) if len(sys.argv) > 5 else 100; rad = int(sys.argv[6]) if len(sys.argv) > 6 else 5
c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); G = {g['id']: g for g in c['geometries']}; O = {o['id']: o for o in c['objects']}
L = LineString([TO_M(*p) for p in G[O['road:qgis:mariehamn:lemlandsvagen-1-100km3']['geometryPeriods'][-1]['geometryId']]['paths'][0]])
m = Mosaic(png)
wp = [snap(m, TO_G(*L.interpolate(d).coords[0]), rad) for d in np.arange(a, b + 0.1, step)]
T = LineString(smooth_metric(m.trace(wp), 7)); bins = {}
for d in np.arange(0, T.length, 5):
    p = T.interpolate(d); s = L.project(p)
    if a <= s < b: bins.setdefault(int((s - a) // 150), []).append(L.distance(p))
med = [round(statistics.median(bins[k]), 1) if k in bins else None for k in range(int((b - a) // 150) + 1)]
json.dump(dict(mosaic=png.rsplit('/', 1)[-1], range=[a, b], step=step, snapPx=rad, trace=[[round(x, 2), round(y, 2)] for x, y in T.simplify(1.0).coords], binMedians=med), open(out + '.json', 'w'))
print(med)
