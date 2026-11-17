"""Local shift of a base-map edition against the 1985 edition of sheet 101208 along today's Lemlandsvägen.

Both editions are resampled to the same EPSG:3874 grid (2 m/px) with the project's registrations
(mariehamn-buildings/conv.py) and phase-correlated in windows; the result is how far the edition's drawing sits from
the 1985 drawing of the same ground (shores, contours, fields, roads). Usage, from the project root:
    sheet_shift.py OBJECT_ID YEAR [STEP_M] [HALF_M]
"""
import sys, json, gzip
import numpy as np
from PIL import Image
from shapely.geometry import LineString
from pyproj import Transformer
sys.path.insert(0, 'data/map-scan-cache/review/mariehamn-buildings')
from conv import converters
Image.MAX_IMAGE_PIXELS = None
TO_M = Transformer.from_crs(4326, 3874, always_xy=True).transform; TO_G = Transformer.from_crs(3874, 4326, always_xy=True).transform
RES = 2.0


def sheet(year):
    """Water mask of the edition (blue print): shores are the features least likely to have moved."""
    _, _, to_px, _ = converters(year)
    rgb = np.asarray(Image.open(f'data/map-scan-cache/101208_{year}.jpg').convert('RGB')).astype(float)
    return ((rgb[..., 2] - rgb[..., 0] > 60) & (rgb[..., 2] > 150)).astype(float), to_px


def resample(img, to_px, cx, cy, half):
    n = int(2 * half / RES); xs = cx - half + (np.arange(n) + 0.5) * RES; ys = cy + half - (np.arange(n) + 0.5) * RES
    E, N = np.meshgrid(xs, ys); lon, lat = TO_G(E.ravel(), N.ravel())
    px = np.array([to_px(a, b) for a, b in zip(lon, lat)])
    c = np.clip(px[:, 0].round().astype(int), 0, img.shape[1] - 1); r = np.clip(px[:, 1].round().astype(int), 0, img.shape[0] - 1)
    return img[r, c].reshape(n, n)


def shift(a, b):
    """(dx east, dy north) in metres that moves b onto a."""
    a = a - a.mean(); b = b - b.mean(); w = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    F = np.fft.fft2(a * w) * np.conj(np.fft.fft2(b * w)); r = np.fft.ifft2(F / (np.abs(F) + 1e-9)).real
    i, j = np.unravel_index(np.argmax(r), r.shape); n = r.shape[0]
    i = i - n if i > n // 2 else i; j = j - n if j > n // 2 else j
    peak = r.max() / r.std()
    return j * RES, -i * RES, round(float(peak), 1)


if __name__ == '__main__':
    oid, year = sys.argv[1], int(sys.argv[2]); step = float(sys.argv[3]) if len(sys.argv) > 3 else 500; half = float(sys.argv[4]) if len(sys.argv) > 4 else 300
    c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read()))
    G = {g['id']: g for g in c['geometries']}; O = {o['id']: o for o in c['objects']}
    L = LineString([TO_M(*p) for p in G[O[oid]['geometryPeriods'][-1]['geometryId']]['paths'][0]])
    ref, ref_px = sheet(1985); img, px = sheet(year)
    for d in np.arange(step / 2, L.length, step):
        cx, cy = L.interpolate(d).coords[0]
        dx, dy, pk = shift(resample(ref, ref_px, cx, cy, half), resample(img, px, cx, cy, half))
        print(int(d), dx, dy, pk)
