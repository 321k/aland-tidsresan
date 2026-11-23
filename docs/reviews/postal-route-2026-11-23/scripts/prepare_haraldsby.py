"""Write data/postal-route-haraldsby.json. Usage: prepare_haraldsby.py CATALOGUE_BEFORE.json.gz

Read on ../renders:
- farj-2944.jpg, farj-29-68.jpg: the 1929 Saltvik sheet draws the main road from Godby north-east to the ferry landing
  at Färjsundet, 60–80 m north-west of today's straight road; along von Knorringsvägen the same sheet lies 50–70 m
  north-west of the catalogue road, so this is the same line seen through the sheet's offset. The 1944 tile is placed
  about 90 m differently and is not used here. The 1968 base map draws today's straight road and the 1937 bridge, and
  the old shore road ending at the former landing.
- h-sheet.jpg (1929, 1944, 1968 with the catalogue's geometry): from the landing the 1929 and 1944 sheets draw the road
  north-east to Vårsundet, north through Västerdal and Enelund into Haraldsby, east past Östergård and in a curve past
  Högbacka to Sundsvägen: the course of Vårsundet–Haraldsby (to the Haraldsbyvägen junction), Haraldsbyvägen (to
  Östergård) and Gamla Sundsvägen (its 1968–2013 line with the curve), 30–80 m off as the tile is.
- hog-sheet.jpg, hog-later.jpg: the 1968–1993 base maps draw the curve at Högbacka on Gamla Sundsvägen's 1968 line.
"""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import digest, fingerprint, TO_METRIC
from hammarlandsvagen_main_road import metric
from shapely.geometry import Point
from postal_route_haraldsby import apply_postal_route_haraldsby, REVIEW

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
S = {s['id'] for s in cat['sources']}
L = {'1929-saltvik': dict(sourceId='nls:map-38157483', year=1929), '1944-saltvik': dict(sourceId='nls:map-38147682', year=1944)}
assert all(l['sourceId'] in S for l in L.values())
P = 'road:qgis:saltvik:'

def early(oid, maps, upto=None, start=None):
    o = O[oid]; gp = o['geometryPeriods'][0]; g = G[gp['geometryId']]; line = metric(g['paths'][0]); n = round(line.length, 1)
    assert len(g['paths']) == 1 and o['states'][0]['from'] == 1968 == gp['from'], oid
    a = round(line.project(Point(start)), 1) if start else 0.0
    b = round(line.project(Point(upto)), 1) if upto else n
    return dict(objectId=oid, inputHash=fingerprint(o), geometryId=g['id'], geometryHash=digest(g), lengthMeters=n, firstYear=1929, until=1968,
                maps={k: 'present' for k in maps}, ranges=[[a, b]])

BOTH = ['1929-saltvik', '1944-saltvik']
E = [early('road:finstrom:sundsvagen:godby-farjsundet', ['1929-saltvik']),
     early(P + 'sundsvagen-varsundet-haraldsby', BOTH, start=(20500950.0, 6680658.0), upto=(20501391.0, 6681002.0)),
     early(P + 'haraldsbyvagen-sodra-anslutningen', BOTH),
     early(P + 'haraldsbyvagen', BOTH, upto=(20501905.0, 6681714.0)),
     early(P + 'gamla-sundsvagen-vaster', BOTH),
     early(P + 'gamla-sundsvagen-oster', BOTH)]
basis = {
    'road:finstrom:sundsvagen:godby-farjsundet': 'Huvudvägen från Godby till färjläget vid Färjsundet. Sockenkartan för Saltvik 1929 ritar den 60–80 m nordväst om dagens raka väg; längs von Knorringsvägen ligger samma blad 50–70 m nordväst om katalogens väg, så det är samma linje sedd genom bladets förskjutning. Utgåvan 1944 är inpassad omkring 90 m annorlunda här och används inte. Bron öppnades 1937; före den gick färjan.',
    P + 'sundsvagen-varsundet-haraldsby': 'Vägen från färjläget på östra sidan av Färjsundet till Vårsundet, där Haraldsbyvägen tar av. Sockenkartan för Saltvik 1929 och utgåvan 1944 ritar den på samma sträckning, 30–50 m från objektet som bladet ligger. Resten av objektet, över Östervik, är senare.',
    P + 'haraldsbyvagen-sodra-anslutningen': 'Den korta anslutningen vid Vårsundet där vägen till Haraldsby by tar av. Sockenkartan för Saltvik 1929 och utgåvan 1944 ritar vägskälet här.',
    P + 'haraldsbyvagen': 'Huvudvägen från Vårsundet norrut genom Västerdal och Enelund in i Haraldsby by till Östergård. Sockenkartan för Saltvik 1929 och utgåvan 1944 ritar den på samma sträckning som grundkartan 1968, 30–80 m från objektet som bladet ligger. Delen norr om Östergård granskas inte här.',
    P + 'gamla-sundsvagen-vaster': 'Huvudvägen från Östergård österut och i kurvan förbi Högbacka. Sockenkartan för Saltvik 1929 och utgåvan 1944 ritar samma sträckning som grundkartorna 1968–1993, 30–80 m från objektet som bladet ligger.',
    P + 'gamla-sundsvagen-oster': 'Huvudvägen från kurvan vid Högbacka österut till Sundsvägen. Sockenkartan för Saltvik 1929 och utgåvan 1944 ritar samma sträckning som grundkartorna 1968–1993, 30–80 m från objektet som bladet ligger.'}
review = dict(schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='postalRouteHaraldsbyReview', geometryPrefix='geometry:postal-route-haraldsby:',
              source=dict(id='review:postal-route-haraldsby', title='Postvägen över Färjsundet och genom Haraldsby på sockenkartorna 1929 och 1944 · granskning', url='assets/postal-route-haraldsby.json'),
              sources=[], maps=L,
              method='Sockenkartorna för Saltvik 1929 och 1944 har lagts över katalogens vägar med ett rutnät på 100 m och jämförts med grundkartorna 1968–1993, som är inpassade på sitt tryckta rutnät. Sockenkartorna ligger 30–90 m fel här; vägarnas sträckning, inte deras exakta läge, är belägget.',
              early=E, earlyBasis=basis, geometryNote='Objektets egen geometri (samma koordinater), där vägen är vägen på sockenkartan.')
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_postal_route_haraldsby(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
for e in E: print(e['objectId'], e['ranges'], e['lengthMeters'])
print('trial ok')
