"""A saved 1929 trace (magenta) and today's road (red) over the 1968, 1978 and 1985 base maps (sheet 101208) and
the 1929 map, in windows along the trace. Positions on the base maps are only as good as their registration here.
Usage: check_base.py MOSAIC1929.png TRACE.json OUT.jpg D1,D2,... HALF_M"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'data/map-scan-cache/review/mariehamn-buildings')
from conv import converters
from trace import Mosaic, TO_M, TO_G
from shapely.geometry import LineString
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
png, tj, out, ds, half = sys.argv[1], sys.argv[2], sys.argv[3], [float(x) for x in sys.argv[4].split(',')], float(sys.argv[5])
T = LineString(json.load(open(tj))['trace']); m = Mosaic(png)
c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); G = {g['id']: g for g in c['geometries']}; O = {o['id']: o for o in c['objects']}
L = [TO_M(*p) for p in G[O['road:qgis:mariehamn:lemlandsvagen-1-100km3']['geometryPeriods'][-1]['geometryId']]['paths'][0]]
panels = [('1929', Image.fromarray(m.rgb.astype('uint8')), m.px)]
for y in (1968, 1978, 1985):
    _, _, to_px, _ = converters(y); panels.append((str(y), Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB'), lambda lo, la, f=to_px: tuple(f(lo, la))))
P = 330; sheet = Image.new('RGB', (P * len(panels), P * len(ds)), 'white')
for i, d_ in enumerate(ds):
    cx, cy = T.interpolate(d_).coords[0]
    for j, (nm, im, px) in enumerate(panels):
        (a, b), (cc, dd) = px(*TO_G(cx - half, cy + half)), px(*TO_G(cx + half, cy - half))
        t = im.crop((int(a), int(b), int(cc), int(dd))).resize((P, P), Image.LANCZOS); dr = ImageDraw.Draw(t)
        f = lambda E, N: ((px(*TO_G(E, N))[0] - int(a)) / (int(cc) - int(a)) * P, (px(*TO_G(E, N))[1] - int(b)) / (int(dd) - int(b)) * P)
        dr.line([f(*p) for p in L], fill=(255, 0, 0), width=1); dr.line([f(*p) for p in T.coords], fill=(255, 0, 255), width=1)
        dr.rectangle((0, 0, 110, 12), fill='black'); dr.text((2, 0), f'{int(d_)} m {nm}', fill='yellow'); sheet.paste(t, (j * P, i * P))
sheet.save(out, quality=86); print(sheet.size)
