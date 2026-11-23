"""Write data/sviby-connections.json and data/sviby-connections-early.json. Usage: prepare.py CATALOGUE_BEFORE.json.gz

Read on the Sviby review's renders (docs/reviews/sviby-2026-11-23/renders, junction/):
- j-sheet.jpg, jw-sheet.jpg, j-g1985.jpg: the 1928 sheet and its 1944 and 1953 Kungsö editions draw the road from Norra
  Svibyvägen south-east to the sheet edge, where the 1929/1948 Mariehamn sheet continues it as Kasbergsvägen; the base
  maps 1978 and 1985 (1012 05) draw it as the main road. Today: Bäckvägen's west way and the start of way 1066273698.
- shore-p1948.jpg, m1929-sviby.jpg, m1929-south.jpg: the 1929 sheet ("Svibyväg") and its 1948 edition draw the road on
  from the junction south along the west shore of Svibyviken, today the cycleway 35072855 and Norra Möckelövägen. The
  1929 sheet lies 50–80 m east at its west edge; the 1948 edition within 20–40 m.
- v-m1929.jpg, z-p1948.jpg, v-b1968.jpg: no road east from the junction to Svibyvägen on the 1929 sheet or its 1948
  edition (an unrevised print of the 1929 survey: it still draws the corner at Talläsen and nothing of the airport). The
  aerial photo of 25 July 1942 shows it from the photo's western edge (E 20 495 596) to Svibyvägen (the 1942 approach
  review's trace 'Västra infarten norrifrån'); the base map 1968 draws it whole as the road to the airport."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from hammarlandsvagen_main_road import metric, SNAPSHOTS
from sviby_connections import _piece, apply_sviby_connections, EARLY, MAIN
from shapely.geometry import Point

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
KB, NS, NM, SV = 'road:qgis:mariehamn:kasbergsvagen-200km2', 'road:qgis:gottby:norra-svibyvagen-100km5', 'road:mariehamn:major-followup:norra-mockelovagen', 'road:qgis:mariehamn:svibyvagen-1-200km2'
JN, EW, SH = 'road:jomala:kasbergsvagen:norra-svibyvagen', 'road:jomala:sviby:vagen-mot-svibyvagen', 'road:jomala:norra-mockelovagen:norra-delen'
F = {ds: {x['id']: x for x in json.load(gzip.open(f))['features']} for ds, (f, _) in SNAPSHOTS.items()}
own = {(l['datasetId'], l['featureId']): l['sourceVertexRange'] for o in cat['objects'] for l in o.get('sourceLinks', []) if l.get('sourceVertexRange')}
r = lambda x: round(x, 1)

def links(spec, basis):
    out = []
    for ds, fid, rng, rev in spec:
        p = F[ds][fid]['paths'][0]; a, b = rng if rng else (0, len(p) - 1)
        out.append(dict(datasetId=ds, featureId=fid, sourceVertexRange=[a, b], sourceVertexCount=len(p), input=digest(F[ds][fid]['paths']), basis=basis, **({'reverse': True} if rev else {})))
    return out

def path2026(ls, join):
    built = []
    for l in [x for x in ls if x['datasetId'] == 'osm-2026']:
        part = _piece(F['osm-2026'][l['featureId']]['paths'][0], *l['sourceVertexRange'], l.get('reverse', False))
        built += part[1:] if built and built[-1] == part[0] else part
    return [built]

L = {'1928-hammarudda': dict(sourceId='nls:9c76c491-898b-4b0b-9331-7af223831264', year=1928), '1929-mariehamn': dict(sourceId='nls:9c76c492-0456-43c6-9478-b2aa0034b26c', year=1929),
     '1942-photo': dict(sourceId='mariehamn-aerial-1942', year=1942, observationType='aerial', observedAt='1942-07-25', imageCoverage='visible'),
     '1944-kungso': dict(sourceId='nls:9c72a692-458e-4804-af82-e6ac6dbf73fe', year=1944), '1948-mariehamn': dict(sourceId='nls:9c72a694-1238-40a8-a8ca-33c754332810', year=1948),
     '1953-kungso': dict(sourceId='nls:9c72a692-80ff-433c-950e-1cf484176101', year=1953),
     '1968-mariehamn': dict(sourceId='nls:101208:1968', year=1968), '1978-mariehamn': dict(sourceId='nls:101208:1978', year=1978),
     '1985-mariehamn': dict(sourceId='nls:101208:1985', year=1985), '1995-mariehamn': dict(sourceId='nls:101208:1995', year=1995),
     '1978-gottby': dict(sourceId='nls:101205:1978', year=1978), '1985-gottby': dict(sourceId='nls:101205:1985', year=1985)}

# --- the east–west road (listed first: the shore piece starts on it) ------------------------------------------------
ew_b = 'Vägen från Norra Svibyvägen österut till Svibyvägen, som den kartlagts detta år.'
ew_links = links([('osm-2026', 'way/1193557303', None, True), ('osm-2026', 'way/1108057940', None, True), ('osm-2026', 'way/1108057939', None, True),
                  ('osm-2026', 'way/1180462200', None, True), ('osm-2026', 'way/35304978', None, True),
                  ('osm-2025', 'road-2025-1193557303', None, True), ('osm-2025', 'road-2025-1108057940', None, True), ('osm-2025', 'road-2025-1108057939', None, True),
                  ('osm-2025', 'road-2025-1180462200', None, True), ('osm-2025', 'road-2025-35304978', None, True),
                  ('osm-2021', 'road-2021-35304978', None, True), ('osm-2014', 'road-2014-35304978', None, True)], ew_b)
ew_path = path2026(ew_links, 10); ewl = metric(ew_path[0])
edge = ewl.project(Point(20495596, 6667688)) / ewl.length               # the 1942 photo's western edge
print('east–west road', r(ewl.length), 'm; the photo covers from', round(edge, 4))
# --- the junction at Kasberget ----------------------------------------------------------------------------------------
jn_b = 'Vägen från Norra Svibyvägen till Kasbergsvägen, som den kartlagts detta år; delen före Kasbergsvägens objekt.'
jn_links = links([('osm-2026', 'way/940586838', None, False), ('osm-2026', 'way/1066273698', [0, own[('osm-2026', 'way/1066273698')][0]], False),
                  ('osm-2025', 'road-2025-940586838', None, False), ('osm-2025', 'road-2025-1066273698', [0, own[('osm-2025', 'road-2025-1066273698')][0]], False),
                  ('osm-2021', 'road-2021-23110460', [0, own[('osm-2021', 'road-2021-23110460')][0]], False),
                  ('osm-2014', 'road-2014-23110460', [0, own[('osm-2014', 'road-2014-23110460')][0]], False)], jn_b)
jn_path = path2026(jn_links, 1)
# --- the shore piece between Norra Svibyvägen and Norra Möckelövägen ----------------------------------------------------
sh_b = 'Den gamla vägen från Norra Svibyvägen söderut mot Norra Möckelövägen, som den kartlagts detta år (i dag en gång- och cykelväg).'
sh_links = links([('osm-2026', 'way/35072855', None, True), ('osm-2025', 'road-2025-35072855', None, True), ('osm-2021', 'road-2021-35072855', None, True),
                  ('osm-2014', 'road-2014-35072855', None, True)], sh_b)
sh_path = path2026(sh_links, 1)
print('junction', r(metric(jn_path[0]).length), 'm; shore piece', r(metric(sh_path[0]).length), 'm')

method = 'Kartorna har lagts över varandra och över dagens vägar med ett rutnät på 100 m. Flygfotot 1942 är granskat i infartsgranskningen 1942 (data/mariehamn-approaches-1942.json).'
stage = []
for s in cat['cityStages']:
    for f in s['features']:
        if f['id'] == 'city-reconstruction-1942:city-1942-street-0:approach-gap:0':
            stage.append(dict(stageId=s['id'], featureId=f['id'], featureHash=digest(f), replacedBy=EW, maxDistanceMeters=35,
                              basis='Infartsgranskningens bit från flygfotots västra kant till Svibyvägen; vägen själv ritas nu med sin egen mittlinje, ansluten till Norra Svibyvägen.'))
review = dict(
    schemaVersion=1, reviewedAt='2026-11-23', method=method, maps=L,
    source=dict(id='review:sviby-connections', title='Vägarna vid Sviby: Kasbergsvägens början, vägen mot Svibyvägen och Norra Möckelövägens norra del · granskning', url='assets/sviby-connections.json'),
    surveySources=[dict(id=x + ':survey', title='OpenStreetMap · ' + t, url='https://www.openstreetmap.org/way/' + w, issuedAt='2026')
                   for x, t, w in ((EW, 'vägen från Norra Svibyvägen till Svibyvägen', '35304978'), (JN, 'Bäckvägen och Kasbergsvägen vid Norra Svibyvägen', '1066273698'),
                                   (SH, 'gång- och cykelvägen mellan Norra Svibyvägen och Norra Möckelövägen', '35072855'))],
    newRoads=[
        dict(id=EW, name='Vägen mot Svibyvägen · Sviby', routeId='road:route:sviby-svibyvagen', modernRoadClass='residential', roadWidth=4, firstYear=1942, surveySourceId=EW + ':survey',
             maps={'1929-mariehamn': 'absent', '1942-photo': 'present', '1968-mariehamn': 'present', '1978-mariehamn': 'present', '1985-mariehamn': 'present', '1995-mariehamn': 'present'},
             coverage={'1942-photo': 'partial'}, canonicalRanges={'1942-photo': [round(edge, 6), 1]},
             start=NS, end=SV, joinMeters=10, paths=ew_path, sourceLinks=ew_links,
             basis='Vägen från Norra Svibyvägens södra ände rakt österut till Svibyvägen. Sockenkartan 1929 ritar den inte (inte heller utgåvan 1948, ett oreviderat tryck av samma kartläggning). Flygfotot den 25 juli 1942 visar den från fotots västra kant till Svibyvägen; de västligaste 190 metrarna ligger utanför fotot, men vägen fortsätter dit och har ingen annan anslutning. Grundkartan 1968 ritar hela vägen, som vägen till flygstationen. I dag är den västra delen en gång- och cykelväg.',
             geometryNote='Mittlinjen i OpenStreetMap 2026 (fem vägar i följd), använd som stabilt läge från 1942. OpenStreetMap 2014 och 2021 har den som en enda väg (35304978).'),
        dict(id=JN, name='Kasbergsvägen · vid Norra Svibyvägen', routeId='road:route:kasbergsvagen', modernRoadClass='residential', roadWidth=4, firstYear=1928, surveySourceId=JN + ':survey',
             maps={k: 'present' for k in ('1928-hammarudda', '1944-kungso', '1953-kungso', '1978-gottby', '1985-gottby')},
             start=NS, end=KB, joinMeters=1, paths=jn_path, sourceLinks=jn_links,
             basis='Kasbergsvägens början vid Norra Svibyvägen. Sockenkartan 1928 och utgåvorna 1944 och 1953 (Kungsö) ritar vägen från Norra Svibyvägen åt sydost till bladkanten, där sockenkartan 1929 för Mariehamn fortsätter den som Kasbergsvägen. Grundkartorna 1978 och 1985 ritar den som huvudväg. I dag är den Bäckvägens västligaste bit och början av Kasbergsvägen, fram till där Kasbergsvägens objekt börjar.',
             geometryNote='Mittlinjen i OpenStreetMap 2026 (Bäckvägen, way 940586838, och början av way 1066273698), använd som stabilt läge från 1928. Kartans väg ligger inom bladets fel, 20–45 m.'),
        dict(id=SH, name='Norra Möckelövägen · norra delen', routeId='road:route:norra-mockelovagen', modernRoadClass='cycleway', roadWidth=3, firstYear=1929, surveySourceId=SH + ':survey',
             maps={k: 'present' for k in ('1929-mariehamn', '1948-mariehamn', '1968-mariehamn', '1978-mariehamn', '1985-mariehamn', '1995-mariehamn')},
             start=EW, end=NM, joinMeters=1, paths=sh_path, sourceLinks=sh_links,
             basis='Den gamla vägen från Norra Svibyvägen söderut längs Svibyvikens västra strand. Sockenkartan 1929 (där den heter "Svibyväg") och utgåvan 1948 ritar den, liksom grundkartorna 1968–1995. I dag är den en gång- och cykelväg; Norra Svibyvägen svänger i stället åt sydväst.',
             geometryNote='Gång- och cykelvägens mittlinje i OpenStreetMap 2026 (way 35072855), använd som stabilt läge från 1929.')],
    stageFeatures=stage)
json.dump(review, open(MAIN, 'w'), ensure_ascii=False, indent=1)

g = G[O[NM]['geometryPeriods'][0]['geometryId']]; nml = metric(g['paths'][0])
early = dict(schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:sviby-connections-1929:',
             source=dict(id='review:sviby-connections-early', title='Norra Möckelövägen på sockenkartan 1929 · granskning', url='assets/sviby-connections-early.json'),
             sources=[], maps={k: L[k] for k in ('1929-mariehamn', '1948-mariehamn')}, method=method,
             early=[dict(objectId=NM, inputHash=fingerprint(O[NM]), geometryId=g['id'], geometryHash=digest(g), lengthMeters=r(nml.length), firstYear=1929, until=O[NM]['states'][0]['from'],
                         maps={'1929-mariehamn': 'present', '1948-mariehamn': 'present'}, ranges=[[0.0, r(nml.length)]])],
             earlyBasis={NM: 'Norra Möckelövägen längs Svibyvikens västra strand är vägen på sockenkartan 1929 ("Svibyväg") och utgåvan 1948, i hela sin längd och inom 20–40 m. Objektet var daterat först från grundkartan 1968.'},
             geometryNote='Objektets egen geometri (samma koordinater), där vägen är vägen på sockenkartan 1929.')
json.dump(early, open(EARLY, 'w'), ensure_ascii=False, indent=1)

trial = deepcopy(cat); data = {MAIN: review, EARLY: early}
apply_sviby_connections(lambda p: data[p] if p in data else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok:', len(trial['objects']) - len(cat['objects']), 'objects added;', len(stage), 'stage features replaced')
