"""Builds data/mariehamn-building-maps.json: Mariehamn buildings dated from the house symbols on sheet 101208.

Retained for audit; it captures input fingerprints from the pre-review snapshot (before.json.gz), so rerunning it
after inputs change silently re-baselines the review. The compiler (scripts/mariehamn_building_maps.py) rejects
changed inputs instead.

Method (match.py, verdict.py, sheets.py in this folder): dark filled house symbols were detected on the 1968, 1978,
1985 and 1995 scans, each modern outline (at least 40 m²) was matched one-to-one to a symbol within 9 m after a local
registration shift, and every tile was then checked visually on the review sheets (KEY-sheet-*.jpg). Dating rules:
- 1978 is a road revision on the 1968 base and is not independent building evidence;
- a building starts at the first of 1968/1985/1995 with a matched symbol and must be matched in every later one;
  a house shown in 1968 and 1995 whose 1985 symbol is not found keeps 1968 with 1985 recorded as unclear;
- a building much larger than the symbol it sits on (more than 3x the drawn area) is not matched to it;
- a later start is deferred if the previous edition shows hatched or stippled drawing inside the outline.
Every proposal was then checked on contact sheets (contact.py: each building at high zoom in the previous and the
first edition, or 1985 and 1968 for 1968 starts). Rejections are recorded per batch in KEY-overrides.json with a
reason: an empty outline matched to a neighbour, a shoreline, pier, line or lettering match, an ambiguous partial
overlap, or an earlier hollow, hatched, offset or text-covered drawing that could make a later start too late.
Map years are first evidence, never construction years.

Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/mariehamn-buildings/prepare.py b1
"""
import gzip, hashlib, json, sys
from pathlib import Path

HERE = Path('data/map-scan-cache/review/mariehamn-buildings')
keys = sys.argv[1:] or ['b1']
r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
catalog = r(str(HERE / 'before.json.gz')); O = {o['id']: o for o in catalog['objects']}
G = {g['id']: g for g in catalog['geometries']}
sys.path.insert(0, 'scripts')
from mariehamn_building_maps import pixel_converters
from shapely.geometry import Polygon, Point
from pyproj import Transformer
TO_M = Transformer.from_crs(4326, 3874, always_xy=True).transform; TO_PX = pixel_converters(r)
digest = lambda v: hashlib.sha256(json.dumps(v, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
fingerprint = lambda o: digest({k: o.get(k) for k in ['id', 'kind', 'states', 'geometryPeriods', 'sourceLinks', 'reconstruction']})
YEARS = [1968, 1985, 1995]
CURATED = ['historicalReview', 'museumReview', 'printedMapSymbol', 'neighborhoodReviews']
NOTE = {'present': 'Hussymbol på grundkartan i samma läge som dagens byggnad (efter lokal registreringsjustering).',
        'unclear': 'Ingen säker symbol hittades i denna utgåva, men huset finns både 1968 och 1995; kontinuitet antas.',
        'absent': 'Ingen hussymbol i läget.'}
BASIS = ('Hussymbolen på grundkartan 101208 tolkas som samma byggnad som dagens inmätta kontur, utifrån läge efter lokal '
         'registreringsjustering, storlek och grannhusen i samma rad. Kartåret är första granskade belägg, inte byggår. '
         'Kontinuitet till dagens kontur antas; äldre takform, tillbyggnader och en möjlig ersättning på samma tomt är inte fastställda.')
decisions, deferred, sources, rejections = [], {}, {}, {}
# Recheck r1 (recheck.py, recheck-earlier-unclear-NN.jpg): every 'earlier-unclear' building was judged on all three
# editions. P: the earlier ink is lettering, lines, an area fill or block hatching, so the proposed edition stands;
# E1968/E1985: that edition already draws the same building (hatched, stippled, hollow or a symbol the detector
# missed), so the building starts there; U: unclear, stays deferred. A visually confirmed edition records the scan
# pixel of the shifted outline's centre. An earlier edition whose surroundings are block-hatched is 'unclear', not
# 'absent'.
# Recheck r2 (recheck-inconsistent-NN.jpg): every 'inconsistent' building (a symbol missing in a later edition) was
# judged the same way. E1968/E1985: that edition and every later one draw the same building (the later symbol was
# missed, set aside by the size rule, or drawn hatched or hollow); U: a later edition lacks it or shows another
# building, a 1968 hatched block, quays, unclear.
recheck = {}
for rkey, kind in (('r1', 'earlier-unclear'), ('r2', 'inconsistent')):
    if rkey in keys:
        codes = json.load(open(HERE / f'recheck-{kind}-decisions.json'))
        for n, it in enumerate(json.load(open(HERE / f'recheck-{kind}.json'))):
            recheck[it['objectId']] = (it, codes[str(n)], rkey, kind)
NOTE['visual'] = 'Byggnaden är ritad på kartan i samma läge (streckad, prickad, ihålig eller som en symbol som den automatiska sökningen missade); visuellt granskad.'
NOTE['hatched'] = 'Kvarteret är streckat som bebyggt område; enskilda hus kan inte urskiljas, så utgåvan ger varken belägg för eller emot huset.'
for key in [k for k in keys if k not in ('r1', 'r2')]:
    m = json.load(open(HERE / f'{key}-match.json')); verdict = json.load(open(HERE / f'{key}-verdict.json'))
    fills = json.load(open(HERE / f'{key}-fills.json'))
    overrides = json.load(open(HERE / f'{key}-overrides.json')) if (HERE / f'{key}-overrides.json').exists() else {}
    for y in ['1968', '1978', '1985', '1995']:
        sources[y] = m['editions'][y]['sourceId']
    for bid, v in sorted(verdict.items()):
        if bid in recheck and recheck[bid][3] == v and recheck[bid][1] != 'U':
            continue  # decided by the r1/r2 recheck below
        if v not in ('1968', '1985', '1995'):
            deferred.setdefault(v, []).append(bid); continue
        if bid in overrides:
            deferred.setdefault('visual-reject', []).append(bid)
            x = overrides[bid]; group = x['contactSheet'].rsplit('-', 1)[1]
            rejections[bid] = dict(batch=key, proposedFirstYear=int(v), **x, sheetFile=f"{key}-contact-{x['cell'] // 20}-{group}.jpg"); continue
        if any(O[bid].get(k) for k in CURATED):
            # A curated history or symbol review decides this building's dates; the map review does not override it.
            deferred.setdefault('curated-review', []).append(bid); continue
        if not O[bid].get('reconstruction'):
            # Modern-only outlines (externalModern) are not part of the reconstructed city building set; an earlier
            # start would need that model first, so the map evidence is not applied.
            deferred.setdefault('external-modern', []).append(bid); continue
        o = O[bid]; b = m['buildings'][bid]; first = int(v); obs = []
        for y in YEARS:
            e = b['editions'].get(str(y)) or fills.get(bid, {}).get(str(y))
            if y < first:
                obs.append(dict(year=y, sourceId=sources[str(y)], outcome='absent', note=NOTE['absent'])); continue
            if e and e.get('unclear'):
                obs.append(dict(year=y, sourceId=sources[str(y)], outcome='unclear', note=NOTE['unclear'])); continue
            assert e, (bid, y)
            obs.append(dict(year=y, sourceId=e['sourceId'], outcome='present', pixel=e['pixel'], shiftMeters=e['shift'],
                            distanceAfterShiftMeters=e['distanceAfterShift'], fillPass=bool(e.get('filled')), note=NOTE['present']))
        # The dated period shows the earliest measured outline; every symbol must also match that outline.
        ref = Polygon([TO_M(*p) for p in G[o['geometryPeriods'][0]['geometryId']]['paths'][0]])
        if any(x['outcome'] == 'present' and Polygon([(px + x['shiftMeters'][0], py + x['shiftMeters'][1]) for px, py in ref.exterior.coords]).distance(
                Point(*TO_PX[x['sourceId']](x['pixel']))) > (14 if x['fillPass'] else 9) for x in obs):
            deferred.setdefault('outline-changed', []).append(bid); continue
        decisions.append(dict(objectId=bid, input=fingerprint(o), referenceGeometryId=o['geometryPeriods'][0]['geometryId'],
                              originalFrom=o['states'][0]['from'], firstYear=first, areaSquareMeters=b['area'],
                              batch=key, observations=obs, basis=BASIS))
if recheck:
    import importlib.util, numpy as np
    from PIL import Image, ImageDraw
    spec = importlib.util.spec_from_file_location('conv', HERE / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
    back = Transformer.from_crs(3874, 4326, always_xy=True).transform
    to_px = {y: conv.converters(y)[2] for y in YEARS}
    dark68 = None
    def hatched(poly, sh):
        global dark68
        if dark68 is None:
            a68 = np.asarray(Image.open('data/map-scan-cache/101208_1968.jpg').convert('RGB'), dtype=float)
            dark68 = (a68.mean(axis=2) < 150) & ((a68.max(axis=2) - a68.min(axis=2)) < 80)
        moved = Polygon([(x + sh[0], y + sh[1]) for x, y in poly.exterior.coords]); ring = moved.buffer(14).difference(moved.buffer(5))
        geoms = list(getattr(ring, 'geoms', [ring])); pts = [to_px[1968](*back(x, y)) for g in geoms for x, y in g.exterior.coords]
        x0, y0 = np.floor(np.min(pts, axis=0)).astype(int) - 1; x1, y1 = np.ceil(np.max(pts, axis=0)).astype(int) + 2
        mk = Image.new('L', (x1 - x0, y1 - y0), 0); d_ = ImageDraw.Draw(mk)
        for g in geoms:
            d_.polygon([tuple(np.array(to_px[1968](*back(x, y))) - [x0, y0]) for x, y in g.exterior.coords], fill=1)
            for h in g.interiors: d_.polygon([tuple(np.array(to_px[1968](*back(x, y))) - [x0, y0]) for x, y in h.coords], fill=0)
        mk = np.asarray(mk, dtype=bool); sub = dark68[y0:y1, x0:x1] & mk
        return np.abs(np.diff(sub.astype(int), axis=1)).sum() / max(mk.sum(), 1) > 0.22
    for bid, (it, code, rkey, kind) in sorted(recheck.items()):
        if code == 'U':
            continue
        key = it['batch']; m = json.load(open(HERE / f'{key}-match.json')); fills = json.load(open(HERE / f'{key}-fills.json'))
        o = O[bid]; b = m['buildings'][bid]; sources.update({y: m['editions'][y]['sourceId'] for y in ['1968', '1978', '1985', '1995']})
        ref = Polygon([TO_M(*p) for p in G[o['geometryPeriods'][0]['geometryId']]['paths'][0]])
        sized = [int(y) for y, x in b['editions'].items() if y != '1978' and b['area'] <= 3.0 * x['symbolAreaPx'] * 1.68 * 1.68]
        first = int(code[1:]) if code.startswith('E') else min(sized)
        obs = []
        for y in YEARS:
            sh = b.get('shifts', {}).get(str(y), [0, 0]); e = b['editions'].get(str(y)) or fills.get(bid, {}).get(str(y))
            if y < first:
                if y == 1968 and hatched(ref, sh):
                    obs.append(dict(year=y, sourceId=sources[str(y)], outcome='unclear', reason='hatched-block', note=NOTE['hatched']))
                else:
                    obs.append(dict(year=y, sourceId=sources[str(y)], outcome='absent', note=NOTE['absent']))
                continue
            # A detected symbol is recorded as such; for a visually confirmed building (E) a symbol the size rule set aside is kept too.
            if e and not e.get('unclear') and (y in sized or e.get('filled') or code.startswith('E')):
                obs.append(dict(year=y, sourceId=e['sourceId'], outcome='present', pixel=e['pixel'], shiftMeters=e['shift'],
                                distanceAfterShiftMeters=e['distanceAfterShift'], fillPass=bool(e.get('filled')), note=NOTE['present']))
            else:
                c = ref.centroid; px = [round(float(v), 2) for v in to_px[y](*back(c.x + sh[0], c.y + sh[1]))]
                obs.append(dict(year=y, sourceId=sources[str(y)], outcome='present', pixel=px, shiftMeters=sh, distanceAfterShiftMeters=0.0,
                                fillPass=False, visualReview=True, note=NOTE['visual']))
        decisions.append(dict(objectId=bid, input=fingerprint(o), referenceGeometryId=o['geometryPeriods'][0]['geometryId'],
                              originalFrom=o['states'][0]['from'], firstYear=first, areaSquareMeters=b['area'],
                              batch=rkey, recheck=dict(sourceBatch=key, code=code, verdict=kind), observations=obs, basis=BASIS))
review = dict(schemaVersion=1, reviewedAt='2026-11-12',
              source=dict(id='review:mariehamn-building-maps', title='Mariehamns byggnader · hussymboler på kartbladet 101208 1968–1995', url='assets/mariehamn-building-maps.json'),
              sheets={y: s for y, s in sources.items()},
              rules=dict(minAreaSquareMeters=40, matchLimitMeters=9, fillLimitMeters=14, sizeRatio=3, maxRawSymbolDistanceMeters=30, symbolObjectOverlapSquareMeters=5,
                         roadRevision1978='1978 är en vägrevision på 1968 års underlag och används inte som eget byggnadsbelägg.'),
              method=__doc__.split('Run from')[0].strip(),
              decisions=decisions,
              deferred={k: sorted(v) for k, v in sorted(deferred.items())},
              visualRejections=dict(sorted(rejections.items())),
              reviewSheets=[dict(file=p.name, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                            for p in sorted([*HERE.glob('*-sheet-*.jpg'), *HERE.glob('*-contact-*.jpg')]) if p.name.split('-')[0] in keys])
review['totals'] = dict(buildings=len(decisions), byFirstYear={str(y): sum(d['firstYear'] == y for d in decisions) for y in YEARS},
                        deferred={k: len(v) for k, v in review['deferred'].items()})
Path('data/mariehamn-building-maps.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(review['totals'])
