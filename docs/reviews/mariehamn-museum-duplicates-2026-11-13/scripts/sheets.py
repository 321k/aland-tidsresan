"""Review sheets for museum-map houses (building:museum:*) that overlap a later house (read-only on sources).
Usage: sheets.py PAIRS.json  -> museum-NN.jpg (6 pairs per sheet). Per pair: 1942 orthophoto plain | 1942 with outlines |
1968 sheet 101208 with outlines. Blue: the museum house (1920 museum map). Magenta: the overlapping later house.
Thin white: every other building outline nearby (its latest geometry)."""
import json, gzip, sys, importlib.util
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Polygon, box
P = Path('data/map-scan-cache/review/museum-duplicates'); TILES = Path('data/map-scan-cache/review/trace-1942/tiles')
spec = importlib.util.spec_from_file_location('conv', 'data/map-scan-cache/review/mariehamn-buildings/conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); O = {o['id']: o for o in c['objects']}; G = {g['id']: g for g in c['geometries']}
T = Transformer.from_crs(4326, 3874, always_xy=True).transform; B = Transformer.from_crs(3874, 4326, always_xy=True).transform
ring = lambda o: [T(*q) for q in G[o['geometryPeriods'][-1]['geometryId']]['paths'][0]]
others = [(o['id'], ring(o)) for o in c['objects'] if o.get('kind') == 'building' and o['geometryPeriods'] and G.get(o['geometryPeriods'][-1]['geometryId'])
          and len(G[o['geometryPeriods'][-1]['geometryId']]['paths'][0]) >= 4]
to68 = conv.converters(1968)[2]; scan = Image.open('data/map-scan-cache/101208_1968.jpg').convert('RGB')
rows = json.load(open(sys.argv[1])); span, res, S, H = 512, 2.0, 5, 40; cells = []
for n, r in enumerate(rows):
    ra, rb = ring(O[r['museum']]), ring(O[r['later']])
    cx = sum(q[0] for q in ra + rb) / len(ra + rb); cy = sum(q[1] for q in ra + rb) / len(ra + rb); e0, e1, n0, n1 = cx - H, cx + H, cy - H, cy + H
    area = box(e0, n0, e1, n1); near = [rr for i, rr in others if i not in (r['museum'], r['later']) and Polygon(rr).intersects(area)]
    xa, xb, ya, yb = int(e0 // span), int(e1 // span), int(n0 // span), int(n1 // span)
    im = Image.new('RGB', ((xb - xa + 1) * 256, (yb - ya + 1) * 256))
    for x in range(xa, xb + 1):
        for y in range(ya, yb + 1):
            im.paste(Image.open(TILES / f'aerial-1942-16-{x}-{y}.png').convert('RGB'), ((x - xa) * 256, (yb - y) * 256))
    px = lambda e, nn: ((e - xa * span) / res, ((yb + 1) * span - nn) / res)
    im = im.crop(tuple(int(v) for v in (*px(e0, n1), *px(e1, n0)))); im = im.resize((im.width * S, im.height * S), Image.LANCZOS)
    plain = im.copy(); dr = ImageDraw.Draw(im); m = lambda e, nn: ((e - e0) / res * S, (n1 - nn) / res * S)
    for rr in near: dr.line([m(*q) for q in rr] + [m(*rr[0])], fill=(255, 255, 255), width=1)
    for rr, col in ((ra, (0, 160, 255)), (rb, (255, 0, 200))): dr.line([m(*q) for q in rr] + [m(*rr[0])], fill=col, width=3)
    q = [to68(*B(x, y)) for x in (e0, e1) for y in (n0, n1)]; x0, y0 = np.min(q, axis=0).astype(int); x1, y1 = np.max(q, axis=0).astype(int); K = im.height / (y1 - y0)
    mp = scan.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * K), im.height), Image.LANCZOS); d2 = ImageDraw.Draw(mp)
    mm = lambda e, nn: tuple((np.array(to68(*B(e, nn))) - [x0, y0]) * K)
    for rr in near: d2.line([mm(*p) for p in rr] + [mm(*rr[0])], fill=(120, 120, 120), width=1)
    for rr, col in ((ra, (0, 160, 255)), (rb, (255, 0, 200))): d2.line([mm(*p) for p in rr] + [mm(*rr[0])], fill=col, width=3)
    for p_, lab in ((plain, '1942'), (im, '1942'), (mp, '1968')):
        ImageDraw.Draw(p_).rectangle([0, 0, 58, 15], fill='black'); ImageDraw.Draw(p_).text((3, 2), f'{n} {lab}', fill='yellow')
    w = plain.width + im.width + mp.width + 8; cell = Image.new('RGB', (w, im.height), 'white'); x = 0
    for p_ in (plain, im, mp): cell.paste(p_, (x, 0)); x += p_.width + 4
    cells.append(cell)
PER = 6
for s in range(0, len(cells), PER):
    chunk = cells[s:s + PER]; sheet = Image.new('RGB', (max(c.width for c in chunk), sum(c.height + 8 for c in chunk)), 'white'); y = 0
    for c_ in chunk: sheet.paste(c_, (0, y)); y += c_.height + 8
    sheet.thumbnail((1500, 2400)); sheet.save(P / f'museum-{s // PER:02d}.jpg', quality=86)
print(len(cells), 'pairs,', (len(cells) + PER - 1) // PER, 'sheets')
