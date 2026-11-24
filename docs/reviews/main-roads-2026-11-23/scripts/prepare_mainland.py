"""Write data/main-roads-mainland.json. Usage: prepare_mainland.py CATALOGUE_BEFORE.json.gz

Ranges come from match_editions.py and propose.py (red main-road symbol within 12 m of the line; batch3-proposal.json),
checked by eye on the contact sheets ../renders/b3-*.jpg, b3L-*.jpg (later stage), b3z-*.jpg (closer views) and b3m-*.jpg
(lines over two sheets). Each range is credited only to the sheets of that edition whose registered frame holds at
least 50 m of it. Sundsvägen öster om Klippan (98 m, below the matcher's candidate limit) was added by hand, as the open item in
docs/postal-route-sund.md asks. Left out: Järsövägen (the 1968 match is short and partly over water; the 1978 pieces are fragments) and the two
Lemlandsvägen objects, which earlier reviews date in more detail."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts')
import maps
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.ops import substring
from mariehamn_frame_1942 import digest, fingerprint
from hammarlandsvagen_main_road import metric
from main_roads_mainland import apply_main_roads_mainland, REVIEW

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
S = {s['id'] for s in cat['sources']}
R = 'docs/reviews/main-roads-2026-11-23/'
P = json.load(open(R + 'batch3-proposal.json')); M = json.load(open(R + 'batch3-match.json'))
SKIP = {'road:qgis:mariehamn:jarsovagen-100km3',
        # Reviewed in more detail before (docs/lemlandsvagen-main-road.md, docs/mariehamn-major-roads.md): the
        # 1968 and 1978 maps still run the main road through Övre-Börs, sheet 1012 08 sits 30–60 m off in Lemland, and the
        # Solstrand stretch is absent on both. Those findings stand.
        'road:qgis:mariehamn:lemlandsvagen-1-100km3', 'road:qgis:mariehamn:lemlandsvagen-2-100km3'}
NOTE = {
 'road:qgis:lumparland:angosundsvagen-100km3': 'Ängösundsvägen ritas som huvudväg på samma linje som i dag, utom vid Åkerkulla, där kartans väg går i en båge strax intill (inte daterad här), och några korta stycken; utgåvan 1978 ritar mer av den.',
 'road:qgis:sund:mangstektavagen': 'Mångstektavägen ritas som huvudväg på samma linje som i dag, utom vid Delvik och några korta stycken, där kartans väg går i bågar strax intill; utgåvan 1978 ritar den hela.',
 'road:qgis:lumparland:svinovagen-100km3': 'Svinövägen ritas som huvudväg på samma linje som i dag, utom den sista biten ned till stranden.',
 'road:qgis:eckero:torpvagen-1-100km1': 'Torpvägen ritas som huvudväg vid Backans och från Torp söderut; mittdelen genom skogen saknas på kartan.',
 'road:qgis:eckero:sodra-overbyvagen-200km2': 'Södra Överbyvägen ritas som huvudväg på samma linje som i dag från Ekör till Överby; den västra delen saknas på kartan.',
 'road:qgis:jomala:norra-svibyvagen-batch5': 'Norra Svibyvägen ritas som huvudväg på samma linje som i dag, utom i kurvan vid Svibyån, där kartans väg går i en snävare båge (inte daterad här).',
 'road:qgis:eckero:skeppsviksvagen-100km1': 'Skeppsviksvägen ritas som huvudväg från Lund mot Skeppsvik, utom i en kurva där kartans väg går i en båge (inte daterad här); utgåvan 1978 ritar dagens linje där. Den första delen vid Torp saknas.',
 'road:qgis:bomarsund:lumpovagen-100km5': 'Lumpovägen ritas som huvudväg på samma linje som i dag från Lumpo by; där vägen korsar kartbladets kant ritas den inte, men den ritas i rött på båda sidor.',
 'road:qgis:sund:persbyvagen': 'Persbyvägen ritas som huvudväg på samma linje som i dag, i hela sin längd.',
 'road:qgis:jomala:narmovagen-100km4': 'Narmovägen ritas som huvudväg på samma linje som i dag, utom den första delen.',
 'road:qgis:mariehamn:norrbyvagen-100km3': 'Norrbyvägen ritas som huvudväg på samma linje som i dag genom Norrby, utom den första delen.',
 'road:qgis:mariehamn:lemlandsvagen-2-100km3': 'Lemlandsvägen ritas som huvudväg på samma linje som i dag, utom ett kort stycke.',
 'road:qgis:lumparland:stickvagen-100km4': 'Stickvägen ritas som huvudväg på samma linje som i dag, utom den första delen vid Klockars.',
 'road:qgis:mariehamn:lemlandsvagen-1-100km3': 'Lemlandsvägen mellan Knutsboda och Dragsvik ritas som huvudväg vid Lindåsen; utgåvan 1978 ritar den hela.',
 'road:qgis:bomarsund:sundsvagen-3-100km5': 'Sundsvägen genom Finby ritas som huvudväg på samma linje som i dag, i hela sin längd.',
 'road:sund:sundsvagen:klippan-vast': 'Sundsvägen vid Klippan ritas som huvudväg på samma linje som i dag, utom det första stycket, där vägen från Svensböle böjer in i den.',
 'road:sund:sundsvagen:klippan-ost': 'Sundsvägen öster om Klippanvägen ritas som huvudväg på samma linje som i dag, i hela sin längd.',
}
def frame(s):
    r = maps.SHEETS[s]['registration']; t = Transformer.from_crs(r['crs'], 'EPSG:3874', always_xy=True).transform
    return Polygon([t(*q) for q in r['metricFrame']])
label = lambda s: f"{s.split(':')[2]}-{s.split(':')[1]}"
sheetname = lambda s: f"{s.split(':')[1][:4]} {s.split(':')[1][4:]}"
L, E, basis, stagebasis = {}, [], {}, {}
for oid, p in P.items():
    if oid in SKIP: continue
    o = O[oid]; gp = o['geometryPeriods'][0]; g = G[gp['geometryId']]; line = metric(g['paths'][0]); n = round(line.length, 1)
    first = o['states'][0]['from']; assert len(g['paths']) == 1 and gp['from'] == first == p['firstYear'], oid
    fix = lambda rs: [[float(a), min(float(b), n)] for a, b in rs]
    used = lambda k, rs: [s for _, s in M[oid]['editions'][k][0]['editions'] if sum(substring(line, a, b).intersection(frame(s)).length for a, b in rs) >= 50]
    maps_ = {}
    s0 = used(0, p['ranges']); assert s0, oid
    for s in s0: maps_[label(s)] = 'present'
    year0 = min(int(s.split(':')[2]) for s in s0); assert year0 == p['year0'], oid
    e = dict(objectId=oid, inputHash=fingerprint(o), geometryId=g['id'], geometryHash=digest(g), lengthMeters=n, firstYear=year0, until=first, maps=maps_, ranges=fix(p['ranges']))
    b = f"Grundkartan {' och '.join(sheetname(s) for s in s0)} från {year0}: " + NOTE[oid]
    if p.get('later'):
        k = next(i for i, ed in enumerate(M[oid]['editions']) if ed[0]['editions'][0][0] == p['later']['year'])
        s1 = used(k, p['later']['ranges']); assert s1, oid
        for s in s1: maps_[label(s)] = 'present'
        e['laterStage'] = dict(firstYear=p['later']['year'], ranges=fix(p['later']['ranges'])); stagebasis[oid] = b
    E.append(e); basis[oid] = b
    for kk in maps_:
        y, sh = kk.split('-'); L[kk] = dict(sourceId=f'nls:{sh}:{y}', year=int(y))
assert all(l['sourceId'] in S for l in L.values()), [l for l in L.values() if l['sourceId'] not in S]
review = dict(schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:main-roads-mainland:',
              source=dict(id='review:main-roads-mainland', title='Huvudvägarna på grundkartorna i Lemland, Lumparland, Jomala, Eckerö och Sund · granskning', url='assets/main-roads-mainland.json'),
              sources=[], maps=dict(sorted(L.items())),
              method='Grundkartorna 1012 03, 08, 09, 11, 12 och 1021 10 (1968, och 1978 för en senare etapp). Vägobjektens linje har jämförts med kartans röda huvudvägssymbol (inom 12 m, docs/reviews/main-roads-2026-11-23/scripts/match_editions.py) och granskats för ögat längs hela linjen.',
              early=E, earlyBasis=basis, laterStageBasis=stagebasis, laterStageNote='Del av objektets egen geometri (samma koordinater), där vägen är huvudvägen på den senare utgåvan.',
              geometryNote='Del av objektets egen geometri (samma koordinater), där dagens väg är den huvudväg grundkartan ritar.')
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_main_roads_mainland(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
for e in E: print(e['objectId'][-38:], e['firstYear'], e['until'], sorted(e['maps']), e['ranges'], e.get('laterStage'))
print(len(E), 'objects; trial ok')
