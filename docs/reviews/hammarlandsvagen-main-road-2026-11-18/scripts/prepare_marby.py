"""Write data/hammarlandsvagen-marby.json: the old road on the Eckerö side of the Marsund ferry, Marby–Klemes–Nissas.
- Marbyvägen (dated from 1968 by the QGIS review) is the 1929 road from Sundkvist past Klemes to Nissas (200–2 000 m
  along it; renders/marbyvagen-*.jpg). The 1956 edition draws the road on its whole line from Sundkvist north to the
  narrow sound (200 m to the end); in 1929 that northern part was a path and the road ran along the shore
  (renders/marbyvagen-north-1929-1956.jpg; the shore road is data/hammarlandsvagen-shore.json).
- The link at Sundkvist, from Marbyvägen (200 m) north-west to the connection at Marby (5 700 m), read on
  renders/sundkvist-marby-grid-1929.jpg and sundkvist-grid-1929.jpg. On the 1929 and 1956 maps, not on the 1968 base map.
Usage: prepare_marby.py CATALOGUE_BEFORE_THE_STEP.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
from grid_trace import window_inverse

R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
MB, M = 'road:qgis:eckero:marbyvagen-100km1', 'road:marsund:eckero-hammarland'
SUND, NISSAS = 200.0, 2000.0
o = O[MB]; gid = o['geometryPeriods'][0]['geometryId']; g = G[gid]; line = LineString([TO_METRIC(*p) for p in g['paths'][0]])
REF = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
early = G[O[M]['geometryPeriods'][0]['geometryId']]['paths']
p5700 = min((q for p in early for q in (p[0], p[-1])), key=lambda q: Point(TO_METRIC(*q)).distance(REF.interpolate(5700)))
assert Point(TO_METRIC(*p5700)).distance(REF.interpolate(5700)) < 1
geo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
a = window_inverse('eckero-1929', 'marsund-reference.json', 5560, 230, 920)
b = window_inverse('eckero-1929', 'marbyvagen-reference.json', 120, 260, 1040)
pts = [a(*p) for p in [(270, 400), (330, 450), (400, 530), (460, 580), (520, 610), (600, 620), (660, 650)]] + \
      [b(*p) for p in [(380, 470), (450, 550), (520, 610)]]
start = geo(line.interpolate(SUND).coords[0])
link = [p5700] + [geo(q) for q in pts] + [start]
L = LineString([TO_METRIC(*q) for q in link])
print('link', round(L.length, 1), 'm; Marsund 5700 snap', round(REF.distance(Point(TO_METRIC(*p5700))), 2), 'start on Marbyvägen', round(line.distance(Point(TO_METRIC(*start))), 2))
maps = {'1929-eckero': dict(sourceId='nls:map-39091228', year=1929), '1956-eckero': dict(sourceId='nls:map-37971493', year=1956),
        '1968': dict(sourceId='nls:101203:1968', year=1968), '1978': dict(sourceId='nls:101203:1978', year=1978)}
data = dict(
    schemaVersion=1, reviewedAt='2026-11-19',
    source=dict(id='review:hammarlandsvagen-marby', title='Landsvägen vid Marby och Klemes · granskning', url='assets/hammarlandsvagen-marby.json'),
    sources=[], maps=maps, geometryPrefix='geometry:hammarlandsvagen-marby:',
    geometryNote='Del av objektets egen geometri (samma koordinater) där Marbyvägen är landsvägen från Marsundsfärjan på sockenkartan 1929.',
    laterStageNote='Del av objektets egen geometri (samma koordinater) där Marbyvägen är landsvägen på sockenkartans utgåva 1956.',
    method='Marbyvägen och vägen vid Sundkvist jämförda med sockenkartan 1012 03 Eckerö 1929 och utgåvan 1956 (karttiler 2,4 m/px, rutnät 50 m), grundkartorna 1968 och 1978 (blad 101203) och OpenStreetMap 2026 (renders/marbyvagen-*.jpg, sundkvist-*.jpg, ferry-route-1968-1978.jpg).',
    early=[dict(objectId=MB, inputHash=fingerprint(o), geometryId=gid, geometryHash=digest(g), lengthMeters=round(line.length, 2),
                ranges=[[SUND, NISSAS]], firstYear=1929, until=o['states'][0]['from'],
                laterStage=dict(firstYear=1956, ranges=[[SUND, round(line.length, 1)]]),
                maps={'1929-eckero': 'present', '1956-eckero': 'present'})],
    earlyBasis={MB: 'Marbyvägen från Sundkvist förbi Klemes till Nissas är landsvägen från Marsundsfärjan som sockenkartan 1929 ritar, inom omkring 10 m från dagens väg (förbi Klemes inom omkring 30 m, med samma form). Norr om Nissas gick vägen 1929 längs stranden; Marbyvägen där var en stig.'},
    laterStageBasis={MB: 'Utgåvan 1956 ritar landsvägen på Marbyvägens hela sträckning från Sundkvist norrut till det smala sundet; strandvägen ritas inte längre. Den korta grenen norrut till dagens väg vid Sundkvist ritas först 1968.'},
    oldRoad=dict(id='road:eckero:gamla-landsvagen:sundkvist', name='Gamla landsvägen · Sundkvist', routeId='road:Gamla landsvägen Eckerö', modernRoadClass='secondary', roadWidth=4,
                 firstYear=1929, until=1968, maps={'1929-eckero': 'present', '1956-eckero': 'present', '1968': 'absent'},
                 paths=[link], lengthMeters=round(L.length, 1), referenceRange=[5700, None], endSnapMeters=[0.0, 0.0], endSnapLimit=1,
                 endObjects=[M, MB],
                 basis='Landsvägen från Sundkvist nordväst till Marby, där den gick in på dagens väg. Sockenkartan 1929 och utgåvan 1956 ritar den, 15–50 m söder om dagens väg. Grundkartan 1968 ritar den inte; då gick vägen via Marbyvägens gren norrut och dagens väg genom Marby.',
                 traceBasis='Mittlinjen är avläst för hand på sockenkartan 1929 (rutnät 50 m, renders/sundkvist-marby-grid-1929.jpg och sundkvist-grid-1929.jpg); ändarna är fästa vid förbindelsens del från 1929 vid Marby och vid Marbyvägen.',
                 afterNote='Grundkartan 1968 ritar ingen väg här. Exakt när den togs ur bruk är inte känt.'),
    route=dict(order=[M, 'road:eckero:gamla-landsvagen:sundkvist', MB], endObjects=[M], joinMeters=2.0))
json.dump(data, open('data/hammarlandsvagen-marby.json', 'w'), ensure_ascii=False, indent=1)
