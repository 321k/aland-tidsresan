"""Fetch Mariehamn orthophoto tiles (1 m/px, z=17, 256 m tiles in EPSG:3874) for a bbox and photo years (read-only
source; tiles are cached in tiles/ and listed with their sha256 in tiles.json).
Usage: fetch.py lon0 lat0 lon1 lat1 YEAR [YEAR ...]"""
import sys, json, hashlib, urllib.request
from pathlib import Path
from pyproj import Transformer
P = Path('data/map-scan-cache/review/photo-dating'); T = P / 'tiles'; T.mkdir(parents=True, exist_ok=True)
lon0, lat0, lon1, lat1 = map(float, sys.argv[1:5]); years = [int(y) for y in sys.argv[5:]]
to = Transformer.from_crs(4326, 3874, always_xy=True).transform
(e0, n0), (e1, n1) = to(lon0, lat0), to(lon1, lat1)
index = json.load(open(P / 'tiles.json')) if (P / 'tiles.json').exists() else {}
got = 0
for year in years:
    for x in range(int(e0 // 256) - 1, int(e1 // 256) + 2):
        for y in range(int(n0 // 256) - 1, int(n1 // 256) + 2):
            f = T / f'ortho-{year}-17-{x}-{y}.png'
            if f.name in index and index[f.name] is None:
                continue  # known to be outside the photographed extent
            if not f.exists():
                url = f'https://karta.mariehamn.ax/IMS/Tile/Layer?layer=Ortofoto%20{year}&x={x}&y={y}&z=17'
                with urllib.request.urlopen(url, timeout=60) as r:
                    data = r.read()
                if not data:
                    index[f.name] = None; continue  # an empty answer: this photo does not cover the tile
                if not data.startswith(b'\x89PNG'):
                    raise ValueError('Not a PNG tile: ' + url)
                f.write_bytes(data); got += 1
            index[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
json.dump(dict(sorted(index.items())), open(P / 'tiles.json', 'w'), indent=0)
print(got, 'tiles fetched,', sum(v is not None for v in index.values()), 'cached,', sum(v is None for v in index.values()), 'outside the photographed extent')
