"""Distance from scan-trace samples to the modern Lemlandsvägen line (metres, EPSG:3874), with position along the line."""
import sys, json, gzip
from shapely.geometry import LineString, Point
sys.path.insert(0, 'scripts')
from postwar_city import METRIC
c = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in c['geometries']}
o = next(o for o in c['objects'] if o['id'] == 'road:qgis:mariehamn:lemlandsvagen-2-100km3')
L = LineString([METRIC(*p) for p in G[o['geometryPeriods'][0]['geometryId']]['paths'][0]])
for p in json.loads(sys.stdin.read()):
    q = Point(METRIC(p[0], p[1])); print(round(L.project(q)), round(L.distance(q), 1), p[2])
