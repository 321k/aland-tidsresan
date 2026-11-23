"""Write data/main-roads-archipelago.json. Usage: prepare_archipelago.py CATALOGUE_BEFORE.json.gz

Ranges come from match_editions.py and propose.py (red main-road symbol within 12 m of the line; batch2-proposal.json),
checked by eye on the contact sheets ../renders/b2-*.jpg (first edition) and b2L-*.jpg (later stage). Each range is
credited only to the sheets whose registered frame holds at least 50 m of it. Left out: tofto Vårdövägen (the 1970
match is fragmented) and Björkövägen del 1 (no match)."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
import maps
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.ops import substring
from mariehamn_frame_1942 import digest, fingerprint
from hammarlandsvagen_main_road import metric
from main_roads_archipelago import apply_main_roads_archipelago, REVIEW

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
S = {s['id'] for s in cat['sources']}
P = json.load(open('docs/reviews/main-roads-2026-11-23/batch2-proposal.json'))
SKIP = {'road:qgis:tofto:vardovagen-200km1'}
BASIS = {
 'road:qgis:sonnboda:foglovagen-200km1': 'Föglövägen genom Sonnboda ritas på grundkartan 1014 04 från 1970 som huvudväg på samma linje som i dag, utom vid Henriks, där kartans väg går i en båge (inte daterad här); den sista sträckan mot Geta saknas 1970.',
 'road:qgis:degerby:foglovagen-200km1': 'Föglövägen från Degerby ritas på grundkartan 1014 01 från 1970 som huvudväg på samma linje som i dag, utom vid Alkär, där kartans väg går i en båge (inte daterad här).',
 'road:qgis:degerby:hummersovagen-200km1': 'Hummersövägen ritas på grundkartan 1014 01 från 1970 som huvudväg på samma linje som i dag, utom en kort båge och den sista sträckan.',
 'road:qgis:fisko:fiskovagen-1-200km2': 'Fiskövägen ritas på grundkartan 1023 12 från 1971 som huvudväg på samma linje som i dag över mitten av sträckan; ändarna saknas på kartan.',
 'road:qgis:overo:overovagen-1-200km1': 'Överövägen ritas på grundkartan 1014 05 från 1970 som huvudväg på samma linje som i dag från 1 050 m till slutet.',
 'road:qgis:vardo:sandovagen-200km1': 'Sandövägen ritas på grundkartan 1023 01 från 1971 som huvudväg på samma linje som i dag; vid Tällholm saknas en kort sträcka och vägen ut mot Alören.',
 'road:qgis:ava:brandovagen-1-200km2': 'Brändövägen ritas på grundkartan 1041 03 från 1968 som huvudväg på samma linje som i dag vid Åva och vid Djurholm–Finnkors; utgåvan 1984 ritar även sträckorna över Andersör och Nötö.',
 'road:qgis:enklinge:enklingevagen-200km2': 'Enklingevägen ritas på grundkartan 1023 08 från 1971 som huvudväg på samma linje som i dag från byn söderut till Bovik och färjfästet; den norra delen saknas.',
 'road:qgis:overo:overovagen-2-200km1': 'Överövägen ritas på grundkartan 1014 05 från 1970 som huvudväg på samma linje som i dag, utom två korta sträckor.',
 'road:qgis:tofto:ango-bussovagen-200km1': 'Ängö-Bussövägen ritas på grundkartan 1014 03 från 1970 som huvudväg på samma linje som i dag från Ängö till Bussö by; den sista sträckan österut saknas.',
 'road:qgis:ava:brandovagen-2-200km2': 'Brändövägen ritas på grundkartan 1041 03 från 1968 som huvudväg på samma linje som i dag, utom en kort sträcka.',
 'road:qgis:overo:notovagen-200km1': 'Nötövägen ritas på grundkartan 1014 05 från 1970 som huvudväg på samma linje som i dag, utom en kort sträcka.',
 'road:qgis:sonnboda:naversholmavagen-200km1': 'Näversholmavägen ritas på grundkartan 1014 04 från 1970 som huvudväg till Näversholm och från utgåvan 1978 vidare mot Bondbacka; sträckan mot Andholm saknas.',
 'road:qgis:overo:ulversovagen-100km6': 'Ulversövägen ritas på grundkartan 1014 05 från 1970 som huvudväg på samma linje som i dag, utom mittdelen.',
 'road:qgis:sonnboda:bofjardsvagen-1-200km1': 'Bofjärdsvägen ritas på grundkartan 1014 04 från 1970 som huvudväg från Sonnboda, och längre ut från utgåvan 1978.',
 'road:qgis:seglinge:seglingevagen-200km2': 'Seglingevägen ritas på grundkartan 1014 09 från 1970 som huvudväg på samma linje som i dag, utom två korta sträckor vid Månsas.',
}
def frame(s):
    r = maps.SHEETS[s]['registration']; t = Transformer.from_crs(r['crs'], 'EPSG:3874', always_xy=True).transform
    return Polygon([t(*q) for q in r['metricFrame']])
label = lambda s: f"{s.split(':')[2]}-{s.split(':')[1]}"
L, E, basis, stagebasis = {}, [], {}, {}
for oid, p in P.items():
    if oid in SKIP: continue
    o = O[oid]; gp = o['geometryPeriods'][0]; g = G[gp['geometryId']]; line = metric(g['paths'][0]); n = round(line.length, 1)
    first = o['states'][0]['from']; assert len(g['paths']) == 1 and gp['from'] == first == p['firstYear'], oid
    fix = lambda rs: [[float(a), min(float(b), n)] for a, b in rs]
    def used(sheets, rs):
        return [s for s in sheets if sum(substring(line, a, b).intersection(frame(s)).length for a, b in rs) >= 50]
    maps_ = {}
    s0 = used(p['sheets0'], p['ranges']); assert s0, oid
    for s in s0: maps_[label(s)] = 'present'
    year0 = min(int(s.split(':')[2]) for s in s0)
    e = dict(objectId=oid, inputHash=fingerprint(o), geometryId=g['id'], geometryHash=digest(g), lengthMeters=n, firstYear=year0, until=first, maps=maps_, ranges=fix(p['ranges']))
    if p.get('later'):
        s1 = used(p['later']['sheets'], p['later']['ranges']); assert s1, oid
        for s in s1: maps_[label(s)] = 'present'
        e['laterStage'] = dict(firstYear=p['later']['year'], ranges=fix(p['later']['ranges'])); stagebasis[oid] = BASIS[oid]
    if oid.endswith(':foglovagen-200km1'): e['geometryName'] = oid.split(':')[2] + '-foglovagen-200km1'   # two Föglövägen objects
    E.append(e); basis[oid] = BASIS[oid]
    for k in maps_:
        y, sh = k.split('-'); L[k] = dict(sourceId=f'nls:{sh}:{y}', year=int(y))
assert all(l['sourceId'] in S for l in L.values()), [l for l in L.values() if l['sourceId'] not in S]
review = dict(schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:main-roads-archipelago:',
              source=dict(id='review:main-roads-archipelago', title='Huvudvägarna på grundkartorna i skärgården · granskning', url='assets/main-roads-archipelago.json'),
              sources=[], maps=dict(sorted(L.items())),
              method='Grundkartorna 1014 01, 03, 04, 05, 09, 1023 01, 08, 12 och 1041 03 (1968–1971, och 1978 eller 1984 för en senare etapp). Vägobjektens linje har jämförts med kartans röda huvudvägssymbol (inom 12 m, docs/reviews/main-roads-2026-11-23/scripts/match_editions.py) och granskats för ögat längs hela linjen.',
              early=E, earlyBasis=basis, laterStageBasis=stagebasis, laterStageNote='Del av objektets egen geometri (samma koordinater), där vägen är huvudvägen på den senare utgåvan.',
              geometryNote='Del av objektets egen geometri (samma koordinater), där dagens väg är den huvudväg grundkartan ritar.')
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_main_roads_archipelago(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
for e in E: print(e['objectId'][-38:], e['firstYear'], e['until'], sorted(e['maps']), e['ranges'], e.get('laterStage'))
print('trial ok')
