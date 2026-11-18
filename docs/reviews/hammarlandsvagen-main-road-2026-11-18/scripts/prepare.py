"""Write data/hammarlandsvagen-main-road.json: where today's Hammarlandsvägen between Söderby and the church is the
road drawn on the 1929 Hammarby parish map, and the old line at Smedens. Decisions are from the visual review
(renders/); boundaries are OSM junction nodes where the old road meets today's road, or measured points.
Usage: prepare.py BEFORE_CATALOGUE.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
from shapely.ops import substring

R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
before = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in before['objects']}; G = {g['id']: g for g in before['geometries']}
ref = json.load(open(f'{R}/data/reference.json')); L = LineString(ref['metric'])
B = {'soderby': 9005, 'drygsbole-south': 11824, 'drygsbole-north': 12405, 'bolstad': 12600, 'smedens-north': 14101,
     'nafsby-south': 14313, 'nafsby-north': 15255}
SAME = [('soderby', 'drygsbole-south'), ('drygsbole-north', 'bolstad'), ('smedens-north', 'nafsby-south'), ('nafsby-north', None)]
CHURCH_END = 17262.3          # end of the church corridor object, where the Kattby-west object (1959) begins
H1929, H1944 = 'nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08', 'nls:9c72a692-bae4-473d-93bb-7bcdee1222e7'
objs = ['road:rural:hammarland-way-345142933', 'road:rural:hammarland-way-345143750', 'road:rural:hammarland-hammarlandsvagen-vastmyra',
        'road:rural:hammarland-hammarlandsvagen-postad-korsangen', 'road:rural:hammarland-hammarlandsvagen-church-corridor']
same = [(B[a], B[b] if b else CHURCH_END) for a, b in SAME]
early = []
for oid in objs:
    o = O[oid]; gid = o['geometryPeriods'][0]['geometryId']; path = G[gid]['paths'][0]
    line = LineString([TO_METRIC(*p) for p in path])
    a0, a1 = sorted([L.project(Point(line.coords[0])), L.project(Point(line.coords[-1]))])
    rev = L.project(Point(line.coords[0])) > L.project(Point(line.coords[-1]))
    ranges = []
    for s, e in same:
        s2, e2 = max(s, a0), min(e, a1)
        if e2 - s2 < 1: continue
        p, q = line.project(Point(L.interpolate(s2).coords[0])), line.project(Point(L.interpolate(e2).coords[0]))
        if abs(s2 - a0) < 1: p = line.project(Point(L.interpolate(a0).coords[0])) if not rev else line.length
        r = sorted([round(p, 1), round(q, 1)])
        if r[0] < 1: r[0] = 0.0
        if line.length - r[1] < 1: r[1] = round(line.length, 1)
        ranges.append(r)
    ranges.sort()
    early.append(dict(objectId=oid, inputHash=fingerprint(o), geometryId=gid, geometryHash=digest(G[gid]), lengthMeters=round(line.length, 2),
                      referenceRange=[round(a0, 1), round(a1, 1)], ranges=ranges, firstYear=1929, until=o['states'][0]['from'],
                      maps={'1929': 'present', '1944': 'present'}))
for e in early: print(e['objectId'][-40:], e['referenceRange'], e['lengthMeters'], e['ranges'])

# The Smedens old line: the hand-read 1929 polyline between the two points where it leaves and rejoins today's road.
T = LineString(json.load(open(f'{R}/data/trace-smedens-1929.json'))['trace'])
pa, pb = Point(L.interpolate(B['bolstad']).coords[0]), Point(L.interpolate(B['smedens-north']).coords[0])
ta, tb = T.project(pa), T.project(pb)
old = substring(T, ta, tb); coords = list(old.coords); coords[0] = pa.coords[0]; coords[-1] = pb.coords[0]
old = LineString(coords)
snaps = [round(T.distance(pa), 1), round(T.distance(pb), 1)]
data = dict(
    schemaVersion=1, reviewedAt='2026-11-18',
    source=dict(id='review:hammarlandsvagen-main-road', title='Hammarlandsvägen på sockenkartan 1929 · granskning', url='assets/hammarlandsvagen-main-road.json'),
    sources=[dict(id=H1929, title='Lantmäteriverket · sockenkarta 1012 06 Hammarby · 1929',
                  url='https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_vari/map-39092401_500-20000-101206_pitajankartta_1929_karttalehti_101206_hammarby_v2.tif',
                  issuedAt='1929', viewer='https://vanhatkartat.fi/?map=9c72eaa7-cd73-4f92-91b0-dc36524bef08'),
             dict(id=H1944, title='Lantmäteriverket · sockenkarta 1012 06 Näfsby–Emkarby · 1944 (svartvit utgåva)',
                  url='https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_mv/map-37946377_500-20000-101206_pitajankartta_mv_1944_karttalehti_101206_nafsby-emkarby_v2.tif',
                  issuedAt='1944', viewer='https://vanhatkartat.fi/?map=9c72a692-bae4-473d-93bb-7bcdee1222e7')],
    maps={'1929': H1929, '1944': H1944},
    method='Dagens väg jämförd med sockenkartan 1929 (Hammarby, karttiler 2,4 m/px), dess svartvita utgåva 1944 och grundkartorna 1968–1995 i fönster var 250:e meter (renders/). Samma väg: 1929 års väg har dagens form inom omkring 25 m. Förbifarter: 1929 års väg går 25–115 m från dagens linje, eller inte alls i dess riktning.',
    boundaries={k: v for k, v in B.items()},
    reference=ref['metric'], sameRoad=[[s, e] for s, e in same],
    early=early,
    earlyBasis={
        'road:rural:hammarland-way-345142933': 'Söderby–Långträsk och biten vid Bolstad är samma väg som sockenkartan 1929 ritar (strandvägen längs Långträsk). Förbifarten vid Drygsböle (11,8–12,4 km) och den nya linjen förbi Smedens finns inte 1929; söder om Söderby är vägen ny (först på grundkartan 1968).',
        'road:rural:hammarland-way-345143750': 'De sista omkring 100 m vid Björkgård är den gamla vägen; linjen förbi Smedens söder om den är ny.',
        'road:rural:hammarland-hammarlandsvagen-vastmyra': 'Ändarna vid Mattas och vid Korsbroström är den gamla vägen. Mellan dem är dagens väg en förbifart öster om Näfsby; den gamla bygatan går genom byn och förbi Klaralund.',
        'road:rural:hammarland-hammarlandsvagen-postad-korsangen': 'Samma väg som sockenkartan 1929 ritar, inom kartans lägesfel (5–20 m).',
        'road:rural:hammarland-hammarlandsvagen-church-corridor': 'Samma väg som sockenkartan 1929 ritar förbi kyrkan och in i Kattby.'},
    oldRoad=dict(id='road:hammarland:gamla-hammarlandsvagen:smedens', name='Gamla Hammarlandsvägen · Smedens', routeId='road:Gamla Hammarlandsvägen',
                 modernRoadClass='secondary', roadWidth=4, firstYear=1929, until=1968,
                 maps={'1929': 'present', '1944': 'present', '1968': 'absent'},
                 path=[list(map(lambda v: round(v, 7), TO_GEO(*p))) for p in old.coords], lengthMeters=round(old.length, 1),
                 referenceRange=[B['bolstad'], B['smedens-north']], endSnapMeters=snaps,
                 basis='Den gamla vägen förbi Smedens och Djäknedal, 25–70 m väster om dagens väg. Sockenkartan 1929 (och utgåvan 1944) ritar den intill gården Smedens; grundkartan 1968 ritar bara dagens väg, omkring 35 m öster om gården. Linjen är avläst på sockenkartan 1929 och inte flyttad; ändarna är fästa vid dagens väg.',
                 traceBasis='Mittlinjen är avläst för hand på sockenkartan 1929 (rutnät 50 m, karttiler 2,4 m/px) och inte flyttad; ändarna är fästa vid dagens väg. Inget av den finns kvar som väg i OpenStreetMap.'),
    langskataFix=dict(objectId='road:qgis:mariehamn:langskata-2-100km3', note='The 1917–1985 partial period referred to the whole Långskata geometry, so the whole road was drawn from 1917; it now has its own cut geometry of the first 300 m.'))
json.dump(data, open('data/hammarlandsvagen-main-road.json', 'w'), ensure_ascii=False, indent=1)
print('old road', round(old.length), 'm, snaps', snaps)
