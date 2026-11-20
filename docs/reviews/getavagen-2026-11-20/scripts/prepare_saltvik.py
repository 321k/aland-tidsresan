"""Write data/getavagen-saltvik.json: Getavägen from Godby to the Tjudö sheet edge, and the old main road around it, on
the 1929 Saltvik parish map (1021 07) and its 1944 edition. Usage: prepare_saltvik.py CATALOGUE.json.gz

Read on renders/ref-*-1929.jpg, candidates-*-1929.jpg, bartsgarda-*.jpg, godby-1944.jpg and bartsgarda-1944.jpg:
- Getavägen is the 1929 road from Kyrkvägen at Godby (569.7 m) to Bartsgårda (4 852 m, where Bartsgårdavägen leaves),
  and from Pålsbölevägen at Bartsgårda (5 658 m) to the sheet edge. The diagonal out of Godby and the straight across
  the fields at Bartsgårda are first on the 1968 base map.
- The 1929 main road ran along Bartsgårdavägen to Mellangård, along Kroklundsvägen north-east and north to Sålis, and west
  along Saltviksvägen back to today's road at Avanåker (8 814 m). The road through Tallnäs and Ödkarby that today's road
  follows was a lesser road then.
- Gamla Getavägen, the shore road past Sjöstrand and Nötholma, and Kyrkvägen into Godby village are 1929 roads.
No line is traced by hand: every early geometry is the object's own geometry, or a cut of it at the junctions."""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from shapely.geometry import LineString, Point

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
GE, KY, BA, KR, GA, SA = ('road:qgis:saltvik:getavagen-godby-norra-bladgransen', 'road:qgis:saltvik:kyrkvagen-batch4', 'road:qgis:saltvik:bartsgardavagen',
                          'road:qgis:saltvik:kroklundsvagen', 'road:qgis:saltvik:gamla-getavagen', 'road:qgis:saltvik:saltviksvagen-1-batch4')
geo = lambda i: G[O[i]['geometryPeriods'][0]['geometryId']]
line = lambda i: LineString([TO_METRIC(*q) for q in geo(i)['paths'][0]])
r = lambda x: round(x, 1)
g = line(GE)
on = lambda i, e: g.project(Point(line(i).coords[e]))
kyrk, barts, pals = on(KY, -1), on(BA, 0), g.project(Point(TO_METRIC(*geo('road:qgis:saltvik:palsbolevagen-norra')['paths'][0][0])))
S = line(SA); krok_end = S.project(Point(line(KR).coords[0]))
print('Getavägen', r(kyrk), r(barts), r(pals), r(g.length), '; Saltviksvägen from', r(krok_end), 'of', r(S.length))
S29, S44 = 'nls:map-38157483', 'nls:map-38147682'
def entry(oid, ranges):
    gg = geo(oid); L = line(oid)
    return dict(objectId=oid, inputHash=fingerprint(O[oid]), geometryId=gg['id'], geometryHash=digest(gg), lengthMeters=r(L.length),
                firstYear=1929, until=O[oid]['states'][0]['from'], maps={'1929': 'present', '1944': 'present'}, ranges=ranges)
early = [entry(KY, [[0.0, r(line(KY).length)]]), entry(GE, [[r(kyrk), r(barts)], [r(pals), r(g.length)]]), entry(BA, [[0.0, r(line(BA).length)]]),
         entry(KR, [[0.0, r(line(KR).length)]]), entry(SA, [[r(krok_end), r(S.length)]]), entry(GA, [[0.0, r(line(GA).length)]])]
data = dict(
    schemaVersion=1, reviewedAt='2026-11-20', reviewProperty='mainRoadReview', geometryPrefix='geometry:getavagen-1929:',
    source=dict(id='review:getavagen-saltvik', title='Getavägen i Saltvik och Finström på sockenkartan 1929 · granskning', url='assets/getavagen-saltvik.json'),
    sources=[dict(id=S29, title='Lantmäteriverket · sockenkarta 1021 07 Saltvik · 1929', issuedAt='1929',
                  url='https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_vari/map-38157483_500-20000-102107_pitajankartta_1929_karttalehti_102107_maarianhamina-saltvik_v2.tif'),
             dict(id=S44, title='Lantmäteriverket · sockenkarta 1021 07 Saltvik · 1944 (svartvit utgåva)', issuedAt='1944',
                  url='https://www.nic.funet.fi/index/geodata/mml/pitajakartta_20k/reunaton/gauss-kryger_mv/map-38147682_500-20000-102107_pitajankartta_mv_1944_karttalehti_102107_saltvik_v2.tif')],
    maps={'1929': dict(sourceId=S29, year=1929), '1944': dict(sourceId=S44, year=1944)},
    early=early,
    earlyBasis={
        GE: 'Dagens väg är vägen på sockenkartan 1929 och utgåvan 1944 från Kyrkvägen vid Godby till Bartsgårda, och från Pålsbölevägen vid Bartsgårda norrut (inom kartans lägesfel). Diagonalen ut ur Godby och den raka sträckan över åkrarna vid Bartsgårda ritas första gången på grundkartan 1968. Mellan Tallnäs och Avanåker var vägen 1929 en mindre väg; huvudvägen gick österut över Bartsgård, Ödkarby och Sålis.',
        KY: 'Den gamla vägen in i Godby by. Sockenkartan 1929 och utgåvan 1944 ritar den som vägen norrut från byn; dagens diagonal finns inte på dem.',
        BA: 'Den gamla huvudvägen norrut genom Bartsgårda till Mellangård. Sockenkartan 1929 och utgåvan 1944 ritar den som landsvägen; dagens raka sträcka väster om den finns inte på dem.',
        KR: 'Den gamla huvudvägen från Mellangård nordost och norrut genom Bartsgårda och Ödkarby till Sålis. Sockenkartan 1929 och utgåvan 1944 ritar den som landsvägen.',
        SA: 'Den västra delen, från Kroklundsvägen vid Sålis till dagens väg vid Avanåker, är den gamla huvudvägens fortsättning på sockenkartan 1929 och utgåvan 1944. Resten av vägen är inte granskad här.',
        GA: 'Strandvägen förbi Sjöstrand och Nötholma vid Avanåker. Sockenkartan 1929 och utgåvan 1944 ritar den.'},
    geometryNote='Del av objektets egen geometri (samma koordinater) där vägen är vägen på sockenkartan 1929.',
    route=dict(order=[KY, GE, BA, KR, SA, GE, GA], repeat=[GE], joinMeters=1.0),
    method='Dagens vägar jämförda för hand med sockenkartan 1021 07 Saltvik 1929 (rutnät 50 m, karttiler), utgåvan 1944 och grundkartorna 1968 (blad 102107), med OpenStreetMap 2026 inritat (docs/reviews/getavagen-2026-11-20/renders/).')
json.dump(data, open('data/getavagen-saltvik.json', 'w'), ensure_ascii=False, indent=1)
