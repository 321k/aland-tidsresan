"""Render map streets over dated orthophotos. Usage: streetview.py OUT lon0 lat0 lon1 lat1 HILITE_REGEX YEAR...
Yellow: catalogue road segments open/planned that year. Red dashed: city-stage street features of that year.
Cyan: objects/features whose id or name matches HILITE_REGEX. Blocks drawn thin white."""
import sys, json, gzip, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pyproj import Transformer
P = Path('data/map-scan-cache/review/photo-dating')
out, lon0, lat0, lon1, lat1, hil = sys.argv[1], *map(float, sys.argv[2:6]), re.compile(sys.argv[6])
years = [tuple(map(int, (a+':'+a).split(':')[:2])) for a in sys.argv[7:]]  # PHOTO[:MAPYEAR]
cat = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read()))
G = {g['id']: g for g in cat['geometries']}
T = Transformer.from_crs(4326, 3874, always_xy=True).transform
(e0, n0), (e1, n1) = T(lon0, lat0), T(lon1, lat1)
idx = json.load(open(P / 'tiles.json'))
import os; SCALE = float(os.environ.get("SCALE", 2))
def photo(year):
    xa, xb, ya, yb = int(e0 // 256), int(e1 // 256), int(n0 // 256), int(n1 // 256)
    im = Image.new('RGB', ((xb - xa + 1) * 256, (yb - ya + 1) * 256), (90, 90, 90))
    for x in range(xa, xb + 1):
        for y in range(ya, yb + 1):
            n = f'ortho-{year}-17-{x}-{y}.png'
            if idx.get(n): im.paste(Image.open(P / 'tiles' / n).convert('RGB'), ((x - xa) * 256, (yb - y) * 256))
    left, top = e0 - xa * 256, (yb + 1) * 256 - n1
    im = im.crop((int(left), int(top), int(left + e1 - e0), int(top + n1 - n0)))
    return im.resize((int(im.width * SCALE), int(im.height * SCALE)))
def px(lon, lat):
    e, n = T(lon, lat); return ((e - e0) * SCALE, (n1 - n) * SCALE)
def active(states, y):
    return any(s['state'] in ('open', 'planned') and s['from'] <= y and (s['to'] is None or y < s['to']) for s in states)
def geom_at(o, y):
    for p in o['geometryPeriods']:
        if p['from'] <= y and (p['to'] is None or y < p['to']): return G.get(p['geometryId'])
def stage_for(y):
    best = None
    for s in cat['cityStages']:
        if s['from'] <= y and (best is None or s['from'] >= best['from']): best = s
    return best
tiles = []
for py, y in years:
    im = photo(py); d = ImageDraw.Draw(im)
    st = stage_for(y)
    for f in st['features']:
        for path in f['paths']:
            pts = [px(*q) for q in path]
            if f['kind'] == 'block': d.line(pts, fill=(255, 255, 255), width=1)
            elif f['kind'] == 'street':
                d.line(pts, fill=(0, 230, 255) if hil.search(f['id'] + ' ' + (f.get('name') or '')) else (255, 60, 60), width=3)
    for o in cat['objects']:
        if o.get('kind') != 'roadSegment' or not active(o['states'], y): continue
        g = geom_at(o, y)
        if not g: continue
        h = hil.search(o['id'] + ' ' + (o.get('name') or ''))
        for path in g['paths']:
            d.line([px(*q) for q in path], fill=(0, 230, 255) if h else (255, 220, 0), width=2 if not h else 4)
    d.rectangle((0, 0, 330, 22), fill=(0, 0, 0)); d.text((4, 4), f'photo {py} · map {y} · {st["id"]}', fill=(255, 255, 0))
    tiles.append(im)
W = max(t.width for t in tiles); cols = 2; rows = (len(tiles) + 1) // 2
sheet = Image.new('RGB', (W * cols + 8, (tiles[0].height + 8) * rows), (255, 255, 255))
for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * (W + 8), (i // cols) * (t.height + 8)))
sheet.save(out, quality=88); print(out, sheet.size)
