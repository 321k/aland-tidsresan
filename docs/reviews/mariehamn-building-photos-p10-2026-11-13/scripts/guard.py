"""Map ink guard for photo dating: a building first seen on the 1991 photo is checked on the 1985 map, and one first
seen on 1999 on the 1995 map. The dark share inside its outline (shifted by the local registration of the building-map
matching) is measured; above 0.3 the map may already draw the house, so the photo date could be too late and the
building is deferred. Usage: guard.py KEY -> KEY-guard.json"""
import sys, json, gzip, importlib.util
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Polygon
P = Path('data/map-scan-cache/review/photo-dating'); B = Path('data/map-scan-cache/review/mariehamn-buildings'); key = sys.argv[1]
spec = importlib.util.spec_from_file_location('conv', B / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
cat = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
T = Transformer.from_crs(4326, 3874, always_xy=True).transform; Bk = Transformer.from_crs(3874, 4326, always_xy=True).transform
items = json.load(open(P / f'{key}.json')); dec = json.load(open(P / f'{key}-decisions.json'))
dark = {}
def darkmap(y):
    if y not in dark:
        a = np.asarray(Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB'), dtype=float)
        dark[y] = (a.mean(axis=2) < 140) & ((a.max(axis=2) - a.min(axis=2)) < 80)
    return dark[y]
out = {}
for n, it in enumerate(items):
    code = dec[str(n)]
    if code not in ('Y1991', 'Y1999'):
        continue
    y = 1985 if code == 'Y1991' else 1995
    m = json.load(open(B / f"{it['batch']}-match.json"))['buildings'][it['objectId']]; sh = m.get('shifts', {}).get(str(y), [0, 0])
    poly = Polygon([T(*q) for q in G[O[it['objectId']]['geometryPeriods'][-1]['geometryId']]['paths'][0]])
    to = conv.converters(y)[2]; pts = [to(*Bk(x + sh[0], yy + sh[1])) for x, yy in poly.exterior.coords]
    x0, y0 = np.floor(np.min(pts, axis=0)).astype(int) - 1; x1, y1 = np.ceil(np.max(pts, axis=0)).astype(int) + 2
    mk = Image.new('L', (x1 - x0, y1 - y0), 0); ImageDraw.Draw(mk).polygon([(px - x0, py - y0) for px, py in pts], fill=1)
    mk = np.asarray(mk, dtype=bool); share = float(darkmap(y)[y0:y1, x0:x1][mk].mean()) if mk.sum() else 0.0
    out[str(n)] = dict(objectId=it['objectId'], code=code, mapYear=y, darkShare=round(share, 3), deferred=share > 0.3)
json.dump(out, open(P / f'{key}-guard.json', 'w'), indent=0)
print(sum(v['deferred'] for v in out.values()), 'of', len(out), 'deferred by the map ink guard')
