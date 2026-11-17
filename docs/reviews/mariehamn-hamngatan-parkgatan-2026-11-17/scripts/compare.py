"""compare.py OUT lon0 lat0 lon1 lat1 RAWFEATURE OBJREGEX YEAR... : photo panels with the raw museum tracing (cyan, thick),
the latest geometry of matching catalogue roads (magenta, always drawn, with its start year), and other roads open that
year (thin yellow)."""
import sys, json, gzip, re, os
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer
P = Path('data/map-scan-cache/review/photo-dating')
out, lon0, lat0, lon1, lat1, fid, rx = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6], re.compile(sys.argv[7])
years = [int(y) for y in sys.argv[8:]]; SCALE = float(os.environ.get('SCALE', 3))
cat = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); G = {g['id']: g for g in cat['geometries']}
raw = next(f for s in json.load(open('dist/assets/mariehamn-city-grid.json'))['sets'] for f in s['features'] if f['id'] == fid)
T = Transformer.from_crs(4326, 3874, always_xy=True).transform
(e0, n0), (e1, n1) = T(lon0, lat0), T(lon1, lat1); idx = json.load(open(P / 'tiles.json'))
def photo(year):
    xa, xb, ya, yb = int(e0 // 256), int(e1 // 256), int(n0 // 256), int(n1 // 256)
    im = Image.new('RGB', ((xb - xa + 1) * 256, (yb - ya + 1) * 256), (90, 90, 90))
    for x in range(xa, xb + 1):
        for y in range(ya, yb + 1):
            n = f'ortho-{year}-17-{x}-{y}.png'
            if idx.get(n): im.paste(Image.open(P / 'tiles' / n).convert('RGB'), ((x - xa) * 256, (yb - y) * 256))
    l, t = e0 - xa * 256, (yb + 1) * 256 - n1
    im = im.crop((int(l), int(t), int(l + e1 - e0), int(t + n1 - n0))); return im.resize((int(im.width * SCALE), int(im.height * SCALE)))
px = lambda lon, lat: ((T(lon, lat)[0] - e0) * SCALE, (n1 - T(lon, lat)[1]) * SCALE)
def open_at(o, y): return any(s['state'] == 'open' and s['from'] <= y and (s['to'] is None or y < s['to']) for s in o['states'])
tiles = []
for y in years:
    im = photo(y); d = ImageDraw.Draw(im)
    for o in cat['objects']:
        if o.get('kind') != 'roadSegment': continue
        if rx.search(o['id']):
            g = G[o['geometryPeriods'][-1]['geometryId']]; col = (255, 0, 200) if not open_at(o, y) else (0, 255, 80)
            for path in g['paths']:
                pts = [px(*q) for q in path]; d.line(pts, fill=col, width=2)
            d.text(pts[len(pts)//2], f"{o['name']} {o['states'][0]['from']}", fill=col)
    for path in raw['paths']: d.line([px(*q) for q in path], fill=(0, 230, 255), width=2)
    d.rectangle((0, 0, 360, 16), fill=(0, 0, 0)); d.text((4, 2), f'photo {y}: cyan museum tracing; green open / magenta not yet open', fill=(255, 255, 0))
    tiles.append(im)
cols = 3; W, H = tiles[0].size; sheet = Image.new('RGB', (W * cols + 6 * cols, (H + 6) * ((len(tiles) + cols - 1) // cols)), 'white')
for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * (W + 6), (i // cols) * (H + 6)))
sheet.save(out, quality=88); print(out, sheet.size)
