"""Overview: today's sections (coloured by first map year) and the old road (magenta) over the 1929 map.
Usage: overview.py MOSAIC1929.png OUT.jpg"""
import sys, json, gzip, math
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from trace import Mosaic, TO_M, TO_G
from PIL import Image, ImageDraw
m = Mosaic(sys.argv[1]); c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read()))
G = {g['id']: g for g in c['geometries']}; O = {o['id']: o for o in c['objects']}; r = json.load(open('data/lemlandsvagen-main-road.json'))
secs = r['sections'] + [dict(r['remainder'], id=r['target']['objectId'])]
col = {1917: (0, 150, 0), 1968: (0, 90, 255), 1985: (230, 0, 0)}
lines = [(O[s['id']], col[s['firstYear']], f"{s['part']} {s['firstYear']}") for s in secs] + [(O[o['id']], (220, 0, 220), '') for o in r['oldRoad']['objects']]
lines.append((O[r['langskata']['objectId']], (220, 0, 220), ''))
pts = [m.px(*p) for o, _, _ in lines for p in G[o['geometryPeriods'][-1]['geometryId']]['paths'][0]]
x0, y0 = min(p[0] for p in pts) - 80, min(p[1] for p in pts) - 80; x1, y1 = max(p[0] for p in pts) + 80, max(p[1] for p in pts) + 80
im = Image.fromarray(m.rgb.astype('uint8')).crop((int(x0), int(y0), int(x1), int(y1))); d = ImageDraw.Draw(im)
for o, colour, label in lines:
    gp = o['geometryPeriods'][0] if o['id'] == r['langskata']['objectId'] else o['geometryPeriods'][-1]
    path = G[gp['geometryId']]['paths'][0]
    if o['id'] == r['langskata']['objectId']:
        n = max(2, int(len(path) * gp['canonicalRange'][1]) + 1); path = path[:n]
    q = [(m.px(*p)[0] - int(x0), m.px(*p)[1] - int(y0)) for p in path]; d.line(q, fill=colour, width=4)
    if label:
        mid = q[len(q) // 2]; d.rectangle((mid[0] + 8, mid[1] - 8, mid[0] + 8 + 7 * len(label), mid[1] + 6), fill='white'); d.text((mid[0] + 10, mid[1] - 8), label, fill=colour)
d.rectangle((8, 8, 330, 66), fill='white')
for i, (t, cl) in enumerate([('dagens vag, belagd fran 1917', col[1917]), ('dagens vag, ny 1948-1968', col[1968]), ('dagens vag, ny 1978-1985', col[1985]), ('gamla vagen (sparad pa 1929 ars karta)', (220, 0, 220))]):
    d.line((14, 18 + i * 13, 40, 18 + i * 13), fill=cl, width=4); d.text((46, 12 + i * 13), t, fill='black')
im.save(sys.argv[2], quality=86); print(im.size)
