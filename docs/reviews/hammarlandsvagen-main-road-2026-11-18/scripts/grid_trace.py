"""Pixel waypoints read on a grid_window.py render, converted to EPSG:3874 metres by inverting the window's projection
(an affine fit on a 9×9 grid; under 0.2 m error for these windows)."""
import sys, json, os
sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, 'scripts')
import numpy as np, maps
from maps import tile_window
from shapely.geometry import LineString
for k, v in {'eckero-1929': 'map-39091228', 'eckero-1956': 'map-37971493', 'morby-1929': 'map-38157016', 'bovik-1946': 'map-38157019'}.items():
    maps.MAPS[k] = {'tiles_url': f'https://historicmaps2.vanhatkartat.fi/maps/mml/{v}/{{z}}/{{x}}/{{y}}.png'}
R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'


def window_inverse(key, ref, d, half, size, center=None):
    L = LineString(json.load(open(f'{R}/data/{ref}'))['metric'])
    cx, cy = center or L.interpolate(d).coords[0]
    _, f = tile_window(key, 15, cx, cy, half, size)
    E, N = np.meshgrid(np.linspace(cx - half, cx + half, 9), np.linspace(cy - half, cy + half, 9)); E, N = E.ravel(), N.ravel()
    P = np.array([f(e, n) for e, n in zip(E, N)]); A = np.c_[P, np.ones(len(P))]
    ce, cn = np.linalg.lstsq(A, E, rcond=None)[0], np.linalg.lstsq(A, N, rcond=None)[0]
    err = max(abs(A @ ce - E).max(), abs(A @ cn - N).max())
    assert err < 0.5, err
    return lambda x, y: (float(np.dot([x, y, 1], ce)), float(np.dot([x, y, 1], cn)))
