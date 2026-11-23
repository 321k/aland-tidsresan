"""Write data/mjolkdalsvagen.json: the roads branching off at the Gustavsberg corner. Usage: prepare_branches.py CATALOGUE_BEFORE.json.gz

Read on ../renders/branches (grid 100 m, EPSG:3874; catalogue red, OSM green):
- mj-cat-sheet.jpg, mj-k1944-cat.jpg, mj-sheet.jpg: Mjölkdalsvägen is the road on the 1928 sheet 1012 05 and its 1944
  and 1953 Kungsö editions, from the Gustavsberg corner south-east and then south along the shore, over its whole length
  and within 20–40 m. Sheet 1012 05 has no 1968 base map, so it was dated from 1978.
- smz-sheet.jpg, sm-cat-sheet.jpg: Småholmavägen is not on the 1928, 1944 or 1953 maps (fields, and a dotted path on
  another line towards Skomakars); the 1978 base map is the first to draw it. It keeps 1978 (no data change)."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest
from hammarlandsvagen_main_road import metric
from mockelo_road import apply_mjolkdalsvagen, MJOLKDAL

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
MJ = 'road:qgis:gottby:mjolkdalsvagen-100km5'
g = G[O[MJ]['geometryPeriods'][0]['geometryId']]; line = metric(g['paths'][0])
L = {'1928-hammarudda': dict(sourceId='nls:9c76c491-898b-4b0b-9331-7af223831264', year=1928), '1944-kungso': dict(sourceId='nls:9c72a692-458e-4804-af82-e6ac6dbf73fe', year=1944),
     '1953-kungso': dict(sourceId='nls:9c72a692-80ff-433c-950e-1cf484176101', year=1953)}
review = dict(schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:mjolkdalsvagen-1928:',
              source=dict(id='review:mjolkdalsvagen', title='Mjölkdalsvägen på sockenkartan 1928 · granskning', url='assets/mjolkdalsvagen.json'),
              sources=[], maps=L, method='Kartorna har lagts över varandra och över dagens vägar med ett rutnät på 100 m.',
              early=[dict(objectId=MJ, inputHash=fingerprint(O[MJ]), geometryId=g['id'], geometryHash=digest(g), lengthMeters=round(line.length, 1), firstYear=1928,
                          until=O[MJ]['states'][0]['from'], maps={k: 'present' for k in L}, ranges=[[0.0, round(line.length, 1)]])],
              earlyBasis={MJ: 'Mjölkdalsvägen från Möckelövägen vid Gustavsberg åt sydost och sedan söderut längs stranden är vägen på sockenkartan 1928 och utgåvorna 1944 och 1953 (Kungsö), i hela sin längd och inom 20–40 m. Bladet 1012 05 har ingen grundkarta från 1968, så objektet var daterat först från 1978.'},
              geometryNote='Objektets egen geometri (samma koordinater), där vägen är vägen på sockenkartan 1928.',
              notChanged={'road:qgis:gottby:smaholmavagen-1-100km5': 'Sockenkartan 1928 och utgåvorna 1944 och 1953 ritar ingen väg här, bara åker och en prickad stig i en annan riktning mot Skomakars. Grundkartan 1978 är den första som ritar vägen; objektet behåller 1978.'})
json.dump(review, open(MJOLKDAL, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_mjolkdalsvagen(lambda p: review if p == MJOLKDAL else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok; Mjölkdalsvägen', round(line.length, 1), 'm from', [s['from'] for s in {o['id']: o for o in trial['objects']}[MJ]['states']])
