"""Convert pixel positions read on a trace_old.py overlay (TRACE.jpg) back to EPSG:3874 metres.
Usage: overlay_to_metric.py MOSAIC.png TRACE.json X,Y [X,Y ...]"""
import sys, json
sys.path.insert(0, 'docs/reviews/lemlandsvagen-main-road-2026-11-17/scripts')
from trace import Mosaic, TO_M, TO_G
png, tj = sys.argv[1:3]; m = Mosaic(png, sigma=0.8); t = json.load(open(tj))
xs = [m.px(*TO_G(*p)) for p in t['trace']]
x0, y0 = int(min(p[0] for p in xs) - 40), int(min(p[1] for p in xs) - 40)
out = []
for s in sys.argv[3:]:
    X, Y = map(float, s.split(',')); E, N = TO_M(*m.geo(X / 3 + x0, Y / 3 + y0)); out.append([round(E), round(N)])
print(json.dumps(out))
