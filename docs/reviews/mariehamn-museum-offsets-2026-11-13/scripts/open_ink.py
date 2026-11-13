"""Dark share inside each open museum house's own footprint on the 1968, 1985 and 1995 editions of sheet 101208, and the
hatching stripe density around it on 1968 (read-only). Writes open-ink.json. A base map draws every house, so a footprint
that is empty on 1985 and 1995 has no house drawn at that spot; on 1968 hatched blocks hide single houses."""
import json, gzip, importlib.util
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Polygon
P = Path('data/map-scan-cache/review/museum-duplicates')
spec = importlib.util.spec_from_file_location('conv', 'data/map-scan-cache/review/mariehamn-buildings/conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); O = {o['id']: o for o in c['objects']}; G = {g['id']: g for g in c['geometries']}
T = Transformer.from_crs(4326, 3874, always_xy=True).transform; B = Transformer.from_crs(3874, 4326, always_xy=True).transform
ix = json.load(open(P / 'open-index.json')); out = {}
arr = {y: np.asarray(Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB'), dtype=float) for y in (1968, 1985, 1995)}
dark = {y: (a.mean(axis=2) < 140) & ((a.max(axis=2) - a.min(axis=2)) < 80) for y, a in arr.items()}
def share(y, poly):
    to = conv.converters(y)[2]; pts = [to(*B(x, yy)) for x, yy in poly.exterior.coords]
    x0, y0 = np.floor(np.min(pts, axis=0)).astype(int) - 1; x1, y1 = np.ceil(np.max(pts, axis=0)).astype(int) + 2
    mk = Image.new('L', (x1 - x0, y1 - y0), 0); ImageDraw.Draw(mk).polygon([(px - x0, py - y0) for px, py in pts], fill=1)
    mk = np.asarray(mk, dtype=bool); sub = dark[y][y0:y1, x0:x1]
    return round(float(sub[mk].mean()), 2), round(float(np.abs(np.diff((sub & mk).astype(int), axis=1)).sum() / max(mk.sum(), 1)), 2)
for n, r in ix.items():
    m = O[r['museum']]; poly = Polygon([T(*q) for q in G[m['geometryPeriods'][-1]['geometryId']]['paths'][0]]).buffer(0)
    ring = poly.buffer(14).difference(poly.buffer(5))
    try:
        out[n] = dict(museum=r['museum'], d1968=share(1968, poly)[0], hatch1968=share(1968, ring)[1], d1985=share(1985, poly)[0], d1995=share(1995, poly)[0])
    except Exception as e:
        out[n] = dict(museum=r['museum'], error=str(e))
json.dump(out, open(P / 'open-ink.json', 'w'), indent=1)
for n, v in out.items(): print(n, v['museum'].split(':')[-1], {k: v[k] for k in v if k != 'museum'})
