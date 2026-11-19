"""The old road through Överby read on renders/overby-grid-1929.jpg (1200 px window, 600 m half-width around 6 560 m
along the Marsund line): pixel waypoints converted to EPSG:3874 metres by inverting the window's projection, then
compared with the OSM ways along it. Writes data/trace-overby-1929.json. Usage: overby_trace.py"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
import numpy as np, maps
from maps import tile_window
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, Point
from shapely.ops import substring
maps.MAPS['eckero-1929'] = {'tiles_url': 'https://historicmaps2.vanhatkartat.fi/maps/mml/map-39091228/{z}/{x}/{y}.png'}
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
L = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
cx, cy = L.interpolate(6560).coords[0]
_, f = tile_window('eckero-1929', 15, cx, cy, 600, 1200)
# affine inverse of the (near-linear) window projection, fitted on a grid
E, N = np.meshgrid(np.linspace(cx - 600, cx + 600, 9), np.linspace(cy - 600, cy + 600, 9)); E, N = E.ravel(), N.ravel()
P = np.array([f(e, n) for e, n in zip(E, N)]); A = np.c_[P, np.ones(len(P))]
ce, cn = np.linalg.lstsq(A, E, rcond=None)[0], np.linalg.lstsq(A, N, rcond=None)[0]
inv = lambda x, y: (float(np.dot([x, y, 1], ce)), float(np.dot([x, y, 1], cn)))
print('inverse fit max error m', round(max(abs(np.dot(A, ce) - E).max(), abs(np.dot(A, cn) - N).max()), 2))
PX = [(1100, 462), (1050, 450), (1000, 438), (965, 430), (940, 445), (910, 480), (880, 510), (850, 535), (820, 550), (790, 560),
      (757, 566), (720, 560), (690, 553), (660, 545), (630, 537), (600, 530), (575, 528), (545, 535), (510, 542), (470, 550),
      (420, 560), (370, 568), (320, 575), (270, 583), (220, 592), (190, 600), (160, 615), (130, 635), (105, 660), (85, 685), (65, 710)]
T = LineString([inv(*p) for p in PX])
print('trace', round(T.length), 'm; ends along the Marsund line', round(L.project(Point(T.coords[0]))), round(L.project(Point(T.coords[-1]))),
      'off', round(L.distance(Point(T.coords[0]))), round(L.distance(Point(T.coords[-1]))))
prof = [(int(d), round(L.project(T.interpolate(d))), round(L.distance(T.interpolate(d)))) for d in range(0, int(T.length), 50)]
print('along-trace : along-Marsund : offset', ' '.join(f'{a}:{b}:{c}' for a, b, c in prof))
for g in json.load(gzip.open('dist/assets/modern.json.gz'))['features']:
    if g.get('kind') != 'road': continue
    for k, p in enumerate(g['paths']):
        l = LineString([TO_METRIC(*q) for q in p]); near = l.intersection(T.buffer(20))
        if near.length > 30:
            on = [i for i, q in enumerate(l.coords) if T.distance(Point(q)) <= 20]
            print(g['id'], g.get('name'), 'path', k, 'len', round(l.length), 'within 20 m', round(near.length), 'vertices', len(l.coords), 'on', on[:1] + on[-1:],
                  'trace', round(T.project(Point(l.coords[on[0]]))), round(T.project(Point(l.coords[on[-1]]))), 'max off', round(max(T.distance(Point(l.coords[i])) for i in on), 1))
json.dump(dict(note='Old road through Överby, read by hand on the 1929 Eckerö parish map (renders/overby-grid-1929.jpg); pixel waypoints and their EPSG:3874 metres.',
               pixels=PX, trace=[[round(x, 2), round(y, 2)] for x, y in T.coords], profile=prof), open(f'{R}/data/trace-overby-1929.json', 'w'))
