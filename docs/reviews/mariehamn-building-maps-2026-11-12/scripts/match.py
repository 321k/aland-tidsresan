"""Detect house symbols on sheet 101208 (1968/1978/1985/1995) and match them to today's building outlines.

Read-only on sources; writes into this folder. Detection is a proposal for visual review, not evidence:
every area is checked on the overlays before a decision is recorded.

Usage: match.py KEY lon0 lat0 lon1 lat1
Writes KEY-match.json (per building: symbol pixel and distance per edition) and KEY-YEAR-match.png overlays.
"""
import sys, json, gzip, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import ndimage
from shapely.geometry import Polygon, Point, MultiPoint
sys.path.insert(0, 'scripts')
from historical_map_observations import load_review, MERCATOR
from rural_registration import registration_pair

r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
_, regs = load_review(r)
P = Path('data/map-scan-cache/review/mariehamn-buildings')
key = sys.argv[1]; bbox = list(map(float, sys.argv[2:6]))
toM = Transformer.from_crs(4326, 3874, always_xy=True).transform
YEARS = [1968, 1978, 1985, 1995]
MIN_AREA = 40          # m²; smaller outbuildings are not drawn at 1:20 000
MATCH_LIMIT = 9.0      # metres from a symbol centre to the outline after the local shift
SHIFT_RADIUS = 150     # metres; neighbourhood for the local registration shift

catalog = r(str(P / 'before.json.gz')); G = {g['id']: g for g in catalog['geometries']}
buildings = []
for o in catalog['objects']:
    if o.get('kind') != 'building' or not o['geometryPeriods']:
        continue
    g = G.get(o['geometryPeriods'][-1]['geometryId'])
    if not g:
        continue
    ring = g['paths'][0]; cx = sum(p[0] for p in ring) / len(ring); cy = sum(p[1] for p in ring) / len(ring)
    if not (bbox[0] <= cx <= bbox[2] and bbox[1] <= cy <= bbox[3]):
        continue
    poly = Polygon([toM(*p) for p in ring])
    op = [s['from'] for s in o['states'] if s['state'] in ('standing', 'occupied')]
    buildings.append(dict(id=o['id'], ring=ring, poly=poly, area=poly.area, first=min(op) if op else None,
                          symbolObject=bool(o.get('printedMapSymbol'))))


def converters(year):
    if year < 1995:
        sheet, convert, _ = regs[f'nls-mariehamn-{year}']
        pix = np.array([[0, 0, 1], [1000, 0, 1], [0, 1000, 1]]); geo = np.array([MERCATOR(*p) for p in convert(pix[:, :2])])
        mat = np.linalg.solve(pix, geo); inv = np.linalg.inv(mat[:2, :]); toWGS = Transformer.from_crs(3857, 4326, always_xy=True).transform
        to_px = lambda lon, lat: (np.array(MERCATOR(lon, lat)) - mat[2, :]) @ inv
        to_geo = lambda x, y: toWGS(*(np.array([x, y, 1.0]) @ mat))
        return sheet, 'nls:' + sheet['id'], to_px, to_geo
    sheet = next(s for s in r('data/rural-map-review.json')['sources'] if s['id'] == 'nls:101208:1995')
    fwd, inv = registration_pair(sheet); crs = sheet['registration']['crs']
    proj = Transformer.from_crs(4326, crs, always_xy=True).transform; back = Transformer.from_crs(crs, 4326, always_xy=True).transform
    return sheet, sheet['id'], (lambda lon, lat: np.array(inv(proj(lon, lat)))), (lambda x, y: back(*fwd((x, y))))


out = dict(bbox=bbox, editions={}, buildings={b['id']: dict(area=round(b['area'], 1), first=b['first'], symbolObject=b['symbolObject'], editions={}) for b in buildings})
for year in YEARS:
    sheet, sid, to_px, to_geo = converters(year)
    raw = Path(f'data/map-scan-cache/101208_{year}.jpg'); assert hashlib.sha256(raw.read_bytes()).hexdigest() == sheet['originalSha256']
    im = Image.open(raw).convert('RGB')
    q = [to_px(x, y) for x in [bbox[0], bbox[2]] for y in [bbox[1], bbox[3]]]
    x0, y0 = np.floor(np.min(q, axis=0)).astype(int) - 10; x1, y1 = np.ceil(np.max(q, axis=0)).astype(int) + 10
    a = np.asarray(im.crop((x0, y0, x1, y1)), dtype=float)
    lum = a.mean(axis=2); sat = a.max(axis=2) - a.min(axis=2)
    dark = (lum < 115) & (sat < 70)                       # dark grey/brown building fill, not red roads or text in red
    core = ndimage.binary_opening(dark, structure=np.ones((3, 3)))   # drops 1–2 px lines and hatching
    lab, n = ndimage.label(core)
    syms = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        comp = lab[sl] == i; area = comp.sum()
        if area < 10 or area > 3000:
            continue
        ys, xs = np.nonzero(comp)
        hull = MultiPoint(list(zip(xs.tolist(), ys.tolist()))).convex_hull
        if hull.area > 0 and area / max(hull.area, 1) < 0.6:   # filled blocks only; diagonal rectangles keep a high solidity
            continue
        cy, cx = ndimage.center_of_mass(comp)
        px, py = x0 + sl[1].start + cx, y0 + sl[0].start + cy
        lon, lat = to_geo(px, py); e, nn = toM(lon, lat)
        syms.append(dict(px=[round(float(px), 2), round(float(py), 2)], m=[e, nn], area=int(area)))
    S = np.array([s['m'] for s in syms]) if syms else np.zeros((0, 2))
    elig = [b for b in buildings if b['area'] >= MIN_AREA]
    # raw nearest distances and offset vectors (symbol centre minus outline centroid)
    raw_vec = {}
    for b in elig:
        c = b['poly'].centroid; d = np.hypot(S[:, 0] - c.x, S[:, 1] - c.y) if len(S) else np.array([])
        if len(d) and d.min() < 25:
            j = int(d.argmin()); raw_vec[b['id']] = (S[j] - [c.x, c.y], c)
    def shift_at(c):
        vs = [v for v, cc in raw_vec.values() if np.hypot(cc.x - c.x, cc.y - c.y) < SHIFT_RADIUS]
        return np.median(np.array(vs), axis=0) if len(vs) >= 5 else np.zeros(2)
    cand = []
    for b in elig:
        sh = shift_at(b['poly'].centroid); moved = Polygon([(x + sh[0], y + sh[1]) for x, y in b['poly'].exterior.coords])
        for j, s in enumerate(syms):
            d = moved.distance(Point(*s['m']))
            if d <= MATCH_LIMIT:
                cand.append((d, -b['area'], b['id'], j, sh))
    cand.sort(); used_b, used_s = set(), set()
    for d, _, bid, j, sh in cand:
        if bid in used_b or j in used_s:
            continue
        used_b.add(bid); used_s.add(j)
        out['buildings'][bid]['editions'][str(year)] = dict(sourceId=sid, pixel=syms[j]['px'], distanceAfterShift=round(d, 1),
                                                            shift=[round(float(v), 1) for v in sh], symbolAreaPx=syms[j]['area'])
    out['editions'][str(year)] = dict(sourceId=sid, symbols=len(syms), matched=len(used_s), box=[int(x0), int(y0), int(x1), int(y1)],
                                      symbolList=[dict(px=s['px'], m=[round(s['m'][0], 2), round(s['m'][1], 2)], area=s['area'], used=j in used_s) for j, s in enumerate(syms)])
    for b in elig:
        sh = shift_at(b['poly'].centroid); out['buildings'][b['id']].setdefault('shifts', {})[str(year)] = [round(float(v), 2) for v in sh]
    # overlay: outlines coloured by match in this edition, symbols as dots
    Sc = 3; ov = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * Sc, (y1 - y0) * Sc), Image.LANCZOS); dr = ImageDraw.Draw(ov)
    for b in buildings:
        xy = [tuple((to_px(*p) - [x0, y0]) * Sc) for p in b['ring']]
        hit = str(year) in out['buildings'][b['id']]['editions']
        col = (0, 200, 0) if hit else (150, 150, 150) if b['area'] < MIN_AREA else (0, 120, 255)
        dr.line(xy + [xy[0]], fill=col, width=2 if hit else 1)
    for j, s in enumerate(syms):
        u, v = (s['px'][0] - x0) * Sc, (s['px'][1] - y0) * Sc
        dr.ellipse([u - 3, v - 3, u + 3, v + 3], fill=(255, 0, 0) if j not in used_s else (255, 200, 0))
    ov.save(P / f'{key}-{year}-match.png')
(P / f'{key}-match.json').write_text(json.dumps(out, indent=1))
print(key, len(buildings), 'buildings,', sum(b['area'] >= MIN_AREA for b in buildings), 'eligible', {y: e for y, e in out['editions'].items()})
