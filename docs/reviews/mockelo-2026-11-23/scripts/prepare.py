"""Write data/mockelo-road.json and data/mockelo-road-early.json. Usage: prepare.py CATALOGUE_BEFORE.json.gz

Read on ../renders (grid 100 m, EPSG:3874, OSM green, catalogue red):
- m-k1928.jpg, m-k1953.jpg: the 1928 sheet 1012 05 and its 1953 Kungsö edition draw the road from the sheet edge at
  Svibyviken south-west to the corner at Gustavsberg, and on past Pellas, Södergård, Lunden, Strömbäck and Sunnvik to
  Möckelö; today's Möckelövägen (dated from 1978, as sheet 1012 05 has no 1968 base map) follows it within 10–20 m.
- z-sheet.jpg, e-sheet.jpg: the road from Norra Möckelövägen's south end along the shore and south-west to Möckelövägen
  is on the 1928 and 1953 sheets (west of the seam), the 1929 sheet and its 1948 edition (east of it, the shore part),
  the base map 1968 ("t. Möckelö") and the base map 1978 (1012 05). Today: the cycleways across Hammarlandsvägen,
  Lönnelundsgatan and the first way of Möckelövägen, which no object owns."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest
from hammarlandsvagen_main_road import metric, SNAPSHOTS
from sviby_connections import _piece
from mockelo_road import apply_mockelo_road, EARLY, MAIN

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
NM, MV, ID = 'road:mariehamn:major-followup:norra-mockelovagen', 'road:qgis:gottby:mockelovagen-100km5', 'road:jomala:mockelovagen:lonnelund'
F = {ds: {x['id']: x for x in json.load(gzip.open(f))['features']} for ds, (f, _) in SNAPSHOTS.items()}
own = {(l['datasetId'], l['featureId']): l['sourceVertexRange'] for l in O[MV]['sourceLinks'] if l.get('sourceVertexRange')}
r = lambda x: round(x, 1)
basis_link = 'Vägen från Norra Möckelövägen längs stranden och Lönnelundsgatan till Möckelövägen, som den kartlagts detta år.'

def links(spec):
    out = []
    for ds, fid, rng, rev in spec:
        if fid not in F[ds]:
            continue                                            # not in this extract
        p = F[ds][fid]['paths'][0]; a, b = rng if rng else (0, len(p) - 1)
        out.append(dict(datasetId=ds, featureId=fid, sourceVertexRange=[a, b], sourceVertexCount=len(p), input=digest(F[ds][fid]['paths']), basis=basis_link,
                        **({'reverse': True} if rev else {})))
    return out

spec = []
for ds, pre in (('osm-2026', 'way/'), ('osm-2025', 'road-2025-'), ('osm-2021', 'road-2021-'), ('osm-2014', 'road-2014-')):
    for w, rev in (('1066273699', True), ('1193325547', True), ('1066273700', True), ('54446881', True), ('35105818', True), ('166080087', True), ('35105743', True), ('166080081', False)):
        fid = pre + w
        rng = [0, own[(ds, fid)][0]] if (ds, fid) in own else None
        spec.append((ds, fid, rng, rev))
ls = links(spec)
built = []
for l in [x for x in ls if x['datasetId'] == 'osm-2026']:
    part = _piece(F['osm-2026'][l['featureId']]['paths'][0], *l['sourceVertexRange'], l.get('reverse', False))
    built += part[1:] if built and built[-1] == part[0] else part
print('link', r(metric(built).length), 'm;', len(ls), 'source links:', sorted({(l['datasetId'], l['featureId'].split('-')[-1].split('/')[-1]) for l in ls}))

L = {'1928-hammarudda': dict(sourceId='nls:9c76c491-898b-4b0b-9331-7af223831264', year=1928), '1929-mariehamn': dict(sourceId='nls:9c76c492-0456-43c6-9478-b2aa0034b26c', year=1929),
     '1944-kungso': dict(sourceId='nls:9c72a692-458e-4804-af82-e6ac6dbf73fe', year=1944), '1948-mariehamn': dict(sourceId='nls:9c72a694-1238-40a8-a8ca-33c754332810', year=1948),
     '1953-kungso': dict(sourceId='nls:9c72a692-80ff-433c-950e-1cf484176101', year=1953), '1968-mariehamn': dict(sourceId='nls:101208:1968', year=1968),
     '1978-gottby': dict(sourceId='nls:101205:1978', year=1978)}
method = 'Kartorna har lagts över varandra och över dagens vägar med ett rutnät på 100 m. Bladen 1012 05 (Kungsö) och 1012 08 (Mariehamn) möts vid E 20 495 400; vägen korsar skarven vid Lönnelund.'
review = dict(
    schemaVersion=1, reviewedAt='2026-11-23', method=method, maps=L, stagePrefix='mockelo-road',
    source=dict(id='review:mockelo-road', title='Vägen från Svibyviken till Möckelö på sockenkartorna 1928 och 1929 · granskning', url='assets/mockelo-road.json'),
    surveySources=[dict(id=ID + ':survey', title='OpenStreetMap · Lönnelundsgatan och gång- och cykelvägen till Norra Möckelövägen', url='https://www.openstreetmap.org/way/166080087', issuedAt='2026')],
    newRoads=[dict(id=ID, name='Möckelövägen · vid Lönnelund', routeId='road:route:mockelovagen', modernRoadClass='residential', roadWidth=4, firstYear=1928, surveySourceId=ID + ':survey',
                   maps={k: 'present' for k in L}, start=NM, end=MV, joinMeters=1, paths=[built], sourceLinks=ls,
                   basis='Vägen från Svibyviken till Möckelö: från Norra Möckelövägens södra ände söderut längs stranden och sedan åt sydväst till Möckelövägen. Sockenkartan 1928 och utgåvorna 1944 och 1953 (Kungsö) ritar delen väster om bladskarven, sockenkartan 1929 och utgåvan 1948 (Mariehamn) delen längs stranden, och grundkartorna 1968 ("t. Möckelö") och 1978 hela vägen. Hammarlandsvägen korsar den sedan 1960-talet. I dag är den Lönnelundsgatan och gång- och cykelvägen över Hammarlandsvägen.',
                   geometryNote='Mittlinjen i OpenStreetMap 2026 (åtta vägar i följd), använd som stabilt läge från 1928. Kartornas väg ligger inom 20–35 m.')])
json.dump(review, open(MAIN, 'w'), ensure_ascii=False, indent=1)

g = G[O[MV]['geometryPeriods'][0]['geometryId']]; ml = metric(g['paths'][0])
early = dict(schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:mockelo-road-1928:',
             source=dict(id='review:mockelo-road-early', title='Möckelövägen på sockenkartan 1928 · granskning', url='assets/mockelo-road-early.json'),
             sources=[], maps={k: L[k] for k in ('1928-hammarudda', '1944-kungso', '1953-kungso')}, method=method,
             early=[dict(objectId=MV, inputHash=fingerprint(O[MV]), geometryId=g['id'], geometryHash=digest(g), lengthMeters=r(ml.length), firstYear=1928, until=O[MV]['states'][0]['from'],
                         maps={'1928-hammarudda': 'present', '1944-kungso': 'present', '1953-kungso': 'present'}, ranges=[[0.0, r(ml.length)]])],
             earlyBasis={MV: 'Möckelövägen från Lönnelund förbi Gustavsberg, Pellas, Södergård, Strömbäck och Sunnvik till Möckelö är vägen på sockenkartan 1928 och utgåvorna 1944 och 1953, i hela sin längd och inom 10–20 m. Bladet 1012 05 har ingen grundkarta från 1968, så objektet var daterat först från 1978.'},
             geometryNote='Objektets egen geometri (samma koordinater), där vägen är vägen på sockenkartan 1928.')
json.dump(early, open(EARLY, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat); data = {MAIN: review, EARLY: early}
apply_mockelo_road(lambda p: data[p] if p in data else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok:', len(trial['objects']) - len(cat['objects']), 'object added')
