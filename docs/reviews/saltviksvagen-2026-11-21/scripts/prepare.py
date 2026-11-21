"""Write data/saltviksvagen-east.json: Saltviksvägen from Saltviksvägen del 1 to Kvarnbo on the parish maps 1021 08
Tjudö–Dåglösa (1927) and 1021 07 Saltvik (1929), their 1941 and 1944 editions and the base maps 1968–1993.
Usage: prepare.py CATALOGUE.json.gz

Read on renders/sheet-*.jpg, andelsby-*.jpg, odkarby-*.jpg, prastgarden-*.jpg and kavelbro-*.jpg:
- The 1927/1929 road is today's road (within the sheet error: 20–40 m east, the same shape, at Ödkarby and Prästgården,
  where the 1968 map sits the same way) except at Andelsby.
- Andelsby: the 1927 and 1941 maps draw the road from the village north along today's Dåglösavägen for about 200 m and
  then east in a curve up to 150 m north of today's diagonal, back to today's road at Nygård. The diagonal is first on
  the 1968 map, which (with the 1978 map) still draws the curve as a lesser road; the 1984 map does not. The curve
  becomes the old-road object below, traced on the 1927 map.
- Kavelbro: the 1929 and 1944 maps and the 1968 map draw the road through the curve east of today's line, today's
  Kavelbrovägen; the straight bypass is first on the 1978 map (its earlier date).
The 1927 sheet ends just north of Saltviksvägen del 2; south of it the road is on the 1929 Saltvik sheet."""
import sys, json, gzip
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
import numpy as np, maps
from maps import tile_window
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
maps.MAPS['tjudo-1927'] = {'tiles_url': 'https://historicmaps2.vanhatkartat.fi/maps/mml/map-38157484/{z}/{x}/{y}.png'}
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
D1, TS, D2 = 'road:qgis:saltvik:saltviksvagen-1-batch4', 'road:qgis:tjudo:saltviksvagen-100km1', 'road:qgis:saltvik:saltviksvagen-2-batch4'
DG, ANT, KN = 'road:qgis:tjudo:daglosavagen-100km1', 'road:qgis:saltvik:saltviksvagen-antbole-nygard', 'road:qgis:saltvik:saltviksvagen-kavelbro-norr'
KAV, KK = 'road:qgis:saltvik:kavelbrovagen', 'road:qgis:saltvik:saltviksvagen-kvarnbo-kavelbro'
AND = 'road:tjudo:gamla-saltviksvagen:andelsby'
geo = lambda i: G[O[i]['geometryPeriods'][0]['geometryId']]
line = lambda i: LineString([TO_METRIC(*q) for q in geo(i)['paths'][0]])
r = lambda x: round(x, 1); togeo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
REF = LineString(json.load(open('docs/reviews/saltviksvagen-2026-11-21/data/reference.json'))['metric'])
ts, dg = line(TS), line(DG)

# The curve at Andelsby, read on renders/andelsby-tjudo-1927.jpg (900 px for 900 m around 1550 m along the reference),
# west to east: from the bend on the road north (today's Dåglösavägen) to where it meets today's road at Nygård.
cx, cy = REF.interpolate(1550).coords[0]; half, size = 450, 900
_, f = tile_window('tjudo-1927', 15, cx, cy, half, size)
E, N = np.meshgrid(np.linspace(cx - half, cx + half, 9), np.linspace(cy - half, cy + half, 9)); E, N = E.ravel(), N.ravel()
P = np.array([f(e, n) for e, n in zip(E, N)]); A = np.c_[P, np.ones(len(P))]
ce, cn = np.linalg.lstsq(A, E, rcond=None)[0], np.linalg.lstsq(A, N, rcond=None)[0]
inv = lambda x, y: (float(np.dot([x, y, 1], ce)), float(np.dot([x, y, 1], cn)))
px = [(300, 332), (350, 320), (400, 310), (450, 300), (490, 297), (525, 302), (560, 312), (590, 330), (620, 355), (645, 380), (675, 397), (725, 405)]
trace = [inv(x, y) for x, y in px]
bend = dg.project(Point(trace[0]))                 # where the old road leaves today's Dåglösavägen (its north end is 0)
rejoin = ts.project(Point(trace[-1]))              # where it meets today's road again (the Tjudö object runs east to west)
leave = ts.project(Point(dg.coords[-1]))           # the village end of Dåglösavägen on today's road
a, b = dg.interpolate(bend).coords[0], ts.interpolate(rejoin).coords[0]
mid = [q for q in trace[1:-1] if Point(q).distance(ts) > 12 and Point(q).distance(dg) > 12]
loop = [togeo(a)] + [togeo(q) for q in mid] + [togeo(b)]
loopL = LineString([TO_METRIC(*q) for q in loop])
snap = [r(Point(trace[0]).distance(Point(a))), r(Point(trace[-1]).distance(Point(b)))]
print('Dåglösavägen bend', r(bend), 'of', r(dg.length), '; Tjudö', r(rejoin), r(leave), 'of', r(ts.length), '; loop', r(loopL.length), 'm; trace ends', snap)

# Västergård–Laby: the 1929 road leaves Saltviksvägen del 1 at 500 m (its dated stretch since the Saltvik review),
# turns east past Bygge and runs north to the edge of the 1929 sheet; the Tjudö object begins at the edge of the 1927
# sheet. Every map has a sheet edge in the strip between them (1927/1929, 1941/1944, 1968), so the link is not drawn.
from shapely.ops import substring
d1 = LineString([TO_METRIC(*q) for q in G[O[D1]['geometryPeriods'][-1]['geometryId']]['paths'][0]])   # today's line; dated from 500 m
cut, west = substring(d1, 500.0, d1.length), substring(ts, leave, ts.length)
seam = min(Point(cut.coords[0]).distance(west), Point(cut.coords[-1]).distance(west), Point(west.coords[0]).distance(cut), Point(west.coords[-1]).distance(cut))
SEAM = ('Västergård–Laby: sockenkartan 1929 ritar vägen från Västergård österut förbi Bygge och norrut till bladkanten; '
        'Tjudö-objektet börjar vid bladkanten på kartan 1927. Alla kartor har bladkant i remsan däremellan (1927/1929, 1941/1944, 1968), '
        'så hur vägen gick där är inte ritat. Den diagonala sträckan genom Västergård ritas första gången 1978.')
L = {'1927-tjudo': dict(sourceId='nls:map-38157484', year=1927), '1941-daglosa': dict(sourceId='nls:map-38147690', year=1941),
     '1929-saltvik': dict(sourceId='nls:map-38157483', year=1929), '1944-saltvik': dict(sourceId='nls:map-38147682', year=1944),
     '1968-tjudo': dict(sourceId='nls:102108:1968', year=1968), '1978-tjudo': dict(sourceId='nls:102108:1978', year=1978),
     '1984-tjudo': dict(sourceId='nls:102108:1984', year=1984), '1968-saltvik': dict(sourceId='nls:102107:1968', year=1968)}
TJ_MAPS = {'1927-tjudo': 'present', '1941-daglosa': 'present'}
SA_MAPS = {'1929-saltvik': 'present', '1944-saltvik': 'present'}

def entry(oid, ranges, maps_, first, **kw):
    gg = geo(oid); Lg = line(oid)
    return dict(objectId=oid, inputHash=fingerprint(O[oid]), geometryId=gg['id'], geometryHash=digest(gg), lengthMeters=r(Lg.length),
                firstYear=first, until=O[oid]['states'][0]['from'], maps=maps_, ranges=ranges, **kw)
whole = lambda i: [[0.0, r(line(i).length)]]
early = [entry(TS, [[0.0, r(rejoin)], [r(leave), r(ts.length)]], TJ_MAPS, 1927),
         entry(DG, [[r(bend), r(dg.length)]], TJ_MAPS, 1927),
         entry(D2, whole(D2), {'1927-tjudo': 'present', '1929-saltvik': 'present'}, 1927),
         entry(ANT, whole(ANT), SA_MAPS, 1929),
         entry(KN, whole(KN), SA_MAPS, 1929),
         entry(KAV, whole(KAV), {**SA_MAPS, '1968-saltvik': 'present'}, 1929),
         entry(KK, whole(KK), SA_MAPS, 1929)]
data = dict(
    schemaVersion=1, reviewedAt='2026-11-21', reviewProperty='mainRoadReview', geometryPrefix='geometry:saltviksvagen-1927:',
    source=dict(id='review:saltviksvagen-east', title='Saltviksvägen från Tjudö till Kvarnbo på sockenkartorna 1927 och 1929 · granskning', url='assets/saltviksvagen-east.json'),
    sources=[], maps=L, early=early,
    earlyBasis={
        TS: 'Dagens väg genom Tjudö är vägen på sockenkartan 1927 och utgåvan 1941 (inom kartans lägesfel), utom vid Andelsby: där gick vägen norrut längs dagens Dåglösavägen och sedan i en båge österut till Nygård. Dagens diagonal där ritas första gången på grundkartan 1968.',
        DG: 'Vägens första 200 m från Andelsby by var en del av landsvägen till Saltvik: sockenkartan 1927 och utgåvan 1941 ritar landsvägen norrut här innan den svänger österut. Resten av Dåglösavägen är inte granskad här.',
        D2: 'En kort bit av dagens väg vid bladgränsen mellan sockenkartorna 1927 (Tjudö–Dåglösa) och 1929 (Saltvik); båda ritar landsvägen här.',
        ANT: 'Dagens väg från Ödkarby förbi Prästgården, Lagmansby och Antböle är vägen på sockenkartan 1929 och utgåvan 1944. Vid Ödkarby och Prästgården ligger kartans väg 20–40 m österut med samma form, liksom på grundkartan 1968: ett lägesfel, inte en annan väg.',
        KN: 'Dagens väg norr om Kavelbro är vägen på sockenkartan 1929 och utgåvan 1944.',
        KAV: 'Den gamla landsvägen genom kurvan vid Kavelbro. Sockenkartan 1929, utgåvan 1944 och grundkartan 1968 ritar landsvägen här; den raka förbifarten ritas först 1978.',
        KK: 'Dagens väg från Kavelbro till Kvarnbo är vägen på sockenkartan 1929 och utgåvan 1944.'},
    geometryNote='Del av objektets egen geometri (samma koordinater) där vägen är vägen på sockenkartorna 1927 och 1929.',
    oldRoad=dict(id=AND, name='Gamla Saltviksvägen · Andelsby', routeId='road:Gamla Saltviksvägen', modernRoadClass='secondary', roadWidth=4,
                 firstYear=1927, until=1984, maps={'1927-tjudo': 'present', '1941-daglosa': 'present', '1968-tjudo': 'present', '1978-tjudo': 'present', '1984-tjudo': 'absent'},
                 paths=[loop], lengthMeters=r(loopL.length), referenceRange=[1390, 1830], endSnapMeters=snap, endSnapLimit=25, endObjects=[TS, DG], todayRoadName='Saltviksvägen',
                 basis='Landsvägen från Andelsby gick först norrut längs dagens Dåglösavägen och sedan i en båge österut till Nygård, upp till 150 m norr om dagens diagonal. Sockenkartan 1927 och utgåvan 1941 ritar den som landsvägen; grundkartorna 1968 och 1978 ritar den som en mindre väg bredvid dagens diagonal; grundkartan 1984 ritar den inte.',
                 traceBasis='Mittlinjen är avläst för hand på sockenkartan 1927 (rutnät 50 m) och inte flyttad; ändarna är fästa vid Dåglösavägen och dagens väg där bågen lämnar och möter dem.',
                 afterNote='Grundkartan 1984 ritar inte bågen vid Andelsby, och nästan inget av den finns i OpenStreetMap. Exakt när den togs ur bruk är inte känt.'),
    route=dict(order=[D1, TS, DG, AND, TS, D2, ANT, KN, KAV, KK], endObjects=[D1], repeat=[TS], joinMeters=1.0,
               gaps=[dict(between=[D1, TS], meters=r(seam), basis=SEAM)]),
    method='Dagens väg jämförd för hand med sockenkartorna 1021 08 Tjudö–Dåglösa 1927 och 1021 07 Saltvik 1929 (rutnät 50 m), utgåvorna 1941 och 1944 och grundkartorna 1968, 1978, 1984 och 1993 (blad 102108, 102107), med OpenStreetMap 2026 inritat (docs/reviews/saltviksvagen-2026-11-21/renders/).')
json.dump(data, open('data/saltviksvagen-east.json', 'w'), ensure_ascii=False, indent=1)
print('seam gap', r(seam))
