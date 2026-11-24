"""Map windows for the Hammarlandsvägen review: tile-served historical maps (vanhatkartat XYZ, cached with sha256 in
data/map-scan-cache/review/church-road/tiles.json) and the registered base-map scans (data/rural-map-review.json,
originals in data/map-scan-cache/). Each window is returned with a function from EPSG:3874 metres to window pixels.
Read-only on all sources. Positions on old maps are only as good as their registration."""
import sys, json, math, hashlib, urllib.request
from pathlib import Path
from PIL import Image
import numpy as np
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC, TO_GEO
from rural_registration import registration_pair
from pyproj import Transformer
Image.MAX_IMAGE_PIXELS = None
CACHE = Path('data/map-scan-cache/review/church-road'); TILES = CACHE / 'tiles'
MAPS = {m['id']: m for m in json.load(open('data/historical-map-sources.json'))['maps']}
SHEETS = {s['id']: s for s in json.load(open('data/rural-map-review.json'))['sources']}
_index = None; _scans = {}


def _tile(mid, z, x, y):
    global _index
    if _index is None:
        _index = json.load(open(CACHE / 'tiles.json'))
    name = f'{mid}-{z}-{x}-{y}.png'; f = TILES / name
    if not f.exists():
        if name in _index and _index[name] is None:
            return None
        url = MAPS[mid]['tiles_url'].format(z=z, x=x, y=y)
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'aland-history-map/1.0'}), timeout=30).read()
            f.write_bytes(data); _index[name] = {'url': url, 'sha256': hashlib.sha256(data).hexdigest()}
        except Exception:
            _index[name] = None
        json.dump(_index, open(CACHE / 'tiles.json', 'w'), indent=0)
        if _index[name] is None:
            return None
    t = Image.open(f).convert('RGBA'); bg = Image.new('RGBA', t.size, 'white'); bg.alpha_composite(t)
    return bg.convert('RGB')


def tile_window(mid, z, cx, cy, half, size):
    """Square window of an XYZ map around metric point (cx, cy), half-width in metres, resized to size px."""
    def xy(lon, lat):
        n = 2 ** z; return (lon + 180) / 360 * n * 256, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n * 256
    corners = [xy(*TO_GEO(cx + dx, cy + dy)) for dx in (-half, half) for dy in (-half, half)]
    x0, y0 = min(c[0] for c in corners), min(c[1] for c in corners); x1, y1 = max(c[0] for c in corners), max(c[1] for c in corners)
    X0, Y0, X1, Y1 = int(x0 // 256), int(y0 // 256), int(x1 // 256), int(y1 // 256)
    im = Image.new('RGB', ((X1 - X0 + 1) * 256, (Y1 - Y0 + 1) * 256), 'white')
    for X in range(X0, X1 + 1):
        for Y in range(Y0, Y1 + 1):
            t = _tile(mid, z, X, Y)
            if t: im.paste(t, ((X - X0) * 256, (Y - Y0) * 256))
    crop = im.crop((int(x0 - X0 * 256), int(y0 - Y0 * 256), int(x1 - X0 * 256), int(y1 - Y0 * 256))).resize((size, size), Image.LANCZOS)
    sx, sy = size / (int(x1) - int(x0)), size / (int(y1) - int(y0))
    return crop, (lambda E, N: ((xy(*TO_GEO(E, N))[0] - int(x0)) * sx, (xy(*TO_GEO(E, N))[1] - int(y0)) * sy))


def scan_window(sheet_id, cx, cy, half, size):
    """Square window of a registered base-map scan (original jpg in the scan cache)."""
    s = SHEETS[sheet_id]; sheet, year = s['sheet'], s['year']
    if sheet_id not in _scans:
        fwd, inv = registration_pair(s); crs = s['registration']['crs']
        proj = Transformer.from_crs(3874, crs, always_xy=True).transform
        # the cached original keeps its download name (e.g. 101207_1968_1978.jpg for the 1978 edition)
        name = s.get('originalUrl', '').rsplit('/', 1)[-1] or f'{sheet}_{year}.jpg'
        img = Image.open(f'data/map-scan-cache/{name}' if Path(f'data/map-scan-cache/{name}').exists() else f'data/map-scan-cache/{sheet}_{year}.jpg').convert('RGB')
        k = img.size[0] / s['imageSize'][0]
        _scans[sheet_id] = (img, lambda E, N: tuple(np.array(inv(proj(E, N))) * k))
    img, px = _scans[sheet_id]
    pts = [px(cx + dx, cy + dy) for dx in (-half, half) for dy in (-half, half)]
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts); x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    crop = img.crop((int(x0), int(y0), int(x1), int(y1))).resize((size, size), Image.LANCZOS)
    sx, sy = size / (int(x1) - int(x0)), size / (int(y1) - int(y0))
    return crop, (lambda E, N: ((px(E, N)[0] - int(x0)) * sx, (px(E, N)[1] - int(y0)) * sy))


def inside(mid, E, N):
    from shapely.geometry import shape, Point
    return shape(MAPS[mid]['area']).contains(Point(*TO_GEO(E, N)))
