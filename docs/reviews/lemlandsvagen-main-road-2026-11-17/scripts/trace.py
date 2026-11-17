"""Least-cost tracing of a drawn road on a stitched XYZ map mosaic (fetch_xyz.py output), between hand-picked waypoints.

The road is found as the darkest connected band after a small blur (double road lines merge into one band); the
waypoints keep the path on the intended road. Every trace is checked by eye on the overlay renders afterwards.
"""
import heapq, json, math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, shift
from pyproj import Transformer

TO_M = Transformer.from_crs(4326, 3874, always_xy=True).transform
TO_G = Transformer.from_crs(3874, 4326, always_xy=True).transform


class Mosaic:
    def __init__(self, png, sigma=0.8, ring=2.5):
        """band: road-centre score. A road is drawn as two dark edge lines with a lighter fill between them, so the
        centre scores high where the ring of radius `ring` px around it is dark and the pixel itself is not."""
        self.meta = json.load(open(png[:-4] + '.json')); self.z = self.meta['zoom']
        self.rgb = np.asarray(Image.open(png).convert('RGB')).astype(float)
        dark = gaussian_filter(1 - self.rgb.mean(axis=2) / 255, sigma)
        acc = np.zeros_like(dark); n = 16
        for k in range(n):
            a = 2 * math.pi * k / n
            acc += shift(dark, (ring * math.sin(a), ring * math.cos(a)), order=1, mode='nearest')
        opp = np.zeros_like(dark)  # both sides dark: min over opposite pairs keeps lines that bound the centre on both sides
        for k in range(n // 2):
            a = 2 * math.pi * k / n; v = (ring * math.sin(a), ring * math.cos(a))
            opp = np.maximum(opp, np.minimum(shift(dark, v, order=1, mode='nearest'), shift(dark, (-v[0], -v[1]), order=1, mode='nearest')))
        self.band = gaussian_filter(np.clip(opp - dark, 0, None), 1.0)

    def px(self, lon, lat):
        n = 2 ** self.z
        return ((lon + 180) / 360 * n - self.meta['x0']) * 256, ((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n - self.meta['y0']) * 256

    def geo(self, x, y):
        n = 2 ** self.z; X = x / 256 + self.meta['x0']; Y = y / 256 + self.meta['y0']
        return X / n * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * Y / n))))

    def path(self, a, b, margin=25):
        (x0, y0), (x1, y1) = self.px(*a), self.px(*b)
        c0, r0 = int(min(x0, x1)) - margin, int(min(y0, y1)) - margin
        c1, r1 = int(max(x0, x1)) + margin, int(max(y0, y1)) + margin
        sub = self.band[r0:r1, c0:c1]; hi = np.percentile(self.band, 99.5)
        cost = (1 - np.clip(sub / hi, 0, 1)) ** 4 + 0.01
        H, W = cost.shape; s = (int(round(y0)) - r0, int(round(x0)) - c0); t = (int(round(y1)) - r0, int(round(x1)) - c0)
        dist = np.full((H, W), np.inf); prev = {}; dist[s] = 0; q = [(0.0, s)]
        while q:
            d, (r, c) = heapq.heappop(q)
            if (r, c) == t: break
            if d > dist[r, c]: continue
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr or dc:
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < H and 0 <= cc < W:
                            nd = d + cost[rr, cc] * (1.4142 if dr and dc else 1)
                            if nd < dist[rr, cc]:
                                dist[rr, cc] = nd; prev[(rr, cc)] = (r, c); heapq.heappush(q, (nd, (rr, cc)))
        out = [t]
        while out[-1] != s: out.append(prev[out[-1]])
        return [self.geo(c + c0 + 0.5, r + r0 + 0.5) for r, c in reversed(out)]

    def trace(self, waypoints):
        pts = []
        for a, b in zip(waypoints, waypoints[1:]):
            seg = self.path(a, b); pts += seg if not pts else seg[1:]
        return pts


def smooth_metric(points, window=5):
    """Metric (EPSG:3874) coordinates of a pixel path, moving-average smoothed to remove the pixel staircase."""
    m = np.array([TO_M(*p) for p in points]); k = window // 2
    out = [m[max(0, i - k):i + k + 1].mean(axis=0) for i in range(len(m))]
    out[0], out[-1] = m[0], m[-1]
    return [tuple(p) for p in out]


def snap(mosaic, lonlat, radius=10):
    """Waypoint moved to the darkest band pixel within radius pixels."""
    x, y = mosaic.px(*lonlat); xi, yi = int(round(x)), int(round(y))
    win = mosaic.band[yi - radius:yi + radius + 1, xi - radius:xi + radius + 1]
    yy, xx = np.mgrid[-radius:radius + 1, -radius:radius + 1]; win = np.where(xx ** 2 + yy ** 2 <= radius ** 2, win, -1)
    r, c = np.unravel_index(np.argmax(win), win.shape)
    return mosaic.geo(xi - radius + c + 0.5, yi - radius + r + 0.5)
