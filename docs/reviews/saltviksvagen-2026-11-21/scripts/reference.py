"""Write data/reference.json: today's Saltviksvägen from Saltviksvägen del 1 east and south to Kvarnbo (EPSG:3874),
the catalogue's objects joined end to end (through the Kavelbro bypass). Usage: reference.py CATALOGUE.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
IDS = ['road:qgis:tjudo:saltviksvagen-100km1', 'road:qgis:saltvik:saltviksvagen-2-batch4', 'road:qgis:saltvik:saltviksvagen-antbole-nygard',
       'road:qgis:saltvik:saltviksvagen-kavelbro-norr', 'road:qgis:saltvik:saltviksvagen-kavelbro-forbifart', 'road:qgis:saltvik:saltviksvagen-kvarnbo-kavelbro']
pts = []
for i in IDS:
    p = [TO_METRIC(*q) for q in G[O[i]['geometryPeriods'][-1]['geometryId']]['paths'][0]]
    if pts and (p[0][0] - pts[-1][0]) ** 2 + (p[0][1] - pts[-1][1]) ** 2 > (p[-1][0] - pts[-1][0]) ** 2 + (p[-1][1] - pts[-1][1]) ** 2: p = p[::-1]
    if not pts: p = p[::-1]   # the Tjudö object runs from del 2 west to del 1: start at del 1
    pts += p if not pts else p[1:]
json.dump(dict(note='Saltviksvägen: Tjudö part, del 2, Antböle–Nygård, Kavelbro (bypass), Kvarnbo–Kavelbro (EPSG:3874), joined end to end', metric=[[round(x, 2), round(y, 2)] for x, y in pts]),
          open('docs/reviews/saltviksvagen-2026-11-21/data/reference.json', 'w'))
from shapely.geometry import LineString
print(round(LineString(pts).length), [ (i.split(':')[-1], round(LineString(pts).project(__import__('shapely.geometry').geometry.Point(TO_METRIC(*G[O[i]['geometryPeriods'][-1]['geometryId']]['paths'][0][0]))))) for i in IDS])
