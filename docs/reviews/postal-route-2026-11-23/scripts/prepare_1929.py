"""Write data/postal-route-1929.json. Usage: prepare_1929.py CATALOGUE_BEFORE.json.gz

Read on ../renders:
- p29-jsheet.jpg (Jomala 1928, catalogue geometry in green): Postgårdsvägen from Bergens past Fagerholm to Norrgård lies
  on the drawn road within 10–20 m; the Gölby junction piece lies on the road at the brook. Björkäng lies 20–40 m east
  of the straight road the map draws, within the map's error here.
- p29-tk-sheet.jpg: the 1968 path of Emkarbyvägen from Tingsbacka round the bend to Buskböle and Bergens is the road
  of the 1928 map (10–30 m); the Godby crossroads lie 30–40 m east of the 1929 Saltvik road, parallel to it, as all of
  von Knorringsvägen does (p29-ssheet.jpg): the sheet's offset here.
- p29-ssheet.jpg: von Knorringsvägen from the Godby crossroads north-east past Östergård and Andersby is the road on
  the 1929 Saltvik sheet (20–30 m); the Hammarland piece of Emkarbyvägen lies on the 1929 road (Hammarby sheet).
"""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import digest, fingerprint
from hammarlandsvagen_main_road import metric
from postal_route_1929 import apply_postal_route_1929, REVIEW

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
S = {s['id'] for s in cat['sources']}
L = {'1928-jomala': dict(sourceId='nls:9c76c492-3fb4-43dd-8cc7-eb03d2a00ecd', year=1928),
     '1929-saltvik': dict(sourceId='nls:map-38157483', year=1929),
     '1929-hammarby': dict(sourceId='nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08', year=1929),
     '1944-saltvik': dict(sourceId='nls:map-38147682', year=1944)}
assert all(l['sourceId'] in S for l in L.values())

def early(oid, maps):
    o = O[oid]; gp = o['geometryPeriods'][0]; g = G[gp['geometryId']]
    n = round(metric(g['paths'][0]).length, 1)
    assert len(g['paths']) == 1 and o['states'][0]['from'] == 1968 == gp['from'], oid
    return dict(objectId=oid, inputHash=fingerprint(o), geometryId=g['id'], geometryHash=digest(g), lengthMeters=n, firstYear=min(L[k]['year'] for k in maps),
                until=1968, maps={k: 'present' for k in maps}, ranges=[[0.0, n]])

E = [early('road:jomala:postgardsvagen', ['1928-jomala']),
     early('road:jomala:godbyvagen:golby-junction', ['1928-jomala']),
     early('road:jomala:godbyvagen:bjorkang', ['1928-jomala']),
     early('road:finstrom:godby-korsningen', ['1929-saltvik', '1944-saltvik']),
     early('road:qgis:saltvik:von-knorringsvagen-1-batch4', ['1929-saltvik', '1944-saltvik']),
     early('road:rural:hammarland-way-459195076', ['1929-hammarby'])]
basis = {
    'road:jomala:postgardsvagen': 'Huvudvägen från Bergens österut förbi Fagerholm och Norrgård till Godbyvägen vid Gölby. Sockenkartan för Jomala 1928 ritar den på samma linje, inom 10–20 m.',
    'road:jomala:godbyvagen:golby-junction': 'Godbyvägen vid bäcken i Gölby, där Postgårdsvägen tar av. Sockenkartan 1928 ritar vägen här.',
    'road:jomala:godbyvagen:bjorkang': 'Godbyvägen vid Björkäng. Sockenkartan 1928 ritar vägen rakt norrut 20–40 m väster om biten, inom kartans fel här; biten är vägen på kartan.',
    'road:finstrom:godby-korsningen': 'Korsningen i Godby, där Godbyvägen möter vägen mot Färjsundet. Sockenkartan för Saltvik 1929 och utgåvan 1944 ritar vägen här, 30–40 m västerut som hela von Knorringsvägen: bladets förskjutning.',
    'road:qgis:saltvik:von-knorringsvagen-1-batch4': 'Huvudvägen från korsningen i Godby mot nordost förbi Östergård och Andersby. Sockenkartan för Saltvik 1929 och utgåvan 1944 ritar den på samma linje, inom 20–40 m.',
    'road:rural:hammarland-way-459195076': 'En kort bit av huvudvägen i Hammarland mellan två delar av Emkarbyvägen. Sockenkartan för Hammarby 1929 ritar vägen här.'}

em = O['road:emkarbyvagen']; godby = json.load(open('data/postal-route-godby.json'))
x = deepcopy(godby['extend'][0]); p68 = x['periods'][0]
gp = next(p for p in em['geometryPeriods'] if p['from'] == 1894 and p['to'] == 1968); g = G[gp['geometryId']]
em_split = deepcopy(em); i = em_split['geometryPeriods'].index(next(p for p in em_split['geometryPeriods'] if p['from'] == 1894 and p['to'] == 1968))
later = deepcopy(em_split['geometryPeriods'][i]); later['from'] = 1928; em_split['geometryPeriods'][i]['to'] = 1928; em_split['geometryPeriods'].insert(i + 1, later)
ext = dict(objectId='road:emkarbyvagen', inputHash=fingerprint(em_split), wholeGeometryId=x['wholeGeometryId'], wholeGeometryHash=x['wholeGeometryHash'],
           periods=[dict(**{'from': 1928, 'to': 1968}, geometryId=g['id'], geometryHash=digest(g), range=p68['range'], maps={'1928-jomala': 'present'},
                         bend=deepcopy(p68['bend']) | {'basis': 'Sockenkartan för Jomala 1928 ritar huvudvägen från Tingsbacka österut och i en båge till Buskböle, på samma linje som grundkartan 1968 (10–30 m). Bågen är samma väg som i perioden från 1968.'},
                         note='Österut från Tingsbacka i bågen förbi Buskböle till Bergens, där vägen svängde österut längs dagens Postgårdsvägen (sockenkartan för Jomala 1928). Perioden från 1894 delas vid 1928; före 1928 visas sträckan inte.')])
review = dict(schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='postalRoute1929Review', geometryPrefix='geometry:postal-route-1929:',
              source=dict(id='review:postal-route-1929', title='Postvägen genom Gölby och Godby på sockenkartorna 1928 och 1929 · granskning', url='assets/postal-route-1929.json'),
              sources=[], maps=L,
              method='Sockenkartorna för Jomala 1928, Saltvik 1929 (och utgåvan 1944) och Hammarby 1929 har lagts över katalogens vägar med ett rutnät på 100 m.',
              early=E, earlyBasis=basis, geometryNote='Objektets egen geometri (samma koordinater), där vägen är vägen på sockenkartan.',
              split=[dict(objectId='road:emkarbyvagen', geometryId=g['id'], **{'from': 1894, 'to': 1968}, at=1928)], extend=[ext])
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_postal_route_1929(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
for e in E: print(e['objectId'], e['firstYear'], e['lengthMeters'])
print('trial ok')
