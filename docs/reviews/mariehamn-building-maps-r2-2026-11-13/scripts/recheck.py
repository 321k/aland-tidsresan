"""Close-ups for rechecking deferred buildings (read-only on sources).
Usage: recheck.py KIND -> recheck-KIND-NN.jpg and recheck-KIND.json, KIND = earlier-unclear or inconsistent.
Every building of b1–b10 with that verdict that still exists and has no curated review is shown in 1968 | 1985 | 1995
(25 m around it, its latest outline shifted by the local registration of each edition, blue). Detected symbols are
not marked; the drawing is judged by eye. 18 cells per sheet, 3 per row."""
import sys, json, gzip, importlib.util
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer
P = Path('data/map-scan-cache/review/mariehamn-buildings'); kind = sys.argv[1]
spec = importlib.util.spec_from_file_location('conv', P / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
cat = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
toM = Transformer.from_crs(4326, 3874, always_xy=True).transform; back = Transformer.from_crs(3874, 4326, always_xy=True).transform
scans = {y: Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB') for y in (1968, 1985, 1995)}; cv = {y: conv.converters(y)[2] for y in scans}
CUR = ['historicalReview', 'museumReview', 'printedMapSymbol', 'neighborhoodReviews']
items = []
for k in ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'b10']:
    v = json.load(open(P / f'{k}-verdict.json')); m = json.load(open(P / f'{k}-match.json'))
    for bid, x in sorted(v.items()):
        o = O.get(bid)
        if x != kind or o is None or o.get('externalModern') or any(o.get(t) for t in CUR) or not o.get('reconstruction'):
            continue
        items.append(dict(batch=k, objectId=bid, matched=sorted(y for y in m['buildings'][bid]['editions'] if y != '1978'),
                          shifts=m['buildings'][bid].get('shifts', {}), start=o['states'][0]['from']))
HALF, S = 25, 4; cells = []
for n, it in enumerate(items):
    o = O[it['objectId']]; ring = [toM(*p) for p in G[o['geometryPeriods'][-1]['geometryId']]['paths'][0]]
    cx = sum(p[0] for p in ring) / len(ring); cy = sum(p[1] for p in ring) / len(ring); panels = []
    for y in (1968, 1985, 1995):
        sh = it['shifts'].get(str(y), [0, 0]); to = cv[y]; ctr = to(*back(cx + sh[0], cy + sh[1])); r = HALF / 1.68
        x0, y0, x1, y1 = int(ctr[0] - r), int(ctr[1] - r), int(ctr[0] + r), int(ctr[1] + r)
        im = scans[y].crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS); dr = ImageDraw.Draw(im)
        xy = [tuple((np.array(to(*back(px + sh[0], py + sh[1]))) - [x0, y0]) * S) for px, py in ring]; dr.line(xy + [xy[0]], fill=(0, 150, 255), width=2)
        tag = '*' if str(y) in it['matched'] else ''
        dr.rectangle([0, 0, 64, 13], fill='black'); dr.text((2, 1), f'{n} {y}{tag}', fill='yellow'); panels.append(im)
    w = sum(p.width + 3 for p in panels); cell = Image.new('RGB', (w, panels[0].height), 'white'); x = 0
    for p in panels: cell.paste(p, (x, 0)); x += p.width + 3
    cells.append(cell)
COLS, PER = 3, 18
for s in range(0, len(cells), PER):
    chunk = cells[s:s + PER]; cw, ch = chunk[0].width + 10, chunk[0].height + 8
    sheet = Image.new('RGB', (cw * COLS, ch * ((len(chunk) + COLS - 1) // COLS)), 'white')
    for i, c in enumerate(chunk): sheet.paste(c, ((i % COLS) * cw, (i // COLS) * ch))
    sheet.save(P / f'recheck-{kind}-{s // PER:02d}.jpg', quality=85)
json.dump(items, open(P / f'recheck-{kind}.json', 'w'), indent=0)
print(kind, len(items), 'buildings,', (len(items) + PER - 1) // PER, 'sheets')
