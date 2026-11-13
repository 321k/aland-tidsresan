"""Shared converters for sheet 101208 (pixel <-> WGS84) used by the building review scripts."""
import sys, json, gzip
from pathlib import Path
import numpy as np
from pyproj import Transformer
sys.path.insert(0, 'scripts')
from historical_map_observations import load_review, MERCATOR
from rural_registration import registration_pair
read = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
_, regs = load_review(read)
def converters(year):
    if year < 1995:
        sheet, convert, _ = regs[f'nls-mariehamn-{year}']
        pix = np.array([[0, 0, 1], [1000, 0, 1], [0, 1000, 1]]); geo = np.array([MERCATOR(*p) for p in convert(pix[:, :2])])
        mat = np.linalg.solve(pix, geo); inv = np.linalg.inv(mat[:2, :]); toWGS = Transformer.from_crs(3857, 4326, always_xy=True).transform
        return sheet, 'nls:' + sheet['id'], (lambda lon, lat: (np.array(MERCATOR(lon, lat)) - mat[2, :]) @ inv), (lambda x, y: toWGS(*(np.array([x, y, 1.0]) @ mat)))
    sheet = next(s for s in read('data/rural-map-review.json')['sources'] if s['id'] == 'nls:101208:1995')
    fwd, inv = registration_pair(sheet); crs = sheet['registration']['crs']
    proj = Transformer.from_crs(4326, crs, always_xy=True).transform; back = Transformer.from_crs(crs, 4326, always_xy=True).transform
    return sheet, sheet['id'], (lambda lon, lat: np.array(inv(proj(lon, lat)))), (lambda x, y: back(*fwd((x, y))))
