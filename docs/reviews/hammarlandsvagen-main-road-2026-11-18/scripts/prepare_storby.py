"""Write data/hammarlandsvagen-storby.json: the old road through Storby village and the later bypass.
- The 1929 road leaves today's line at 10 230 m (from Frebbenby), runs south-west to Kars and curves west through the
  village (Hinders, Storby), rejoining today's line at 11 100 m. Read on renders/storby-mosaic-1929.jpg (Eckerö and
  Mörby sheets combined, 1 px/m). The 1968 base maps still draw it as the main road; the bypass is first drawn in 1978.
- Bypass: the connection's 1959–1985 period (already without the Överby bypass) is split at 1978; until then it leaves
  out 10 230–11 100 m.
Usage: prepare_storby.py CATALOGUE_BEFORE_THE_STEP.json.gz"""
import sys, json, gzip, copy
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
from grid_trace import window_inverse
import hammarlandsvagen_main_road as H

R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
M = 'road:marsund:eckero-hammarland'; m = O[M]
REF = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric']); LEN = REF.length
A, B = 10230.0, 11100.0
period = next(gp for gp in m['geometryPeriods'] if gp['from'] == 1959); g = G[period['geometryId']]
lines = [LineString([TO_METRIC(*q) for q in p]) for p in g['paths']]
span = [(REF.project(Point(l.coords[0])), REF.project(Point(l.coords[-1]))) for l in lines]
order = sorted(range(len(lines)), key=lambda i: span[i][0])
removed = []
for i, (s, e) in enumerate(span):
    a, b = max(s, A), min(e, B)
    if b - a > 0.5:
        la, lb = lines[i].project(REF.interpolate(a)), lines[i].project(REF.interpolate(b))
        removed.append([i, round(la, 2), round(min(lb, lines[i].length), 2)])
print('removed', removed)
canon = [[0.0, 6040.0], [6300.0, 6430.0], [7080.0, A], [B, LEN]]
canon = [[round(a / LEN, 6), round(b / LEN, 6)] for a, b in canon]
early = G[m['geometryPeriods'][0]['geometryId']]['paths']
def at(d):
    q = min((q for p in early for q in (p[0], p[-1])), key=lambda q: Point(TO_METRIC(*q)).distance(REF.interpolate(d)))
    assert Point(TO_METRIC(*q)).distance(REF.interpolate(d)) < 1, d
    return q
geo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
inv = window_inverse('eckero-1929', 'marsund-reference.json', 0, 550, 1100, center=(20475950, 6679050))
pts = [inv(*p) for p in [(1000, 460), (950, 540), (890, 610), (840, 670), (805, 720), (780, 750), (720, 775), (650, 790), (580, 790), (520, 770),
                         (450, 733), (380, 693), (310, 650), (240, 615)]]
start, end = at(A), at(B)
T = LineString([TO_METRIC(*start)] + pts + [TO_METRIC(*end)])
modern = json.load(gzip.open('dist/assets/modern.json.gz'))['features']
owned = {l['featureId'] for o in cat['objects'] for l in o.get('sourceLinks', []) if l.get('datasetId') == 'osm-2026'}
cands = [f['id'] for f in modern if f.get('kind') == 'road' and f.get('class') not in ('footway', 'path', 'cycleway', 'steps') and f['id'] not in owned
         and len(f['paths']) == 1 and LineString([TO_METRIC(*q) for q in f['paths'][0]]).intersection(T.buffer(20)).length >= 40]
print('candidates', cands)
from old_road_lib import old_line
feats = [f for f in modern if f['id'] in cands]
path, keep, ranges, total = old_line(start, end, T, feats)
print('old road', round(total, 1), 'm; surviving', [(k[0], k[1], k[2]) for k in keep], 'extents', ranges)
SURVEY = 'road:eckero:gamla-landsvagen-storby:survey'
maps = {'1929': dict(sourceId='nls:map-39091228', year=1929), '1929-morby': dict(sourceId='nls:map-38157016', year=1929),
        '1946': dict(sourceId='nls:map-38157019', year=1946), '1968-101203': dict(sourceId='nls:101203:1968', year=1968),
        '1968': dict(sourceId='nls:102101:1968', year=1968), '1978': dict(sourceId='nls:102101:1978', year=1978)}
OLD = 'road:eckero:gamla-landsvagen:storby'
review = dict(
    schemaVersion=1, reviewedAt='2026-11-19',
    source=dict(id='review:hammarlandsvagen-storby', title='Gamla landsvägen genom Storby · granskning', url='assets/hammarlandsvagen-storby.json'),
    sources=[dict(id=SURVEY, title='OpenStreetMap · vägarna genom Storby by', url='https://www.openstreetmap.org/way/433455766', issuedAt='2026')],
    maps=maps, geometryPrefix='geometry:hammarlandsvagen-storby:',
    bypass=dict(objectId=M, inputHash=fingerprint(m), geometryId=g['id'], geometryHash=digest(g), **{'from': 1959}, until=1978,
                pathOrder=order, removed=removed, canonicalRanges=canon, maps={'1968': 'absent', '1978': 'present'}),
    bypassBasis='Förbifarten norr om Storby by (10,23–11,10 km från Frebbenby) finns inte på grundkartan 1968, där huvudvägen ännu går genom byn via Kars. Grundkartan 1978 ritar den som huvudväg. Fram till dess visas förbindelsen här utan förbifarten; den gamla vägen genom byn är ett eget objekt.',
    bypassGeometryNote='Förbindelsens egen geometri (samma koordinater) utan förbifarterna vid Överby och Storby.',
    connection=M, connectionHash=None,
    oldRoads=[dict(id=OLD, name='Gamla landsvägen · Storby', routeId='road:Gamla landsvägen Eckerö', modernRoadClass='secondary', roadWidth=4, firstYear=1929, mainUntil=1978,
                   surveySourceId=SURVEY, maps={'1929': 'present', '1929-morby': 'present', '1946': 'present', '1968-101203': 'present', '1968': 'present'},
                   mainUntilBasis='Grundkartan 1978 ritar förbifarten som huvudväg; 1968 går huvudvägen ännu genom byn.',
                   paths=[path], lengthMeters=round(total, 1), laterPaths=[k[3] for k in keep], laterCanonicalRanges=ranges,
                   sourceLinks=[dict(datasetId='osm-2026', featureId=k[0], sourceVertexRange=[k[1], k[2]], sourceVertexCount=k[4],
                                     basis='Den del av vägen som ligger på den gamla landsvägen genom Storby (sockenkartan 1929).') for k in keep],
                   trace=[list(q) for q in T.coords], sameRoadMeters=20,
                   basis='Den gamla landsvägen genom Storby by: från dagens väg söderut till Kars och sedan västerut genom byn (Hinders) tillbaka till dagens väg. Sockenkartorna 1929 (Eckerö och Mörby) och utgåvan 1946 ritar den, och grundkartorna 1968 ritar den som huvudväg.',
                   traceBasis='Mittlinjen är avläst för hand på sockenkartorna 1929 (Eckerö och Mörby sammanfogade, rutnät 50 m) där inget finns kvar, och följer OpenStreetMap där vägen finns kvar (inom 20 m). Ändarna är fästa vid förbindelsens delar från 1929.',
                   laterBasis='Efter förbifarten (grundkartan 1978) visas bara de delar som finns kvar i dag som vägar i byn, med samma koordinater.')],
    method='Storby by på sockenkartorna 1012 03 Eckerö 1929 och 1021 01 Mörby 1929 (sammanfogade, rutnät 50 m), utgåvan 1946 (Bovik), grundkartorna 1968–1993 (blad 101203, 102101) och OpenStreetMap 2026 (renders/storby-*).')
# the connection as the old-road check will see it: after the bypass split
trial = copy.deepcopy(cat)
H._bypass(lambda p: review if p == 'data/hammarlandsvagen-storby.json' else None, trial, 'data/hammarlandsvagen-storby.json')
review['connectionHash'] = fingerprint(next(o for o in trial['objects'] if o['id'] == M))
json.dump(review, open('data/hammarlandsvagen-storby.json', 'w'), ensure_ascii=False, indent=1)
