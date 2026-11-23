"""Where an object's geometry lies on the base map's red main-road symbol (redmask.py): every STEP m along each path, is
the mask within NEAR m? Runs of matching steps, with gaps up to BRIDGE m bridged and runs under MIN m dropped, are the
ranges (metres along the path) where today's line is the road the map draws; the rest are where the map's road runs
elsewhere (or is not a main road). Usage: match.py OBJECT_ID SHEET_ID [PERIOD_INDEX]  → JSON on stdout"""
import sys, json, gzip, math
sys.path.insert(0, 'docs/reviews/main-roads-2026-11-23/scripts'); sys.path.insert(0, 'scripts')
import numpy as np, redmask
from mariehamn_frame_1942 import TO_METRIC
from shapely.geometry import LineString
STEP, NEAR, BRIDGE, MIN = 10, 12, 40, 50
def match(path_ll, sid):
    mask, px, xy = redmask.load(sid); H, W = mask.shape
    line = LineString([TO_METRIC(*q) for q in path_ll]); n = int(line.length // STEP) + 1
    hits = []
    for i in range(n + 1):
        d = min(i * STEP, line.length); E, N = line.interpolate(d).coords[0]
        c, r = px(E, N); c2, _ = px(E + NEAR, N); rad = max(2, int(abs(c2 - c)))
        c, r = int(c), int(r)
        if not (rad <= c < W - rad and rad <= r < H - rad): hits.append((d, None)); continue
        w = mask[r - rad:r + rad + 1, c - rad:c + rad + 1]
        hits.append((d, bool(w.any())))
    runs, cur = [], None
    for d, h in hits:
        if h:
            if cur is None: cur = [d, d]
            elif d - cur[1] <= BRIDGE + STEP: cur[1] = d
            else: runs.append(cur); cur = [d, d]
    if cur: runs.append(cur)
    runs = [[round(a, 1), round(b, 1)] for a, b in runs if b - a >= MIN]
    off = sum(1 for _, h in hits if h is None)
    return dict(length=round(line.length, 1), ranges=runs, matched=round(sum(b - a for a, b in runs), 1), offSheet=off * STEP)
if __name__ == '__main__':
    oid, sid = sys.argv[1], sys.argv[2]; pi = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    cat = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
    g = G[O[oid]['geometryPeriods'][pi]['geometryId']]
    print(json.dumps([match(p, sid) for p in g['paths'] if len(p) > 1]))
