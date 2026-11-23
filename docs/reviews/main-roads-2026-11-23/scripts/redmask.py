"""The base map's red main-road symbol as a mask on a registered scan: strong red pixels (R > 160, G < 130, B < 130),
opened with a disc (radius OPEN px) so that thin red lines (property boundaries) and small red text drop out and the
filled road band remains. load(sheet_id) returns (mask, px, xy): px(E, N) → pixel, xy(col, row) → (E, N)."""
import sys, numpy as np
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from rural_registration import registration_pair
from pyproj import Transformer
from scipy import ndimage
OPEN = 2
_cache = {}
def load(sid):
    if sid in _cache: return _cache[sid]
    s = maps.SHEETS[sid]
    maps.scan_window(sid, *centre(s), 50, 10)
    img, px = maps._scans[sid]; a = np.asarray(img)
    r, g, b = (a[..., i].astype(np.int16) for i in range(3))
    red = (r > 160) & (g < 130) & (b < 130)
    y, x = np.ogrid[-OPEN:OPEN + 1, -OPEN:OPEN + 1]; disc = x * x + y * y <= OPEN * OPEN
    mask = ndimage.binary_opening(red, structure=disc)
    fwd, inv = registration_pair(s); back = Transformer.from_crs(s['registration']['crs'], 3874, always_xy=True).transform
    k = img.size[0] / s['imageSize'][0]
    xy = lambda c, r_: back(*fwd((c / k, r_ / k)))
    _cache[sid] = (mask, px, xy); return _cache[sid]
def centre(s):
    t = Transformer.from_crs(s['registration']['crs'], 3874, always_xy=True).transform
    fr = s['registration'].get('metricFrame')
    xs = [t(*p) for p in fr]; return sum(p[0] for p in xs) / 4, sum(p[1] for p in xs) / 4
