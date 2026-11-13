"""zoom.py KEY GROUP OUT cell [cell ...]: 1968 | 1985 | 1995 close-ups (HALF 22 m, x9) of contact cells, outline in blue."""
import sys, json, importlib.util
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
P = Path('data/map-scan-cache/review/mariehamn-buildings'); key, group, out = sys.argv[1:4]; cells = sys.argv[4:]
spec = importlib.util.spec_from_file_location('conv', P / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
m = json.load(open(P / f'{key}-match.json')); idx = json.load(open(P / f'{key}-contact-{group}.json'))
cat = conv.read(str(P / 'before.json.gz')); G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
toM = Transformer.from_crs(4326, 3874, always_xy=True).transform; back = Transformer.from_crs(3874, 4326, always_xy=True).transform
scans = {y: Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB') for y in (1968, 1985, 1995)}
cv = {y: conv.converters(y)[2] for y in (1968, 1985, 1995)}
HALF, SC = 22, 9; rows = []
for n in cells:
    bid = idx[n]; ring = [toM(*p) for p in G[O[bid]['geometryPeriods'][-1]['geometryId']]['paths'][0]]
    cx = sum(p[0] for p in ring) / len(ring); cy = sum(p[1] for p in ring) / len(ring); panels = []
    for y in (1968, 1985, 1995):
        sh = m['buildings'][bid].get('shifts', {}).get(str(y), [0, 0]); to_px = cv[y]
        c = to_px(*back(cx + sh[0], cy + sh[1])); r = HALF / 1.68
        x0, y0, x1, y1 = int(c[0] - r), int(c[1] - r), int(c[0] + r), int(c[1] + r)
        im = scans[y].crop((x0, y0, x1, y1)).resize(((x1 - x0) * SC, (y1 - y0) * SC), Image.BICUBIC); dr = ImageDraw.Draw(im)
        xy = [tuple((np.array(to_px(*back(px + sh[0], py + sh[1]))) - [x0, y0]) * SC) for px, py in ring]
        dr.line(xy + [xy[0]], fill=(0, 160, 255), width=2); dr.rectangle([0, 0, 90, 16], fill='black'); dr.text((3, 2), f'{n} {y}', fill='yellow')
        panels.append(im)
    w = sum(p.width + 6 for p in panels); row = Image.new('RGB', (w, panels[0].height), 'white'); x = 0
    for p in panels: row.paste(p, (x, 0)); x += p.width + 6
    rows.append(row)
sheet = Image.new('RGB', (max(r.width for r in rows), sum(r.height + 8 for r in rows)), 'white'); y = 0
for r in rows: sheet.paste(r, (0, y)); y += r.height + 8
sheet.save(out, quality=88); print(sheet.size)
