"""Norra kvarterens tvärgata · 1942 on the 1942 orthophoto, with the persistent road objects
nearby (read-only). Writes south-plain.png, south-overlay.png and south-legend.json in this folder.
White: raw 1942 traces. Magenta: the trace pieces still drawn 1968–1985. Green: road objects open in 1942.
Cyan: road objects that open later (number = legend entry)."""
import json, gzip
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import LineString, box
P = Path('data/map-scan-cache/review/trace-1942'); span, res = 512, 2.0
r = lambda p: json.loads(gzip.decompress(open(p, 'rb').read()) if p.endswith('.gz') else open(p, 'rb').read())
toE = Transformer.from_crs(4326, 3874, always_xy=True).transform
c = r('dist/assets/temporal-objects.json.gz'); G = {g['id']: g for g in c['geometries']}
stage = lambda sid: next(s for s in c['cityStages'] if s['id'] == sid)
TRACES = ['city-1942-trace-13']
raw = {f['traceId']: [[toE(*p) for p in path] for path in f['paths']] for f in stage('city-reconstruction-1942')['features'] if f.get('traceId') in TRACES}
# Södra stadsgatan's raw trace is a two-point line; the stage keeps only its ends, so draw the full chord.
pass
late = [[toE(*p) for p in path] for f in stage('city-nls-1968')['features'] if f.get('traceId') in TRACES for path in f['paths']]
e0, n0 = toE(19.922, 60.0960); e1, n1 = toE(19.950, 60.1050); area = box(e0, n0, e1, n1)
a, b, cc, dd = int(e0 // span), int(e1 // span), int(n0 // span), int(n1 // span)
im = Image.new('RGB', ((b - a + 1) * 256, (dd - cc + 1) * 256))
for x in range(a, b + 1):
    for y in range(cc, dd + 1):
        im.paste(Image.open(P / 'tiles' / f'aerial-1942-16-{x}-{y}.png').convert('RGB'), ((x - a) * 256, (dd - y) * 256))
px = lambda e, n: ((e - a * span) / res * 2, ((dd + 1) * span - n) / res * 2)
im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS); im.save(P / 'north-plain.png')
dr = ImageDraw.Draw(im); legend = []
for o in c['objects']:
    if o.get('kind') != 'roadSegment':
        continue
    opens = [st['from'] for st in o['states'] if st['state'] == 'open']
    if not opens:
        continue
    g = G.get(o['geometryPeriods'][-1]['geometryId'])
    if not g:
        continue
    for path in g['paths']:
        L = LineString([toE(*p) for p in path])
        if not L.intersects(area):
            continue
        first = min(opens); col = (0, 220, 0) if first <= 1942 else (0, 200, 255)
        xy = [px(*p) for p in L.coords]; dr.line(xy, fill=col, width=3)
        if first > 1942:
            n = len(legend); mx, my = xy[len(xy) // 2]; dr.text((mx + 4, my), str(n), fill=col, stroke_width=2, stroke_fill='black')
            legend.append(dict(n=n, objectId=o['id'], name=o.get('name'), firstOpen=first))
for tid, paths in raw.items():
    for path in paths:
        dr.line([px(*p) for p in path], fill=(255, 255, 255), width=3)
for path in late:
    dr.line([px(*p) for p in path], fill=(255, 0, 255), width=5)
im.save(P / 'north-overlay.png'); json.dump(legend, open(P / 'north-legend.json', 'w'), ensure_ascii=False, indent=0)
print(im.size, len(legend), 'later objects labelled')
