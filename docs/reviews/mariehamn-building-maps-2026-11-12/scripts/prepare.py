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
NOTE = {'present': 'Hussymbol på grundkartan i samma läge som dagens byggnad (efter lokal registreringsjustering).',
        'unclear': 'Ingen säker symbol hittades i denna utgåva, men huset finns både 1968 och 1995; kontinuitet antas.',
        'absent': 'Ingen hussymbol i läget.'}
BASIS = ('Hussymbolen på grundkartan 101208 tolkas som samma byggnad som dagens inmätta kontur, utifrån läge efter lokal '
         'registreringsjustering, storlek och grannhusen i samma rad. Kartåret är första granskade belägg, inte byggår. '
         'Kontinuitet till dagens kontur antas; äldre takform, tillbyggnader och en möjlig ersättning på samma tomt är inte fastställda.')
decisions, deferred, sources = [], {}, {}
for key in keys:
    m = json.load(open(HERE / f'{key}-match.json')); verdict = json.load(open(HERE / f'{key}-verdict.json'))
    fills = json.load(open(HERE / f'{key}-fills.json'))
    for y in ['1968', '1978', '1985', '1995']:
        sources[y] = m['editions'][y]['sourceId']
    for bid, v in sorted(verdict.items()):
        if v not in ('1968', '1985', '1995'):
            deferred.setdefault(v, []).append(bid); continue
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
review = dict(schemaVersion=1, reviewedAt='2026-11-12',
              source=dict(id='review:mariehamn-building-maps', title='Mariehamns byggnader · hussymboler på kartbladet 101208 1968–1995', url='assets/mariehamn-building-maps.json'),
              sheets={y: s for y, s in sources.items()},
              rules=dict(minAreaSquareMeters=40, matchLimitMeters=9, fillLimitMeters=14, sizeRatio=3, maxRawSymbolDistanceMeters=30,
                         roadRevision1978='1978 är en vägrevision på 1968 års underlag och används inte som eget byggnadsbelägg.'),
              method=__doc__.split('Run from')[0].strip(),
              decisions=decisions,
              deferred={k: sorted(v) for k, v in sorted(deferred.items())},
              reviewSheets=[dict(file=p.name, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(HERE.glob('*-sheet-*.jpg'))])
review['totals'] = dict(buildings=len(decisions), byFirstYear={str(y): sum(d['firstYear'] == y for d in decisions) for y in YEARS},
                        deferred={k: len(v) for k, v in review['deferred'].items()})
Path('data/mariehamn-building-maps.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(review['totals'])
