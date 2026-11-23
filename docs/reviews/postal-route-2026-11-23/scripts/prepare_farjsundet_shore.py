"""Write data/postal-route-farjsundet-shore.json. Usage: prepare_farjsundet_shore.py CATALOGUE_AFTER_HARALDSBY_EARLY.json.gz

Read on ../renders/shore-sheet.jpg (1968 and 1978, OSM in green) and hamn-sheet.jpg (1929, 1944, 1968): from the north
end of Hamnvägen the road to the old ferry landing ran east along the shore of Färjsundet. OSM way 960124939 (a service
track today, owned by no object) follows the 1968 and 1978 red road within about 10 m and ends at the shore 50–60 m
south-west of the bridge's west end: the old landing."""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import digest
from hammarlandsvagen_main_road import metric, SNAPSHOTS
from sviby_connections import _piece, _check, _add

cat = json.load(gzip.open(sys.argv[1])); S = {s['id'] for s in cat['sources']}
F = {ds: {x['id']: x for x in json.load(gzip.open(f))['features']} for ds, (f, _) in SNAPSHOTS.items()}
OWNED = {(l['datasetId'], l['featureId']) for o in cat['objects'] for l in o.get('sourceLinks', [])}
L = {'1929-saltvik': dict(sourceId='nls:map-38157483', year=1929), '1944-saltvik': dict(sourceId='nls:map-38147682', year=1944),
     '1968-saltvik': dict(sourceId='nls:102107:1968', year=1968), '1978-saltvik': dict(sourceId='nls:102107:1978', year=1978)}
assert all(l['sourceId'] in S for l in L.values())
ID = 'road:saltvik:farjvagen:farjsundet'
links = []
for ds, pre in (('osm-2026', 'way/'), ('osm-2025', 'road-2025-'), ('osm-2021', 'road-2021-'), ('osm-2014', 'road-2014-')):
    f = F[ds].get(pre + '960124939')
    if not f or len(f['paths']) != 1 or (ds, f['id']) in OWNED: continue
    if ds != 'osm-2026' and metric(f['paths'][0]).hausdorff_distance(metric(F['osm-2026']['way/960124939']['paths'][0])) > 5: continue
    links.append(dict(datasetId=ds, featureId=f['id'], sourceVertexRange=[0, len(f['paths'][0]) - 1], sourceVertexCount=len(f['paths'][0]), input=digest(f['paths']),
                      basis='Vägen längs stranden till det gamla färjläget vid Färjsundet, som den kartlagts detta år.'))
path = _piece(F['osm-2026']['way/960124939']['paths'][0], 0, len(F['osm-2026']['way/960124939']['paths'][0]) - 1, False)
review = dict(
    schemaVersion=1, reviewedAt='2026-11-23', maps=L, stagePrefix='postal-route-farjsundet',
    source=dict(id='review:postal-route-farjsundet', title='Vägen till färjläget vid Färjsundet på sockenkartorna och grundkartorna · granskning', url='assets/postal-route-farjsundet-shore.json'),
    method='Sockenkartorna för Saltvik 1929 och 1944 och grundkartorna 1021 07 från 1968 och 1978 har lagts över dagens vägar med ett rutnät på 100 m.',
    surveySources=[dict(id=ID + ':survey', title='OpenStreetMap · vägen längs stranden vid Färjsundet', url='https://www.openstreetmap.org/way/960124939', issuedAt='2026')],
    newRoads=[dict(id=ID, name='Färjvägen · Färjsundet', routeId='road:route:postvagen', modernRoadClass='service', roadWidth=3, firstYear=1929, surveySourceId=ID + ':survey',
                   maps={k: 'present' for k in L}, start='road:qgis:saltvik:hamnvagen-batch4', end=None, joinMeters=1, paths=[path], sourceLinks=links,
                   freeEndBasis='Det gamla färjläget på västra stranden av Färjsundet. Färjan gick här tills bron öppnades 4 juli 1937.',
                   basis='Vägen från Hamnvägens norra del österut längs stranden till färjläget vid Färjsundet. Sockenkartan för Saltvik 1929 och utgåvan 1944 ritar den som huvudvägen till färjan; grundkartorna 1968 och 1978 ritar den i rött till stranden. I dag finns den kvar som en mindre väg.',
                   geometryNote='Mittlinjen i OpenStreetMap 2026 (way 960124939), som följer vägen på grundkartorna 1968 och 1978 inom omkring 10 m, använd som stabilt läge från 1929.')],
    stageFeatures=[])
json.dump(review, open('data/postal-route-farjsundet-shore.json', 'w'), ensure_ascii=False, indent=1)
print(round(metric(path).length, 1), 'm,', len(links), 'links')
