"""match.py across sheets and editions: for an object, for each edition index (0 = first, 1 = second, …) of the
registered sheets it crosses, the ranges along its earliest geometry where the red main-road symbol lies under it. A
step is read on the sheet whose metric frame contains it. Editions at or after the object's current first year are
skipped. Usage: match_editions.py OUT.json OBJECT_ID [OBJECT_ID ...]"""
import sys, json, gzip
sys.path.insert(0, 'docs/reviews/main-roads-2026-11-23/scripts'); sys.path.insert(0, 'scripts')
import redmask
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, Point, Polygon
from pyproj import Transformer
import os
STEP, NEAR, BRIDGE, MIN = 10, int(os.environ.get("NEAR", 12)), 40, 50
rev = json.load(open('data/rural-map-review.json'))
eds = {}
for s in rev['sources']:
    r = s.get('registration') or {}
    if 'metricFrame' not in r: continue
    t = Transformer.from_crs(r['crs'], 'EPSG:3874', always_xy=True).transform
    eds.setdefault(s['sheet'], []).append((s['year'], s['id'], Polygon([t(*p) for p in r['metricFrame']])))
for v in eds.values(): v.sort()
def sheet_at(pt, k):
    for sheet, v in eds.items():
        if len(v) > k and v[0][2].contains(pt): return v[k]
    return None
def run(path_ll, k, before):
    line = LineString([TO_METRIC(*q) for q in path_ll]); n = int(line.length // STEP) + 1
    hits, years = [], set()
    for i in range(n + 1):
        d = min(i * STEP, line.length); pt = line.interpolate(d); ed = sheet_at(pt, k)
        if not ed or ed[0] >= before: hits.append((d, None)); continue
        years.add((ed[0], ed[1])); mask, px, _ = redmask.load(ed[1]); H, W = mask.shape
        E, N = pt.coords[0]; c, r = px(E, N); c2, _ = px(E + NEAR, N); rad = max(2, int(abs(c2 - c))); c, r = int(c), int(r)
        if not (rad <= c < W - rad and rad <= r < H - rad): hits.append((d, None)); continue
        hits.append((d, bool(mask[r - rad:r + rad + 1, c - rad:c + rad + 1].any())))
    runs, cur = [], None
    for d, h in hits:
        if h:
            if cur is None: cur = [d, d]
            elif d - cur[1] <= BRIDGE + STEP: cur[1] = d
            else: runs.append(cur); cur = [d, d]
    if cur: runs.append(cur)
    runs = [[round(a, 1), round(b, 1)] for a, b in runs if b - a >= MIN]
    read = sum(STEP for _, h in hits if h is not None)
    return dict(editions=sorted(years), length=round(line.length, 1), read=read, ranges=runs, matched=round(sum(b - a for a, b in runs), 1))
out = sys.argv[1]
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
res = {}
for oid in sys.argv[2:]:
    o = O[oid]; first = o['states'][0]['from']; g = G[o['geometryPeriods'][0]['geometryId']]
    res[oid] = dict(name=o.get('name'), firstYear=first, paths=len(g['paths']), editions=[])
    for k in range(4):
        r = [run(p, k, first) for p in g['paths'] if len(p) > 1]
        if not any(x['read'] for x in r): break
        res[oid]['editions'].append(r)
        e = r[0]['editions']; print(f"{oid[-38:]:38s} ed{k} {[y for y, _ in e]} matched {sum(x['matched'] for x in r):7.0f} of {sum(x['length'] for x in r):7.0f}  ranges {[x['ranges'] for x in r]}")
json.dump(res, open(out, 'w'), indent=1, ensure_ascii=False)
