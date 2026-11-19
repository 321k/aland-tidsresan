"""Write data/hammarlandsvagen-shore.json: the 1929 road from the narrow sound at Holmberg south along the shore to
Nissas, where it joined Marbyvägen. Read on renders/ferry-landing-grid-1929-osm.jpg (north) and shore-road-grid-1929.jpg
(south). The 1956 edition no longer draws it (renders/marbyvagen-north-1929-1956.jpg); nothing of it is in OSM.
Usage: prepare_shore.py CATALOGUE_AFTER_THE_MARBY_STEP.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
from mariehamn_frame_1942 import TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
from grid_trace import window_inverse

R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
MB, M = 'road:qgis:eckero:marbyvagen-100km1', 'road:marsund:eckero-hammarland'
REF = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
early = G[O[M]['geometryPeriods'][0]['geometryId']]['paths']
p3880 = min((q for p in early for q in (p[0], p[-1])), key=lambda q: Point(TO_METRIC(*q)).distance(REF.interpolate(3880)))
assert Point(TO_METRIC(*p3880)).distance(REF.interpolate(3880)) < 1
mb_cut = G[O[MB]['geometryPeriods'][0]['geometryId']]['paths'][0]       # Marbyvägen's 1929 cut, Sundkvist–Nissas
assert O[MB]['geometryPeriods'][0]['from'] == 1929
end = mb_cut[-1] if LineString([TO_METRIC(*q) for q in mb_cut]).project(Point(TO_METRIC(*mb_cut[-1]))) > 0 else mb_cut[0]
geo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
a = window_inverse('eckero-1929', 'marsund-reference.json', 4150, 650, 1300)
b = window_inverse('eckero-1929', 'marbyvagen-reference.json', 2450, 650, 1300)
pts = [a(*p) for p in [(900, 620)]] + \
      [b(*p) for p in [(743, 140), (745, 220), (746, 300), (745, 380), (744, 460), (740, 540), (733, 620), (722, 700), (712, 800), (705, 880), (700, 940), (692, 1000), (680, 1040)]]
path = [p3880] + [geo(q) for q in pts] + [end]
L = LineString([TO_METRIC(*q) for q in path])
mbl = LineString(json.load(open(f'{R}/data/marbyvagen-reference.json'))['metric'])
print('shore road', round(L.length, 1), 'm; ends at Marsund', round(REF.project(Point(TO_METRIC(*p3880)))), 'and Marbyvägen', round(mbl.project(Point(TO_METRIC(*end)))))
maps = {'1929-eckero': dict(sourceId='nls:map-39091228', year=1929), '1956-eckero': dict(sourceId='nls:map-37971493', year=1956)}
data = dict(
    schemaVersion=1, reviewedAt='2026-11-19',
    source=dict(id='review:hammarlandsvagen-shore', title='Strandvägen vid Holmbergssundet · granskning', url='assets/hammarlandsvagen-shore.json'),
    sources=[], maps=maps, early=[], earlyBasis={},
    method='Strandvägen avläst för hand på sockenkartan 1012 03 Eckerö 1929 (rutnät 50 m) och jämförd med utgåvan 1956 och OpenStreetMap 2026 (renders/ferry-landing-grid-1929-osm.jpg, shore-road-grid-1929.jpg, marbyvagen-north-1929-1956.jpg).',
    oldRoad=dict(id='road:eckero:gamla-landsvagen:strandvagen', name='Gamla landsvägen · strandvägen vid Holmbergssundet', routeId='road:Gamla landsvägen Eckerö', modernRoadClass='secondary', roadWidth=4,
                 firstYear=1929, until=1956, maps={'1929-eckero': 'present', '1956-eckero': 'absent'},
                 paths=[path], lengthMeters=round(L.length, 1), referenceRange=[3880, None], endSnapMeters=[0.0, 0.0], endSnapLimit=1,
                 endObjects=[M, MB],
                 basis='Landsvägen från färjan gick efter det smala sundet söderut längs stranden till Nissas, 45–80 m öster om dagens Marbyvägen. Sockenkartan 1929 ritar den; utgåvan 1956 ritar i stället vägen på Marbyvägens linje, och strandvägen inte alls. Inget av den finns i OpenStreetMap.',
                 traceBasis='Mittlinjen är avläst för hand på sockenkartan 1929 (rutnät 50 m) och inte flyttad; ändarna är fästa vid förbindelsens del från 1929 vid sundet och vid Marbyvägen vid Nissas.',
                 afterNote='Utgåvan 1956 ritar ingen väg här. Exakt när den togs ur bruk är inte känt.'),
    route=dict(order=[M, 'road:eckero:gamla-landsvagen:strandvagen', MB], endObjects=[M, MB], joinMeters=2.0))
json.dump(data, open('data/hammarlandsvagen-shore.json', 'w'), ensure_ascii=False, indent=1)
