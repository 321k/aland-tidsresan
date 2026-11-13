"""Writes data/mariehamn-building-photos.json: buildings with no symbol on sheet 101208 dated from Mariehamn's
orthophotos (1991, 1999, 2007, 2015; 1 m/px tiles from the town's map service, cached with sha256 in tiles.json).

Method: sheets.py draws every such building of a building-map batch on the four photos with its outline; each was
judged by eye (KEY-decisions.json): Y<year> = the first photo that shows the building, every later photo shows it;
N = not shown on any photo (built after 2015), unclear, or under 40 m² (too small to judge at 1 m/px). guard.py then
defers a building first seen in 1991 (1999) whose outline is dark on the 1985 (1995) map, where the map may already
draw it. An earlier photo that covers the spot without the building is 'absent'; one that does not cover it is
'not-covered'. The photo year is first evidence, not a construction year.
Retained for audit; it fingerprints the catalogue as it was before this step (photos-before.json.gz in this folder).
Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/photo-dating/prepare.py p10 [KEY ...]
"""
import gzip, json, sys
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import Polygon
sys.path.insert(0, 'scripts')
from mariehamn_building_photos import fingerprint
P = Path('data/map-scan-cache/review/photo-dating'); keys = sys.argv[1:]
cat = json.loads(gzip.decompress((P / 'photos-before.json.gz').read_bytes())); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
T = Transformer.from_crs(4326, 3874, always_xy=True).transform
tiles = json.load(open(P / 'tiles.json')); YEARS = [1991, 1999, 2007, 2015]
NOTE = {'present': 'Byggnaden syns på flygfotot i samma läge som dagens kontur.',
        'absent': 'Flygfotot visar platsen utan byggnaden.'}
BASIS = ('Byggnaden saknas på grundkartorna 1968–1995 och syns första gången på flygfotot {year}, i samma läge som dagens inmätta '
         'kontur och på alla senare granskade flygfoton. Fotoåret är första belägg, inte byggår; den senare konturen används med antagen '
         'formkontinuitet.')
decisions, deferred = [], {}
for key in keys:
    items = json.load(open(P / f'{key}.json')); dec = json.load(open(P / f'{key}-decisions.json'))
    guard = json.load(open(P / f'{key}-guard.json'))
    for n, it in enumerate(items):
        code = dec[str(n)]; bid = it['objectId']
        if code == 'N':
            deferred.setdefault('no-photo-evidence', []).append(bid); continue
        if guard.get(str(n), {}).get('deferred'):
            deferred.setdefault('map-ink', []).append(bid); continue
        o = O[bid]; first = int(code[1:])
        if first >= o['states'][0]['from']:
            deferred.setdefault('not-earlier', []).append(bid); continue
        poly = Polygon([T(*q) for q in G[o['geometryPeriods'][0]['geometryId']]['paths'][0]]); c = poly.centroid
        if poly.area < 40:  # the earliest outline, which the dated period shows, is below the reviewed size
            deferred.setdefault('below-size', []).append(bid); continue
        obs = []
        for y in YEARS:
            covered = tiles.get(f'ortho-{y}-17-{int(c.x // 256)}-{int(c.y // 256)}.png') is not None
            if y >= first:
                assert covered, (bid, y)
                obs.append(dict(year=y, outcome='present', note=NOTE['present']))
            else:
                obs.append(dict(year=y, outcome='absent', note=NOTE['absent']) if covered else dict(year=y, outcome='not-covered'))
        decisions.append(dict(objectId=bid, input=fingerprint(o), referenceGeometryId=o['geometryPeriods'][0]['geometryId'],
                              originalFrom=o['states'][0]['from'], firstYear=first, areaSquareMeters=round(poly.area), batch=key,
                              sourceBatch=it['batch'], observations=obs, basis=BASIS.format(year=first)))
review = dict(schemaVersion=1, reviewedAt='2026-11-13',
              source=dict(id='review:mariehamn-building-photos', title='Mariehamns byggnader · daterade från flygfoton 1991–2015',
                          url='assets/mariehamn-building-photos.json'),
              photoYears=YEARS, minAreaSquareMeters=40, method=__doc__.split('Retained for')[0].strip(),
              decisions=decisions, deferred={k: sorted(v) for k, v in sorted(deferred.items())},
              tiles=dict(sorted((k, v) for k, v in tiles.items() if v is not None)))
review['totals'] = dict(buildings=len(decisions), byFirstYear={str(y): sum(d['firstYear'] == y for d in decisions) for y in YEARS},
                        deferred={k: len(v) for k, v in review['deferred'].items()})
Path('data/mariehamn-building-photos.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(review['totals'])
