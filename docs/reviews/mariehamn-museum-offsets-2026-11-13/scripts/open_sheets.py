"""Review sheets for every museum-map house that is still open after the overlap review (read-only on sources).
Usage: open_sheets.py -> open-NN.jpg (5 houses per sheet) and open-index.json.
Per house: 1942 orthophoto | 1968 sheet 101208 | 1985 sheet 101208, 50 m around the museum house. Blue: the museum
house. Magenta, numbered 1..: every other building within 40 m that stands in 2026 or 1985 (latest outline), nearest
first; open-index.json lists the numbers with object ids, starts, areas and distances."""
import json, gzip, importlib.util
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Polygon
P = Path('data/map-scan-cache/review/museum-duplicates'); TILES = Path('data/map-scan-cache/review/trace-1942/tiles')
spec = importlib.util.spec_from_file_location('conv', 'data/map-scan-cache/review/mariehamn-buildings/conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); G = {g['id']: g for g in c['geometries']}
T = Transformer.from_crs(4326, 3874, always_xy=True).transform; B = Transformer.from_crs(3874, 4326, always_xy=True).transform
def ring(o):
    g = G.get(o['geometryPeriods'][-1]['geometryId']) if o['geometryPeriods'] else None
    return [T(*q) for q in g['paths'][0]] if g and len(g['paths'][0]) >= 4 else None
def alive(o, y):
    return any(s['state'] in ('standing', 'occupied', 'construction') and s['from'] <= y and (s.get('to') is None or y < s['to']) for s in o['states'])
museums = sorted([o for o in c['objects'] if o['id'].startswith('building:museum:') and o['states'][-1]['state'] != 'demolished'], key=lambda o: int(o['id'].split(':')[-1]))
others = [(o, ring(o)) for o in c['objects'] if o.get('kind') == 'building' and not o['id'].startswith('building:museum:') and (alive(o, 2026) or alive(o, 1985))]
others = [(o, r) for o, r in others if r]
cv = {y: conv.converters(y)[2] for y in (1968, 1985)}; scans = {y: Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB') for y in cv}
span, res, S, H = 512, 2.0, 4, 50; index, cells = {}, []
for n, m in enumerate(museums):
    rm = ring(m); pm = Polygon(rm); cx, cy = pm.centroid.x, pm.centroid.y
    near = sorted(((pm.distance(Polygon(r)), o, r) for o, r in others if abs(r[0][0] - cx) < 120 and abs(r[0][1] - cy) < 120 and pm.distance(Polygon(r)) <= 40), key=lambda t: t[0])
    index[n] = dict(museum=m['id'], area=round(pm.area), neighbours={i + 1: dict(id=o['id'], start=o['states'][0]['from'], area=round(Polygon(r).area), distance=round(d, 1),
                    tags=[k for k in ('printedMapSymbol', 'symbolMap1968', 'buildingMapReview', 'museumDuplicateReview') if o.get(k)]) for i, (d, o, r) in enumerate(near)})
    e0, e1, n0, n1 = cx - H, cx + H, cy - H, cy + H
    xa, xb, ya, yb = int(e0 // span), int(e1 // span), int(n0 // span), int(n1 // span)
    im = Image.new('RGB', ((xb - xa + 1) * 256, (yb - ya + 1) * 256))
    for x in range(xa, xb + 1):
        for y in range(ya, yb + 1):
            t = TILES / f'aerial-1942-16-{x}-{y}.png'
            if t.exists(): im.paste(Image.open(t).convert('RGB'), ((x - xa) * 256, (yb - y) * 256))
    px = lambda e, nn: ((e - xa * span) / res, ((yb + 1) * span - nn) / res)
    im = im.crop(tuple(int(v) for v in (*px(e0, n1), *px(e1, n0)))).resize((int(2 * H / res * S),) * 2, Image.LANCZOS)
    panels = [im]
    for y in (1968, 1985):
        q = [cv[y](*B(x, yy)) for x in (e0, e1) for yy in (n0, n1)]; x0, y0 = np.min(q, axis=0).astype(int); x1, y1 = np.max(q, axis=0).astype(int)
        panels.append(scans[y].crop((x0, y0, x1, y1)).resize(im.size, Image.LANCZOS))
    for k, p_ in enumerate(panels):
        dr = ImageDraw.Draw(p_)
        if k == 0: f = lambda e, nn: ((e - e0) / res * S, (n1 - nn) / res * S)
        else:
            y = (1968, 1985)[k - 1]; q = [cv[y](*B(x, yy)) for x in (e0, e1) for yy in (n0, n1)]; x0, y0 = np.min(q, axis=0); x1, y1 = np.max(q, axis=0)
            f = lambda e, nn, y=y, x0=x0, y0=y0, x1=x1, y1=y1: tuple((np.array(cv[y](*B(e, nn))) - [x0, y0]) / [x1 - x0, y1 - y0] * im.size[0])
        for i, (d, o, r) in enumerate(near):
            xy = [f(*v) for v in r]; dr.line(xy + [xy[0]], fill=(255, 0, 200), width=2)
            cxy = f(*Polygon(r).centroid.coords[0]); dr.text((cxy[0] - 3, cxy[1] - 5), str(i + 1), fill=(255, 0, 200) if k else (255, 255, 0))
        xy = [f(*v) for v in rm]; dr.line(xy + [xy[0]], fill=(0, 150, 255), width=3)
        dr.rectangle([0, 0, 120, 14], fill='black'); dr.text((3, 1), f"{n} m{m['id'].split(':')[-1]} {('1942', '1968', '1985')[k]}", fill='yellow')
    cell = Image.new('RGB', (im.size[0] * 3 + 8, im.size[1]), 'white')
    for k, p_ in enumerate(panels): cell.paste(p_, (k * (im.size[0] + 4), 0))
    cells.append(cell)
PER = 5
for s in range(0, len(cells), PER):
    chunk = cells[s:s + PER]; sheet = Image.new('RGB', (chunk[0].width, sum(c_.height + 8 for c_ in chunk)), 'white'); y = 0
    for c_ in chunk: sheet.paste(c_, (0, y)); y += c_.height + 8
    sheet.save(P / f'open-{s // PER:02d}.jpg', quality=85)
json.dump(index, open(P / 'open-index.json', 'w'), indent=1)
print(len(cells), 'houses,', (len(cells) + PER - 1) // PER, 'sheets')
