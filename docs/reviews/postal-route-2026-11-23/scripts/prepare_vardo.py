"""Write data/postal-route-vardo.json. Usage: prepare_vardo.py CATALOGUE_BEFORE.json.gz

Read on ../renders/vargata-sheet.jpg (1971, 1978; Vårdövägen in green) and vbend-sheet.jpg (1971, 1978, 1985; OSM in
green): Vårdövägen's object follows the 1971 and 1978 main road from the Kumnäs landing into Vargata and from the east
end of Drottning Kristinas gata eastwards. Between the two (OSM 296585218, from E 20 519 258 N 6 681 408 to
20 519 559/6 681 368) the 1971 and 1978 road ran in a bend north along today's Drottning Kristinas gata; the straight
is first on the 1985 map."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from hammarlandsvagen_main_road import metric
from postal_route_vardo import apply_postal_route_vardo, REVIEW
from shapely.geometry import Point

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
VV, DK = 'road:qgis:vardo:vardovagen-200km1', 'road:qgis:vardo:drottning-kristinas-gata-100k'
DK = next(k for k in O if k.startswith(DK))
g = G[O[VV]['geometryPeriods'][0]['geometryId']]; line = metric(g['paths'][0])
dk = G[O[DK]['geometryPeriods'][0]['geometryId']]['paths'][0]
a = round(line.project(Point(TO_METRIC(*dk[0]))), 1); b = round(line.project(Point(TO_METRIC(*dk[-1]))), 1)
print('Vårdövägen', round(line.length, 1), 'm; Drottning Kristinas gata meets it at', a, 'and', b, '; ends off the line',
      [round(line.distance(Point(TO_METRIC(*q))), 2) for q in (dk[0], dk[-1])], '; DK from', O[DK]['states'][0]['from'])
L = {'1971-vardo': dict(sourceId='nls:102301:1971', year=1971), '1978-vardo': dict(sourceId='nls:102301:1978', year=1978)}
review = dict(schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:postal-route-vardo:',
              source=dict(id='review:postal-route-vardo', title='Vårdövägen genom Vargata på grundkartorna 1971 och 1978 · granskning', url='assets/postal-route-vardo.json'),
              sources=[], maps=L, method='Grundkartan 1023 01 (1971, 1978, 1985, 1995) har lagts över dagens vägar med ett rutnät på 100 m.',
              early=[dict(objectId=VV, inputHash=fingerprint(O[VV]), geometryId=g['id'], geometryHash=digest(g), lengthMeters=round(line.length, 1), firstYear=1971,
                          until=O[VV]['states'][0]['from'], maps={'1971-vardo': 'present', '1978-vardo': 'present'}, ranges=[[0.0, a], [b, round(line.length, 1)]])],
              earlyBasis={VV: 'Vårdövägen från färjläget vid Kumnäs in i Vargata och österut från Drottning Kristinas gata är vägen på grundkartorna 1971 och 1978. Däremellan gick vägen i en båge norrut förbi gården Post vid Västergård–Östergård, längs dagens Drottning Kristinas gata (daterad från 1971); dagens raka väg genom Vargata ritas först 1985.'},
              geometryNote='Delar av objektets egen geometri (samma koordinater) där vägen är vägen på grundkartorna 1971 och 1978.')
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_postal_route_vardo(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok:', [(p['from'], p['to'], p.get('coverage')) for p in {o['id']: o for o in trial['objects']}[VV]['geometryPeriods']])
