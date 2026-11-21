"""Write data/getavagen-tjudo-geta.json: Getavägen through Tjudö and Geta on the 1927 parish maps 1021 08 Tjudö–Dåglösa
and 1021 05 Geta, their 1941 editions and the base maps 1968–1984. Usage: prepare_tjudo_geta.py CATALOGUE.json.gz

Read on renders/ref-*-1927.jpg, fenell-*.jpg, skraddars-*.jpg, st-*.jpg and base-*-1978.jpg:
- The 1927 road is today's road (within the sheet error; 30–40 m near Klevberg and Höckböle, the same shape, kept as one
  road) except at two places.
- Fenell–Dala: the 1927 and 1941 maps draw the road in a loop up to 170 m east past Lignell, which the 1968 and 1978
  base maps still draw as a lesser road and the 1984 map no longer draws. Today's diagonal is first on the 1968 map.
  Almost nothing of the loop is in OSM. It becomes the old-road object below, traced on the 1927 map.
- Östergeta: the 1927 map and the 1968 base map draw the main road along today's Skräddarsvägen; today's straight is
  first on the 1984 map (the earlier review's date).
Västanträsk and Örang, where the earlier review noted a straightening, are the same road on the 1927 map."""
import sys, json, gzip
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
import numpy as np, maps
from maps import tile_window
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
maps.MAPS['tjudo-1927'] = {'tiles_url': 'https://historicmaps2.vanhatkartat.fi/maps/mml/map-38157484/{z}/{x}/{y}.png'}
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
TJ, GD, SK = 'road:qgis:tjudo:getavagen-100km1', 'road:qgis:geta:getavagen-1-200km2', 'road:qgis:geta:skraddarsvagen-200km2'
geo = lambda i: G[O[i]['geometryPeriods'][0]['geometryId']]
line = lambda i: LineString([TO_METRIC(*q) for q in geo(i)['paths'][0]])
r = lambda x: round(x, 1); togeo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
REF = LineString(json.load(open('docs/reviews/getavagen-2026-11-20/data/reference.json'))['metric'])
t, gd, sk = line(TJ), line(GD), line(SK)
# Fenell: the loop leaves today's road at 11 160 m along the reference and runs south to the sheet edge, where the Tjudö object begins (10 391 m)
back, leave = t.project(REF.interpolate(10600)), t.project(REF.interpolate(11160))
cx, cy = REF.interpolate(10700).coords[0]; half, size = 450, 900
_, f = tile_window('tjudo-1927', 15, cx, cy, half, size)
E, N = np.meshgrid(np.linspace(cx - half, cx + half, 9), np.linspace(cy - half, cy + half, 9)); E, N = E.ravel(), N.ravel()
P = np.array([f(e, n) for e, n in zip(E, N)]); A = np.c_[P, np.ones(len(P))]
ce, cn = np.linalg.lstsq(A, E, rcond=None)[0], np.linalg.lstsq(A, N, rcond=None)[0]
inv = lambda x, y: (float(np.dot([x, y, 1], ce)), float(np.dot([x, y, 1], cn)))
px = [(540, 470), (542, 400), (540, 330), (520, 290), (470, 250), (420, 222), (360, 195), (300, 185), (240, 178), (180, 172)]   # south to north
# the pixel positions were read on the 700 px contact sheet of renders/fenell-tjudo-1927.jpg (900 px): scale them up
trace = [inv(x * 900 / 700, y * 900 / 700) for x, y in px]
# The 1927 road runs on south to the sheet edge (the last trace point); the Saltvik sheet south of it draws the road on
# today's line, so the loop joins today's road straight across from there (a seam of about 50 m between the sheets).
px = [(540, 500)] + px
trace = [inv(x * 900 / 700, y * 900 / 700) for x, y in px]
back = t.project(Point(trace[0]))
assert back < 1, 'the sheet edge is where the Tjudö object begins, at the end of the Saltvik object'
back = 0.0
a, b = t.interpolate(back).coords[0], t.interpolate(leave).coords[0]
mid = [q for q in trace if Point(q).distance(t) > 12]
loop = [togeo(a)] + [togeo(q) for q in mid] + [togeo(b)]
loopL = LineString([TO_METRIC(*q) for q in loop])
# Östergeta: Skräddarsvägen's ends on today's road
ska, skb = sorted([gd.project(Point(sk.coords[0])), gd.project(Point(sk.coords[-1]))])
print('Tjudö', r(back), r(leave), 'of', r(t.length), '; loop', r(loopL.length), 'm; Geta', r(ska), r(skb), 'of', r(gd.length))
T27, G27, D41, G41 = 'nls:map-38157484', 'nls:map-38157399', 'nls:map-38147690', 'nls:map-38138095'
labels = {'1927-tjudo': dict(sourceId=T27, year=1927), '1927-geta': dict(sourceId=G27, year=1927), '1941-daglosa': dict(sourceId=D41, year=1941),
          '1941-geta': dict(sourceId=G41, year=1941), '1968': dict(sourceId='nls:102108:1968', year=1968), '1978': dict(sourceId='nls:102108:1978', year=1978),
          '1984': dict(sourceId='nls:102108:1984', year=1984), '1968-geta': dict(sourceId='nls:102105:1968', year=1968)}
def entry(oid, ranges, maps_, **kw):
    gg = geo(oid); L = line(oid)
    return dict(objectId=oid, inputHash=fingerprint(O[oid]), geometryId=gg['id'], geometryHash=digest(gg), lengthMeters=r(L.length),
                firstYear=1927, until=O[oid]['states'][0]['from'], maps=maps_, ranges=ranges, **kw)
early = [entry(TJ, [[r(leave), r(t.length)]], {'1927-tjudo': 'present', '1941-daglosa': 'present', '1968': 'present'},
               laterStage=dict(firstYear=1968, ranges=[[0.0, r(t.length)]])),
         entry(GD, [[0.0, r(ska)], [r(skb), r(gd.length)]], {'1927-geta': 'present', '1941-geta': 'present'}),
         entry(SK, [[0.0, r(sk.length)]], {'1927-geta': 'present', '1941-geta': 'present', '1968-geta': 'present'})]
FEN = 'road:tjudo:gamla-getavagen:fenell'
src = lambda i, t_, u: dict(id=i, title=t_, issuedAt=i[-4:] if False else t_[-4:], url=u)
data = dict(
    schemaVersion=1, reviewedAt='2026-11-20', reviewProperty='mainRoadReview', geometryPrefix='geometry:getavagen-1927:',
    source=dict(id='review:getavagen-tjudo-geta', title='Getavägen i Tjudö och Geta på sockenkartorna 1927 · granskning', url='assets/getavagen-tjudo-geta.json'),
    sources=[src(T27, 'Lantmäteriverket · sockenkarta 1021 08 Tjudö–Dåglösa · 1927', 'https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_vari/map-38157484_500-20000-102108_pitajankartta_1927_karttalehti_102108_tjudo-daglosa_v2.tif'),
             src(G27, 'Lantmäteriverket · sockenkarta 1021 05 Geta · 1927', 'https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_vari/map-38157399_500-20000-102105_pitajankartta_1927_karttalehti_102105_geta_v2.tif'),
             src(D41, 'Lantmäteriverket · sockenkarta 1021 08 Dåglösa · 1941', 'https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_mv/map-38147690_500-20000-102108_pitajankartta_mv_1941_karttalehti_102108_daglosa_v2.tif'),
             src(G41, 'Lantmäteriverket · sockenkarta 1021 05 Geta · 1941', 'https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_mv/map-38138095_500-20000-102105_pitajankartta_mv_1941_karttalehti_102105_geta_v2.tif')],
    maps=labels, early=early,
    earlyBasis={
        TJ: 'Dagens väg genom Tjudö är vägen på sockenkartan 1927 och utgåvan 1941 (inom kartans lägesfel), utom vid Fenell och Dala: där gick vägen i en båge österut förbi Lignell. Dagens diagonal där ritas första gången på grundkartan 1968.',
        GD: 'Dagens väg genom Geta är vägen på sockenkartan 1927 och utgåvan 1941, utom vid Östergeta: där gick vägen i en kurva österut, dagens Skräddarsvägen. Dagens raka sträcka där ritas första gången på grundkartan 1984.',
        SK: 'Den gamla huvudvägen i kurvan vid Östergeta. Sockenkartan 1927, utgåvan 1941 och grundkartan 1968 ritar den som landsvägen; dagens raka sträcka ritas först 1984.'},
    laterStageNote='Objektets hela geometri: diagonalen vid Fenell ritas från grundkartan 1968.',
    laterStageBasis={TJ: 'Grundkartan 1968 ritar dagens diagonal vid Fenell som huvudväg; den gamla bågen förbi Lignell ritas där som en mindre väg.'},
    geometryNote='Del av objektets egen geometri (samma koordinater) där vägen är vägen på sockenkartan 1927.',
    oldRoad=dict(id=FEN, name='Gamla Getavägen · Fenell', routeId='road:Gamla Getavägen', modernRoadClass='secondary', roadWidth=4,
                 firstYear=1927, until=1984, maps={'1927-tjudo': 'present', '1941-daglosa': 'present', '1968': 'present', '1978': 'present', '1984': 'absent'},
                 paths=[loop], lengthMeters=r(loopL.length), referenceRange=[10600, 11160], endSnapMeters=[0.0, 0.0], endSnapLimit=1, endObjects=[TJ], todayRoadName='Getavägen',
                 basis='Landsvägen vid Fenell och Dala gick i en båge österut förbi Lignell, upp till 170 m från dagens diagonal. Sockenkartan 1927 och utgåvan 1941 ritar den som landsvägen; grundkartorna 1968 och 1978 ritar den som en mindre väg bredvid dagens diagonal; grundkartan 1984 ritar den inte.',
                 traceBasis='Mittlinjen är avläst för hand på sockenkartan 1927 (rutnät 50 m) och inte flyttad; ändarna är fästa vid dagens väg där bågen lämnar och möter den.',
                 afterNote='Grundkartan 1984 ritar inte bågen förbi Lignell, och nästan inget av den finns i OpenStreetMap. Exakt när den togs ur bruk är inte känt.'),
    route=dict(order=['road:qgis:saltvik:getavagen-godby-norra-bladgransen', FEN, TJ, GD, SK, GD], endObjects=['road:qgis:saltvik:getavagen-godby-norra-bladgransen'], repeat=[GD], joinMeters=1.0),
    method='Dagens väg jämförd för hand med sockenkartorna 1021 08 Tjudö–Dåglösa och 1021 05 Geta 1927 (rutnät 50 m), utgåvorna 1941 och grundkartorna 1968, 1978, 1984 och 1993 (blad 102108, 102105), med OpenStreetMap 2026 inritat (docs/reviews/getavagen-2026-11-20/renders/).')
for s in data['sources']: s['issuedAt'] = s['title'][-4:]
json.dump(data, open('data/getavagen-tjudo-geta.json', 'w'), ensure_ascii=False, indent=1)
