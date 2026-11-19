import gzip, json, sys
sys.path.insert(0, 'scripts')
from plan_1860_buildings import apply_plan_1860_buildings
from PIL import Image, ImageDraw
from pyproj import Transformer
TO_M = Transformer.from_crs(4326, 3874, always_xy=True).transform
c = json.loads(gzip.open(sys.argv[1]).read())
read = lambda p: json.loads(gzip.open(p).read() if p.endswith('.gz') else open(p).read())
apply_plan_1860_buildings(read, c)
O = {o['id']: o for o in c['objects']}; G = {g['id']: g for g in c['geometries']}
st = next(s for s in c['cityStages'] if s['id'] == 'city-reconstruction-1860')
def geo(f):
    if f.get('objectId') and f['objectId'] in O:
        o = O[f['objectId']]; p = next((p for p in o['geometryPeriods'] if p['from'] <= 1860 and (p['to'] is None or 1860 < p['to'])), None)
        return G[p['geometryId']]['paths'] if p else []
    return f.get('paths', [])
pts = [TO_M(*q) for f in st['features'] for path in geo(f) for q in path]
x0, x1 = min(p[0] for p in pts) - 80, max(p[0] for p in pts) + 80; y0, y1 = min(p[1] for p in pts) - 80, max(p[1] for p in pts) + 80
k = 1600 / (x1 - x0); W, H = 1600, int((y1 - y0) * k)
P = lambda q: ((TO_M(*q)[0] - x0) * k, (y1 - TO_M(*q)[1]) * k)
im = Image.new('RGB', (W, H), (250, 247, 240)); d = ImageDraw.Draw(im)
for f in st['features']:
    for path in geo(f):
        if f['kind'] in ('block',): d.polygon([P(q) for q in path], fill=(232, 226, 205), outline=(180, 170, 150))
        elif f['kind'] in ('park',): d.polygon([P(q) for q in path], fill=(185, 200, 160))
for f in st['features']:
    if f['kind'] == 'street':
        for path in geo(f): d.line([P(q) for q in path], fill=(255, 255, 255), width=5)
for o in c['objects']:
    if o['id'].startswith('building:plan-1860:'):
        r = G[o['geometryPeriods'][0]['geometryId']]['paths'][0]
        row = o['kind'] == 'buildingGroup'
        d.polygon([P(q) for q in r], fill=(225, 170, 160) if row else (175, 125, 100), outline=(150, 70, 60))
        if not row: d.text(P(r[0]), o['id'].split(':')[-1], fill=(120, 0, 0))
im.save(sys.argv[2]); print(im.size)
