"""Check render: a saved trace (magenta) and today's road (red) over a mosaic, in windows along the trace.
Usage: check_render.py MOSAIC.png TRACE.json OUT.jpg STEP_M HALF_M [OBJECT_ID]"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from trace import Mosaic, TO_M, TO_G
from shapely.geometry import LineString
from PIL import Image, ImageDraw
png, tj, out, step, half = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
oid = sys.argv[6] if len(sys.argv) > 6 else 'road:qgis:mariehamn:lemlandsvagen-1-100km3'
m = Mosaic(png); img = Image.fromarray(m.rgb.astype('uint8')); T = LineString(json.load(open(tj))['trace'])
c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); G = {g['id']: g for g in c['geometries']}; O = {o['id']: o for o in c['objects']}
L = [TO_M(*p) for p in G[O[oid]['geometryPeriods'][-1]['geometryId']]['paths'][0]]
P = 420; tiles = []
d_ = step / 2
while d_ < T.length:
    cx, cy = T.interpolate(d_).coords[0]
    (a, b), (cc, dd) = m.px(*TO_G(cx - half, cy + half)), m.px(*TO_G(cx + half, cy - half))
    im = img.crop((int(a), int(b), int(cc), int(dd))).resize((P, P), Image.LANCZOS); dr = ImageDraw.Draw(im)
    f = lambda E, N: ((m.px(*TO_G(E, N))[0] - int(a)) / (int(cc) - int(a)) * P, (m.px(*TO_G(E, N))[1] - int(b)) / (int(dd) - int(b)) * P)
    dr.line([f(*p) for p in L], fill=(255, 0, 0), width=1); dr.line([f(*p) for p in T.coords], fill=(255, 0, 255), width=1)
    dr.rectangle((0, 0, 90, 12), fill='black'); dr.text((2, 0), f'{int(d_)} m', fill='yellow'); tiles.append(im); d_ += step
cols = 3; rows = (len(tiles) + cols - 1) // cols; sheet = Image.new('RGB', (P * cols, P * rows), 'white')
for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * P, (i // cols) * P))
sheet.save(out, quality=86); print(sheet.size)
