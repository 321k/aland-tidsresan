"""The 1968 base map (sheet 101208) with 1942 traces and road objects drawn on it, as a second witness (read-only).
Usage: map1968.py KEY lon0 lat0 lon1 lat1 traceId [traceId ...]   Writes map1968-KEY.jpg (plain | overlay).
White: raw 1942 traces. Magenta: trace pieces drawn 1968–1985. Green/cyan: road objects (open by 1942 / later)."""
import json, gzip, sys, importlib.util
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import LineString, box
sys.path.insert(0, 'scripts')
B = Path('data/map-scan-cache/review/mariehamn-buildings'); P = Path('data/map-scan-cache/review/trace-1942')
spec = importlib.util.spec_from_file_location('conv', B / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
key = sys.argv[1]; lon0, lat0, lon1, lat1 = map(float, sys.argv[2:6]); traces = sys.argv[6:]
r = lambda p: json.loads(gzip.decompress(open(p, 'rb').read()) if p.endswith('.gz') else open(p, 'rb').read())
c = r('dist/assets/temporal-objects.json.gz'); G = {g['id']: g for g in c['geometries']}
city = next(s for s in r('data/mariehamn-city-traces.json')['sets'] if s['id'] == 'city-1942'); ref = city['reference']
back = Transformer.from_crs(3874, 4326, always_xy=True).transform
_, _, to_px, _ = conv.converters(1968); S = 3
q = [to_px(x, y) for x in (lon0, lon1) for y in (lat0, lat1)]
x0, y0 = np.min(q, axis=0).astype(int); x1, y1 = np.max(q, axis=0).astype(int)
scan = Image.open('data/map-scan-cache/101208_1968.jpg').convert('RGB').crop((x0, y0, x1, y1))
scan = scan.resize((scan.width * S, scan.height * S), Image.LANCZOS); ov = scan.copy(); dr = ImageDraw.Draw(ov)
px = lambda lon, lat: tuple((np.array(to_px(lon, lat)) - [x0, y0]) * S)
area = box(lon0, lat0, lon1, lat1)
for o in c['objects']:
    if o.get('kind') != 'roadSegment':
        continue
    opens = [s['from'] for s in o['states'] if s['state'] == 'open']; g = G.get(o['geometryPeriods'][0]['geometryId'])
    if not opens or not g:
        continue
    for path in g['paths']:
        if LineString(path).intersects(area):
            dr.line([px(*p) for p in path], fill=(0, 200, 0) if min(opens) <= 1942 else (0, 170, 255), width=2)
for t in city['roads']:
    if t['traceId'] in traces:
        dr.line([px(*back(ref['west'] + x * 4, ref['north'] - y * 4)) for x, y in t['pixels']], fill=(255, 255, 255), width=3)
late = next(s for s in c['cityStages'] if s['id'] == 'city-nls-1968')
for f in late['features']:
    if f.get('traceId') in traces and not f.get('objectId'):
        for path in f['paths']:
            dr.line([px(*p) for p in path], fill=(255, 0, 255), width=4)
out = Image.new('RGB', (scan.width * 2 + 8, scan.height), 'white'); out.paste(scan, (0, 0)); out.paste(ov, (scan.width + 8, 0))
out.thumbnail((1800, 1400)); out.save(P / f'map1968-{key}.jpg', quality=88); print(key, out.size)
