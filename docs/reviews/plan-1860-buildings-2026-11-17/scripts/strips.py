import sys, json
from PIL import Image, ImageDraw
im = Image.open(sys.argv[1]).convert('RGB'); K = 2048/1824; Z = 4
spec = json.loads(sys.argv[3]); tiles = []
for name, vx0, vy0, vx1, vy1 in spec:
    c = im.crop((int(vx0*K), int(vy0*K), int(vx1*K), int(vy1*K))).resize(((vx1-vx0)*Z, (vy1-vy0)*Z), Image.LANCZOS); d = ImageDraw.Draw(c)
    for g in range(vx0 - vx0 % 5, vx1+1, 5):
        X = (g-vx0)*Z; d.line([(X, 0), (X, c.size[1])], fill=(0, 90, 255) if g % 50 == 0 else (150, 190, 255) if g % 10 == 0 else (200, 220, 255), width=1)
        if g % 10 == 0: d.text((X+2, 2), str(g), fill=(0, 0, 180))
    for g in range(vy0 - vy0 % 5, vy1+1, 5):
        Y = (g-vy0)*Z; d.line([(0, Y), (c.size[0], Y)], fill=(0, 90, 255) if g % 50 == 0 else (150, 190, 255) if g % 10 == 0 else (200, 220, 255), width=1)
        if g % 10 == 0: d.text((2, Y+2), str(g), fill=(0, 0, 180))
    d.text((c.size[0]-60, c.size[1]-14), name, fill=(200, 0, 0)); tiles.append(c)
W = max(t.size[0] for t in tiles); out = Image.new('RGB', (W, sum(t.size[1]+6 for t in tiles)), 'white'); y = 0
for t in tiles: out.paste(t, (0, y)); y += t.size[1]+6
out.save(sys.argv[2]); print(out.size)
