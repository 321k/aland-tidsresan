"""Capture the catalogue right before apply_museum_streets and write data/mariehamn-museum-streets.json with fingerprints."""
import json, gzip, sys
sys.path.insert(0, '.')
from pathlib import Path
import mariehamn_museum_streets as ms
from mariehamn_frame_1942 import digest, fingerprint, TO_METRIC
from shapely.geometry import LineString, Point
box = {}
def capture(read, catalog): box['cat'] = json.loads(json.dumps(catalog, ensure_ascii=False))
ms.apply_museum_streets = capture
import build_temporal_objects as t
t.compile_catalog()
cat = box['cat']
O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
grid = json.load(open('../dist/assets/mariehamn-city-grid.json'))
raw = {f['id']: f for s in grid['sets'] for f in s['features']}
setf = {(s['id'], f['id']): f for s in grid['sets'] for f in s['features']}
def stagefeats(trace):
    return [dict(stageId=s['id'], featureId=f['id'], inputHash=digest(f)) for s in cat['cityStages'] for f in s['features'] if f.get('traceId') == trace]
def far(oid, fid):
    L = LineString([TO_METRIC(*p) for p in raw[fid]['paths'][0]]); g = G[O[oid]['geometryPeriods'][0]['geometryId']]
    return round(max(L.distance(Point(TO_METRIC(*p))) for path in g['paths'] for p in path), 1)
HB = ('Museets 1920-talsbild visar "Gata längs västra kvarteren" längs kvarterens västra sida. Flygfotona 1942, 1952 och 1962 '
      'visar där en gata som tomterna vetter mot, i samma läge som grundkartan 1968 och dagens Hamngatan. Avritningen är grov: i norr '
      'ligger den 10–15 meter väster om gatan, genom sjöfartsmuseets tomt, och i söder fortsätter den rakt mot stranden där gatan '
      'svänger mot sydost. Den tolkas som Hamngatan och ersätts i kartan av Hamngatans inmätta mittlinjer; originalspåret bevaras '
      'som källbelägg. 1920 är visningsår för årtiondet, inte öppningsår.')
HN = ('Flygfotot 25 juli 1942 visar gatan längs kvarterens västra sida i samma läge som dagens Hamngatan; fotona 1952 och 1962 '
      'visar samma gata.')
PB = ('Museets 1920-talsbild visar "Gata söderut vid östra stranden" längs parkens västra kant och vidare mot sydost. Flygfotona '
      '1942, 1952 och 1962 visar Parkgatan i båda delarna. Avritningen är grov och ligger 10–14 meter öster om gatan, i parkkanten. '
      'Den tolkas som Parkgatan och ersätts i kartan av Parkgatans inmätta mittlinjer; originalspåret bevaras som källbelägg. '
      '1920 är visningsår för årtiondet, inte öppningsår.')
PN = ('Flygfotot 25 juli 1942 visar Parkgatans sydostliga del genom skogen i samma läge som dagens gata; fotona 1952 och 1962 '
      'visar samma gata.')
ham = ['road:postwar:way-35011941', 'road:postwar:way-392187942', 'road:postwar:way-37210769', 'road:postwar:way-1081060422', 'road:postwar:way-935611737']
park = [('road:postwar:way-39585442', 1942, 'Redan daterad från flygfotot 1942; museibilden ger ett tidigare belägg.'), ('road:mariehamn:major:way-35304989', 1968, PN)]
pieces = []
for ids in [('city-2014-street-2990', 'city-2021-street-3565', 'city-2025-street-3677', 'city-2026-street-3686'),
            ('city-2014-street-122', 'city-2021-street-122', 'city-2025-street-123', 'city-2026-street-123'),
            ('city-2014-street-1200', 'city-2021-street-1211', 'city-2025-street-1221', 'city-2026-street-1221'),
            ('city-2014-street-2984', 'city-2021-street-3559', 'city-2025-street-3671', 'city-2026-street-3680')]:
    feats = [dict(datasetId=f.split('-street')[0], featureId=f) for f in ids]
    hs = {digest(raw[f]['paths']) for f in ids}; assert len(hs) == 1, ids
    pieces.append(dict(pathHash=hs.pop(), features=feats))
for fid, members in [('city-1920-street-37', ham), ('city-1920-street-42', [p[0] for p in park])]:
    print(fid, {m: far(m, fid) for m in members})
review = dict(schemaVersion=1, reviewedAt='2026-11-17',
    source=dict(id='review:mariehamn-museum-streets', title='Hamngatan och Parkgatan · museikartans gator granskade mot flygfoton och grundkartor',
                url='assets/mariehamn-museum-streets.json'),
    museumDatasetId='city-1920', museumYear=1920, aerialSourceId='mariehamn-aerial-1942', photoYear=1942, photoObservedAt='1942-07-25',
    modernSourceId='city-2026',
    mapEvidence=[dict(year=1968, sourceId='nls:91fde6e7-f99c-426a-a739-abaef03455b5'), dict(year=1985, sourceId='nls:91fde6e8-0a89-46fc-83df-2c984ef34f1d')],
    streets=[
     dict(key='hamngatan', featureId='city-1920-street-37', traceId='city-1920-trace-11', inputHash=digest(raw['city-1920-street-37']),
          stageFeatures=stagefeats('city-1920-trace-11'), linkObjectId='road:postwar:way-35011941', maxDistanceMeters=35, basis=HB,
          members=[dict(objectId=m, inputHash=fingerprint(O[m]), originalFrom=1968, note=HN) for m in ham],
          newObjects=[dict(id='road:mariehamn:museum-streets:hamngatan-norra', name='Hamngatan', routeId='road:Hamngatan', modernRoadClass='residential',
                           roadWidth=5, joinsObjectId='road:postwar:way-1081060422', pieces=pieces, photoNote=HN,
                           mapNote=('Grundkartorna 1968 och 1985 ritar gatan från Norragatan längs kvarterens västra sida till Hamngatans korsning. '
                                    'Kartåret är första granskade kartbelägg, inte byggår. Dagens OSM-mittlinje används för hela perioden.'),
                           basis=('Hamngatans norra del, från Norragatan till korsningen, syns på flygfotona 1942–2021 och grundkartorna 1968 och 1985 '
                                  'men saknade objekt; kartan visade gatan först med 2014 års gatunät. Den visas nu från museets 1920-talsbild med dagens '
                                  'mittlinje. Museets, fotots och kartans år är belägg, inte byggår.'))]),
     dict(key='parkgatan', featureId='city-1920-street-42', traceId='city-1920-trace-18', inputHash=digest(raw['city-1920-street-42']),
          stageFeatures=stagefeats('city-1920-trace-18'), linkObjectId='road:postwar:way-39585442', maxDistanceMeters=35, basis=PB,
          members=[dict(objectId=m, inputHash=fingerprint(O[m]), originalFrom=f, note=n, **({'museumRange': [0, 0.637], 'cutLatitude': 60.0925} if m.endswith('35304989') else {})) for m, f, n in park])])
Path('../data/mariehamn-museum-streets.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print('written', [len(s['stageFeatures']) for s in review['streets']])
