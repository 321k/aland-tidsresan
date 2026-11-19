"""Write data/hammarlandsvagen-marsund.json: the Marsund connection (Frebbenby–Storby, shown from 1959 by the bridge
assumption) where today's road is the road on the 1929 Eckerö parish map and its 1956 edition, from the visual review
(renders/marsund-*.jpg, marsund-close-*.jpg, overby-grid-1929.jpg, frebbenby-grid-1929-osm.jpg): Frebbenby 0–472 m,
Marby 5 700–6 040 m, Överby 6 300–6 430 m and
Kyrkoby 7 080–8 220 m from Frebbenby. Between them the old road went in two loops north through Överby village
(data/hammarlandsvagen-overby.json).
Usage: prepare_marsund.py BEFORE_CATALOGUE.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from shapely.geometry import LineString

before = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in before['objects']}; G = {g['id']: g for g in before['geometries']}
E29, E56 = 'nls:map-39091228', 'nls:map-37971493'
M = 'road:marsund:eckero-hammarland'
STRETCHES = [(0.0, None), (3690.0, 3880.0), (5700.0, 6040.0), (6300.0, 6430.0), (7080.0, 8220.0), (9200.0, 9400.0), (9850.0, 10230.0)]   # metres from Frebbenby along the object (paths 18 … 0); None: the end of path 16
o = O[M]; gid = o['geometryPeriods'][0]['geometryId']; g = G[gid]
order = list(reversed(range(len(g['paths']))))
lines = {i: LineString([TO_METRIC(*p) for p in g['paths'][i]]) for i in order}
offset, at = {}, 0.0
for i in order:
    offset[i] = at; at += lines[i].length
# Frebbenby: from Kattby west to the junction with Marsundsvägen and Kattnäsvägen, the end of path 16 (renders/frebbenby-grid-1929-osm.jpg)
STRETCHES = [(a, round(offset[15], 2) if b is None else b) for a, b in STRETCHES]
cuts = []
for a, b in STRETCHES:
    for i in order:
        s, e = max(a, offset[i]), min(b, offset[i] + lines[i].length)
        if e - s > 0.01:
            cuts.append([i, round(s - offset[i], 2), round(e - offset[i], 2)])
for c in cuts:
    c[2] = min(c[2], round(lines[c[0]].length, 2))
print(round(at, 1), cuts)
early = [dict(objectId=M, inputHash=fingerprint(o), geometryId=gid, geometryHash=digest(g), lengthMeters=round(at, 2),
              ranges=[list(s) for s in STRETCHES], pathOrder=order, pathRanges=cuts, firstYear=1929, until=o['states'][0]['from'],
              maps={'1929-eckero': 'present', '1929-morby': 'present', '1946-bovik': 'present', '1956-eckero': 'present'})]
data = dict(
    schemaVersion=1, reviewedAt='2026-11-19',
    source=dict(id='review:hammarlandsvagen-marsund', title='Marsundsförbindelsen vid Marby och Kyrkoby · granskning', url='assets/hammarlandsvagen-marsund.json'),
    sources=[dict(id='nls:map-38157016', title='Lantmäteriverket · sockenkarta 1021 01 Mörby · 1929', issuedAt='1929',
                  url='https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_vari/map-38157016_500-20000-102101_pitajankartta_1929_karttalehti_102101_morby_v2.tif'),
             dict(id='nls:map-38157019', title='Lantmäteriverket · sockenkarta 1021 01 Bovik · 1946', issuedAt='1946',
                  url='https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_vari/map-38157019_500-20000-102101_pitajankartta_1946_karttalehti_102101_bovik_v2.tif')],
    maps={'1929-eckero': dict(sourceId=E29, year=1929), '1956-eckero': dict(sourceId=E56, year=1956),
          '1929-morby': dict(sourceId='nls:map-38157016', year=1929), '1946-bovik': dict(sourceId='nls:map-38157019', year=1946)},
    geometryPrefix='geometry:hammarlandsvagen-marsund:',
    geometryNote='Delar av objektets egen geometri (samma koordinater) där dagens väg är den väg sockenkartan 1929 för Eckerö ritar: vid Marby och från Överby till Kyrkoby.',
    method='Marsundsförbindelsen jämförd med sockenkartan 1012 03 Eckerö 1929 och utgåvan 1956 (karttiler 2,4 m/px) och OpenStreetMap 2026, var 1,1 km och närmare var 400 m (renders/marsund-*.jpg). Samma väg: kartans väg har dagens form inom omkring 25 m.',
    early=early,
    earlyBasis={M: 'Sju delar av förbindelsen är den gamla landsvägen som sockenkartan 1929 för Eckerö ritar, och utgåvan 1956 likadant: genom Frebbenby fram till Marsundsvägen (0–0,47 km), över det smala sundet vid Holmberg (3,69–3,88 km), vid Marby (5,7–6,0 km från Frebbenby), en kort bit mitt i Överby (6,3–6,4 km) från Överby genom Kyrkoby (7,1–8,2 km), vid Kristiansund (9,2–9,4 km) och från Bagars till Storby (9,85–10,23 km; sockenkartan 1929 för Mörby och utgåvan 1946), inom omkring 15 m från dagens väg. Från Frebbenby gick den gamla vägen västerut längs Marsundsvägen till färjan. Däremellan gick den gamla vägen i två slingor norrut genom Överby by, där dagens väg är en senare förbifart. Resten av förbindelsen, med bron över Marsund, visas fortfarande från 1959.'})
json.dump(data, open('data/hammarlandsvagen-marsund.json', 'w'), ensure_ascii=False, indent=1)
