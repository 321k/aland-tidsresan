"""Write data/hammarlandsvagen-marsund.json: the Marsund connection (Frebbenby–Storby, shown from 1959 by the bridge
assumption) where today's road is the road on the 1929 Eckerö parish map and its 1956 edition, from the visual review
(renders/marsund-*.jpg, marsund-close-*.jpg): Marby 5 700–6 040 m and Kyrkoby 7 080–8 220 m from Frebbenby. Between them
the old road went north through Överby village (today's Gamla Landsvägen; not in the catalogue).
Usage: prepare_marsund.py BEFORE_CATALOGUE.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from shapely.geometry import LineString

before = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in before['objects']}; G = {g['id']: g for g in before['geometries']}
E29, E56 = 'nls:map-39091228', 'nls:map-37971493'
M = 'road:marsund:eckero-hammarland'
STRETCHES = [(5700.0, 6040.0), (7080.0, 8220.0)]       # metres from Frebbenby along the object (paths 18 … 0)
o = O[M]; gid = o['geometryPeriods'][0]['geometryId']; g = G[gid]
order = list(reversed(range(len(g['paths']))))
lines = {i: LineString([TO_METRIC(*p) for p in g['paths'][i]]) for i in order}
offset, at = {}, 0.0
for i in order:
    offset[i] = at; at += lines[i].length
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
              maps={'1929-eckero': 'present', '1956-eckero': 'present'})]
data = dict(
    schemaVersion=1, reviewedAt='2026-11-19',
    source=dict(id='review:hammarlandsvagen-marsund', title='Marsundsförbindelsen vid Marby och Kyrkoby · granskning', url='assets/hammarlandsvagen-marsund.json'),
    sources=[], maps={'1929-eckero': dict(sourceId=E29, year=1929), '1956-eckero': dict(sourceId=E56, year=1956)},
    geometryPrefix='geometry:hammarlandsvagen-marsund:',
    geometryNote='Delar av objektets egen geometri (samma koordinater) där dagens väg är den väg sockenkartan 1929 för Eckerö ritar: vid Marby och från Överby till Kyrkoby.',
    method='Marsundsförbindelsen jämförd med sockenkartan 1012 03 Eckerö 1929 och utgåvan 1956 (karttiler 2,4 m/px) och OpenStreetMap 2026, var 1,1 km och närmare var 400 m (renders/marsund-*.jpg). Samma väg: kartans väg har dagens form inom omkring 25 m.',
    early=early,
    earlyBasis={M: 'Två delar av förbindelsen är den gamla landsvägen genom Eckerö som sockenkartan 1929 ritar, och utgåvan 1956 likadant: vid Marby (5,7–6,0 km från Frebbenby) och från Överby genom Kyrkoby (7,1–8,2 km), inom omkring 10 m från dagens väg. Mellan dem gick den gamla vägen norrut genom Överby by, där dagens väg är en senare förbifart. Resten av förbindelsen, med bron över Marsund, visas fortfarande från 1959.'})
json.dump(data, open('data/hammarlandsvagen-marsund.json', 'w'), ensure_ascii=False, indent=1)
