"""The 1929 trace of an old-road object (magenta) and the OpenStreetMap ways next to it (cyan, green, orange, blue in the order given; today's main road red)
over the 1929 parish map, the 1985 base map and a plain OSM 2026 panel, in windows along the trace.
Usage: render.py MOSAIC1929.png OBJECT_SUFFIX OUT.jpg D1,D2,... HALF_M WAY,WAY,... [CATALOGUE_AFTER.json.gz]
With a catalogue after the review, the object's phase lines are drawn instead of the ways: the first phase black,
the second dark green, the surviving part (from 1995) thick yellow; the raw 1929 trace stays magenta.
Positions on the scanned maps are only as good as their registration (1929: 3-30 m; 1985: a few metres)."""
import sys, json, gzip
sys.path.insert(0, 'docs/reviews/lemlandsvagen-main-road-2026-11-17/scripts'); sys.path.insert(0, 'data/map-scan-cache/review/mariehamn-buildings')
from conv import converters
from trace import Mosaic, TO_M, TO_G
from shapely.geometry import LineString
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
png, suffix, out, ds, half, ways = sys.argv[1], sys.argv[2], sys.argv[3], [float(x) for x in sys.argv[4].split(',')], float(sys.argv[5]), sys.argv[6].split(',')
c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); G = {g['id']: g for g in c['geometries']}; O = {o['id']: o for o in c['objects']}
T = LineString([TO_M(*p) for p in G[O['road:lemland:gamla-lemlandsvagen:' + suffix]['geometryPeriods'][0]['geometryId']]['paths'][0]])
mod = {f['id']: f for f in json.loads(gzip.decompress(open('dist/assets/modern.json.gz', 'rb').read()))['features']}
main = [f for f in mod.values() if f.get('name') == 'Lemlandsvägen' and f.get('class') == 'primary']
after = json.loads(gzip.decompress(open(sys.argv[7], 'rb').read())) if len(sys.argv) > 7 else None
phases = []
if after:
    AG = {g['id']: g for g in after['geometries']}; AO = {o['id']: o for o in after['objects']}['road:lemland:gamla-lemlandsvagen:' + suffix]
    phases = [[[TO_M(*q) for q in p] for p in AG[gp['geometryId']]['paths']] for gp in AO['geometryPeriods']]
m = Mosaic(png)
_, _, p85, _ = converters(1985)
panels = [('1929', Image.fromarray(m.rgb.astype('uint8')), m.px), ('1985', Image.open('data/map-scan-cache/101208_1985.jpg').convert('RGB'), lambda lo, la: tuple(p85(lo, la))), ('OSM 2026', None, None)]
P = 360; sheet = Image.new('RGB', (P * len(panels), P * len(ds)), 'white')
for i, d_ in enumerate(ds):
    cx, cy = T.interpolate(d_).coords[0]
    for j, (nm, im, px) in enumerate(panels):
        if im is None:
            t = Image.new('RGB', (P, P), (245, 243, 236)); f = lambda E, N: ((E - cx + half) / (2 * half) * P, (cy + half - N) / (2 * half) * P)
        else:
            (a, b), (cc, dd) = px(*TO_G(cx - half, cy + half)), px(*TO_G(cx + half, cy - half))
            t = im.crop((int(a), int(b), int(cc), int(dd))).resize((P, P), Image.LANCZOS)
            f = lambda E, N, a=a, b=b, cc=cc, dd=dd, px=px: ((px(*TO_G(E, N))[0] - int(a)) / (int(cc) - int(a)) * P, (px(*TO_G(E, N))[1] - int(b)) / (int(dd) - int(b)) * P)
        dr = ImageDraw.Draw(t)
        if im is None:
            for g in mod.values():
                if g.get('kind') == 'road':
                    for p in g['paths']: dr.line([f(*TO_M(*q)) for q in p], fill=(170, 170, 170), width=1)
        for g in main:
            for p in g['paths']: dr.line([f(*TO_M(*q)) for q in p], fill=(255, 0, 0), width=1)
        for k, ph in enumerate(phases):
            last = k == len(phases) - 1
            for p in ph: dr.line([f(*q) for q in p], fill=(240, 200, 0) if last else [(0, 0, 0), (0, 110, 40)][k % 2], width=4 if last else 2)
        for k, w in enumerate([] if phases else ways):
            for p in mod[w]['paths']: dr.line([f(*TO_M(*q)) for q in p], fill=[(0, 190, 230), (0, 160, 0), (230, 140, 0), (0, 0, 200)][k % 4], width=2)
        dr.line([f(*p) for p in T.coords], fill=(255, 0, 255), width=1)
        dr.rectangle((0, 0, 150, 12), fill='black'); dr.text((2, 0), f'{suffix[:10]} {int(d_)} m {nm}', fill='yellow'); sheet.paste(t, (j * P, i * P))
sheet.save(out, quality=86); print(out, sheet.size)
