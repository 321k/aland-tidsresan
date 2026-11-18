"""Write data/hammarlandsvagen-nafsby.json: the old main road through Näfsby (1929 Hammarby parish map, 1944 edition)
as the smaller roads it survives as, and the short vanished link where it left today's road. Decisions are from the
visual review (renders/nafsby-*.jpg, data/trace-nafsby-1929.*).
Usage: prepare_nafsby.py BEFORE_CATALOGUE.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
from shapely.ops import substring

R = 'docs/reviews/hammarlandsvagen-main-road-2026-11-18'
before = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in before['objects']}; G = {g['id']: g for g in before['geometries']}
T = LineString(json.load(open(f'{R}/data/trace-nafsby-1929.json'))['trace'])
north = json.load(open('data/hammarlandsvagen-main-road.json'))
H29, H44 = 'nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08', 'nls:9c72a692-bae4-473d-93bb-7bcdee1222e7'
maps = {'1929': H29, '1944': H44, '1968': 'nls:101206:1968', '1978': 'nls:101206:1978'}
OLD = {'1929': 'present', '1944': 'present'}
P = 'road:rural:hammarland-'
VAST, LILL, PAR, ARM, EAST, SCHOOL = (P + 'hammarlandsvagen-vastmyra', P + 'way-545279820', P + 'way-1419026567', P + 'way-1419026568',
                                      P + 'vastmyra-old-school-approach-east', P + 'vastmyra-old-school-approach')
LILL_END = 85.0     # metres along Lillåkersgränd: beyond it the way turns south-west, away from the old road


def line_of(gid, i=0):
    return LineString([TO_METRIC(*p) for p in G[gid]['paths'][i]])


def entry(oid, ranges=None, gid=None, path_index=None, mp=OLD, until=None, gap=None, **extra):
    o = O[oid]; gid = gid or o['geometryPeriods'][0]['geometryId']; g = G[gid]
    lines = [line_of(gid, i) for i in range(len(g['paths']))]
    line = lines[path_index or 0]
    length = line.length if (len(lines) == 1 or path_index is not None) else sum(l.length for l in lines)
    e = dict(objectId=oid, inputHash=fingerprint(o), geometryId=gid, geometryHash=digest(g), lengthMeters=round(length, 2),
             ranges=ranges or [[0.0, round(length, 1)]], firstYear=1929, until=until or o['states'][0]['from'], maps=mp, **extra)
    if path_index is not None: e['pathIndex'] = path_index
    if gap: e['gapUntil'] = gap
    print(oid.split(':')[-1], o['states'][0]['from'], round(length, 1), e['ranges'], 'trace', [round(T.project(Point(l.coords[k]))) for l in lines for k in (0, -1)])
    return e


early = [
    entry(LILL, [[0.0, LILL_END]]),
    entry(PAR, mp={**OLD, '1968': 'unclear', '1978': 'unclear'}, until=1968, gap=1985),
    entry(ARM, gid='geometry:d8c47bbbb031baa04e9c', laterGeometry=True),
    entry(EAST),
    entry(SCHOOL, path_index=0),
]
# The vanished link: from where the old road leaves today's road (end of Västmyra's 1929 cut, north review) to
# Lillåkersgränd, along the line read on the 1929 map.
vr = next(r for r in north['early'] if r['objectId'] == VAST)['ranges'][0][1]
p0 = Point(line_of('geometry:6a90725882c05068b93c').interpolate(vr).coords[0])
assert O[VAST]['geometryPeriods'][1]['geometryId'] == 'geometry:6a90725882c05068b93c'
q = Point(line_of(O[LILL]['geometryPeriods'][0]['geometryId']).interpolate(LILL_END).coords[0])
def piece(a, b):
    """The 1929 line between two points on today's roads, ends fixed to those points."""
    ta, tb = T.project(a), T.project(b); mid = substring(T, ta, tb)
    line = LineString([a.coords[0]] + list(mid.coords)[1:-1] + [b.coords[0]])
    print('piece', round(line.length, 1), 'm, trace', round(ta), round(tb), 'snaps', round(T.distance(a), 1), round(T.distance(b), 1))
    return line, [round(T.distance(a), 1), round(T.distance(b), 1)]


link, s1 = piece(p0, q)
# Korsbroström: from the north end of the old school road (Klaralund–Korsbroström) up to today's road, where the
# north review's same-road stretch begins again. The school road's eastward branch is a younger junction.
school_end = Point(line_of(O[SCHOOL]['geometryPeriods'][0]['geometryId'], 0).coords[0])
cut1_start = Point(line_of('geometry:6a90725882c05068b93c').interpolate(next(r for r in north['early'] if r['objectId'] == VAST)['ranges'][1][0]).coords[0])
korsbro, s2 = piece(school_end, cut1_start)
snaps = s1 + s2
oid_link = 'road:hammarland:gamla-hammarlandsvagen:nafsby'
data = dict(
    schemaVersion=1, reviewedAt='2026-11-18',
    source=dict(id='review:hammarlandsvagen-nafsby', title='Den gamla vägen genom Näfsby · granskning', url='assets/hammarlandsvagen-nafsby.json'),
    sources=[], maps=maps, geometryPrefix='geometry:hammarlandsvagen-nafsby:',
    geometryNote='Del av objektets egen geometri (samma koordinater) där vägen är den gamla huvudvägen genom Näfsby på sockenkartan 1929.',
    method='Den gamla huvudvägen genom Näfsby avläst på sockenkartan 1929 (Hammarby, karttiler 2,4 m/px; data/trace-nafsby-1929.json) och jämförd med utgåvan 1944, grundkartorna 1968–1995 och OpenStreetMap 2026 (renders/nafsby-*). Samma väg: kartans väg ligger inom omkring 25 m från den nutida vägen och har dess form.',
    early=early,
    earlyBasis={
        LILL: 'De första omkring 85 m av Lillåkersgränd, från norr, är den gamla huvudvägen genom Näfsby som sockenkartan 1929 (och utgåvan 1944) ritar. Där svänger dagens gränd mot sydväst; den gamla vägen fortsatte mot sydost till dagens Hammarlandsväg.',
        PAR: 'Den gamla huvudvägen genom Näfsby, som sockenkartan 1929 (och utgåvan 1944) ritar här, längs västra sidan av dagens väg.',
        ARM: 'Den gamla huvudvägen genom Näfsby, från byn upp mot korsningen vid Krokgränd, som sockenkartan 1929 (och utgåvan 1944) ritar.',
        EAST: 'Den gamla huvudvägen genom Näfsby förbi Klaralund, som sockenkartan 1929 (och utgåvan 1944) ritar. Kartan ritar kröken vid Klaralund omkring 25 m söder om dagens väg, inom kartans lägesfel.',
        SCHOOL: 'Den gamla huvudvägen genom Näfsby, från Klaralund norrut mot Korsbroström, som sockenkartan 1929 (och utgåvan 1944) ritar. Den korta anslutningen österut till dagens Hammarlandsväg (vägens andra del) är yngre och dateras inte här.'},
    gapBasis={
        PAR: 'Grundkartorna 1968 och 1978 ritar bara en tunn linje längs den nya vägens västra kant här, inte säkert en väg; först 1985 är vägen ritad igen. Om den var i bruk däremellan är inte känt.'},
    oldRoad=dict(id=oid_link, name='Gamla Hammarlandsvägen · Näfsby', routeId='road:Gamla Hammarlandsvägen', modernRoadClass='secondary', roadWidth=4,
                 firstYear=1929, until=1968, maps={'1929': 'present', '1944': 'present', '1968': 'absent'},
                 paths=[[list(map(lambda v: round(v, 7), TO_GEO(*p))) for p in l.coords] for l in (link, korsbro)], lengthMeters=round(link.length + korsbro.length, 1),
                 referenceRange=[north['boundaries']['nafsby-south'], None], endSnapMeters=snaps, endSnapLimit=25,
                 endObjects=[VAST, LILL, SCHOOL],
                 basis='De två korta bitar av den gamla huvudvägen genom Näfsby som inte finns kvar: där den lämnade dagens väg vid Mattas och gick in i byn mot Lillåkersgränd, och sista biten norr om Klaralund upp till dagens väg vid Korsbroström. Sockenkartan 1929 (och utgåvan 1944) ritar dem; grundkartan 1968 ritar ingen väg där, och inget av dem finns i OpenStreetMap. Resten av den gamla vägen finns kvar som mindre vägar i byn.',
                 traceBasis='Mittlinjen är avläst för hand på sockenkartan 1929 (karttiler 2,4 m/px) och inte flyttad; ändarna är fästa vid dagens Hammarlandsväg, Lillåkersgränd och den gamla skolvägen.',
                 afterNote='Grundkartan 1968 ritar ingen väg här, och den finns inte i OpenStreetMap. Exakt när den togs ur bruk är inte känt.'),
    route=dict(order=[VAST, oid_link, LILL, PAR, ARM, EAST, SCHOOL, oid_link, VAST], endObjects=[VAST], repeat=[oid_link], joinMeters=2.0))
json.dump(data, open('data/hammarlandsvagen-nafsby.json', 'w'), ensure_ascii=False, indent=1)
