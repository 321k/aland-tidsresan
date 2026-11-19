import sys, json
from PIL import Image, ImageDraw
im = Image.open(sys.argv[1]).convert('RGB'); K = 2048/1824
rows = json.load(open('rows_px.json')); d = ImageDraw.Draw(im)
for k, p in rows.items():
    d.polygon([(x*K, y*K) for x, y in p], outline=(255, 0, 0), width=2)
    d.text((p[0][0]*K+2, p[0][1]*K+1), k, fill=(200, 0, 120))
for name, box in [('ovl-w', (180, 330, 760, 800)), ('ovl-e', (740, 330, 1420, 890))]:
    x0, y0, x1, y1 = [int(v*K) for v in box]; c = im.crop((x0, y0, x1, y1)); c = c.resize((int(c.width*1.5), int(c.height*1.5))); c.save(f'crops/{name}.png')
