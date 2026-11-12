"""Contact sheets for later starts: each building proposed from 1985 (or 1995) is shown in the previous edition and in
its first edition, at high zoom with the shifted outline, so hollow or hatched drawings that the ink guard cannot see
are caught visually. Usage: contact.py KEY [VERDICT ...]  (default 1985 1995). Writes KEY-contact-N.jpg and
KEY-contact.json (cell number -> building id). Read-only on sources."""
import sys, json, importlib.util
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
P = Path('data/map-scan-cache/review/mariehamn-buildings'); key = sys.argv[1]; wanted = sys.argv[2:] or ['1985', '1995']
spec = importlib.util.spec_from_file_location('conv', P / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
m = json.load(open(P / f'{key}-match.json')); verdict = json.load(open(P / f'{key}-verdict.json'))
cat = conv.read(str(P / 'before.json.gz')); G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
toM = Transformer.from_crs(4326, 3874, always_xy=True).transform; back = Transformer.from_crs(3874, 4326, always_xy=True).transform
scans = {y: Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB') for y in (1968, 1985, 1995)}
cv = {y: conv.converters(y)[2] for y in (1968, 1985, 1995)}
HALF, S = 30, 5   # metres around the centroid; upscale factor
ids = sorted(b for b, v in verdict.items() if v in wanted)
cells, index = [], {}
for n, bid in enumerate(ids):
    first = int(verdict[bid]); prev = 1968 if first == 1985 else 1985
    ring = [toM(*p) for p in G[O[bid]['geometryPeriods'][-1]['geometryId']]['paths'][0]]
    cx = sum(p[0] for p in ring) / len(ring); cy = sum(p[1] for p in ring) / len(ring)
    panels = []
    for y in (prev, first):
        sh = m['buildings'][bid].get('shifts', {}).get(str(y), [0, 0]); to_px = cv[y]
        c = to_px(*back(cx + sh[0], cy + sh[1])); r = HALF / 1.68
        x0, y0, x1, y1 = int(c[0] - r), int(c[1] - r), int(c[0] + r), int(c[1] + r)
        im = scans[y].crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS); dr = ImageDraw.Draw(im)
        xy = [tuple((np.array(to_px(*back(px + sh[0], py + sh[1]))) - [x0, y0]) * S) for px, py in ring]
        dr.line(xy + [xy[0]], fill=(0, 160, 255), width=2); dr.rectangle([0, 0, 70, 14], fill='black'); dr.text((3, 2), f'{n} {y}', fill='yellow')
        panels.append(im)
    w = sum(p.width for p in panels) + 4; cell = Image.new('RGB', (w, panels[0].height), 'white'); cell.paste(panels[0], (0, 0)); cell.paste(panels[1], (panels[0].width + 4, 0))
    cells.append(cell); index[n] = bid
COLS, ROWS = 4, 5
for s in range(0, len(cells), COLS * ROWS):
    chunk = cells[s:s + COLS * ROWS]; cw, ch = chunk[0].width + 10, chunk[0].height + 10
    sheet = Image.new('RGB', (cw * COLS, ch * ((len(chunk) + COLS - 1) // COLS)), 'white')
    for i, c in enumerate(chunk): sheet.paste(c, ((i % COLS) * cw, (i // COLS) * ch))
    sheet.save(P / f'{key}-contact-{s // (COLS * ROWS)}.jpg', quality=85)
json.dump(index, open(P / f'{key}-contact.json', 'w'), indent=0)
print(key, len(cells), 'cells,', (len(cells) + COLS * ROWS - 1) // (COLS * ROWS), 'sheets')
