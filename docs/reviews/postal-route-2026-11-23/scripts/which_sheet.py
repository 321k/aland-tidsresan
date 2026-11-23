"""Which registered base-map scans (data/rural-map-review.json) cover a point. Usage: which_sheet.py E N [E N ...]"""
import sys, json
sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts'); sys.path.insert(0, 'scripts')
import maps
from rural_registration import registration_pair
from pyproj import Transformer
for E, N in zip(*[iter(map(float, sys.argv[1:]))] * 2):
    hits = []
    for sid, s in maps.SHEETS.items():
        if not sid.startswith('nls:'): continue
        fwd, inv = registration_pair(s); proj = Transformer.from_crs(3874, s['registration']['crs'], always_xy=True).transform
        x, y = inv(proj(E, N)); w, h = s['imageSize']
        if 0.03 * w < x < 0.97 * w and 0.03 * h < y < 0.97 * h: hits.append(sid)
    print(round(E), round(N), sorted(hits))
