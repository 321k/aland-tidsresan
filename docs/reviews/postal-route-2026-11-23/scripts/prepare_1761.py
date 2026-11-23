"""Write data/postal-route-1761.json. Usage: prepare_1761.py CATALOGUE_BEFORE.json.gz

The trace: from the east end of von Knorringsvägen along today's main road (its own coordinates, where the registry
says the remains of the postal road run west under the main road) to where the registry outline of Fi 8.17 begins,
then along the outline's middle to the shore at the old ferry place. The outline is in
../data/registry-fi-8-17.json (Ålands kulturarvsregister, fetched 2026-11-23)."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC, TO_GEO
from hammarlandsvagen_main_road import metric
from lemlandsvagen_main_road import cut
from shapely.geometry import Point, LineString
from postal_route_1761 import apply_postal_route_1761, REVIEW

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
VK = 'road:qgis:saltvik:von-knorringsvagen-1-batch4'; SF = 'road:finstrom:sundsvagen:godby-farjsundet'
vk = G[O[VK]['geometryPeriods'][0]['geometryId']]['paths'][0]
start = vk[0]                                                        # von Knorringsvägen's east end, at Färjsundet
sf = G[O[SF]['geometryPeriods'][0]['geometryId']]['paths'][0]; line = metric(sf)
assert Point(TO_METRIC(*start)).distance(Point(line.coords[0])) < 1
CORRIDOR_START = 148.5                                               # where the registry outline begins (12 m off the road)
under = cut(sf, line, 0, CORRIDOR_START)
# the middle of the registry outline, read from its two sides (EPSG:3874, E 20500000 + / N 6680000 +)
mid = [(638, 297), (668, 308), (694, 321), (733, 331), (774, 340), (806, 348), (835, 360), (855, 383), (870, 410), (888, 432), (906, 446)]
path = [list(start)] + [list(q) for q in under[1:]] + [[round(v, 7) for v in TO_GEO(20500000 + e, 6680000 + n)] for e, n in mid]
m = metric(path)
reg = json.load(open('docs/reviews/postal-route-2026-11-23/data/registry-fi-8-17.json'))
from shapely.geometry import Polygon
outline = Polygon([TO_METRIC(*q) for q in reg['features'][0]['geometry']['rings'][0]])
inside = m.intersection(outline.buffer(5)).length
print('length', round(m.length, 1), 'inside the registry outline (5 m)', round(inside, 1))
REG = dict(id='review:postal-route-1761:fi-8-17', title='Ålands kulturarvsregister · Fi 8.17 · Väglämning – Godby',
           url='https://kartor.regeringen.ax/arcgis/rest/services/Kulturarv/Fornminnen/MapServer/1/query?where=FornID+%3D+%27Fi+8.17%27&outFields=%2A&returnGeometry=false&f=pjson', issuedAt=None)
OPEN = dict(id='review:postal-route-1761:postal-1638', title='Postvägen över Åland inrättades 1638 (Ålands landskapsregering; Wikipedia, Stockholm–Turku mail route)',
            url='https://aland.se/besok/sevardheter/postvagen-over-aland/', issuedAt=None)
review = dict(
    schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='postalRoute1761Review', geometryPrefix='geometry:postal-route-1761:',
    source=dict(id='review:postal-route-1761', title='Den gamla färjvägen vid Färjsundet, till 1761 · granskning', url='assets/postal-route-1761.json'),
    sources=[REG, OPEN],
    maps={'1638-postal': dict(sourceId=OPEN['id'], year=1638), '1761-registry': dict(sourceId=REG['id'], year=1761)},
    observationTypes={'1638-postal': 'historical-source', '1761-registry': 'heritage-register'},
    method='Registrets avgränsning av Fi 8.17 har lagts över katalogens vägar och grundkartan 1968 med ett rutnät på 100 m.',
    early=[], earlyBasis={},
    oldRoad=dict(
        id='road:finstrom:gamla-farjvagen:farjsundet', name='Gamla färjvägen · Färjsundet', routeId='road:route:postvagen', modernRoadClass='tertiary', roadWidth=4,
        firstYear=1638, until=1761, maps={'1638-postal': 'present', '1761-registry': 'absent'},
        path=path, lengthMeters=round(m.length, 1), referenceRange=[0, round(m.length, 1)], endSnapMeters=[0.0, 0.0], endSnapLimit=1,
        endObjects=[VK], freeEnds=[[0, -1]], freeEndBasis='Det gamla färjstället på västra stranden av Färjsundet, söder om dagens bro (Fi 8.17).',
        todayRoadName='Sundsvägen',
        basis='Postvägens nedfart till det gamla färjstället vid Färjsundet: enligt fornlämningsregistret (Fi 8.17) en serpentinväg i en brant klyfta, med lämningar av postvägen västerut fram till dagens huvudväg. Den var i bruk till 1761, då ett nytt färjställe anlades norr om dagens bro. När den började användas är inte känt; den visas från postvägens inrättande 1638.',
        traceBasis='Från von Knorringsvägens ände längs dagens huvudväg (dess egna koordinater), där registret säger att postvägens lämningar fortsätter, och sedan längs mitten av registrets avgränsning av Fi 8.17 ned till stranden. Registrets avgränsning omfattar serpentinkurvorna; mittlinjen återger dem inte i detalj.',
        afterNote='Från 1761 gick färjan från det nya färjstället norr om dagens bro (Färjvägen). Vägen finns kvar som fornlämning.'))
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_postal_route_1761(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok')
