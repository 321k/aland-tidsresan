"""Candidates and contact sheets for dating printed-map symbol objects (map-building:nls-symbol-*) from the 1968 edition.

A symbol object starts at the 1985 edition's survey year (1983 or 1982). Candidates are those whose 1968 symbol was
matched one-to-one in the b6–b8 matching (match.py), whose first state starts after 1968, and whose 1968 symbol lies
outside the 1968 hatched built-up areas (printedMapArea objects, shown 1968–1985), where single houses cannot be told
from the hatching. The hatching reaches beyond those area objects, so the surroundings (5–14 m outside the shifted
outline) are also measured on the 1968 scan: a candidate is left out as hatched if the dark share there is above 0.40
or the dark stripe density (dark/light changes per pixel along rows) is above 0.22; on the first sheet hatched
surroundings measured 0.32 or more and open ones 0.21 or less. Usage: sym_prepare.py  -> writes sym-candidates.json and sym-contact-N.jpg (1968 | 1985 | 1995).
Read-only on sources; uses before.json.gz for the catalogue."""
import json, importlib.util
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Polygon, Point
P = Path('data/map-scan-cache/review/mariehamn-buildings')
spec = importlib.util.spec_from_file_location('conv', P / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
cat = conv.read(str(P / 'before.json.gz')); G = {g['id']: g for g in cat['geometries']}; O = {o['id']: o for o in cat['objects']}
toM = Transformer.from_crs(4326, 3874, always_xy=True).transform; back = Transformer.from_crs(3874, 4326, always_xy=True).transform
cv = {y: conv.converters(y) for y in (1968, 1985, 1995)}
areas = [Polygon([toM(*p) for p in G[a['geometryPeriods'][0]['geometryId']]['paths'][0]]) for a in cat['objects'] if a.get('printedMapArea')]
lum = None
def surroundings(o, sh):
    global lum, dark
    if lum is None:
        im = np.asarray(Image.open('data/map-scan-cache/101208_1968.jpg').convert('RGB'), dtype=float)
        lum = im.mean(axis=2); dark = (lum < 150) & ((im.max(axis=2) - im.min(axis=2)) < 80)
    to_px = cv[1968][2]
    poly = Polygon([toM(*p) for p in G[o['geometryPeriods'][0]['geometryId']]['paths'][0]])
    moved = Polygon([(x + sh[0], y + sh[1]) for x, y in poly.exterior.coords]); ring = moved.buffer(14).difference(moved.buffer(5))
    geoms = list(getattr(ring, 'geoms', [ring])); pts = [to_px(*back(x, y)) for g in geoms for x, y in g.exterior.coords]
    x0, y0 = np.floor(np.min(pts, axis=0)).astype(int) - 1; x1, y1 = np.ceil(np.max(pts, axis=0)).astype(int) + 2
    mask = Image.new('L', (x1 - x0, y1 - y0), 0); d = ImageDraw.Draw(mask)
    for g in geoms:
        d.polygon([tuple(np.array(to_px(*back(x, y))) - [x0, y0]) for x, y in g.exterior.coords], fill=1)
        for hole in g.interiors: d.polygon([tuple(np.array(to_px(*back(x, y))) - [x0, y0]) for x, y in hole.coords], fill=0)
    mk = np.asarray(mask, dtype=bool); sub = dark[y0:y1, x0:x1]
    return round(float(sub[mk].mean()), 3), round(float(np.abs(np.diff((sub & mk).astype(int), axis=1)).sum() / max(mk.sum(), 1)), 3)
cands, hatched = [], []
for key in ['b6', 'b7', 'b8']:
    m = json.load(open(P / f'{key}-match.json'))
    for bid, b in sorted(m['buildings'].items()):
        if not b['symbolObject'] or '1968' not in b['editions']:
            continue
        o = O[bid]; first = o['states'][0]
        if first['from'] <= 1968 or first['state'] not in ('occupied', 'standing'):
            continue
        e = b['editions']['1968']; pt = Point(toM(*cv[1968][3](*e['pixel'])))
        if any(a.contains(pt) for a in areas):
            continue
        share, stripes = surroundings(o, e['shift'])
        if share > 0.40 or stripes > 0.22:
            hatched.append(dict(objectId=bid, batch=key, darkShare=share, stripeDensity=stripes)); continue
        cands.append(dict(objectId=bid, batch=key, originalFrom=first['from'], pixel=e['pixel'], shift=e['shift'],
                          distanceAfterShift=e['distanceAfterShift'], symbolAreaPx=e['symbolAreaPx'],
                          matched1985='1985' in b['editions'], matched1995='1995' in b['editions']))
json.dump(dict(candidates=cands, hatched=hatched), open(P / 'sym-candidates.json', 'w'), indent=1)
scans = {y: Image.open(f'data/map-scan-cache/101208_{y}.jpg').convert('RGB') for y in (1968, 1985, 1995)}
HALF, S = 30, 5; cells = []
for n, c in enumerate(cands):
    o = O[c['objectId']]; ring = [toM(*p) for p in G[o['geometryPeriods'][0]['geometryId']]['paths'][0]]
    cx = sum(p[0] for p in ring) / len(ring); cy = sum(p[1] for p in ring) / len(ring); panels = []
    for y in (1968, 1985, 1995):
        sh = c['shift'] if y == 1968 else [0, 0]; to_px = cv[y][2]
        ctr = to_px(*back(cx + sh[0], cy + sh[1])); r = HALF / 1.68
        x0, y0, x1, y1 = int(ctr[0] - r), int(ctr[1] - r), int(ctr[0] + r), int(ctr[1] + r)
        im = scans[y].crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS); dr = ImageDraw.Draw(im)
        xy = [tuple((np.array(to_px(*back(px + sh[0], py + sh[1]))) - [x0, y0]) * S) for px, py in ring]
        dr.line(xy + [xy[0]], fill=(0, 160, 255), width=2)
        if y == 1968:
            u, v = (np.array(c['pixel']) - [x0, y0]) * S; dr.ellipse([u - 4, v - 4, u + 4, v + 4], outline=(255, 0, 255), width=2)
        dr.rectangle([0, 0, 70, 14], fill='black'); dr.text((3, 2), f'{n} {y}', fill='yellow'); panels.append(im)
    w = sum(p.width + 4 for p in panels); cell = Image.new('RGB', (w, panels[0].height), 'white'); x = 0
    for p in panels: cell.paste(p, (x, 0)); x += p.width + 4
    cells.append(cell)
COLS, ROWS = 3, 6
for s in range(0, len(cells), COLS * ROWS):
    chunk = cells[s:s + COLS * ROWS]; cw, ch = chunk[0].width + 10, chunk[0].height + 10
    sheet = Image.new('RGB', (cw * COLS, ch * ((len(chunk) + COLS - 1) // COLS)), 'white')
    for i, c in enumerate(chunk): sheet.paste(c, ((i % COLS) * cw, (i // COLS) * ch))
    sheet.save(P / f'sym-contact-{s // (COLS * ROWS)}.jpg', quality=85)
print(len(cands), 'candidates,', len(hatched), 'hatched', (len(cells) + COLS * ROWS - 1) // (COLS * ROWS), 'sheets')
