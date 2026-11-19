"""Write data/hammarlandsvagen-holmberg.json:
- the 1929 road from the narrow sound (the connection's 1929 crossing stretch, 3 690 m) straight east across Holmberg to
  the ferry pier, read on renders/holmberg-road-grid-1929-close.jpg; the 1956 edition no longer draws it to that pier
- Öravägen (OSM way 169282417), the road to the later pier at Örliden: first on the 1956 edition, the main road on the
  base maps 1968 and 1978, a minor road in 1985 (renders/holmberg-road-grid-1956.jpg, holmberg-road-1968-1985.jpg)
Usage: prepare_holmberg.py CATALOGUE_BEFORE_THE_STEP.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
from mariehamn_frame_1942 import TO_METRIC, TO_GEO, digest
from shapely.geometry import LineString, Point
from grid_trace import window_inverse

R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
M = 'road:marsund:eckero-hammarland'
REF = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
early = G[O[M]['geometryPeriods'][0]['geometryId']]['paths']
p3690 = min((q for p in early for q in (p[0], p[-1])), key=lambda q: Point(TO_METRIC(*q)).distance(REF.interpolate(3690)))
assert Point(TO_METRIC(*p3690)).distance(REF.interpolate(3690)) < 1
geo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
inv = window_inverse('eckero-1929', 'marsund-reference.json', 0, 260, 1040, center=(20482300, 6678250))
pts = [inv(*p) for p in [(60, 455), (200, 465), (400, 480), (600, 492), (800, 505), (860, 508)]]
s0 = Point(TO_METRIC(*p3690)); pts = [q for q in pts if Point(q).x > s0.x + 10]
path = [p3690] + [geo(q) for q in pts]
L = LineString([TO_METRIC(*q) for q in path]); print('old road', round(L.length, 1), 'm')
feats = {'osm-2026': [f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features'] if f['id'] == 'way/169282417'][0]}
for y in (2014, 2021, 2025):
    feats[f'osm-{y}'] = [f for f in json.load(gzip.open(f'dist/assets/roads-{y}.json.gz'))['features'] if f['id'] == f'road-{y}-169282417'][0]
links = [dict(datasetId=d, featureId=f['id'], sourceVertexRange=[0, len(f['paths'][0]) - 1], sourceVertexCount=len(f['paths'][0]), input=digest(f['paths']),
              basis='Öravägen, vägen till bryggan vid Örliden, som den kartlagts detta år.') for d, f in feats.items()]
SURVEY = 'road:eckero:oravagen:survey'
maps = {'1929-eckero': dict(sourceId='nls:map-39091228', year=1929), '1956-eckero': dict(sourceId='nls:map-37971493', year=1956),
        '1968': dict(sourceId='nls:101203:1968', year=1968), '1978': dict(sourceId='nls:101203:1978', year=1978), '1985': dict(sourceId='nls:101203:1985', year=1985)}
data = dict(
    schemaVersion=1, reviewedAt='2026-11-19',
    source=dict(id='review:hammarlandsvagen-holmberg', title='Vägen över Holmberg till färjan · granskning', url='assets/hammarlandsvagen-holmberg.json'),
    sources=[], maps=maps, early=[], earlyBasis={},
    method='Vägen över Holmberg avläst för hand på sockenkartan 1012 03 Eckerö 1929 (rutnät 50 m) och jämförd med utgåvan 1956, grundkartorna 1968, 1978 och 1985 (blad 101203) och OpenStreetMap 2014–2026 (renders/holmberg-*).',
    oldRoad=dict(id='road:eckero:gamla-landsvagen:holmberg', name='Gamla landsvägen · Holmberg', routeId='road:Gamla landsvägen Eckerö', modernRoadClass='secondary', roadWidth=4,
                 firstYear=1929, until=1956, maps={'1929-eckero': 'present', '1956-eckero': 'absent'},
                 paths=[path], lengthMeters=round(L.length, 1), referenceRange=[3690, None], endSnapMeters=[0.0, 0.0], endSnapLimit=1,
                 endObjects=[M], freeEnds=[[0, -1]], freeEndBasis='Vägens östra ände är färjebryggan på Holmbergs östra strand; där fortsatte vägen med färjan över Marsund till bryggan vid Marsundsvägen.',
                 basis='Landsvägen från färjan över Marsund gick från bryggan på Holmbergs östra strand rakt västerut till det smala sundet. Sockenkartan 1929 ritar den. Utgåvan 1956 ritar i stället vägen söderut till en ny brygga vid Örliden (dagens Öravägen); vägen fram till den gamla bryggan ritas inte. Inget av den finns i OpenStreetMap.',
                 traceBasis='Mittlinjen är avläst för hand på sockenkartan 1929 (rutnät 50 m) och inte flyttad; den västra änden är fäst vid förbindelsens del från 1929 vid sundet, den östra är färjebryggan.',
                 afterNote='Utgåvan 1956 ritar ingen väg fram till den gamla bryggan. Exakt när den togs ur bruk är inte känt.'),
    route=dict(order=[M, 'road:eckero:gamla-landsvagen:holmberg'], endObjects=[M], joinMeters=2.0),
    newRoadSource=dict(id=SURVEY, title='OpenStreetMap · Öravägen', url='https://www.openstreetmap.org/way/169282417', issuedAt='2026'),
    newRoad=dict(id='road:eckero:oravagen', name='Öravägen', routeId='road:route:oravagen', modernRoadClass='residential', roadWidth=4, firstYear=1956, surveySourceId=SURVEY,
                 maps={'1956-eckero': 'present', '1968': 'present', '1978': 'present', '1985': 'present'},
                 paths=feats['osm-2026']['paths'], sourceLinks=links,
                 basis='Vägen från det smala sundet över Holmberg till bryggan vid Örliden. Utgåvan 1956 ritar den första gången, och grundkartorna 1968 och 1978 ritar den som huvudväg till bryggan; 1985 är den en mindre väg. Dagens mittlinje (OpenStreetMap) används som stabilt läge; vid korsningen med dagens väg är den yngre.',
                 geometryNote='Öravägens mittlinje i OpenStreetMap 2026, använd som stabilt läge från 1956.'))
json.dump(data, open('data/hammarlandsvagen-holmberg.json', 'w'), ensure_ascii=False, indent=1)
