"""Write data/lemlandsvagen-east.json from the catalogue before the step (usage: prepare.py CATALOGUE.json.gz).

Read on the renders in ../renders:
- ov-lumparland-1929-*.jpg, simons-*-grid-1929.jpg, delsviken-grid-1929.jpg: the 1929 parish map 1012 11 Lumparland
- ov-senate-1917-*.jpg: the 1917 Senate atlas (presence only; too coarse for position)
- ov-101211-1968-*.jpg, simons-*-1985.jpg, simons-wide-1995.jpg: the base maps
No line is traced by hand: every early geometry is a cut of an existing object's own geometry (OSM coordinates), and
Fiskartorpsvägen is its OSM way. The cut points are the junctions with Skolsvängen, Klubbensvägen and Fiskartorpsvägen.
"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from shapely.geometry import LineString, Point

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
met = lambda p: LineString([TO_METRIC(*q) for q in p])
MAIN, SKOL, KLUB = 'road:qgis:lumparland:lemlandsvagen-100km3', 'road:qgis:lumparland:skolsvangen-100km6', 'road:qgis:lumparland:klubbensvagen-100km4'
FISK = 'way/349946211'
geo = {i: G[O[i]['geometryPeriods'][0]['geometryId']] for i in (MAIN, SKOL, KLUB)}
main, skol, klub = (met(geo[i]['paths'][0]) for i in (MAIN, SKOL, KLUB))
mod = {f['id']: f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']}
sk, kl, fi = geo[SKOL]['paths'][0], geo[KLUB]['paths'][0], mod[FISK]['paths'][0]
assert sk == mod['way/611723906']['paths'][0] and kl[:40] == mod['way/349946213']['paths'][0]

# Skolsvängen: the loop to vertex 26; vertex 27 is the later spur north-east to the house at Simons.
SK_END = 26
sk_len = met(sk[:SK_END + 1]).length
p = lambda q: main.project(Point(TO_METRIC(*q)))
west, east = p(sk[0]), p(sk[SK_END])               # where the loop leaves and (15 m away, across the cycle path) rejoins
granboda = p(kl[0]); bergoren = p(fi[0])           # Klubbensvägen and Fiskartorpsvägen start on today's road
assert main.distance(Point(TO_METRIC(*sk[0]))) < 0.01 and main.distance(Point(TO_METRIC(*kl[0]))) < 0.01 and main.distance(Point(TO_METRIC(*fi[0]))) < 0.01
assert fi[-1] == kl[39]                             # Fiskartorpsvägen ends at Klubbensvägen's corner
gap = main.distance(Point(TO_METRIC(*sk[SK_END])))
r = lambda x: round(x, 1)
print('main', r(main.length), 'Skolsvängen', r(west), r(east), 'gap', r(gap), 'Klubbensvägen', r(granboda), 'Fiskartorpsvägen', r(bergoren))

S17, S29, S68 = 'nls:92062c61-d68d-43ef-b581-e9bdcdc8e0ba', 'nls:map-39093010', 'nls:101211:1968'
maps = {'1917': dict(sourceId=S17, year=1917), '1929': dict(sourceId=S29, year=1929), '1968': dict(sourceId=S68, year=1968)}
early = [
    dict(objectId=MAIN, inputHash=fingerprint(O[MAIN]), geometryId=geo[MAIN]['id'], geometryHash=digest(geo[MAIN]), lengthMeters=r(main.length),
         firstYear=1917, until=1968, maps={'1917': 'present', '1929': 'present'},
         ranges=[[0.0, r(west)], [r(east), r(granboda)]],
         laterStage=dict(firstYear=1929, ranges=[[0.0, r(west)], [r(east), r(granboda)], [r(bergoren), r(main.length)]])),
    dict(objectId=SKOL, inputHash=fingerprint(O[SKOL]), geometryId=geo[SKOL]['id'], geometryHash=digest(geo[SKOL]), lengthMeters=r(skol.length),
         firstYear=1917, until=1968, maps={'1917': 'present', '1929': 'present'}, ranges=[[0.0, r(sk_len)]]),
    dict(objectId=KLUB, inputHash=fingerprint(O[KLUB]), geometryId=geo[KLUB]['id'], geometryHash=digest(geo[KLUB]), lengthMeters=r(klub.length),
         firstYear=1917, until=1968, maps={'1917': 'present', '1929': 'present'}, ranges=[[0.0, r(klub.length)]]),
]
feats = {'osm-2026': mod[FISK]}
for y in (2021, 2025):
    feats[f'osm-{y}'] = next(f for f in json.load(gzip.open(f'dist/assets/roads-{y}.json.gz'))['features'] if f['id'] == f'road-{y}-349946211')
links = [dict(datasetId=d, featureId=f['id'], sourceVertexRange=[0, len(f['paths'][0]) - 1], sourceVertexCount=len(f['paths'][0]), input=digest(f['paths']),
              basis='Fiskartorpsvägen, den gamla landsvägens sträcka norrut från Klubbensvägen till dagens väg vid Bergören, som den kartlagts detta år.') for d, f in feats.items()]
SURVEY = 'road:lumparland:fiskartorpsvagen:survey'
data = dict(
    schemaVersion=1, reviewedAt='2026-11-19', reviewProperty='lemlandsvagenMainRoad', geometryPrefix='geometry:lemlandsvagen-east:',
    source=dict(id='review:lemlandsvagen-east', title='Lemlandsvägen öster om kyrkbyn · granskning', url='assets/lemlandsvagen-east.json'),
    sources=[dict(id=S29, title='Lantmäteriverket · sockenkarta 1012 11 Lumparland · 1929', issuedAt='1929',
                  url='https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_vari/map-39093010_500-20000-101211_pitajankartta_1929_karttalehti_101211_lumparland_v2.tif')],
    maps=maps, early=early,
    earlyBasis={
        MAIN: 'Dagens väg från kyrkbyn genom Norrböle, Rörstorp och Granboda är vägen på Senatens karta 1917 och sockenkartan 1929 (inom 25 m, kartbladets fel). '
              'Undantagen: vid Simons gick vägen i en båge norrut (dagens Skolsvängen), och öster om Granboda gick den österut längs dagens Klubbensvägen och sedan norrut (Fiskartorpsvägen). '
              'Dagens raka väg vid Simons och diagonalen mot Bergören ritas första gången på grundkartan 1968.',
        SKOL: 'Den gamla landsvägen i en båge norrut förbi Simons. Sockenkartan 1929 ritar den som landsvägen; Senatens karta 1917 ritar vägen här men är för grov för formen. '
              'Grundkartan 1968 ritar dagens raka väg söder om den. Bågen slutar 15 m från dagens väg (dagens gång- och cykelväg ligger emellan); den sista anslutningen ritas inte.',
        KLUB: 'Den gamla landsvägen österut från Granboda mot Delsviken. Senatens karta 1917 ritar vägen fram till stranden vid Delsviken, sockenkartan 1929 ritar den med svängen norrut (Fiskartorpsvägen) mot Bergören. '
              'Grundkartan 1968 ritar dagens diagonal som huvudväg.'},
    laterStageNote='Del av objektets egen geometri (samma koordinater) där dagens väg är vägen på sockenkartan 1929, nu också över Bergören till sundet.',
    laterStageBasis={MAIN: 'Sockenkartan 1929 ritar vägen över Bergören och över sundet mot Skag. Senatens karta 1917 ritar ingen väg dit; där slutar vägen vid stranden vid Delsviken.'},
    geometryNote='Del av objektets egen geometri (samma koordinater) där dagens väg är vägen på Senatens karta 1917 och sockenkartan 1929.',
    route=dict(order=[MAIN, SKOL, MAIN, KLUB], repeat=[MAIN], joinMeters=1.0),
    statedGaps=[dict(objectId=SKOL, end=-1, meters=r(gap), basis='Skolsvängens båge slutar 15 m från dagens väg; dagens gång- och cykelväg ligger emellan. Den gamla anslutningen ritas inte.')],
    newRoadSource=dict(id=SURVEY, title='OpenStreetMap · Fiskartorpsvägen', url='https://www.openstreetmap.org/way/349946211', issuedAt='2026'),
    newRoad=dict(id='road:lumparland:fiskartorpsvagen', name='Fiskartorpsvägen', routeId='road:route:fiskartorpsvagen', modernRoadClass='unclassified', roadWidth=4, firstYear=1929,
                 surveySourceId=SURVEY, maps={'1929': 'present', '1968': 'present'}, paths=mod[FISK]['paths'], sourceLinks=links,
                 missingExtracts=['osm-2014'], missingExtractsBasis='OpenStreetMap 2014 har inte vägen; att den saknas i utdraget är inte belägg för att den saknades.',
                 basis='Den gamla landsvägens sträcka norrut från Klubbensvägen till dagens väg vid Bergören. Sockenkartan 1929 ritar den som landsvägen och grundkartan 1968 som en mindre väg bredvid dagens diagonal. '
                       'Senatens karta 1917 ritar ingen väg här. Dagens mittlinje (OpenStreetMap) används som stabilt läge.',
                 geometryNote='Fiskartorpsvägens mittlinje i OpenStreetMap 2026, använd som stabilt läge från 1929.'),
    method='Dagens väg jämförd för hand med Senatens karta 1917, sockenkartan 1012 11 Lumparland 1929 (rutnät 50 m) och grundkartorna 1968, 1985 och 1995 (blad 101211), med OpenStreetMap 2026 inritat (renders/). '
           'Ingen linje är avläst för hand: de tidiga perioderna är delar av objektens egna geometrier, avskurna vid korsningarna.')
json.dump(data, open('data/lemlandsvagen-east.json', 'w'), ensure_ascii=False, indent=1)
