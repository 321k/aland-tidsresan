"""Tile review sheets: 1968 | 1985 | 1995 crops with today's outlines coloured by the proposed first edition.
Usage: sheets.py KEY NX NY  (uses KEY-match.json and KEY-verdict.json). Read-only on sources."""
import sys, json, gzip, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'scripts'); sys.path.insert(0, str(Path(__file__).parent))
P = Path('data/map-scan-cache/review/mariehamn-buildings')
key, NX, NY = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
import importlib.util
spec = importlib.util.spec_from_file_location('m', P / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
m = json.load(open(P / f'{key}-match.json')); verdict = json.load(open(P / f'{key}-verdict.json'))
cat = conv.read(str(P / 'before.json.gz')); G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
COL = {'1968': (170, 0, 255), '1978?': (255, 140, 0), '1985': (0, 190, 0), '1995': (0, 170, 255), 'inconsistent': (255, 0, 0), 'absent': (130, 130, 130), 'already-dated': (0, 0, 0)}
bb = m['bbox']; scans = {y: Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB') for y in [1968, 1985, 1995]}
cv = {y: conv.converters(y) for y in [1968, 1985, 1995]}
for i in range(NX):
    for j in range(NY):
        t = [bb[0] + (bb[2] - bb[0]) * i / NX, bb[1] + (bb[3] - bb[1]) * j / NY, bb[0] + (bb[2] - bb[0]) * (i + 1) / NX, bb[1] + (bb[3] - bb[1]) * (j + 1) / NY]
        panels = []
        for y in [1968, 1985, 1995]:
            to_px = cv[y][2]; q = [to_px(x, yy) for x in [t[0], t[2]] for yy in [t[1], t[3]]]
            x0, y0 = np.min(q, axis=0).astype(int); x1, y1 = np.max(q, axis=0).astype(int); S = 3
            im = scans[y].crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS); dr = ImageDraw.Draw(im)
            for bid, v in verdict.items():
                ring = G[O[bid]['geometryPeriods'][-1]['geometryId']]['paths'][0]
                cx = sum(p[0] for p in ring) / len(ring); cy = sum(p[1] for p in ring) / len(ring)
                if not (t[0] <= cx < t[2] and t[1] <= cy < t[3]): continue
                xy = [tuple((to_px(*p) - [x0, y0]) * S) for p in ring]; dr.line(xy + [xy[0]], fill=COL.get(v, (0, 0, 0)), width=2)
                e = m['buildings'][bid]['editions'].get(str(y))
                if e:
                    u, w = (e['pixel'][0] - x0) * S, (e['pixel'][1] - y0) * S; dr.ellipse([u - 3, w - 3, u + 3, w + 3], fill=(255, 220, 0))
            dr.rectangle([0, 0, 46, 14], fill='black'); dr.text((3, 2), str(y), fill='yellow'); panels.append(im)
        H = max(p.height for p in panels); o = Image.new('RGB', (sum(p.width + 6 for p in panels), H), 'white'); x = 0
        for p in panels: o.paste(p, (x, 0)); x += p.width + 6
        o.thumbnail((2400, 1400)); o.save(P / f'{key}-sheet-{i}{j}.jpg', quality=86)
print('sheets', NX * NY)
