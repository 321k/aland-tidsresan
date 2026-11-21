"""Write data/sodersundavagen.json and data/sodersundavagen-jomala.json: Södersundavägen from Mattas towards Jomala
church on the parish maps 1012 06 Hammarby (1929), its Näfsby–Emkarby print (1944) and 1012 09 Jomala (1928, 1955), and
the base maps 1012 09 (1968–1995). Usage: prepare.py CATALOGUE_BEFORE.json.gz

Read on renders/sheet-sod.jpg (the three sheets along Södersundavägen), al-*.jpg (the loop, 1928 and 1955),
al-base-1968-1985.jpg and al-base-1995.jpg:
- Södersundavägen (way 86548779) is the 1929/1928 road from Mattas to E 20 496 253, within 20–40 m and with the same
  shape (the S-curve through Ulvsby included).
- There the 1928 road turns north-east and runs round a loop past Al, along today's Drittel-Mattes Gränd, then east
  past Häggblom along today's S:t Olofs vägen to Godbyvägen at the church. The 1955 edition and the base maps 1968,
  1978 and 1985 draw the main road on the loop; the 1995 map draws today's straight and Nya Godbyvägen, and the loop as
  a local road.
Read by hand on al-9c76c492-*.jpg (780 px for 520 m) and stolof.jpg (900 px for 900 m), in EPSG:3874."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from hammarlandsvagen_main_road import _apply, metric
sys.path.insert(0, 'scripts'); from sodersundavagen import _coverage
from lemlandsvagen_main_road import cut
from shapely.geometry import LineString, Point

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
SV, GB = 'road:rural:hammarland-way-86548779', 'road:qgis:jomala:godbyvagen-batch5'
OLD = 'road:jomala:gamla-sodersundavagen:jomala-kyrkby'
r = lambda x: round(x, 1); togeo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
modern = {f['id']: f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']}
g = G[O[SV]['geometryPeriods'][-1]['geometryId']]; path = g['paths'][0]; line = metric(path)   # the whole way (from 2021); the earlier periods draw less of it
west_first = line.coords[0][0] > line.coords[-1][0]          # the way runs east to west
# where the 1928 road leaves today's line (al render: the double line at E 6253, N 1320)
leave_pt = Point(20496253, 6671320)
m = line.project(leave_pt)
# the west end: where the object's 1968–1995 geometry (the rural review) begins; west of it today's road is the 1995
# bypass past Mattas, and the old road came up from the old bend at Mattas (ways 495221553, 160987689) further east
g68 = G[O[SV]['geometryPeriods'][0]['geometryId']]['paths'][0]; west68 = min((g68[0], g68[-1]), key=lambda q: TO_METRIC(*q)[0])
mw = line.project(Point(TO_METRIC(*west68)))
keep = [m, mw] if west_first else [mw, m]                      # the stretch from the rural review's west end to the bend
gone = [0.0, m] if west_first else [m, line.length]
early_cut = cut(path, line, *keep); end_geo = early_cut[0] if west_first else early_cut[-1]
print('Södersundavägen', r(line.length), 'm; bend at', r(m), '; kept', [r(x) for x in keep], '; starts at the east end', west_first)

dr = modern['way/294650123']['paths'][0]; so = modern['way/1165936573']['paths'][0]
drittel = dr[1:][::-1]           # the old part (vertices 1–9), west to east; vertex 0 is the later link to today's road
bend = [(20496280, 6671347), (20496313, 6671387), (20496347, 6671427)]
link = [(20496720, 6671378), (20496770, 6671360), (20496815, 6671340)]
old = [end_geo] + [togeo(q) for q in bend] + drittel + [togeo(q) for q in link] + so
oldL = metric(old)
trace = [(20496253, 6671320), (20496280, 6671347), (20496313, 6671387), (20496347, 6671427), (20496380, 6671450), (20496407, 6671457), (20496460, 6671447),
         (20496540, 6671427), (20496613, 6671403), (20496673, 6671392), (20496720, 6671386), (20496750, 6671365), (20496810, 6671350), (20496900, 6671350),
         (20497000, 6671352), (20497090, 6671352)]
def canon(sub):
    a, b = oldL.project(Point(TO_METRIC(*sub[0]))), oldL.project(Point(TO_METRIC(*sub[-1])))
    return [round(min(a, b) / oldL.length, 6), round(max(a, b) / oldL.length, 6)]
print('old road', r(oldL.length), 'm; surviving', canon(drittel), canon(so))

L = {'1929-hammarby': dict(sourceId='nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08', year=1929), '1944-nafsby': dict(sourceId='nls:9c72a692-bae4-473d-93bb-7bcdee1222e7', year=1944),
     '1928-jomala': dict(sourceId='nls:9c76c492-3fb4-43dd-8cc7-eb03d2a00ecd', year=1928), '1955-jomala': dict(sourceId='nls:9c72a694-4f10-4780-beb7-d5d0d63ff0eb', year=1955),
     '1968-jomala': dict(sourceId='nls:101209:1968', year=1968), '1978-jomala': dict(sourceId='nls:101209:1978', year=1978),
     '1985-jomala': dict(sourceId='nls:101209:1985', year=1985), '1995-jomala': dict(sourceId='nls:101209:1995', year=1995),
     '1968-hammarby': dict(sourceId='nls:101206:1968', year=1968), '1978-hammarby': dict(sourceId='nls:101206:1978', year=1978),
     '1985-hammarby': dict(sourceId='nls:101206:1985', year=1985), '1995-hammarby': dict(sourceId='nls:101206:1995', year=1995)}
SOURCES = [dict(id='nls:9c76c492-3fb4-43dd-8cc7-eb03d2a00ecd', title='Lantmäteriverket · sockenkarta 1012 09 Jomala · 1928', issuedAt='1928',
                url='https://api.vanhatkartat.fi/api/maps/9c76c492-3fb4-43dd-8cc7-eb03d2a00ecd/image'),
           dict(id='nls:9c72a694-4f10-4780-beb7-d5d0d63ff0eb', title='Lantmäteriverket · sockenkarta 1012 09 Jomala · 1955 (svartvit utgåva)', issuedAt='1955',
                url='https://api.vanhatkartat.fi/api/maps/9c72a694-4f10-4780-beb7-d5d0d63ff0eb/image')]
review = dict(
    schemaVersion=1, reviewedAt='2026-11-21', reviewProperty='mainRoadReview', geometryPrefix='geometry:sodersundavagen-1929:',
    source=dict(id='review:sodersundavagen', title='Södersundavägen mot Jomala kyrka på sockenkartorna 1928 och 1929 · granskning', url='assets/sodersundavagen.json'),
    sources=SOURCES, maps=L,
    early=[dict(objectId=SV, inputHash=fingerprint(O[SV]), geometryId=g['id'], geometryHash=digest(g), lengthMeters=r(line.length), firstYear=1929,
                until=O[SV]['states'][0]['from'], maps={'1929-hammarby': 'present', '1944-nafsby': 'present'}, ranges=[[r(keep[0]), r(keep[1])]], laterGeometry=True)],
    earlyBasis={SV: 'Södersundavägen från Södersunda förbi Ulvsby är vägen på sockenkartan 1929 (Hammarby) och 1944 års tryck av samma kartläggning (Näfsby–Emkarby), inom 20–40 m och med samma form; sockenkartan 1928 för Jomala ritar den östra delen likadant. Den raka östligaste biten är yngre: där gick vägen i en båge norrut. Den västligaste biten är förbifarten vid Mattas från 1995.'},
    geometryNote='Del av objektets egen geometri (samma koordinater) där vägen är vägen på sockenkartorna 1928 och 1929.')
json.dump(review, open('data/sodersundavagen.json', 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat); rd = lambda p: review if p == 'data/sodersundavagen.json' else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p)))
_apply(rd, trial, 'data/sodersundavagen.json')
T = {o['id']: o for o in trial['objects']}; TG = {x['id']: x for x in trial['geometries']}
periods = [gp for gp in T[SV]['geometryPeriods'] if 1968 <= gp['from'] < 2021]
J68 = {'1968-jomala': 'present', '1978-jomala': 'present', '1985-jomala': 'present'}
CUT = 'Grundkartorna 1012 06 och 1012 09 ritar vägen från Södersunda genom Ulvsby fram till bågen mot kyrkan; den raka östligaste biten mot Nya Godbyvägen ritas först 1995. Tidigare visades bara delen på bladet 1012 06.'
WHOLE = 'Grundkartan 1012 09 1995 ritar hela dagens väg, med den raka östligaste biten mot Nya Godbyvägen. Tidigare visades bara delen på bladet 1012 06.'
sv_cov = dict(objectId=SV, inputHash=fingerprint(T[SV]), wholeGeometryId=g['id'], wholeGeometryHash=digest(g),
                          geometryNote='Del av objektets egen geometri (samma koordinater), från Mattas genom Ulvsby fram till bågen mot Jomala kyrka.',
                          periods=[dict(**{'from': gp['from'], 'to': gp['to']}, geometryId=gp['geometryId'],
                                        **(dict(range=[r(keep[0]), r(keep[1])], maps={k: v for k, v in J68.items() if gp['from'] <= L[k]['year'] < gp['to']}, basis=CUT) if gp['to'] <= 1995
                                           else dict(maps={'1995-jomala': 'present'}, basis=WHOLE))) for gp in periods])
review['coverage'] = [sv_cov]
json.dump(review, open('data/sodersundavagen.json', 'w'), ensure_ascii=False, indent=1)
_coverage(rd, trial, 'data/sodersundavagen.json')
T = {o['id']: o for o in trial['objects']}
SURVEY = 'road:jomala:gamla-sodersundavagen:survey'
al = dict(
    schemaVersion=1, reviewedAt='2026-11-21', reviewProperty='mainRoadReview',
    source=dict(id='review:sodersundavagen-jomala', title='Den gamla vägen till Jomala kyrka genom Ulvsby · granskning', url='assets/sodersundavagen-jomala.json'),
    sources=[dict(id=SURVEY, title='OpenStreetMap · Drittel-Mattes Gränd och S:t Olofs vägen, Jomala', url='https://www.openstreetmap.org/way/294650123', issuedAt='2026')],
    maps=L, connections=[dict(id=SV, hash=fingerprint(T[SV]), earlyPeriods=1)],
    oldRoads=[dict(
        id=OLD, name='Gamla Södersundavägen · Jomala kyrkby', routeId='road:Gamla Södersundavägen', modernRoadClass='secondary', roadWidth=4,
        firstYear=1928, mainUntil=1995, surveySourceId=SURVEY,
        maps={'1928-jomala': 'present', '1955-jomala': 'present', '1968-jomala': 'present', '1978-jomala': 'present', '1985-jomala': 'present', '1995-jomala': 'present'},
        mainUntilBasis='Grundkartan 1995 ritar dagens raka väg och Nya Godbyvägen som huvudväg; 1985 går vägen till kyrkan ännu i bågen genom Ulvsby.',
        paths=[old], lengthMeters=r(oldL.length), laterPaths=[drittel, so], laterCanonicalRanges=[canon(drittel), canon(so)],
        sourceLinks=[dict(datasetId='osm-2026', featureId='way/294650123', sourceVertexRange=[1, len(dr) - 1], sourceVertexCount=len(dr),
                          basis='Drittel-Mattes Gränd, den gamla vägens båge genom Ulvsby, som den kartlagts i dag. Vägens första bit från dagens Södersundavägen är en senare anslutning och ingår inte.'),
                     dict(datasetId='osm-2026', featureId='way/1165936573', sourceVertexRange=[0, len(so) - 1], sourceVertexCount=len(so),
                          basis='S:t Olofs vägen, den gamla vägens sista sträcka fram till Godbyvägen vid kyrkan, som den kartlagts i dag.')],
        trace=[list(q) for q in trace], sameRoadMeters=35,
        endsOn=[dict(path=0, end=-1, objectId=GB, basis='Vägen slutar vid Godbyvägen vid Jomala kyrka, mitt på det objektet.')],
        basis='Den gamla vägen från Hammarland till Jomala kyrka: från Södersundavägen vid Ulvsby i en båge norrut förbi Al, längs dagens Drittel-Mattes Gränd, och sedan österut förbi Häggblom längs dagens S:t Olofs vägen till kyrkan. Sockenkartan 1928 och utgåvan 1955 ritar den, och grundkartorna 1968, 1978 och 1985 ritar den som huvudväg.',
        traceBasis='Mittlinjen följer OpenStreetMap där vägen finns kvar (Drittel-Mattes Gränd, S:t Olofs vägen) och är avläst för hand på sockenkartan 1928 (rutnät 50 m) där inget finns kvar. Kartans väg ligger upp till 30 m norr om S:t Olofs vägen, med samma form.',
        laterBasis='Efter dagens raka väg (grundkartan 1995) visas bara de delar som finns kvar i dag: Drittel-Mattes Gränd och S:t Olofs vägen, med samma koordinater.')],
    method='Dagens vägar jämförda för hand med sockenkartorna 1012 06 Hammarby 1929 (och trycket Näfsby–Emkarby 1944) och 1012 09 Jomala 1928 och 1955 (rutnät 50 m) och grundkartorna 1012 09 1968–1995, med OpenStreetMap 2026 inritat (docs/reviews/hammarland-jomala-2026-11-21/renders/).')
json.dump(al, open('data/sodersundavagen-jomala.json', 'w'), ensure_ascii=False, indent=1)
review['method'] = al['method']; json.dump(review, open('data/sodersundavagen.json', 'w'), ensure_ascii=False, indent=1)
