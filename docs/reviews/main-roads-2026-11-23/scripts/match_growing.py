"""Batch 5: objects of the Hammarland rural review whose geometry grows over time and whose early periods cover only
the sheet that review read (1012 06). For each object, along its latest geometry (today's line): where the first
edition of another registered sheet draws the red main-road symbol within NEAR m (sheets the earlier review read are
skipped), and where the next editions do. Ranges as in batch 1: runs of red samples, gaps up to BRIDGE m joined, runs
under MIN m dropped; then gaps up to 100 m bridged and pieces under 150 m dropped (propose.py). Pieces within 5 m of
the object's own first-period geometry, or along another road open in that year (OVERLAP), are left out.
Usage: match_growing.py OUT.json OBJECT_ID [OBJECT_ID ...]"""
import sys, json, gzip
sys.path.insert(0, 'docs/reviews/main-roads-2026-11-23/scripts'); sys.path.insert(0, 'scripts')
import redmask
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import substring
from shapely.strtree import STRtree
from pyproj import Transformer
STEP, NEAR, BRIDGE, MIN, GAP, STUB, OWN, OVERLAP = 10, 12, 40, 50, 100, 150, 5, 12
rev = json.load(open('data/rural-map-review.json'))
eds = {}
for s in rev['sources']:
    r = s.get('registration') or {}
    if 'metricFrame' not in r: continue
    t = Transformer.from_crs(r['crs'], 'EPSG:3874', always_xy=True).transform
    eds.setdefault(s['sheet'], []).append((s['year'], s['id'], Polygon([t(*p) for p in r['metricFrame']])))
for v in eds.values(): v.sort()
cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
met = lambda p: LineString([TO_METRIC(*q) for q in p])

def others(oid, year):
    ls = []
    for o in cat['objects']:
        if o.get('kind') != 'roadSegment' or o['id'] == oid: continue
        st = next((s for s in o['states'] if s['from'] <= year < (s['to'] or 9999)), None)
        gp = next((g for g in o['geometryPeriods'] if g['from'] <= year < (g['to'] or 9999)), None)
        if st and st['state'] == 'open' and gp: ls += [met(p) for p in G[gp['geometryId']]['paths'] if len(p) > 1]
    return ls, STRtree(ls)

def runs(hits, bridge, minimum):
    out, cur = [], None
    for d, h in hits:
        if h:
            if cur is None: cur = [d, d]
            elif d - cur[1] <= bridge + STEP: cur[1] = d
            else: out.append(cur); cur = [d, d]
    if cur: out.append(cur)
    return [r for r in out if r[1] - r[0] >= minimum]

res = {}
for oid in sys.argv[2:]:
    o = O[oid]; skip = {e['sourceId'].split(':')[1] for e in o['evidence'] if str(e.get('sourceId', '')).startswith('nls:')}
    last = o['geometryPeriods'][-1]; paths = [p for p in G[last['geometryId']]['paths'] if len(p) > 1]
    assert len(paths) == 1, oid
    line = met(paths[0]); first = [met(p) for p in G[o['geometryPeriods'][0]['geometryId']]['paths'] if len(p) > 1]
    n = int(line.length // STEP) + 1
    samples = [min(i * STEP, line.length) for i in range(n + 1)]
    sheet_of = []
    for d in samples:
        pt = line.interpolate(d)
        sh = [k for k, v in eds.items() if v[0][2].contains(pt)]
        sheet_of.append(None if not sh or any(k in skip for k in sh) else sh[0])
    out = dict(name=o.get('name'), skipSheets=sorted(skip), length=round(line.length, 1), latestFrom=last['from'], editions=[])
    for k in range(4):
        hits, used = [], set()
        for d, sh in zip(samples, sheet_of):
            if sh is None or len(eds[sh]) <= k: hits.append((d, None)); continue
            year, sid, _ = eds[sh][k]; used.add((year, sid))
            mask, px, _ = redmask.load(sid); H, W = mask.shape
            E, N = line.interpolate(d).coords[0]; c, r = px(E, N); c2, _ = px(E + NEAR, N); rad = max(2, int(abs(c2 - c))); c, r = int(c), int(r)
            hits.append((d, bool(mask[r - rad:r + rad + 1, c - rad:c + rad + 1].any()) if rad <= c < W - rad and rad <= r < H - rad else None))
        if not used: break
        rr = runs(hits, BRIDGE, MIN)
        merged = []
        for a, b in rr:
            if merged and a - merged[-1][1] <= GAP: merged[-1][1] = b
            else: merged.append([a, b])
        merged = [r for r in merged if r[1] - r[0] >= STUB]
        # leave out what the first period already has, and what runs along another road open in that year
        year0 = min(y for y, _ in used); ls, tree = others(oid, year0)
        keep = []
        for a, b in merged:
            cur = None
            for d in [a + i * STEP for i in range(int((b - a) // STEP) + 1)] + [b]:
                pt = line.interpolate(d)
                bad = any(f.distance(pt) <= OWN for f in first) or any(ls[j].distance(pt) <= OVERLAP for j in tree.query(pt.buffer(OVERLAP)))
                if not bad: cur = [cur[0], d] if cur else [d, d]
                elif cur: keep.append(cur); cur = None
            if cur: keep.append(cur)
        keep = [[round(a, 1), round(b, 1)] for a, b in keep if b - a >= STUB]
        out['editions'].append(dict(years=sorted(used), ranges=keep, matched=round(sum(b - a for a, b in keep), 1)))
        print(f"{oid[-40:]:40s} ed{k} {sorted({y for y, _ in used})} {round(sum(b - a for a, b in keep)):6d} m  {keep}")
    res[oid] = out
json.dump(res, open(sys.argv[1], 'w'), indent=1, ensure_ascii=False)
