"""Turn symbol matches into proposed first editions, with a bounded fill-in pass for missed intermediate symbols.
Rules: 1978 is a road revision on the 1968 base and is not independent building evidence. A building starts at the
first of 1968/1985/1995 with a matched symbol and must be matched in every later one of those editions; a missing
intermediate edition may be filled by an unused symbol within FILL_LIMIT of the shifted outline. Others are deferred."""
import sys, json, gzip
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import Polygon, Point
P = Path('data/map-scan-cache/review/mariehamn-buildings'); key = sys.argv[1]
FILL_LIMIT = 14.0
SIZE_RATIO = 3.0
PX_AREA = 1.68 * 1.68   # m² per scan pixel (1968–1995 scans are about 1.68 m/px)
r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
toM = Transformer.from_crs(4326, 3874, always_xy=True).transform
m = json.load(open(P / f'{key}-match.json')); cat = r(str(P / 'before.json.gz'))
G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
used = {y: [s['used'] for s in e['symbolList']] for y, e in m['editions'].items()}
verdict, fills, mismatch = {}, {}, {}
for bid, b in m['buildings'].items():
    if b['first'] is not None and b['first'] <= 1995: verdict[bid] = 'already-dated'; continue
    if b['symbolObject']: verdict[bid] = 'symbol-object'; continue
    # A much larger building than the symbol it sits on is more likely a replacement of a smaller house.
    sized = {y: x for y, x in b['editions'].items() if y != '1978' and b['area'] <= SIZE_RATIO * x['symbolAreaPx'] * PX_AREA}
    if len(sized) < len([y for y in b['editions'] if y != '1978']): mismatch[bid] = sorted(set(b['editions']) - set(sized) - {'1978'})
    e = {int(y) for y in sized}
    if not e: verdict[bid] = 'absent'; continue
    first, last = min(e), max(e)
    missing = [y for y in (1968, 1985, 1995) if first < y and y not in e]
    poly = Polygon([toM(*p) for p in G[O[bid]['geometryPeriods'][-1]['geometryId']]['paths'][0]])
    for y in list(missing):
        if y > last: continue  # a later edition without the house is not filled
        sh = b.get('shifts', {}).get(str(y), [0, 0]); moved = Polygon([(x + sh[0], yy + sh[1]) for x, yy in poly.exterior.coords])
        best = None
        for j, s in enumerate(m['editions'][str(y)]['symbolList']):
            if used[str(y)][j]: continue
            d = moved.distance(Point(*s['m']))
            if d <= FILL_LIMIT and (best is None or d < best[0]): best = (d, j)
        if best:
            used[str(y)][best[1]] = True; s = m['editions'][str(y)]['symbolList'][best[1]]
            fills[bid] = fills.get(bid, {}); fills[bid][str(y)] = dict(sourceId=m['editions'][str(y)]['sourceId'], pixel=s['px'], distanceAfterShift=round(best[0], 1), shift=sh, filled=True)
            missing.remove(y)
    # 1968 and 1995 both show the house but no 1985 symbol is found nearby: keep 1968, record 1985 as unclear.
    if first == 1968 and 1995 in e and missing == [1985]:
        verdict[bid] = '1968'; fills.setdefault(bid, {})['1985'] = dict(unclear=True); continue
    verdict[bid] = str(first) if not missing else 'inconsistent'
# Guard: a later first edition is only accepted if the previous edition shows no hatched or stippled building
# (not detected as a filled symbol) inside the shifted outline. Otherwise the date is deferred, never set too late.
import importlib.util, numpy as np
from PIL import Image, ImageDraw
spec = importlib.util.spec_from_file_location('conv', P / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
ink = {}
for y in (1968, 1985):
    to_px = conv.converters(y)[2]; im = Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB')
    for bid, v in verdict.items():
        if v not in (('1985',) if y == 1968 else ('1995',)): continue
        ring = G[O[bid]['geometryPeriods'][-1]['geometryId']]['paths'][0]
        sh = m['buildings'][bid].get('shifts', {}).get(str(y), [0, 0])
        poly = Polygon([toM(*p) for p in ring]); back = Transformer.from_crs(3874, 4326, always_xy=True).transform
        pts = [to_px(*back(x + sh[0], yy + sh[1])) for x, yy in poly.exterior.coords]
        x0, y0 = np.floor(np.min(pts, axis=0)).astype(int) - 1; x1, y1 = np.ceil(np.max(pts, axis=0)).astype(int) + 1
        a = np.asarray(im.crop((x0, y0, x1, y1)), dtype=float); mask = Image.new('L', (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(mask).polygon([(px - x0, py - y0) for px, py in pts], fill=1); mk = np.asarray(mask, dtype=bool)
        if mk.sum() < 3: continue
        lum = a.mean(axis=2); sat = a.max(axis=2) - a.min(axis=2); dark = (lum < 140) & (sat < 70)
        frac = float(dark[mk].mean()); ink[bid] = round(frac, 3)
        if frac > (0.18 if y == 1968 else 0.06): verdict[bid] = 'earlier-unclear'
json.dump(ink, open(P / f'{key}-ink.json', 'w')); json.dump(mismatch, open(P / f'{key}-mismatch.json', 'w'))
json.dump(verdict, open(P / f'{key}-verdict.json', 'w')); json.dump(fills, open(P / f'{key}-fills.json', 'w'), indent=1)
from collections import Counter; print(Counter(verdict.values()), 'filled', len(fills))
