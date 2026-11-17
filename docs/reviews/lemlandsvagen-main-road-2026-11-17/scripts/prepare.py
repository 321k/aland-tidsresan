"""Writes data/lemlandsvagen-main-road.json from the visual review of Lemlandsvägen del 1 on the early maps.

Run from the project root with the catalogue as it is just before the step:
    .venv-geo/bin/python docs/reviews/lemlandsvagen-main-road-2026-11-17/scripts/prepare.py BEFORE.json.gz
The decisions below were made by eye on the 1917 Senate atlas, the 1929 and 1948 parish maps and the 1968, 1978 and
1985 base maps of sheet 101208 (renders in ../renders). The old road was traced on the 1929 map between hand-picked
waypoints (../data/waypoints.json, scripts/trace_route.py); the traces are in ../data. This script only records the
decisions with fingerprints; the build step (scripts/lemlandsvagen_main_road.py) validates and applies them.
"""
import gzip, json, sys
from pathlib import Path
from shapely.geometry import LineString, Point
from shapely.ops import substring
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from mariehamn_lemlandsvagen_split import fractional_index, sub_path

HERE = Path(__file__).resolve().parents[1]
cat = json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
TARGET = 'road:qgis:mariehamn:lemlandsvagen-1-100km3'; LANGSKATA = 'road:qgis:mariehamn:langskata-2-100km3'
t = O[TARGET]; geo = G[t['geometryPeriods'][0]['geometryId']]; path = geo['paths'][0]
L = LineString([TO_METRIC(*p) for p in path])
ll = lambda xy: [round(c, 7) for c in TO_GEO(*xy)]

SENATE = dict(id='nls:92062c61-d68d-43ef-b581-e9bdcdc8e0ba', title='Senatens kartverk · Maarianhamina (V–VI 5–7) · 1917',
              url='https://astia.narc.fi/uusiastia/ws/getFile.php?fileId=5729498678&aineistoId=2388132142',
              issuedAt='1917', viewer='https://vanhatkartat.fi/?map=92062c61-d68d-43ef-b581-e9bdcdc8e0ba')
MAPS = {1917: SENATE['id'], 1929: 'nls:9c76c492-0456-43c6-9478-b2aa0034b26c', 1948: 'nls:9c72a694-1238-40a8-a8ca-33c754332810',
        1968: 'nls:101208:1968', 1978: 'nls:101208:1978', 1985: 'nls:101208:1985'}

# Section boundaries along today's road (metres from its western end), read from the 1929 traces (data/*.json).
B = dict(askelund=1526.0, kanal=3276.0, solstrand=4930.0, knutsboda=6290.0, dragsvik=7250.0, johans=8060.0, lindebo=8233.0)
P, A_ = 'present', 'absent'
SECTIONS = [
    dict(part='A', id='road:lemland:lemlandsvagen:kalmarnas-askelund', name='Lemlandsvägen · Kalmarnäs–Askelund', range=[0, B['askelund']], firstYear=1968,
         maps={1917: A_, 1929: A_, 1948: A_, 1968: P, 1978: P, 1985: P},
         basis='Den raka vägen från Kalmarnäs till Askelund saknas på sockenkartorna 1929 och 1948; den gamla vägen kom norrifrån längs Önningebyvägen till Askelund. Grundkartan 1968 är första karta som ritar dagens sträcka.'),
    dict(part='B', id='road:lemland:lemlandsvagen:askelund-lemstrom', name='Lemlandsvägen · Askelund–Lemströms kanal', range=[B['askelund'], B['kanal']], firstYear=1917,
         maps={1917: P, 1929: P, 1948: P, 1968: P, 1978: P, 1985: P},
         basis='Samma väg på alla kartor från Senatens kartverk 1917. På sockenkartan 1929 ligger vägen 3–10 m från dagens mittlinje vid Askelund och Björkelund och 15–30 m österut närmast norr om kanalen, där den går över bron på samma ställe som i dag. Avvikelsen kan vara kartbladets fel och räcker inte för att skilja ut en annan väg.'),
    dict(part='C', id='road:lemland:lemlandsvagen:tomtebo-solstrand', name='Lemlandsvägen · Tomtebo–Solstrand', range=[B['kanal'], B['solstrand']], firstYear=1968,
         maps={1917: 'unclear', 1929: A_, 1948: A_, 1968: P, 1978: P, 1985: P},
         basis='Ny sträckning väster om den gamla strandvägen. Sockenkartorna 1929 och 1948 ritar vägen från kanalbron österut förbi Tomtebo och längs stranden, 15–90 m från dagens mittlinje; den rör dagens väg bara vid Strömsnäs och vid Långbrinken. Grundkartan 1968 ritar huvudvägen här och den gamla vägen som mindre väg bredvid. Kartbladet 1968 ligger 30–60 m fel här, så bara vägarnas inbördes läge används.'),
    dict(part='D', id='road:lemland:lemlandsvagen:solstrand-knutsboda', name='Lemlandsvägen · Solstrand–Knutsboda', range=[B['solstrand'], B['knutsboda']], firstYear=1917,
         maps={1917: P, 1929: P, 1948: P, 1968: P, 1978: P, 1985: P},
         basis='Samma väg på alla kartor från Senatens kartverk 1917. Sockenkartan 1929 ritar den 5–22 m öster om dagens mittlinje (medianer per 150 m), i samma form; det är kartbladets fel, inte en flytt.'),
    dict(part='F1', id='road:lemland:lemlandsvagen:dragsvik-johans', name='Lemlandsvägen · Dragsvik–Johans', range=[B['dragsvik'], B['johans']], firstYear=1968,
         maps={1917: 'unclear', 1929: A_, 1948: A_, 1968: P, 1978: P, 1985: P},
         basis='Förbifarten norr om Johans. Sockenkartorna 1929 och 1948 ritar vägen söderut förbi Johans; grundkartan 1968 är första karta med dagens raka sträcka.'),
    dict(part='F2', id='road:lemland:lemlandsvagen:johans-lindebo', name='Lemlandsvägen · vid Lindebo', range=[B['johans'], B['lindebo']], firstYear=1917,
         maps={1917: P, 1929: P, 1948: P, 1968: P, 1978: P, 1985: P},
         basis='En kort bit där förbifarten följer den gamla vägen; sockenkartan 1929 ritar vägen inom 5 m från dagens mittlinje.'),
    dict(part='F3', id='road:lemland:lemlandsvagen:lindebo-kyrkby', name='Lemlandsvägen · Lindebo–kyrkbyn', range=[B['lindebo'], L.length], firstYear=1968,
         maps={1917: A_, 1929: A_, 1948: A_, 1968: P, 1978: P, 1985: P},
         basis='Förbifarten söder om Lindebo, Mangård och Söderby. Sockenkartorna 1929 och 1948 ritar den gamla vägen 100–340 m norrut genom byarna; grundkartan 1968 är första karta med dagens raka sträcka.'),
]
REMAINDER = dict(part='E', range=[B['knutsboda'], B['dragsvik']], name='Lemlandsvägen · Knutsboda–Dragsvik', firstYear=1985,
                 maps={1917: 'unclear', 1929: A_, 1948: A_, 1968: A_, 1978: 'unclear', 1985: P},
                 basis='Förbifarten öster om Övre-Börs. Grundkartorna 1968 och 1978 ritar huvudvägen genom Övre-Börs; 1978 syns dagens sträckning bara som ett ljust rött band (byggs eller planeras). Grundkartan 1985 är första karta med vägen.')

# Old road, traced on the 1929 map. Ranges are distances along each trace (data/trace-*.json).
OLD = [
    dict(id='road:lemland:gamla-lemlandsvagen:tomtebo-solstrand', name='Gamla Lemlandsvägen · Tomtebo–Solstrand', trace='stromsnas', along=[None, None], at=[B['kanal'], B['solstrand']], minTrace=190,
         maps={1917: P, 1929: P, 1948: P, 1968: P, 1978: P, 1985: 'unclear'},
         basis='Den gamla vägen från kanalbron förbi Tomtebo och längs stranden vid Strömsnäs, Långbrinken och Solstrand, öster om dagens väg. Grundkartorna 1968 och 1978 ritar den som mindre väg bredvid den nya huvudvägen; 1985 är den inte säker.'),
    dict(id='road:lemland:gamla-lemlandsvagen:ovre-bors-ostergard', name='Gamla Lemlandsvägen · Övre-Börs–Östergård', trace='old-main', along=[None, None], at=[B['knutsboda'], B['dragsvik']],
         maps={1917: P, 1929: P, 1948: P, 1968: P, 1978: P, 1985: P},
         basis='Den gamla vägen genom Övre-Börs och längs stranden förbi Östergård. Huvudväg på grundkartorna 1968 och 1978; 1985 går huvudvägen öster om byn. Delar finns kvar som Knutsbodavägen (OpenStreetMap). Grundkartorna 1968–1978 ritar sträckan Fridelund–Dragsvik rakare än 1929; om det är en rätning eller kartgeneralisering är inte avgjort, så 1929 års linje används.'),
    dict(id='road:lemland:gamla-lemlandsvagen:johans', name='Gamla Lemlandsvägen · Johans', trace='old-main', along=[None, None], at=[B['dragsvik'], B['johans']],
         maps={1917: P, 1929: P, 1948: P, 1968: P, 1978: P, 1985: P},
         basis='Den gamla vägen i en båge söderut förbi Johans. Grundkartorna 1968–1985 ritar den som mindre väg; en del finns kvar som Kockobacka (OpenStreetMap).'),
    dict(id='road:lemland:gamla-lemlandsvagen:mangard-soderby', name='Gamla Lemlandsvägen · Mangård–Söderby', trace='old-main', along=['langskata', None], at=[None, L.length],
         maps={1917: P, 1929: P, 1948: P, 1968: P, 1978: P, 1985: P},
         basis='Den gamla vägen från Långskatavägen förbi Mangård, Frankby, Nygård och Klockars till kyrkbyn. Grundkartorna 1968–1985 ritar den som byväg; stora delar finns kvar som Kommunrundan och Norra Söderbyvägen (OpenStreetMap), ännu inte sammanförda med denna enhet.'),
]
OLD_FROM = 1917
NEXT_EDITION = {1978: 1985, 1985: 1995}

traces = {n: LineString(json.load(open(HERE / 'data' / f'trace-{n}-1929.json'))['trace']) for n in ['stromsnas', 'old-main']}
lg = O[LANGSKATA]; lg_line = LineString([TO_METRIC(*p) for p in G[lg['geometryPeriods'][0]['geometryId']]['paths'][0]])
LG_END = 300.0  # Långskata del 2 follows the 1929 road for its first 300 m (5–18 m), then turns away to the east.


def trace_at_L(T, s, lo=0):
    """Distance along trace T (from lo on) of its point closest to today's road at distance s."""
    p = L.interpolate(s); best = min(range(int(lo), int(T.length), 2), key=lambda d: T.interpolate(d).distance(p))
    return float(best)


old = []
for spec in OLD:
    T = traces[spec['trace']]
    a = T.project(lg_line.interpolate(LG_END)) if spec['along'][0] == 'langskata' else trace_at_L(T, spec['at'][0], spec.get('minTrace', 0))
    b = trace_at_L(T, spec['at'][1])
    inner = list(substring(T, a, b).coords)[1:-1]
    start = lg_line.interpolate(LG_END).coords[0] if spec['along'][0] == 'langskata' else L.interpolate(spec['at'][0]).coords[0]
    end = L.interpolate(spec['at'][1]).coords[0]
    snaps = [round(Point(start).distance(T.interpolate(a)), 1), round(Point(end).distance(T.interpolate(b)), 1)]
    old.append(dict({k: v for k, v in spec.items() if k not in ('trace', 'along', 'at', 'maps', 'minTrace')}, traceId=spec['trace'], traceRange=[round(a, 1), round(b, 1)],
                    startsOn=LANGSKATA if spec['along'][0] == 'langskata' else None, todayRange=[spec['at'][0], round(spec['at'][1], 2)],
                    endSnapMeters=snaps, maps={str(k): v for k, v in spec['maps'].items()},
                    lastPresent=max(int(y) for y, v in spec['maps'].items() if v == P),
                    path=[ll(start)] + [ll(p) for p in inner] + [ll(end)]))
    old[-1]['until'] = NEXT_EDITION[old[-1]['lastPresent']]

# Source ownership: every source range of the original object is cut at the section boundaries.
modern = {f['id']: f for f in json.loads(gzip.decompress(open('dist/assets/modern.json.gz', 'rb').read()))['features']}
snap_sets = {f'osm-{y}': {f['id']: f for f in json.loads(gzip.decompress(open(f'dist/assets/roads-{y}.json.gz', 'rb').read()))['features']} for y in [2014, 2021, 2025]}
parts = sorted([dict(part=s['part'], range=s['range']) for s in SECTIONS] + [dict(part='E', range=REMAINDER['range'])], key=lambda s: s['range'][0])
cuts = sorted({b for s in parts for b in s['range']} - {0, L.length})
owner = lambda s: next(p['part'] for p in parts if p['range'][0] <= s < p['range'][1] or (p['range'][1] == L.length and s >= p['range'][1]))
links = {p['part']: [] for p in parts}
for l in t['sourceLinks']:
    src = (modern[l['featureId']] if l['datasetId'] == 'osm-2026' else snap_sets[l['datasetId']][l['featureId']])['paths'][0]
    a, b = l['sourceVertexRange']; S = LineString([TO_METRIC(*p) for p in sub_path(src, a, b)])
    ts = sorted(fractional_index(src, ll(L.interpolate(d).coords[0])) for d in cuts if S.distance(L.interpolate(d)) < 20)
    ts = [x for x in ts if a + 1e-6 < x < b - 1e-6]
    pieces = []
    for lo, hi in zip([a] + ts, ts + [b]):
        mid = LineString([TO_METRIC(*p) for p in sub_path(src, lo, hi)]).interpolate(0.5, normalized=True)
        part = owner(L.project(mid))
        if pieces and pieces[-1][0] == part:
            pieces[-1][2] = hi
        else:
            pieces.append([part, lo, hi])
    for part, lo, hi in pieces:
        links[part].append(dict(datasetId=l['datasetId'], featureId=l['featureId'], sourceVertexRange=[round(lo, 8), round(hi, 8)], sourceVertexCount=l['sourceVertexCount']))

lg_frac = round(LG_END / lg_line.length, 6)
review = dict(
    schemaVersion=1, reviewedAt='2026-11-17',
    source=dict(id='review:lemlandsvagen-main-road', title='Lemlandsvägen på de tidiga kartorna · granskning', url='assets/lemlandsvagen-main-road.json'),
    method=('Dagens Lemlandsvägen (del 1) jämfördes för hand med Senatens kartverk 1917, sockenkartorna 1929 och 1948 och grundkartorna 1968, 1978 och 1985. '
            'Den gamla vägen spårades på sockenkartan 1929 mellan handplacerade stödpunkter. På sträckor där gammal och ny väg sammanfaller ligger 1929 års väg 3–25 m '
            'från dagens mittlinje; avvikelser på 30–340 m med annan form räknas som annan väg. Grundkartorna 1968 och 1978 ligger 30–60 m fel i Lemland och används bara för '
            'vilka vägar som finns och deras inbördes läge. Kartår är belägg, inte byggår.'),
    sources=[SENATE], maps={str(k): v for k, v in MAPS.items()},
    target=dict(objectId=TARGET, inputHash=fingerprint(t), geometryId=geo['id'], geometryHash=digest(geo), lengthMeters=round(L.length, 2)),
    boundaries=B, sections=[dict(s, maps={str(k): v for k, v in s['maps'].items()}) for s in SECTIONS],
    remainder=dict(REMAINDER, maps={str(k): v for k, v in REMAINDER['maps'].items()}),
    sourceLinks=links,
    oldRoad=dict(routeId='road:Gamla Lemlandsvägen', modernRoadClass='secondary', roadWidth=3, firstYear=OLD_FROM, objects=old,
                 traceBasis='Mittlinjen är spårad på sockenkartan 1929 (karttiler 2,4 m/px) och inte flyttad; ändarna är fästa vid dagens väg eller Långskatavägen.'),
    langskata=dict(objectId=LANGSKATA, inputHash=fingerprint(lg), canonicalRange=[0, lg_frac], lengthMeters=round(LG_END, 1), firstYear=OLD_FROM, until=1985,
                   maps={'1917': P, '1929': P, '1948': P, '1968': P, '1978': P},
                   basis='Långskatavägens första 300 m är den gamla Lemlandsvägen mot Lindebo; sockenkartan 1929 ritar vägen 5–18 m från dagens mittlinje. Resten av Långskatavägen är yngre.'),
)
out = Path('data/lemlandsvagen-main-road.json'); out.write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print({p: len(v) for p, v in links.items()}, [(o['id'].rsplit(':', 1)[1], o['traceRange'], o['endSnapMeters'], len(o['path'])) for o in old])
