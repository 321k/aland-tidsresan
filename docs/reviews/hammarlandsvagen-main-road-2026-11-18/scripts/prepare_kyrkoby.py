"""Write data/hammarlandsvagen-kyrkoby.json: the old main road beside today's road north of Kyrkoby (8 220–9 200 m from
Frebbenby, "från Storby"; partly today's Södra Bölevägen) and through Bagars (9 400–9 850 m), read on the 1929 Eckerö and
Mörby parish maps (renders/kyrkoby-north-grid-*.jpg, bagars-grid-1929-osm.jpg). Surviving parts: the OSM vertex runs
within 20 m of the trace. Usage: prepare_kyrkoby.py CATALOGUE_BEFORE_THE_STEP.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
from mariehamn_frame_1942 import fingerprint, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
from grid_trace import window_inverse

R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
M = 'road:marsund:eckero-hammarland'
REF = LineString(json.load(open(f'{R}/data/marsund-reference.json'))['metric'])
early = G[O[M]['geometryPeriods'][0]['geometryId']]['paths']
def at(d):
    q = min((q for p in early for q in (p[0], p[-1])), key=lambda q: Point(TO_METRIC(*q)).distance(REF.interpolate(d)))
    assert Point(TO_METRIC(*q)).distance(REF.interpolate(d)) < 1, d
    return q
geo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
modern = {f['id']: f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']}


def survivor(T, fid, limit=20):
    p = modern[fid]['paths'][0]; ok = [T.distance(Point(TO_METRIC(*q))) <= limit for q in p]
    runs, s = [], None
    for i, v in enumerate(ok + [False]):
        if v and s is None: s = i
        if not v and s is not None: runs.append((s, i - 1)); s = None
    a, b = max(runs, key=lambda r: LineString([TO_METRIC(*q) for q in p[r[0]:r[1] + 1]]).length if r[1] > r[0] else 0)
    run = p[a:b + 1]; L = LineString([TO_METRIC(*q) for q in run]).length
    print(' ', fid, modern[fid].get('name'), 'vertices', a, b, 'of', len(p), round(L), 'm, max off', round(max(T.distance(Point(TO_METRIC(*q))) for q in run), 1))
    return (fid, a, b, run) if L >= 40 else None


def old_line(start, end, T, fids, gap=10):
    surv = [s for s in (survivor(T, f) for f in fids) if s]
    pos = lambda q: T.project(Point(TO_METRIC(*q)))
    surv = [(f, a, b, run if pos(run[0]) < pos(run[-1]) else run[::-1]) for f, a, b, run in surv]
    surv.sort(key=lambda s: pos(s[3][0]))
    path, t = [start], pos(start)
    for f, a, b, run in surv:
        path += [geo(q) for q in T.coords if t + gap < T.project(Point(q)) < pos(run[0]) - gap] + run; t = pos(run[-1])
    path += [geo(q) for q in T.coords if t + gap < T.project(Point(q)) < pos(end) - gap] + [end]
    return path, surv


def entry(oid, name, start, end, pts, fids, basis, later_basis):
    T = LineString([TO_METRIC(*start)] + pts + [TO_METRIC(*end)])
    path, surv = old_line(start, end, T, fids)
    L = LineString([TO_METRIC(*q) for q in path]); total = L.length
    ranges = []
    for f, a, b, run in surv:
        k = next(i for i in range(len(path)) if path[i:i + len(run)] == run)
        s0 = LineString([TO_METRIC(*q) for q in path[:k + 1]]).length if k else 0.0
        ranges.append([round(s0 / total, 6), round((s0 + LineString([TO_METRIC(*q) for q in run]).length) / total, 6)])
    merged = []                 # runs that meet end to end (two OSM ways of one road) are one extent
    for r in sorted(ranges):
        if merged and r[0] - merged[-1][1] < 1e-5: merged[-1][1] = r[1]
        else: merged.append(list(r))
    ranges = merged
    print(oid, round(total, 1), 'm; surviving', [(f, a, b) for f, a, b, _ in surv], 'extents', ranges)
    return dict(id=oid, name=name, routeId='road:Gamla landsvägen Eckerö', modernRoadClass='secondary', roadWidth=4, firstYear=1929, mainUntil=1959,
                surveySourceId=SURVEY, maps={'1929': 'present', '1946': 'present'},
                mainUntilBasis='Förbindelsens antagande: dagens väg visas från 1959, då bron över Marsund öppnades; grundkartan 1968 ritar den som huvudväg. Mellan utgåvorna 1946/1956 och 1968 finns ingen karta här.',
                paths=[path], lengthMeters=round(total, 1), laterPaths=[run for _, _, _, run in surv], laterCanonicalRanges=ranges,
                sourceLinks=[dict(datasetId='osm-2026', featureId=f, sourceVertexRange=[a, b], sourceVertexCount=len(modern[f]['paths'][0]),
                                  basis='Den del av vägen som ligger på den gamla landsvägen (sockenkartan 1929); resten av vägen är yngre eller annan.') for f, a, b, _ in surv],
                trace=[list(q) for q in T.coords], sameRoadMeters=20, basis=basis,
                traceBasis='Mittlinjen är avläst för hand på sockenkartan 1929 (rutnät 50 m) där inget finns kvar, och följer OpenStreetMap där vägen finns kvar (inom 20 m). Ändarna är fästa vid förbindelsens delar från 1929.',
                laterBasis=later_basis)


SURVEY = 'road:eckero:gamla-landsvagen-kyrkoby:survey'
a = window_inverse('eckero-1929', 'marsund-reference.json', 8650, 450, 1350)
b = window_inverse('morby-1929', 'marsund-reference.json', 8800, 400, 1200)
c = window_inverse('morby-1929', 'marsund-reference.json', 9600, 300, 1200)
kyrkoby = [a(*p) for p in [(1050, 1150), (1040, 1090), (1000, 1040), (940, 1000), (880, 988), (800, 935), (700, 850), (620, 775), (550, 705), (450, 610), (380, 540), (330, 480), (260, 380), (200, 260)]] + \
          [b(*p) for p in [(230, 300), (215, 240), (200, 180)]]
bagars = [c(*p) for p in [(850, 735), (750, 752), (650, 758), (550, 752), (450, 735), (350, 708), (250, 684), (150, 672)]]
maps = {'1929': dict(sourceId='nls:map-39091228', year=1929), '1946': dict(sourceId='nls:map-38157019', year=1946),
        '1929-morby': dict(sourceId='nls:map-38157016', year=1929), '1956': dict(sourceId='nls:map-37971493', year=1956)}
roads = [
    entry('road:eckero:gamla-landsvagen:kyrkoby-bole', 'Gamla landsvägen · Kyrkoby–Böle', at(8220), at(9200), kyrkoby, ['way/638460378', 'way/638460377'],
          'Den gamla landsvägen norr om Kyrkoby ("från Storby"), väster om dagens raka väg: runt en kulle vid Furuboda och sedan nordväst till Kristiansund. Sockenkartorna 1929 (Eckerö och Mörby) och utgåvorna 1946 och 1956 ritar den. En del av den är dagens Södra Bölevägen.',
          'Efter att dagens raka väg tagit över visas bara de delar som finns kvar i dag (Södra Bölevägen), med samma koordinater.'),
    entry('road:eckero:gamla-landsvagen:bagars', 'Gamla landsvägen · Bagars', at(9400), at(9850), bagars, ['way/642668321'],
          'Den gamla landsvägen rakt genom Bagars, söder om dagens båge. Sockenkartan 1929 (Mörby) och utgåvan 1946 ritar den.',
          'Efter att dagens väg tagit över visas bara den del som finns kvar i dag, med samma koordinater.')]
roads[0]['maps'] = {'1929': 'present', '1929-morby': 'present', '1946': 'present', '1956': 'present'}     # Eckerö 1929/1956 (south), Mörby 1929/Bovik 1946 (north)
roads[1]['maps'] = {'1929-morby': 'present', '1946': 'present'}
data = dict(schemaVersion=1, reviewedAt='2026-11-19', connection=M, connectionHash=fingerprint(O[M]),
            source=dict(id='review:hammarlandsvagen-kyrkoby', title='Gamla landsvägen vid Kyrkoby och Bagars · granskning', url='assets/hammarlandsvagen-kyrkoby.json'),
            sources=[dict(id=SURVEY, title='OpenStreetMap · Södra Bölevägen och vägen genom Bagars', url='https://www.openstreetmap.org/way/638460377', issuedAt='2026')],
            maps=maps, oldRoads=roads,
            method='De gamla vägarna avlästa för hand på sockenkartorna 1012 03 Eckerö 1929 och 1021 01 Mörby 1929 (rutnät 50 m) och jämförda med utgåvan 1946 (Bovik), grundkartorna 1968–1993 (blad 101203, 102101) och OpenStreetMap 2026.')
json.dump(data, open('data/hammarlandsvagen-kyrkoby.json', 'w'), ensure_ascii=False, indent=1)
