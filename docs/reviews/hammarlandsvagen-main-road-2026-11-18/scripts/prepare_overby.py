"""Write data/hammarlandsvagen-overby.json: the old road through Överby and the later bypass, from the visual review
(renders/overby-grid-1929*.jpg, overby-base-maps.jpg, overby-east-1956-1985.jpg, overby-west-1956-1985.jpg,
overby-bypass-symbol-1978.jpg) and the 1929 trace (data/trace-overby-1929.json).
- The old road: two loops north of today's road, 6 040–6 300 m and 6 430–7 080 m from Frebbenby. Where Brinkbacken
  (OSM way 1140848345, vertices 1–8) and Gamla Landsvägen (way 641674806, vertices 7–31) survive, their coordinates; in
  between, the trace; the ends are the Marsund connection's 1929 cut ends.
- The bypass: the Marsund connection's path 3 without 6 040–6 300 and 6 430–7 080 m until 1985.
Usage: prepare_overby.py CATALOGUE_BEFORE_THE_STEP.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point

R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
M = 'road:marsund:eckero-hammarland'; m = O[M]
early = G[m['geometryPeriods'][0]['geometryId']]['paths']          # Marsund 1929 cuts, in order along the road
late = next(gp for gp in m['geometryPeriods'] if gp['from'] == 1959); g = G[late['geometryId']]
T = LineString(json.load(open(f'{R}/data/trace-overby-1929.json'))['trace'])
modern = {f['id']: f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']}
met = lambda p: [TO_METRIC(*q) for q in p]
geo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
REF = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
ends_ = [q for p in early for q in (p[0], p[-1])]
at = lambda d: min(ends_, key=lambda q: Point(TO_METRIC(*q)).distance(REF.interpolate(d)))      # the cut end at d m along the connection
P6040, P6300, P6430, P7080 = at(6040), at(6300), at(6430), at(7080)
assert all(Point(TO_METRIC(*q)).distance(REF.interpolate(d)) < 1 for q, d in ((P6040, 6040), (P6300, 6300), (P6430, 6430), (P7080, 7080)))
for name, p in (('6040', P6040), ('6300', P6300), ('6430', P6430), ('7080', P7080)):
    print(name, 'on trace at', round(T.project(Point(TO_METRIC(*p)))), 'off', round(T.distance(Point(TO_METRIC(*p))), 1))


def run(fid, a, b):
    return modern[fid]['paths'][0][a:b + 1]


def loop(start, survivor, end, gap=10):
    """start → trace → survivor (in trace order) → trace → end; trace waypoints within `gap` m of a join are left out."""
    s_m = met(survivor)
    if T.project(Point(s_m[0])) > T.project(Point(s_m[-1])):
        survivor = survivor[::-1]; s_m = s_m[::-1]
    t0, t1 = T.project(Point(TO_METRIC(*start))), T.project(Point(s_m[0]))
    t2, t3 = T.project(Point(s_m[-1])), T.project(Point(TO_METRIC(*end)))
    way = lambda a, b: [geo(q) for q in T.coords if a + gap < T.project(Point(q)) < b - gap]
    return [start] + way(t0, t1) + survivor + way(t2, t3) + [end], survivor


BB, GL = ('way/1140848345', 1, 8), ('way/641674806', 7, 31)
east, bb = loop(P6040, run(*BB), P6300)
west, gl = loop(P6430, run(*GL), P7080)
lens = [LineString(met(p)).length for p in (east, west)]
total = sum(lens)


def span(path, part, base):
    k = next(i for i in range(len(path)) if path[i:i + len(part)] == part)
    a = LineString(met(path[:k + 1])).length if k else 0.0
    return [round((base + a) / total, 6), round((base + a + LineString(met(part)).length) / total, 6)]


ranges = [span(east, bb, 0.0), span(west, gl, lens[0])]
print('east', round(lens[0], 1), 'west', round(lens[1], 1), 'surviving ranges', ranges)
links = [dict(datasetId='osm-2026', featureId=f, sourceVertexRange=[a, b], sourceVertexCount=len(modern[f]['paths'][0]),
              basis='Den del av vägen som ligger på den gamla landsvägen genom Överby (sockenkartan 1929); resten av vägen är yngre.') for f, a, b in (BB, GL)]
order = list(reversed(range(len(g['paths'])))); pl = {i: LineString(met(g['paths'][i])) for i in order}
maps = {'1929-eckero': dict(sourceId='nls:map-39091228', year=1929), '1956-eckero': dict(sourceId='nls:map-37971493', year=1956),
        '1968': dict(sourceId='nls:101203:1968', year=1968), '1978': dict(sourceId='nls:101203:1978', year=1978), '1985': dict(sourceId='nls:101203:1985', year=1985)}
SURVEY = 'road:eckero:gamla-landsvagen-overby:survey'
data = dict(
    schemaVersion=1, reviewedAt='2026-11-19',
    source=dict(id='review:hammarlandsvagen-overby', title='Gamla landsvägen genom Överby · granskning', url='assets/hammarlandsvagen-overby.json'),
    sources=[dict(id=SURVEY, title='OpenStreetMap · Gamla Landsvägen och Brinkbacken i Överby', url='https://www.openstreetmap.org/way/641674806', issuedAt='2026')],
    maps=maps, geometryPrefix='geometry:hammarlandsvagen-overby:',
    method='Den gamla landsvägen genom Överby avläst för hand på sockenkartan 1929 för Eckerö (rutnät 50 m, renders/overby-grid-1929.jpg; data/trace-overby-1929.json) och jämförd med utgåvan 1956, grundkartorna 1968, 1978 och 1985 (blad 101203) och OpenStreetMap 2026 (renders/overby-*).',
    bypass=dict(objectId=M, inputHash=fingerprint(m), geometryId=g['id'], geometryHash=digest(g), **{'from': 1959}, until=1985,
                pathOrder=order, pathIndex=3, pathLength=round(pl[3].length, 2), keep=[[0.0, 76.02], [336.02, 466.02], [1116.02, round(pl[3].length, 2)]],
                maps={'1968': 'absent', '1978': 'unclear', '1985': 'present'}),
    bypassBasis='Förbifarten söder om Överby by (6,0–6,3 och 6,4–7,1 km från Frebbenby) finns inte på grundkartan 1968, där huvudvägen ännu går genom byn. Grundkartan 1978 ritar den som ett rött band utan kantlinjer, inte som en väg (påtryck; troligen planerad eller under byggnad). Först grundkartan 1985 ritar den som väg. Fram till dess visas förbindelsen här utan förbifarten; den gamla vägen genom byn är ett eget objekt.',
    bypassGeometryNote='Förbindelsens egen geometri (samma koordinater) utan förbifarten söder om Överby by.',
    oldRoad=dict(id='road:eckero:gamla-landsvagen:overby', name='Gamla landsvägen · Överby', routeId='road:Gamla landsvägen Eckerö', modernRoadClass='secondary', roadWidth=4,
                 firstYear=1929, mainUntil=1985, surveySourceId=SURVEY,
                 maps={'1929-eckero': 'present', '1956-eckero': 'present', '1968': 'present', '1978': 'present', '1985': 'present'},
                 paths=[east, west], lengthMeters=round(total, 1), laterPaths=[bb, gl], laterCanonicalRanges=ranges, sourceLinks=links,
                 trace=[list(q) for q in T.coords], sameRoadMeters=20,
                 basis='Den gamla landsvägen genom Överby by, i två slingor norr om dagens väg: förbi Henrikas (dagens Brinkbacken) och genom byn (dagens Gamla Landsvägen). Sockenkartan 1929 och utgåvan 1956 ritar den, och grundkartorna 1968 och 1978 ritar den som huvudväg. Grundkartan 1985 ritar förbifarten som huvudväg och den gamla vägen som mindre väg.',
                 traceBasis='Mittlinjen är avläst för hand på sockenkartan 1929 (rutnät 50 m) där inget finns kvar, och följer Brinkbacken och Gamla Landsvägen (OpenStreetMap) där de ligger på den gamla vägen, inom 17 m. Ändarna är fästa vid förbindelsens delar från 1929.',
                 laterBasis='Efter förbifarten (grundkartan 1985) visas bara de delar som finns kvar i dag: Brinkbacken och Gamla Landsvägen, med samma koordinater som tidigare. Grundkartan 1985 ritar mer av den gamla vägen som mindre väg; de delarna finns inte i OpenStreetMap.'))
json.dump(data, open('data/hammarlandsvagen-overby.json', 'w'), ensure_ascii=False, indent=1)
