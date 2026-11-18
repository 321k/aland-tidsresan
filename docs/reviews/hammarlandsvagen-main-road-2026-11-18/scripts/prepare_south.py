"""Write data/hammarlandsvagen-south.json: the older roads on the route Mariehamn–Söderby that the 1928/1929 parish
maps print, from the visual review (renders/south-*, route-*, utang-odanbole.jpg, natbacken-*.jpg).
Usage: prepare_south.py BEFORE_CATALOGUE.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from shapely.geometry import LineString, Point

R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
before = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in before['objects']}; G = {g['id']: g for g in before['geometries']}
L = LineString(json.load(open(f'{R}/data/reference.json'))['metric'])
MAPS = {m['id']: m for m in json.load(open('data/historical-map-sources.json'))['maps']}
HK, K44, K53 = '9c76c491-898b-4b0b-9331-7af223831264', '9c72a692-458e-4804-af82-e6ac6dbf73fe', '9c72a692-80ff-433c-950e-1cf484176101'
maps = {'1928': dict(sourceId='nls:' + HK, year=1928), '1929': dict(sourceId='nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08', year=1929),
        '1944-kungso': dict(sourceId='nls:' + K44, year=1944), '1944-nafsby': dict(sourceId='nls:9c72a692-bae4-473d-93bb-7bcdee1222e7', year=1944),
        '1953': dict(sourceId='nls:' + K53, year=1953)}
sources = [dict(id='nls:' + HK, title='Lantmäteriverket · sockenkarta 1012 05 Hammarudda–Kungsö · 1928', url=MAPS[HK]['original_url'], issuedAt='1928', viewer=f'https://vanhatkartat.fi/?map={HK}'),
           dict(id='nls:' + K44, title='Lantmäteriverket · sockenkarta 1012 05 Kungsö · 1944 (svartvit utgåva)', url=MAPS[K44]['original_url'], issuedAt='1944', viewer=f'https://vanhatkartat.fi/?map={K44}'),
           dict(id='nls:' + K53, title='Lantmäteriverket · sockenkarta 1012 05 Kungsö · 1953', url=MAPS[K53]['original_url'], issuedAt='1953', viewer=f'https://vanhatkartat.fi/?map={K53}')]
KUNGSO = {'1928': 'present', '1944-kungso': 'present', '1953': 'present'}
HAMMARBY = {'1929': 'present', '1944-nafsby': 'present'}
EAST = 'Den gamla huvudvägen österut från Söderby, via Östanträsk, Västansunda och Burs till Mattas i Södersunda. Sockenkartan 1929 (och utgåvan 1944) ritar den där dagens väg går, inom kartans lägesfel (10–30 m). Senatens kartverk 1917 ritar en huvudväg Söderby–Västansunda–Södersunda, men dess läge är för grovt för att knytas till en viss nutida väg; därför 1929.'
plan = [
    ('road:qgis:gottby:hammarlandsvagen-1-100km5', 'range', (4108, 5504), KUNGSO, 1928,
     'Biten Natbacken–Sagalund (4,1–5,5 km från Mariehamn) är den byväg som sockenkartan 1928 ritar; dagens väg följer den. Resten av del 1 är ny (rakan förbi Gottby, först på grundkartan 1978).'),
    ('road:qgis:gottby:utangsvagen-100km5', 'full', None, KUNGSO, 1928,
     'Sockenkartan 1928 ritar vägen i hela dess längd, och utgåvorna 1944 och 1953 betecknar den "Andelsl." (andelslagsväg). Den är en del av den äldre förbindelsen från Sviby mot Ödanböle.'),
] + [(f'road:rural:hammarland-way-{w}', 'full', None, HAMMARBY, 1929, EAST)
     for w in ('1422997221', '350329986', '350329985', '350329984', '350329848', '1422793394', '350329847', '160987691', '1422779920')]
early = []; basis = {}
for oid, kind, rr, mp, fy, b in plan:
    o = O[oid]; gid = o['geometryPeriods'][0]['geometryId']; g = G[gid]; line = LineString([TO_METRIC(*p) for p in g['paths'][0]])
    if kind == 'full':
        ranges = [[0.0, round(line.length, 1)]]
    else:
        p, q = sorted([line.project(Point(L.interpolate(d).coords[0])) for d in rr]); ranges = [[round(p, 1), round(q, 1)]]
    early.append(dict(objectId=oid, inputHash=fingerprint(o), geometryId=gid, geometryHash=digest(g), lengthMeters=round(line.length, 2),
                      ranges=ranges, firstYear=fy, until=o['states'][0]['from'], maps=mp, **({'referenceRange': list(rr)} if rr else {})))
    basis[oid] = b
    print(oid, o['states'][0]['from'], round(line.length), ranges)
data = dict(schemaVersion=1, reviewedAt='2026-11-18',
            source=dict(id='review:hammarlandsvagen-south', title='Hammarlandsvägens södra del och de äldre vägarna · granskning', url='assets/hammarlandsvagen-south.json'),
            sources=sources, maps=maps, geometryPrefix='geometry:hammarlandsvagen-south:',
            method='Dagens Hammarlandsväg söder om Söderby och de äldre vägarna mot Mariehamn jämförda med Senatens kartverk 1917, sockenkartorna 1928 (Hammarudda–Kungsö) och 1929 (Hammarby), deras utgåvor 1944 och 1953 samt grundkartorna 1968–1985 (renders/). Samma väg: kartans väg har dagens form inom omkring 25–30 m.',
            early=early, earlyBasis=basis)
json.dump(data, open('data/hammarlandsvagen-south.json', 'w'), ensure_ascii=False, indent=1)
