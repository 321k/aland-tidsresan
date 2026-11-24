"""Contact sheet: Vägen mot Svibyvägen and the north piece of Norra Möckelövägen on Mariehamn's aerial photos (1 m/px
tiles from fetch.py in docs/reviews/mariehamn-building-photos-p2-2026-11-17), one tile per year, with the OSM 2026 ways
drawn thin: cycleway/footway magenta, residential green. Usage: render.py OUT.jpg [E0 N0 E1 N1] [YEARS...]"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from pathlib import Path
from PIL import Image, ImageDraw
from hammarlandsvagen_main_road import metric
T = Path('data/map-scan-cache/review/photo-dating/tiles')
out = sys.argv[1]
E0, N0, E1, N1 = map(float, sys.argv[2:6]) if len(sys.argv) > 5 else (20495380, 6667560, 20495900, 6667820)
years = [int(y) for y in sys.argv[6:]] or [1942, 1952, 1962, 1975, 1982, 1991, 1999, 2007, 2015, 2021]
M = {f['id']: f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']}
ways = {'way/1193557303': 'c', 'way/1108057940': 'c', 'way/1108057939': 'c', 'way/1180462200': 'c', 'way/35304978': 'r', 'way/35072855': 'c', 'way/35072925': 'r'}
W, H = int(E1 - E0), int(N1 - N0)
tiles = []
for y in years:
    im = Image.new('RGB', (W, H), 'white')
    for tx in range(int(E0 // 256), int(E1 // 256) + 1):
        for ty in range(int(N0 // 256), int(N1 // 256) + 1):
            f = T / f'ortho-{y}-17-{tx}-{ty}.png'
            if f.exists(): im.paste(Image.open(f).convert('RGB'), (int(tx * 256 - E0), int(N1 - (ty + 1) * 256)))
    d = ImageDraw.Draw(im)
    for w, k in ways.items():
        for p in M[w]['paths']:
            d.line([(x - E0, N1 - yy) for x, yy in metric(p).coords], fill=(230, 0, 230) if k == 'c' else (0, 190, 0), width=1)
    for e in range(int(E0) // 100 * 100 + 100, int(E1), 100): d.text((e - E0 + 2, 2), str(e)[-4:], fill=(255, 255, 0))
    d.rectangle([0, H - 16, 60, H], fill='black'); d.text((4, H - 14), str(y), fill='white')
    tiles.append(im)
cols = 2; rows = (len(tiles) + 1) // 2
sheet = Image.new('RGB', (cols * W, rows * H), 'white')
for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * W, (i // cols) * H))
sheet.save(out, quality=88); print(out, sheet.size)
