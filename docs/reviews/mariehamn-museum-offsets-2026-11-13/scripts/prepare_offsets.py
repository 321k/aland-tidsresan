"""Writes data/mariehamn-museum-offsets.json: the second pass over every museum-map house still open after the overlap
review (open_sheets.py, open-NN.jpg; open-index.json numbers the neighbours; open_ink.py measures each footprint).

The museum map is often shifted about a house depth, mostly northwards, so a museum house can stand in a street, front
garden or yard next to its house without overlapping it. Each house was judged on the 1942 orthophoto and the 1968
and 1985 editions of sheet 101208:
- merge: the 1942 photo shows a house at a directly neighbouring later outline and none at the museum spot; the later
  object takes over the museum record (two museum houses may join one longer building);
- ending: the museum footprint is empty on the 1985 map (dark share at most 0.3; the 1995 share is recorded; 1968 where that
  edition draws the spot empty and unhatched) and no neighbour is clearly the same house; the house ends at the map's
  survey year, the latest boundary, not a demolition year;
- deferred: the photo and maps do not settle it, a footprint carries street lines, or the neighbour is a curated
  history building without a reconstruction record.
Retained for audit; it fingerprints the catalogue as it was before this pass (offsets-before.json.gz in this folder).
Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/museum-duplicates/prepare_offsets.py
"""
import gzip, json, sys
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import Polygon
sys.path.insert(0, 'scripts')
from mariehamn_museum_duplicates import fingerprint
P = Path('data/map-scan-cache/review/museum-duplicates')
cat = json.loads(gzip.decompress((P / 'offsets-before.json.gz').read_bytes())); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
T = Transformer.from_crs(4326, 3874, always_xy=True).transform
poly = lambda i: Polygon([T(*q) for q in G[O[i]['geometryPeriods'][-1]['geometryId']]['paths'][0]]).buffer(0)
ink = {v['museum']: v for v in json.load(open(P / 'open-ink.json')).values()}
sheets = json.load(open('data/mariehamn-building-maps.json'))['sheets']
MUS, SYM, OSM = 'building:museum:', 'map-building:nls-symbol-', 'building:osm:way-'
merges = {41: SYM + '392', 42: SYM + '392', 43: SYM + '414', 47: SYM + '384', 54: SYM + '439', 69: SYM + '446', 95: OSM + '166517479',
          96: SYM + '401', 113: SYM + '514', 136: SYM + '498', 138: OSM + '165436732', 139: SYM + '492', 140: SYM + '501',
          143: OSM + '496985040', 149: SYM + '489', 150: SYM + '489', 152: SYM + '487', 155: SYM + '504', 165: SYM + '569',
          168: SYM + '599', 170: SYM + '590', 175: SYM + '650', 178: OSM + '331981628', 209: SYM + '643'}
end1985 = [2, 13, 16, 52, 58, 59, 61, 68, 109, 114, 115, 117, 141, 148, 153, 156, 157, 163, 166, 169, 173, 176, 177, 179, 180, 182,
           192, 196, 205, 206, 207, 210, 211]
end1968 = []  # museum 2's courtyard is also empty on 1968, but every 1920 house shown in 1967 stays at the 1968 stage boundary
deferred = {'unclear': [5, 8, 11, 34, 48, 55, 56, 74, 103, 104, 105, 119, 142, 213], 'street-lines-in-footprint': [116, 186],
            'history-building-without-reconstruction': [158]}
MERGE = ('Museikartans hus och den intilliggande senare byggnaden tolkas som samma hus. Museikartan är här förskjuten omkring ett husdjup: '
         'museikartans kontur ligger i {where}, {gap} meter från den senare konturen, och flygfotot 1942 visar huset där den senare konturen '
         'ligger men inget hus på museikartans plats. Den senare uppmätta konturen används från museikartans 1920-tal; detta är ett '
         'kontinuitetsantagande, inte ett fastställt byggår.')
END = ('Museikartans hus har ingen tydlig motsvarighet bland grannhusen, och grundkartan {map} visar platsen tom. Husets antagna '
       'fortsättning avslutas därför senast {year}, kartans inventeringsår. Huset kan ha rivits tidigare eller vara felplacerat på '
       'museikartan; {year} är den senaste gränsen, inte ett rivningsår.')
start = lambda o: o['states'][0]['from']
inputs, out_m, out_e = {}, [], []
for m, keep in sorted(merges.items()):
    donor = MUS + str(m); a, b = poly(donor), poly(keep); gap = round(a.distance(b), 1)
    inputs[donor] = fingerprint(O[donor]); inputs[keep] = fingerprint(O[keep])
    where = 'gatan eller förgården' if a.centroid.y > b.centroid.y else 'gården'
    out_m.append(dict(id=f'museum-{m}', keep=keep, donor=donor, fromYear=start(O[donor]), keepFrom=start(O[keep]), gapMeters=gap,
                      offsetMeters=[round(b.centroid.x - a.centroid.x, 1), round(b.centroid.y - a.centroid.y, 1)],
                      basis=MERGE.format(where=where, gap=gap)))
for m in end1985 + end1968:
    museum = MUS + str(m); inputs[museum] = fingerprint(O[museum]); i = ink[museum]
    if m in end1968:
        d = dict(mapYear=1968, endYear=1968, sourceId=sheets['1968'], darkShare=i['d1968'])
    else:
        assert i['d1985'] <= 0.3, (m, i)  # 1995 is recorded only: a newer house may stand on the spot by then
        d = dict(mapYear=1985, endYear=1983, sourceId=sheets['1985'], darkShare=i['d1985'], darkShare1995=i['d1995'])
    out_e.append(dict(id=f'museum-{m}', museum=museum, **d, basis=END.format(map=d['mapYear'], year=d['endYear'])))
review = dict(schemaVersion=1, reviewedAt='2026-11-13',
              source=dict(id='review:mariehamn-museum-offsets', title='Mariehamns museikartehus · förskjutna dubbletter och försvunna hus',
                          url='assets/mariehamn-museum-offsets.json'),
              aerialSourceId='mariehamn-aerial-1942', mergeRule='adjacent', maxGapMeters=12, maxCentroidMeters=35, maxDarkShare=0.3,
              marker='museumOffsetReview', method=__doc__.split('Retained for')[0].strip(), merges=out_m, replacements=[], endings=out_e,
              deferred={k: [MUS + str(m) for m in v] for k, v in deferred.items()}, inputs=dict(sorted(inputs.items())))
all_ = sorted(list(merges) + end1985 + end1968 + [m for v in deferred.values() for m in v])
assert all_ == sorted(int(v['museum'].split(':')[-1]) for v in ink.values()), 'every open museum house is decided'
Path('data/mariehamn-museum-offsets.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(len(out_m), 'merges into', len(set(merges.values())), 'houses,', len(out_e), 'endings,', sum(map(len, deferred.values())), 'deferred')
print('max gap', max(m['gapMeters'] for m in out_m), 'max centroid', max((m['offsetMeters'][0] ** 2 + m['offsetMeters'][1] ** 2) ** .5 for m in out_m))
