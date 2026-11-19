"""Write data/langnasvagen.json and data/langnasvagen-skag.json from the catalogue before the step
(usage: prepare.py CATALOGUE.json.gz).

Read on the renders in ../renders (distances along today's road from the sound at Bergören):
- skag-close-1929.jpg (0.5 m/px): the old road from the crossing straight north to the corner in Skag village, then
  east. It leaves today's line at 600 m and is back within the sheet error (18 m) at 1 090 m.
- sodergard-close-1929.jpg (0.625 m/px): the old road north-east through Södergård, from 1 770 m (west of the farm track north) to
  2 370 m, where it is back on today's line.
- grid-*-1929.jpg, ov-*.jpg: the same-road stretches 0–600 m, 1 090–1 980 m (to where the road south to Åkerlund
  leaves today's line) and 2 370–3 220 m (Sjögård, where the 1929 road turns north to Nyabonds).
The 1929 sheet lies north of today's road here: about 30 m at the Södergård junction and 18 m east of Skag, and close
at the other trace ends. Each trace is moved south linearly from the offset at one end to that at the other.
"""
import sys, json, gzip
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
import numpy as np, maps
from maps import tile_window
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
from old_road_lib import old_line
maps.MAPS['lumparland-1929'] = {'tiles_url': 'https://historicmaps2.vanhatkartat.fi/maps/mml/map-39093010/{z}/{x}/{y}.png'}
D = 'docs/reviews/langnasvagen-2026-11-19'
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
MAIN = 'road:qgis:lumparland:langnasvagen-100km3'
g = G[O[MAIN]['geometryPeriods'][0]['geometryId']]; assert len(g['paths']) == 1
main = LineString([TO_METRIC(*q) for q in g['paths'][0]])
REF = LineString(json.load(open(f'{D}/data/reference.json'))['metric'])
geo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
on = lambda d: geo(main.interpolate(d).coords[0])
r = lambda x: round(x, 1)


def inverse(d, half, size):
    cx, cy = REF.interpolate(d).coords[0]
    _, f = tile_window('lumparland-1929', 15, cx, cy, half, size)
    E, N = np.meshgrid(np.linspace(cx - half, cx + half, 9), np.linspace(cy - half, cy + half, 9)); E, N = E.ravel(), N.ravel()
    P = np.array([f(e, n) for e, n in zip(E, N)]); A = np.c_[P, np.ones(len(P))]
    ce, cn = np.linalg.lstsq(A, E, rcond=None)[0], np.linalg.lstsq(A, N, rcond=None)[0]
    assert max(abs(A @ ce - E).max(), abs(A @ cn - N).max()) < 0.5
    return lambda x, y: (float(np.dot([x, y, 1], ce)), float(np.dot([x, y, 1], cn)))


def trace(d, half, size, px, south0, south1):
    inv = inverse(d, half, size); pts = [inv(*p) for p in px]; n = len(pts) - 1
    return [(e, nn - (south0 + (south1 - south0) * i / n)) for i, (e, nn) in enumerate(pts)]


S_LEAVE, S_BACK = 600.0, 1090.0                 # Skag
D_LEAVE, D_BACK = 1770.0, 2370.0                # Södergård
B_END, C_END = 1980.0, 3220.0
skag = trace(820, 260, 1040, [(345, 800), (375, 700), (410, 600), (440, 500), (462, 420), (487, 350), (520, 305), (560, 285), (620, 277),
                              (700, 283), (800, 290), (900, 295)], 0, 18)
sod = trace(2130, 330, 1056, [(50, 650), (100, 597), (200, 497), (300, 390), (347, 343), (413, 297), (507, 250), (600, 210)], 30, 0)

# Södergård: nothing survives (the step checks OSM); the trace with its ends on today's road.
sod_path = [on(D_LEAVE)] + [geo(q) for q in sod] + [on(D_BACK)]
sod_len = LineString([TO_METRIC(*q) for q in sod_path]).length

# Skag: the trace and the surviving track (its exact OSM coordinates where it lies within 20 m).
modern = {f['id']: f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']}
T = LineString([main.interpolate(S_LEAVE).coords[0]] + skag + [main.interpolate(S_BACK).coords[0]])
path, keep, ranges, total = old_line(on(S_LEAVE), on(S_BACK), T, [modern['way/349946241']])
print('Skag', r(total), 'm, surviving', [(f, a, b) for f, a, b, _, _ in keep], ranges, '; Södergård', r(sod_len), 'm')

S17, S29, S68 = 'nls:92062c61-d68d-43ef-b581-e9bdcdc8e0ba', 'nls:map-39093010', 'nls:101211:1968'
maps_ = {'1917': dict(sourceId=S17, year=1917), '1929': dict(sourceId=S29, year=1929), '1968': dict(sourceId=S68, year=1968)}
review = dict(
    schemaVersion=1, reviewedAt='2026-11-19', reviewProperty='mainRoadReview', geometryPrefix='geometry:langnasvagen:',
    source=dict(id='review:langnasvagen', title='Långnäsvägen vid Skag och Södergård · granskning', url='assets/langnasvagen.json'),
    sources=[], maps=maps_,
    early=[dict(objectId=MAIN, inputHash=fingerprint(O[MAIN]), geometryId=g['id'], geometryHash=digest(g), lengthMeters=r(main.length),
                firstYear=1917, until=1968, maps={'1917': 'present', '1929': 'present'},
                ranges=[[S_BACK, B_END], [D_BACK, C_END]],
                laterStage=dict(firstYear=1929, ranges=[[0.0, S_LEAVE], [S_BACK, B_END], [D_BACK, C_END]]))],
    earlyBasis={MAIN: 'Dagens väg från Skag österut till Södergård och vidare norrut längs Krokstadviken till Sjögård är vägen på Senatens karta 1917 och sockenkartan 1929 (inom kartbladets fel, upp till 30 m). '
                      'Undantagen: vid Skag gick vägen rakt norrut till ett skarpt hörn i byn, och vid Södergård gick den nordost genom byn. Dagens kurva vid Skag och sträckningen över åkrarna vid Södergård ritas första gången på grundkartan 1968. '
                      'Norr om Sjögård gick vägen 1929 norrut genom Nyabonds; dagens väg därifrån ritas första gången 1968.'},
    laterStageNote='Del av objektets egen geometri (samma koordinater) där dagens väg är vägen på sockenkartan 1929, nu också från sundet vid Bergören till Skag.',
    laterStageBasis={MAIN: 'Sockenkartan 1929 ritar vägen över sundet från Bergören och vidare till Skag. Senatens karta 1917 ritar ingen väg över sundet.'},
    geometryNote='Del av objektets egen geometri (samma koordinater) där dagens väg är vägen på Senatens karta 1917 och sockenkartan 1929.',
    oldRoad=dict(id='road:lumparland:gamla-landsvagen:sodergard', name='Gamla landsvägen · Södergård', routeId='road:Gamla landsvägen Lumparland', modernRoadClass='secondary', roadWidth=4,
                 firstYear=1917, until=1968, maps={'1917': 'present', '1929': 'present', '1968': 'unclear'},
                 untilBasis='Grundkartan 1968 ritar dagens väg som huvudväg; den gamla linjen ritas där bara delvis, som en mindre väg längs åkerkanterna. Den granskas inte längre fram.',
                 paths=[sod_path], lengthMeters=r(sod_len), referenceRange=[D_LEAVE, D_BACK], endSnapMeters=[0.0, 0.0], endSnapLimit=1, endObjects=[MAIN],
                 basis='Den gamla landsvägen nordost genom Södergård, från korsningen med vägen söderut mot Åkerlund till Krokstadviken. Sockenkartan 1929 ritar den; Senatens karta 1917 ritar vägen här men är för grov för formen. Inget av den finns i OpenStreetMap.',
                 traceBasis='Mittlinjen är avläst för hand på sockenkartan 1929 (rutnät 50 m) och flyttad söderut, 30 m vid korsningen och inget vid Krokstadviken (kartbladets fel mätt mot dagens väg). Ändarna ligger på dagens väg.',
                 afterNote='Grundkartan 1968 ritar dagens väg som huvudväg och den gamla linjen bara delvis, som en mindre väg. Senare kartor är inte granskade för den, och den finns inte i OpenStreetMap; det betyder inte att den försvann 1968.'),
    route=dict(order=[MAIN, 'road:lumparland:gamla-landsvagen:sodergard', MAIN], repeat=[MAIN], joinMeters=1.0),
    method='Dagens väg jämförd för hand med Senatens karta 1917, sockenkartan 1012 11 Lumparland 1929 (rutnät 50 m) och grundkartorna 1968, 1978, 1985 och 1995 (blad 101211), med OpenStreetMap 2026 inritat (renders/).')
json.dump(review, open('data/langnasvagen.json', 'w'), ensure_ascii=False, indent=1)

# The Skag review applies after the first one: the connection's fingerprint is taken after it.
sys.path.insert(0, 'scripts')
from hammarlandsvagen_main_road import _apply
import copy
after = copy.deepcopy(cat); _apply(lambda p: review if p == 'data/langnasvagen.json' else json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p)), after, 'data/langnasvagen.json')
M2 = next(o for o in after['objects'] if o['id'] == MAIN)
SURVEY = 'road:lumparland:gamla-landsvagen-skag:survey'
skag_review = dict(
    schemaVersion=1, reviewedAt='2026-11-19', connection=MAIN, connectionHash=fingerprint(M2), connectionEarlyPeriods=2,
    source=dict(id='review:langnasvagen-skag', title='Gamla landsvägen vid Skag · granskning', url='assets/langnasvagen-skag.json'),
    sources=[dict(id=SURVEY, title='OpenStreetMap · vägen vid Skag', url='https://www.openstreetmap.org/way/349946241', issuedAt='2026')],
    maps={'1929': dict(sourceId=S29, year=1929)},
    oldRoads=[dict(id='road:lumparland:gamla-landsvagen:skag', name='Gamla landsvägen · Skag', routeId='road:Gamla landsvägen Lumparland', modernRoadClass='secondary', roadWidth=4,
                   firstYear=1929, mainUntil=1968, surveySourceId=SURVEY, maps={'1929': 'present'},
                   mainUntilBasis='Grundkartan 1968 ritar dagens kurva som huvudväg och inget hörn i byn. Mellan 1929 och 1968 finns ingen karta här.',
                   paths=[path], lengthMeters=r(total), laterPaths=[run for _, _, _, run, _ in keep], laterCanonicalRanges=ranges,
                   sourceLinks=[dict(datasetId='osm-2026', featureId=f, sourceVertexRange=[a, b], sourceVertexCount=n,
                                     basis='Den del av stigen som ligger på den gamla landsvägen (sockenkartan 1929).') for f, a, b, _, n in keep],
                   trace=[list(q) for q in T.coords], sameRoadMeters=20,
                   basis='Den gamla landsvägen från sundet vid Bergören rakt norrut till ett skarpt hörn i Skag by och sedan österut. Sockenkartan 1929 ritar den. Senatens karta 1917 ritar ingen väg över sundet. En del av den är i dag en stig.',
                   traceBasis='Mittlinjen är avläst för hand på sockenkartan 1929 (rutnät 50 m), flyttad söderut upp till 18 m öster om hörnet (kartbladets fel mätt mot dagens väg), och följer OpenStreetMap där stigen ligger på den. Ändarna ligger på dagens vägs delar från 1929.',
                   laterBasis='Efter att dagens kurva tagit över visas bara den del som finns kvar i dag (en stig), med samma koordinater.')],
    method='Den gamla vägen avläst för hand på sockenkartan 1012 11 Lumparland 1929 (rutnät 50 m, renders/skag-close-1929.jpg) och jämförd med grundkartan 1968 och OpenStreetMap 2026.')
json.dump(skag_review, open('data/langnasvagen-skag.json', 'w'), ensure_ascii=False, indent=1)
