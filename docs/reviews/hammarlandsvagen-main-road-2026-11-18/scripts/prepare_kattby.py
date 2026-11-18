"""Write data/hammarlandsvagen-kattby.json: Hammarlandsvägen west of Kattby (17.3–18.6 km) on the 1929 parish maps of
sheets 1012 06 Hammarby and 1012 03 Eckerö, and their editions 1944 and 1956, from the visual review
(renders/kattby-west*.jpg). The object was shown from 1959 only by assumption (the Marsund bridge opening).
Usage: prepare_kattby.py BEFORE_CATALOGUE.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from shapely.geometry import LineString

before = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in before['objects']}; G = {g['id']: g for g in before['geometries']}
FUNET = 'https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/'
E29, E56 = 'nls:map-39091228', 'nls:map-37971493'
H29, H44 = 'nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08', 'nls:9c72a692-bae4-473d-93bb-7bcdee1222e7'
sources = [dict(id=E29, title='Lantmäteriverket · sockenkarta 1012 03 Eckerö · 1929', issuedAt='1929',
                url=FUNET + 'gauss-kryger_vari/map-39091228_500-20000-101203_pitajankartta_1929_karttalehti_101203_eckero_v2.tif'),
           dict(id=E56, title='Lantmäteriverket · sockenkarta 1012 03 Eckerö · 1956 (svartvit utgåva)', issuedAt='1956',
                url=FUNET + 'gauss-kryger_mv/map-37971493_500-20000-101203_pitajankartta_mv_1956_karttalehti_101203_eckero_v2.tif')]
maps = {'1929-hammarby': dict(sourceId=H29, year=1929), '1929-eckero': dict(sourceId=E29, year=1929),
        '1944-nafsby': dict(sourceId=H44, year=1944), '1956-eckero': dict(sourceId=E56, year=1956)}
K = 'road:rural:hammarland-hammarlandsvagen-kattby-west'; CH = 'road:rural:hammarland-hammarlandsvagen-church-corridor'
o = O[K]; gid = o['geometryPeriods'][0]['geometryId']; g = G[gid]; line = LineString([TO_METRIC(*p) for p in g['paths'][0]])
early = [dict(objectId=K, inputHash=fingerprint(o), geometryId=gid, geometryHash=digest(g), lengthMeters=round(line.length, 2),
              ranges=[[0.0, round(line.length, 1)]], firstYear=1929, until=o['states'][0]['from'],
              maps={'1929-hammarby': 'present', '1929-eckero': 'present', '1944-nafsby': 'present', '1956-eckero': 'present'})]
print(K, o['states'][0]['from'], round(line.length, 1))
data = dict(
    schemaVersion=1, reviewedAt='2026-11-18',
    source=dict(id='review:hammarlandsvagen-kattby', title='Hammarlandsvägen väster om Kattby · granskning', url='assets/hammarlandsvagen-kattby.json'),
    sources=sources, maps=maps, geometryPrefix='geometry:hammarlandsvagen-kattby:',
    geometryNote='Objektets egen geometri (samma koordinater): dagens väg är den väg sockenkartorna 1929 ritar.',
    method='Dagens väg väster om Kattby jämförd med sockenkartorna 1929 för bladen 1012 06 Hammarby och 1012 03 Eckerö (karttiler 2,4 m/px), utgåvorna 1944 och 1956 och OpenStreetMap 2026 (renders/kattby-west*.jpg). Samma väg: kartans väg har dagens form inom omkring 25–30 m.',
    early=early,
    earlyBasis={K: 'Samma väg som sockenkartorna 1929 ritar från kyrkan väster ut förbi Kockars, på bladen Hammarby och Eckerö; utgåvorna 1944 och 1956 ritar den likadant. Kartorna ritar vägen 9–15 m söder om dagens vid Kockars och 17–29 m söder om den vid bladgränsen, med samma form; det ligger inom kartornas lägesfel. Tidigare visades vägen först från 1959, då bron över Marsund öppnades; det var ett antagande, inte ett kartbelägg.'},
    route=dict(order=[CH, K], endObjects=[CH], joinMeters=2.0))
json.dump(data, open('data/hammarlandsvagen-kattby.json', 'w'), ensure_ascii=False, indent=1)
