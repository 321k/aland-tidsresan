"""Photo review sheets for buildings with no symbol on sheet 101208 (read-only on sources).
Usage: sheets.py KEY BATCH [BATCH ...] -> KEY-NN.jpg and KEY.json. Every building of the given building-map batches
whose verdict is 'absent' and that still exists is shown on the 1991, 1999, 2007 and 2015 orthophotos (1 m/px, 22 m
around it, its latest outline in blue, others thin white). A grey panel means the photo does not cover the spot."""
import sys, json, gzip
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Polygon, box
P = Path('data/map-scan-cache/review/photo-dating'); B = Path('data/map-scan-cache/review/mariehamn-buildings')
key, batches = sys.argv[1], sys.argv[2:]; YEARS = [1991, 1999, 2007, 2015]
cat = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
T = Transformer.from_crs(4326, 3874, always_xy=True).transform
idx = json.load(open(P / 'tiles.json'))
ring = lambda o: [T(*q) for q in G[o['geometryPeriods'][-1]['geometryId']]['paths'][0]]
deferred = set(json.load(open('data/mariehamn-building-maps.json'))['deferred'].get('absent', []))
items = []
for k in batches:
    for bid, v in sorted(json.load(open(B / f'{k}-verdict.json')).items()):
        if v == 'absent' and bid in O and bid in deferred:
            o = O[bid]; items.append(dict(batch=k, objectId=bid, start=o['states'][0]['from'], area=round(Polygon(ring(o)).area)))
allr = [(o['id'], ring(o)) for o in cat['objects'] if o.get('kind') == 'building' and o['geometryPeriods'] and G.get(o['geometryPeriods'][-1]['geometryId']) and len(G[o['geometryPeriods'][-1]['geometryId']]['paths'][0]) >= 4]
cache = {}
def tile(year, x, y):
    name = f'ortho-{year}-17-{x}-{y}.png'
    if idx.get(name) is None: return None
    if name not in cache: cache[name] = Image.open(P / 'tiles' / name).convert('RGB')
    return cache[name]
H, S = 22, 4; cells = []
for n, it in enumerate(items):
    r = ring(O[it['objectId']]); cx = sum(p[0] for p in r) / len(r); cy = sum(p[1] for p in r) / len(r)
    e0, e1, n0, n1 = cx - H, cx + H, cy - H, cy + H; area = box(e0, n0, e1, n1)
    near = [rr for i, rr in allr if i != it['objectId'] and abs(rr[0][0] - cx) < 60 and abs(rr[0][1] - cy) < 60 and Polygon(rr).intersects(area)]
    panels = []
    for year in YEARS:
        xa, xb, ya, yb = int(e0 // 256), int(e1 // 256), int(n0 // 256), int(n1 // 256)
        im = Image.new('RGB', ((xb - xa + 1) * 256, (yb - ya + 1) * 256), (128, 128, 128)); covered = True
        for x in range(xa, xb + 1):
            for y in range(ya, yb + 1):
                t = tile(year, x, y)
                if t is None: covered = False
                else: im.paste(t, ((x - xa) * 256, (yb - y) * 256))
        px = lambda e, nn: (e - xa * 256, (yb + 1) * 256 - nn)
        im = im.crop(tuple(int(v) for v in (*px(e0, n1), *px(e1, n0)))).resize((2 * H * S, 2 * H * S), Image.LANCZOS)
        dr = ImageDraw.Draw(im); f = lambda e, nn: ((e - e0) * S, (n1 - nn) * S)
        for rr in near: dr.line([f(*q) for q in rr] + [f(*rr[0])], fill=(255, 255, 255), width=1)
        dr.line([f(*q) for q in r] + [f(*r[0])], fill=(0, 160, 255), width=2)
        dr.rectangle([0, 0, 88, 13], fill='black'); dr.text((2, 1), f'{n} {year}' + ('' if covered else ' (part)'), fill='yellow')
        panels.append(im)
    w = sum(p.width + 3 for p in panels); cell = Image.new('RGB', (w, panels[0].height + 14), 'white'); x = 0
    for p in panels: cell.paste(p, (x, 14)); x += p.width + 3
    ImageDraw.Draw(cell).text((2, 1), f"{n} start {it['start']} · {it['area']} m²", fill='black')
    cells.append(cell)
COLS, PER = 2, 14
for s in range(0, len(cells), PER):
    chunk = cells[s:s + PER]; cw, ch = chunk[0].width + 12, chunk[0].height + 6
    sheet = Image.new('RGB', (cw * COLS, ch * ((len(chunk) + COLS - 1) // COLS)), 'white')
    for i, c in enumerate(chunk): sheet.paste(c, ((i % COLS) * cw, (i // COLS) * ch))
    sheet.save(P / f'{key}-{s // PER:02d}.jpg', quality=85)
json.dump(items, open(P / f'{key}.json', 'w'), indent=0)
print(key, len(items), 'buildings,', (len(items) + PER - 1) // PER, 'sheets')
