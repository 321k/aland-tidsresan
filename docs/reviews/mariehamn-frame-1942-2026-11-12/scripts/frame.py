"""1942 town-frame traces on the 1942 orthophoto with the persistent road objects nearby (read-only).
Usage: frame.py KEY lon0 lat0 lon1 lat1 traceId [traceId ...]
Writes frame-KEY-plain.png, frame-KEY-overlay.png and frame-KEY-legend.json in this folder.
White: the raw 1942 traces (from the original pixels). Yellow: what the 1942 city stage draws now without an object. Magenta: trace pieces still drawn 1968–1985.
Green: road objects open in 1942. Cyan: road objects that open later, numbered (legend: object, name, first year,
distance to the nearest trace)."""
import json, gzip, sys
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import LineString, box
P = Path('data/map-scan-cache/review/trace-1942'); span, res, S = 512, 2.0, 2
key = sys.argv[1]; lon0, lat0, lon1, lat1 = map(float, sys.argv[2:6]); traces = sys.argv[6:]
r = lambda p: json.loads(gzip.decompress(open(p, 'rb').read()) if p.endswith('.gz') else open(p, 'rb').read())
toE = Transformer.from_crs(4326, 3874, always_xy=True).transform
c = r('dist/assets/temporal-objects.json.gz'); G = {g['id']: g for g in c['geometries']}
city = next(s for s in r('data/mariehamn-city-traces.json')['sets'] if s['id'] == 'city-1942'); ref = city['reference']
raw = {t['traceId']: LineString([(ref['west'] + x * ref['metersPerViewPixel'], ref['north'] - y * ref['metersPerViewPixel']) for x, y in t['pixels']])
       for t in city['roads'] if t['traceId'] in traces}
stage = next(s for s in c['cityStages'] if s['id'] == 'city-reconstruction-1942')
e0, n0 = toE(lon0, lat0); e1, n1 = toE(lon1, lat1); area = box(e0, n0, e1, n1)
a, b, cc, dd = int(e0 // span), int(e1 // span), int(n0 // span), int(n1 // span)
im = Image.new('RGB', ((b - a + 1) * 256, (dd - cc + 1) * 256))
for x in range(a, b + 1):
    for y in range(cc, dd + 1):
        im.paste(Image.open(P / 'tiles' / f'aerial-1942-16-{x}-{y}.png').convert('RGB'), ((x - a) * 256, (dd - y) * 256))
px = lambda e, n: ((e - a * span) / res * S, ((dd + 1) * span - n) / res * S)
im = im.resize((im.width * S, im.height * S), Image.LANCZOS)
crop = tuple(int(v) for v in (*px(e0, n1), *px(e1, n0)))
im.crop(crop).save(P / f'frame-{key}-plain.png')
dr = ImageDraw.Draw(im); legend = []
for f in stage['features']:
    if f.get('objectId') or f.get('kind') != 'street':
        continue
    for path in f['paths']:
        dr.line([px(*toE(*p)) for p in path], fill=(255, 220, 0), width=3)
for o in c['objects']:
    if o.get('kind') != 'roadSegment':
        continue
    opens = [s['from'] for s in o['states'] if s['state'] == 'open']
    g = G.get(o['geometryPeriods'][0]['geometryId'])
    if not opens or not g:
        continue
    first = min(opens)
    for path in g['paths']:
        L = LineString([toE(*p) for p in path])
        if not L.intersects(area):
            continue
        col = (0, 220, 0) if first <= 1942 else (0, 200, 255)
        xy = [px(*p) for p in L.coords]; dr.line(xy, fill=col, width=3)
        if first > 1942:
            n = len(legend); mx, my = xy[len(xy) // 2]
            dr.text((mx + 4, my - 6), str(n), fill=col, stroke_width=2, stroke_fill='black')
            legend.append(dict(n=n, objectId=o['id'], name=o.get('name'), firstOpen=first, lengthMeters=round(L.length),
                               traceDistance={t: round(L.hausdorff_distance(T)) if False else round(max(T.distance(type(L.centroid)(p)) for p in L.coords)) for t, T in raw.items()}))
        break
for t, T in raw.items():
    dr.line([px(*p) for p in T.coords], fill=(255, 255, 255), width=2)
late = next(s for s in c['cityStages'] if s['id'] == 'city-nls-1968')
for f in late['features']:
    if f.get('traceId') in traces and not f.get('objectId'):
        for path in f['paths']:
            dr.line([px(*toE(*p)) for p in path], fill=(255, 0, 255), width=4)
im.crop(crop).save(P / f'frame-{key}-overlay.png'); json.dump(legend, open(P / f'frame-{key}-legend.json', 'w'), ensure_ascii=False, indent=0)
print(key, im.crop(crop).size, len(legend), 'later objects')
