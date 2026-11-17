"""Grid render of a map mosaic for hand-picking road waypoints: 3x enlarged crop with a 50 m EPSG:3874 grid.
Grid labels are metres east/north of (E0, N0). Today's road objects are drawn thin red, modern OSM roads thin green.
Usage: grid_render.py MOSAIC.png E0 N0 W H OUT.jpg [OBJECT_ID ...]"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from trace import Mosaic, TO_M, TO_G
from PIL import Image, ImageDraw
png, E0, N0, W, H, out = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6]
m = Mosaic(png); K = 3
(xa, ya), (xb, yb) = m.px(*TO_G(E0, N0 + H)), m.px(*TO_G(E0 + W, N0))
im = Image.fromarray(m.rgb.astype('uint8')).crop((int(xa), int(ya), int(xb) + 1, int(yb) + 1))
im = im.resize((im.width * K, im.height * K), Image.LANCZOS); d = ImageDraw.Draw(im)
f = lambda E, N: ((m.px(*TO_G(E, N))[0] - int(xa)) * K, (m.px(*TO_G(E, N))[1] - int(ya)) * K)
mod = json.loads(gzip.decompress(open('dist/assets/modern.json.gz', 'rb').read()))['features']
for ft in mod:
    if ft['kind'] == 'road' and ft.get('class') not in ('footway', 'path', 'cycleway', 'steps', 'corridor'):
        for p in ft['paths']:
            q = [TO_M(*c) for c in p]
            if any(E0 - 50 < x < E0 + W + 50 and N0 - 50 < y < N0 + H + 50 for x, y in q):
                d.line([f(*c) for c in q], fill=(0, 170, 0), width=1)
if len(sys.argv) > 7:
    c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read()))
    G = {g['id']: g for g in c['geometries']}; O = {o['id']: o for o in c['objects']}
    for oid in sys.argv[7:]:
        for p in G[O[oid]['geometryPeriods'][-1]['geometryId']]['paths']:
            d.line([f(*TO_M(*c_)) for c_ in p], fill=(255, 0, 0), width=1)
for e in range(0, int(W) + 1, 50):
    d.line([f(E0 + e, N0), f(E0 + e, N0 + H)], fill=(0, 0, 255) if e % 250 else (0, 0, 160), width=1)
    for n in range(0, int(H) + 1, 250): d.text((f(E0 + e, N0 + n)[0] + 2, f(E0 + e, N0 + n)[1] - 12), str(e), fill=(0, 0, 200))
for n in range(0, int(H) + 1, 50):
    d.line([f(E0, N0 + n), f(E0 + W, N0 + n)], fill=(0, 0, 255) if n % 250 else (0, 0, 160), width=1)
    for e in range(0, int(W) + 1, 250): d.text((f(E0 + e, N0 + n)[0] + 2, f(E0 + e, N0 + n)[1] + 1), str(n), fill=(200, 0, 0))
im.save(out, quality=88); print(im.size)
