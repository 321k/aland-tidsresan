"""Write data/svibyvagen.json and data/svibyvagen-kasberg.json: the road from Hammarland through Sviby towards Mariehamn
on the parish maps 1012 05 Hammarudda–Kungsö (1928; Kungsö 1944 and 1953) and 1012 08 Maarianhamina (1929; Mariehamn
1948), and the base maps 1012 05 (1978) and 1012 08 (1968–1995). Usage: prepare.py CATALOGUE_BEFORE.json.gz

Read on the renders in ../renders (grid 100 m, EPSG:3874):
- t-w-k1953.jpg, t-e-k1928.jpg, t-e-k1953.jpg, s-k1944.jpg: the 1928 road runs straight from Utängsvägen's east end
  east-south-east through Sviby to a T-junction with the north–south road at the sheet edge (E 20 495 392). The 1944
  and 1953 editions draw the same line. s-b1978g.jpg, t-e-b1978.jpg: the airport (Mariehamns flygstation) covers its
  western half, and Flygfältsvägen leaves it; the old line is not drawn.
- nsv-k1928.jpg, s-k1953.jpg: the north–south road is today's Norra Svibyvägen (way 166080083) over its whole length;
  the 1929 sheet labels it "Svibyväg".
- corner-sheet.jpg (1929, 1948, 1968, 1978, 1985, 1995): Kasbergsvägen is the 1929 road, except at Talläsen, where
  the road turned east and then south round a corner until the 1978 map; the 1985 map draws today's diagonal.
- m1929-sviby.jpg, z-p1948.jpg, w-p1948.jpg: from Kasbergsvägen the 1929 road runs on south along today's
  Kasbergsgatan and Svibyvägen towards the town.
- v-m1929.jpg, z-m1929.jpg, v-b1968.jpg: there is no direct road east from the junction to Svibyvägen on the 1929 and
  1948 maps; the airport road along it is first on the 1968 map.
The corner is read on the 1968 map (corner-b1968.jpg) and moved 18 m east, the scan's offset from OSM along the
stretches the two share; the Sviby line is read on the 1928 and 1953 sheets, which agree within 20 m."""
import sys, json, gzip, hashlib
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from hammarlandsvagen_main_road import metric
from lemlandsvagen_main_road import cut
from shapely.geometry import LineString, Point

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
UT, NS = 'road:qgis:gottby:utangsvagen-100km5', 'road:qgis:gottby:norra-svibyvagen-100km5'
KB, SV = 'road:qgis:mariehamn:kasbergsvagen-200km2', 'road:qgis:mariehamn:svibyvagen-1-200km2'
OLD, CORNER, KG = 'road:jomala:gamla-vagen:sviby', 'road:jomala:gamla-kasbergsvagen:tallasen', 'road:jomala:kasbergsgatan'
r = lambda x: round(x, 1); togeo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
E0, N0 = 20490000, 6660000; local = lambda x, y: (E0 + x, N0 + y)
first = lambda oid: G[O[oid]['geometryPeriods'][0]['geometryId']]

L = {'1928-hammarudda': dict(sourceId='nls:9c76c491-898b-4b0b-9331-7af223831264', year=1928),
     '1929-mariehamn': dict(sourceId='nls:9c76c492-0456-43c6-9478-b2aa0034b26c', year=1929),
     '1944-kungso': dict(sourceId='nls:9c72a692-458e-4804-af82-e6ac6dbf73fe', year=1944),
     '1948-mariehamn': dict(sourceId='nls:9c72a694-1238-40a8-a8ca-33c754332810', year=1948),
     '1953-kungso': dict(sourceId='nls:9c72a692-80ff-433c-950e-1cf484176101', year=1953),
     '1978-gottby': dict(sourceId='nls:101205:1978', year=1978),
     '1968-mariehamn': dict(sourceId='nls:101208:1968', year=1968), '1978-mariehamn': dict(sourceId='nls:101208:1978', year=1978),
     '1985-mariehamn': dict(sourceId='nls:101208:1985', year=1985), '1995-mariehamn': dict(sourceId='nls:101208:1995', year=1995)}
SOURCE = dict(id='review:svibyvagen', title='Vägen från Hammarland genom Sviby mot Mariehamn på sockenkartorna 1928 och 1929 · granskning', url='assets/svibyvagen.json')
SOURCE_KB = dict(id='review:svibyvagen-kasberg', title='Kasbergsvägen vid Talläsen på sockenkartan 1929 och grundkartorna · granskning', url='assets/svibyvagen-kasberg.json')

# --- Norra Svibyvägen and Svibyvägen del 1: whole objects -----------------------------------------------------------
def whole(oid, first_year, maps):
    g = first(oid); line = metric(g['paths'][0])
    return dict(objectId=oid, inputHash=fingerprint(O[oid]), geometryId=g['id'], geometryHash=digest(g), lengthMeters=r(line.length), firstYear=first_year,
                until=O[oid]['states'][0]['from'], maps=maps, ranges=[[0.0, r(line.length)]])

ns = whole(NS, 1928, {'1928-hammarudda': 'present', '1929-mariehamn': 'present', '1944-kungso': 'present', '1953-kungso': 'present'})
sv = whole(SV, 1929, {'1929-mariehamn': 'present'})

# --- the old road through Sviby (its first 120 m survive as the service road beside the airport, way 162795209) ----
ut_end = max((first(UT)['paths'][0][0], first(UT)['paths'][0][-1]), key=lambda q: TO_METRIC(*q)[0])   # its east end
nsl = metric(first(NS)['paths'][0]); junction = nsl.interpolate(nsl.project(Point(local(5392, 7712))))
modern = {f['id']: f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']}
svc = modern['way/162795209']['paths'][0]; SA, SB = 15, 20      # vertices 15-20, 8-15 m from the 1928/1953 line
survive = svc[SA:SB + 1]
trace = [TO_METRIC(*ut_end), local(4600, 8000), local(4900, 7880), local(5100, 7804), local(5300, 7729), junction.coords[0]]
old_path = [list(ut_end)] + survive + [togeo(q) for q in trace[2:-1]] + [togeo(junction.coords[0])]
oldL = metric(old_path)
k0 = oldL.project(Point(TO_METRIC(*survive[0]))) / oldL.length; k1 = oldL.project(Point(TO_METRIC(*survive[-1]))) / oldL.length
print('Sviby old road', r(oldL.length), 'm; junction on Norra Svibyvägen at', r(nsl.project(junction)), 'of', r(nsl.length), '; surviving', round(k0, 6), round(k1, 6))

# --- Kasbergsvägen: the corner at Talläsen ----------------------------------------------------------------------------
kg = first(KB); kpath = kg['paths'][0]; kl = metric(kpath)
a, b = 475.0, 625.0                                      # where today's diagonal leaves and rejoins the 1929–1978 road
pa, pb = kl.interpolate(a), kl.interpolate(b)
apex = [local(5703, 8176), local(5713, 8124)]            # read on the 1968 map, moved 18 m east
corner_path = [togeo(pa.coords[0])] + [togeo(q) for q in apex] + [togeo(pb.coords[0])]
cornerL = metric(corner_path)
dev = max(kl.distance(Point(q)) for q in metric(corner_path).coords)
print('Kasbergsvägen', r(kl.length), 'm; corner', r(cornerL.length), 'm in place of', b - a, 'm; largest distance from today', r(dev))
kb = dict(objectId=KB, inputHash=fingerprint(O[KB]), geometryId=kg['id'], geometryHash=digest(kg), lengthMeters=r(kl.length), firstYear=1929,
          until=O[KB]['states'][0]['from'], maps={'1929-mariehamn': 'present', '1948-mariehamn': 'present', '1968-mariehamn': 'present', '1978-mariehamn': 'present'},
          ranges=[[0.0, a], [b, r(kl.length)]])

# --- Kasbergsgatan: a new object from its OSM way ---------------------------------------------------------------------
SNAP = {'osm-2026': ('dist/assets/modern.json.gz', 'way/'), 'osm-2021': ('dist/assets/roads-2021.json.gz', 'road-2021-'), 'osm-2025': ('dist/assets/roads-2025.json.gz', 'road-2025-')}
links = []
for ds, (file, prefix) in SNAP.items():
    f = next(x for x in json.load(gzip.open(file))['features'] if x['id'] == prefix + '490727406')
    links.append(dict(datasetId=ds, featureId=f['id'], sourceVertexRange=[0, len(f['paths'][0]) - 1], sourceVertexCount=len(f['paths'][0]), input=digest(f['paths']),
                      basis='Kasbergsgatan, vägen från Kasbergsvägen till Svibyvägen, som den kartlagts detta år.'))
    if ds == 'osm-2026': kg_paths = f['paths']
print('Kasbergsgatan', r(metric(kg_paths[0]).length), 'm')

maps_main = {k: L[k] for k in ('1928-hammarudda', '1929-mariehamn', '1944-kungso', '1953-kungso', '1978-gottby', '1968-mariehamn', '1978-mariehamn', '1985-mariehamn', '1995-mariehamn')}
review = dict(
    schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:svibyvagen-1929:',
    source=SOURCE, sources=[], maps=maps_main, early=[ns, sv],
    earlyBasis={NS: 'Norra Svibyvägen är vägen på sockenkartan 1928 (Hammarudda–Kungsö) och dess utgåvor 1944 och 1953 (Kungsö), i hela sin längd och inom 10–20 m. Sockenkartan 1929 för Mariehamn kallar den "Svibyväg". Bladet 1012 05 har ingen grundkarta från 1968, så objektet var daterat först från 1978.',
                SV: 'Svibyvägen från Kasbergsgatan mot staden är vägen på sockenkartan 1929 (Maarianhamina) och dess utgåva 1948, med samma form. Den var daterad först från stadskartan 1937.'},
    method='Kartorna har lagts över varandra och över dagens vägar med ett rutnät på 100 m. Sockenkartan 1929 ligger 50–80 m fel vid sin västra kant; utgåvan 1948 av samma blad och bladen 1928–1953 för Kungsö ligger inom 10–30 m.',
    geometryNote='Objektets egen geometri (samma koordinater), där vägen är vägen på sockenkartorna 1928 och 1929.',
    newRoadSource=dict(id=KG + ':survey', title='OpenStreetMap · Kasbergsgatan', url='https://www.openstreetmap.org/way/490727406', issuedAt='2026'),
    newRoad=dict(id=KG, name='Kasbergsgatan', routeId='road:route:kasbergsgatan', modernRoadClass='residential', roadWidth=4, firstYear=1929, surveySourceId=KG + ':survey',
                 maps={'1929-mariehamn': 'present', '1968-mariehamn': 'present', '1978-mariehamn': 'present', '1985-mariehamn': 'present', '1995-mariehamn': 'present'},
                 paths=kg_paths, sourceLinks=links, missingExtracts=['osm-2014'],
                 missingExtractsBasis='I OpenStreetMap 2014 var sträckan en del av Kasbergsvägen (way 23110460), som den raden hör till.',
                 basis='Vägen från Kasbergsvägen söderut till Svibyvägen. Sockenkartan 1929 och utgåvan 1948 ritar den som en del av vägen från Kasberget mot staden, och grundkartorna 1968–1995 ritar den. Dagens mittlinje (OpenStreetMap) används som stabilt läge.',
                 geometryNote='Kasbergsgatans mittlinje i OpenStreetMap 2026, använd som stabilt läge från 1929.'))
review['maps'] = {k: v for k, v in review['maps'].items() if k in {m for e in review['early'] for m in e['maps']} | set(review['newRoad']['maps'])}
json.dump(review, open('data/svibyvagen.json', 'w'), ensure_ascii=False, indent=1)

review_kb = dict(
    schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:svibyvagen-1929:',
    source=SOURCE_KB, sources=[], maps={k: L[k] for k in ('1929-mariehamn', '1948-mariehamn', '1968-mariehamn', '1978-mariehamn', '1985-mariehamn')}, early=[kb],
    earlyBasis={KB: 'Kasbergsvägen från Norra Svibyvägen förbi Talläsen mot Kasbergsgatan är vägen på sockenkartan 1929 och utgåvan 1948 och på grundkartorna 1968 och 1978, utom vid Talläsen. Där gick vägen i en vinkel österut och sedan söderut; den raka diagonalen ritas först 1985.'},
    method=review['method'], geometryNote='Delar av objektets egen geometri (samma koordinater) där vägen är vägen på sockenkartan 1929.',
    oldRoad=dict(id=CORNER, name='Gamla Kasbergsvägen · Talläsen', routeId='road:route:kasbergsvagen', modernRoadClass='residential', roadWidth=4, firstYear=1929, until=1985,
                 maps={'1929-mariehamn': 'present', '1948-mariehamn': 'present', '1968-mariehamn': 'present', '1978-mariehamn': 'present', '1985-mariehamn': 'absent'},
                 path=corner_path, lengthMeters=r(cornerL.length), referenceRange=[0, None], endSnapMeters=[0.0, 0.0], endSnapLimit=1, endObjects=[KB], todayRoadName='Kasbergsvägen',
                 basis='Vid Talläsen gick Kasbergsvägen i en vinkel: österut och sedan söderut längs backen. Sockenkartan 1929, utgåvan 1948 och grundkartorna 1968 och 1978 ritar vinkeln. Grundkartan 1985 ritar i stället dagens raka diagonal. Den gamla vinkeln finns inte i OpenStreetMap.',
                 traceBasis='Mittlinjen är avläst för hand på grundkartan 1968 och flyttad 18 m österut, kartans avvikelse från dagens väg där de två sammanfaller. Båda ändarna ligger på dagens Kasbergsvägen.',
                 afterNote='Grundkartan 1985 ritar inte vinkeln. Exakt när den togs ur bruk är inte känt.'))
json.dump(review_kb, open('data/svibyvagen-kasberg.json', 'w'), ensure_ascii=False, indent=1)

review_old = dict(
    schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview',
    source=dict(id='review:svibyvagen-old', title='Den gamla vägen genom Sviby på sockenkartorna 1928–1953 · granskning', url='assets/svibyvagen-old.json'),
    sources=[dict(id=OLD + ':survey', title='OpenStreetMap · vägen vid flygfältet i Sviby, Jomala', url='https://www.openstreetmap.org/way/162795209', issuedAt='2026')],
    maps={k: L[k] for k in ('1928-hammarudda', '1944-kungso', '1953-kungso', '1978-gottby')},
    connections=[dict(id=UT, hash=fingerprint(O[UT]), earlyPeriods=1)],
    method=review['method'],
    oldRoads=[dict(id=OLD, name='Gamla vägen genom Sviby', routeId='road:route:hammarland-sviby', modernRoadClass='tertiary', roadWidth=4, firstYear=1928, mainUntil=1978,
                   surveySourceId=OLD + ':survey', maps={'1928-hammarudda': 'present', '1944-kungso': 'present', '1953-kungso': 'present', '1978-gottby': 'present'},
                   mainUntilBasis='Grundkartan 1978 ritar flygfältet över vägens västra hälft och Flygfältsvägen bredvid den; bara vägens första 200 m öster om Utängsvägen ritas, fram till flygfältets stängsel. Bladet 1012 05 har ingen grundkarta från 1968, så när vägen bröts mellan 1953 och 1978 är inte känt.',
                   paths=[old_path], lengthMeters=r(oldL.length), laterPaths=[survive], laterCanonicalRanges=[[round(k0, 6), round(k1, 6)]],
                   sourceLinks=[dict(datasetId='osm-2026', featureId='way/162795209', sourceVertexRange=[SA, SB], sourceVertexCount=len(svc),
                                     basis='Vägen vid flygfältets stängsel, den gamla vägens första bit öster om Utängsvägen, som den kartlagts i dag. Resten av vägen (åt sydväst) är en senare väg runt flygfältet och ingår inte.')],
                   trace=[list(q) for q in trace], sameRoadMeters=20,
                   endsOn=[dict(path=0, end=-1, objectId=NS, basis='Vägen slutar i en trevägskorsning på Norra Svibyvägen, nära det objektets södra ände.')],
                   basis='Vägen från Hammarland gick från Utängsvägens östra ände rakt österut genom Sviby till Norra Svibyvägen. Sockenkartan 1928 och utgåvorna 1944 och 1953 ritar den. Sockenkartan 1929 för Mariehamn ritar ingen direkt väg vidare österut mot Svibyvägen; vägen mot staden gick norrut längs Norra Svibyvägen och sedan Kasbergsvägen.',
                   traceBasis='Mittlinjen följer OpenStreetMap där vägen finns kvar (vägen vid flygfältets stängsel) och är avläst för hand på sockenkartan 1928 och utgåvan 1953 (rutnät 100 m), som stämmer inom 20 m, där inget finns kvar. Den västra änden är Utängsvägens östra ände, den östra en punkt på Norra Svibyvägen.',
                   laterBasis='Efter flygfältet (grundkartan 1978) visas bara vägens första bit öster om Utängsvägen, som finns kvar vid flygfältets stängsel, med samma koordinater.')])
json.dump(review_old, open('data/svibyvagen-old.json', 'w'), ensure_ascii=False, indent=1)

# Dry run on a copy, both files, in build order.
trial = deepcopy(cat); data = {'data/svibyvagen.json': review, 'data/svibyvagen-kasberg.json': review_kb, 'data/svibyvagen-old.json': review_old}
rd = lambda p: data[p] if p in data else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p)))
sys.path.insert(0, 'scripts'); from svibyvagen import apply_svibyvagen
apply_svibyvagen(rd, trial)
print('trial ok:', len(trial['objects']) - len(cat['objects']), 'objects added')
