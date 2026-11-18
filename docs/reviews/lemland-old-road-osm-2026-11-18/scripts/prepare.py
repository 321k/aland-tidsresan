"""Write data/lemland-old-road-osm.json: which OpenStreetMap ways the old Lemlandsvägen survives as, and how each
old-road object's line is assembled from them and from its 1929 trace. Decisions are written here by hand after the
visual review (renders/); the build step (scripts/lemland_old_road_osm.py) does all geometry, matching and checks.
Usage: prepare.py BEFORE_CATALOGUE.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest

before = json.load(gzip.open(sys.argv[1]))
O = {o['id']: o for o in before['objects']}; G = {g['id']: g for g in before['geometries']}
modern = {f['id']: f for f in json.load(gzip.open('dist/assets/modern.json.gz'))['features']}
snap = {y: {f['id']: f for f in json.load(gzip.open(f'dist/assets/roads-{y}.json.gz'))['features']} for y in (2014, 2021, 2025)}


def osm(way, a, b, reverse=True):
    return dict(way=way, range=[a, b], reverse=reverse)


GAP = dict(trace=True)
K = 'way/119232836'; KO = 'way/349910225'
KOMMUNRUNDAN = [osm('way/173992646', 0, 15), osm('way/932105680', 0, 3)]
SODERBY = [osm('way/551271209', 0, 5), osm('way/611965363', 0, 8), osm('way/611965361', 0, 1), osm('way/179382606', 0, 21),
           osm('way/1180076498', 0, 9), osm('way/611965359', 0, 4), osm('way/611965360', 0, 2), osm('way/179382608', 0, 3),
           osm('way/179382607', 0, 3), osm('way/179382609', 0, 16)]
objects = [
    dict(id='road:lemland:gamla-lemlandsvagen:ovre-bors-ostergard', name='Gamla Lemlandsvägen · Övre-Börs–Östergård (Knutsbodavägen)',
         modernNames=['Knutsbodavägen'],
         phases=[
             dict(**{'from': 1917, 'to': 1968}, pieces=[GAP, osm(K, 2, 9, False), GAP, osm(K, 13, 23, False), GAP], traceCheck=True,
                  basis='Vägen genom Övre-Börs med den skarpa kröken vid Fridelund som sockenkartorna 1929 och 1948 ritar. Där Knutsbodavägen finns kvar följer linjen den (OpenStreetMap); kröken och sträckan förbi Östergård är 1929 års spår, flyttat med den uppmätta kartförskjutningen mellan de moderna fästpunkterna.'),
             dict(**{'from': 1968, 'to': 1995}, pieces=[GAP, osm(K, 2, 23, False), GAP], traceCheck=False,
                  basis='Grundkartan 1968 ritar en mjuk kurva i stället för kröken vid Fridelund, samma kurva som Knutsbodavägen har i dag; 1978 och 1985 likaså. Kröken är alltså uträtad mellan 1948 och 1968 (1968 är första kartbelägg, inte byggår). Sträckan förbi Östergård är fortfarande 1929 års spår.'),
             dict(**{'from': 1995, 'to': None}, pieces=[osm(K, 2, 23, False)],
                  basis='Delen genom Övre-Börs finns kvar som Knutsbodavägen (OpenStreetMap 2014–2026). Knutsbodavägens första 35 m är den nutida anslutningen till förbifarten (1985) och hör inte till den gamla vägen. Sträckan förbi Östergård är inte granskad efter grundkartan 1985 och saknas i OpenStreetMap; det betyder inte att den försvann just då.')],
         realignment=dict(year=1968, previousMap=1948, map=1968, note='Kröken vid Fridelund (1929, 1948) ersatt av en kurva (1968, 1978, 1985, OpenStreetMap). Rester av kröken finns som en stig och som östra änden av Bolviksvägen; de ägs inte av denna väg.')),
    dict(id='road:lemland:gamla-lemlandsvagen:johans', name='Gamla Lemlandsvägen · Johans (Kockobacka)', modernNames=['Kockobacka'],
         phases=[
             dict(**{'from': 1917, 'to': 1995}, pieces=[GAP, osm(KO, 4, 23), GAP], traceCheck=True,
                  basis='Den gamla vägen i en båge söderut förbi Johans. Bågen följer Kockobacka (OpenStreetMap); ändarna mot dagens väg är 1929 års spår, flyttat med den uppmätta kartförskjutningen.'),
             dict(**{'from': 1995, 'to': None}, pieces=[osm(KO, 4, 23)],
                  basis='Bågen förbi Johans finns kvar som Kockobacka (OpenStreetMap 2021–2026). Kockobackas korta anslutning norrut till förbifarten är senare och hör inte till den gamla vägen. Ändarna mot dagens väg är inte granskade efter grundkartan 1985.')]),
    dict(id='road:lemland:gamla-lemlandsvagen:mangard-soderby', name='Gamla Lemlandsvägen · Mangård–Söderby (Kommunrundan, Norra Söderbyvägen)',
         modernNames=['Kommunrundan', 'Norra Söderbyvägen'],
         phases=[
             dict(**{'from': 1917, 'to': 1995}, pieces=KOMMUNRUNDAN + [GAP] + SODERBY + [GAP], traceCheck=True,
                  basis='Den gamla vägen förbi Mangård, Frankbo, Nygård och Söderby till kyrkbyn. Där den finns kvar följer linjen Kommunrundan och Norra Söderbyvägen (OpenStreetMap), som går rakt över korsningen med Norrbyvägen; sträckan vid Frankbo och sista biten mot kyrkbyn är 1929 års spår, flyttat med den uppmätta kartförskjutningen.'),
             dict(**{'from': 1995, 'to': None}, pieces=KOMMUNRUNDAN + SODERBY,
                  basis='Delarna finns kvar som Kommunrundan och Norra Söderbyvägen (OpenStreetMap 2014–2026). Sträckan vid Frankbo, som förbifarten 1968 skär av, och sista biten mot kyrkbyn saknas i OpenStreetMap och är inte granskade efter grundkartan 1985.')]),
]
ways = sorted({p['way'] for o in objects for ph in o['phases'] for p in ph['pieces'] if 'way' in p})
for o in objects:
    obj = O[o['id']]; gid = obj['geometryPeriods'][0]['geometryId']
    o.update(inputHash=fingerprint(obj), traceGeometryId=gid, traceGeometryHash=digest(G[gid]))
data = dict(
    schemaVersion=1, reviewedAt='2026-11-18',
    source=dict(id='review:lemland-old-road-osm', title='Gamla Lemlandsvägen i dagens vägnät · granskning', url='assets/lemland-old-road-osm.json'),
    method='Varje karta och OpenStreetMap-väg är granskad visuellt (docs/reviews/lemland-old-road-osm-2026-11-18/renders). Där den gamla vägen finns kvar används OpenStreetMaps mittlinje genom alla år; sockenkartan 1929 ligger 3–30 m fel här, och det felet ska inte flytta vägen. Mellan de kvarvarande delarna flyttas 1929 års spår linjärt med förskjutningen vid fästpunkterna. Det oflyttade spåret finns kvar som belägg.',
    limits=dict(traceMeters=40, traceP90Meters=25, linkMeters=15, joinMeters=0.01, anchorMeters=1.0, overlapBuffer=12, overlapMeters=80),
    snapshots={'osm-2014': 'city-2014', 'osm-2021': 'city-2021', 'osm-2025': 'city-2025', 'osm-2026': 'city-2026'},
    wayHashes={w: digest(modern[w]['paths']) for w in ways},
    snapshotHashes={f'osm-{y}': {f'road-{y}-{w[4:]}': digest(snap[y][f'road-{y}-{w[4:]}']['paths']) for w in ways if f'road-{y}-{w[4:]}' in snap[y]} for y in snap},
    unchanged=[dict(id='road:lemland:gamla-lemlandsvagen:tomtebo-solstrand', inputHash=fingerprint(O['road:lemland:gamla-lemlandsvagen:tomtebo-solstrand']),
                    note='Inget av den gamla strandvägen Tomtebo–Solstrand finns kvar som väg i OpenStreetMap, bara korta infarter som korsar den.')],
    objects=objects)
json.dump(data, open('data/lemland-old-road-osm.json', 'w'), ensure_ascii=False, indent=1)
print(len(ways), 'ways;', {k: len(v) for k, v in data['snapshotHashes'].items()})
