"""Write data/main-roads-saltvik.json. Usage: prepare_saltvik.py CATALOGUE_BEFORE.json.gz

Ranges come from match_editions.py (red main-road symbol within 12 m of the line; batch1-match.json), checked by eye on
the contact sheets in ../renders/b1-*.jpg; short unmatched gaps where the map draws the same road beside the line (at
most 30 m off) are bridged. See docs/main-roads-saltvik.md for each object."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import digest, fingerprint
from hammarlandsvagen_main_road import metric
from main_roads_saltvik import apply_main_roads_saltvik, REVIEW

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
S = {s['id'] for s in cat['sources']}
SHEETS = {'svartsmara': '102104', 'geta': '102105', 'tjudo': '102108', 'hamnsund': '102111'}
L = {f'{y}-{n}': dict(sourceId=f'nls:{sh}:{y}', year=y) for n, sh in SHEETS.items() for y in (1968, 1978, 1984)}
L |= {f'{y}-saltvik': dict(sourceId=f'nls:102107:{y}', year=y) for y in (1968, 1978)}
assert all(l['sourceId'] in S for l in L.values()), [l for l in L.values() if l['sourceId'] not in S]
WHOLE = 'whole'
# object: (sheets, ranges 1968, later stage (year, ranges) or None, basis)
SPEC = {
 'road:qgis:tjudo:tjudovagen-100km1': (['tjudo', 'saltvik'], WHOLE, None,
   'Tjudövägen ritas på grundkartorna 1021 07 och 1021 08 från 1968 som huvudväg (röd) på samma linje som i dag, i hela sin längd; vid korsningen vid Backas går kartans väg i en något annan kurva, inom 30 m.'),
 'road:qgis:tjudo:hamnsundsvagen-1-100km1': (['tjudo'], WHOLE, None, 'Hamnsundsvägen ritas på grundkartan 1021 08 från 1968 som huvudväg på samma linje som i dag.'),
 'road:qgis:tjudo:hamnsundsvagen-2-100km1': (['tjudo', 'hamnsund'], WHOLE, None, 'Hamnsundsvägen ritas på grundkartorna 1021 08 och 1021 11 från 1968 som huvudväg på samma linje som i dag; två korta kurvor ligger inom 20 m.'),
 'road:qgis:tjudo:hamnsundsvagen-3-100km1': (['tjudo'], [[0.0, 290.0]], (1978, WHOLE), 'Hamnsundsvägen: grundkartan 1968 ritar de första 290 m som huvudväg på samma linje som i dag, och utgåvan 1978 hela sträckan.'),
 'road:qgis:svartsmara:skarpnatovagen-3': (['svartsmara'], WHOLE, None, 'Skarpnåtövägen ritas på grundkartan 1021 04 från 1968 som huvudväg längs samma sträckning som i dag; kartans väg följer några kurvor upp till 30 m från dagens rätade linje.'),
 'road:qgis:geta:sodravagen-2-200km2': (['geta'], [[0.0, 2210.0], [2600.0, 5950.0], [6340.0, 'end']], None,
   'Södravägen ritas på grundkartan 1021 05 från 1968 som huvudväg på samma linje som i dag, utom vid Bolstaholm och vid Östergård, där kartans väg går i äldre bågar 100–150 m från dagens raka väg (inte daterade här). Vid Tallbacka följer kartans väg några kurvor upp till 30 m från dagens linje.'),
 'road:qgis:tjudo:tobolevagen-100km1': (['tjudo'], [[0.0, 2120.0], [2540.0, 4340.0]], None,
   'Tobölevägen ritas på grundkartan 1021 08 från 1968 som huvudväg på samma linje som i dag, utom vid Norrgård, där kartans väg går i en båge västerut (inte daterad här). Den sista sträckan längs sjön vid Skaffan finns inte på kartan 1968.'),
 'road:qgis:hamnsund:hamnsundsvagen-200km2': (['hamnsund'], [[0.0, 1700.0], [1940.0, 'end']], None,
   'Hamnsundsvägen ritas på grundkartan 1021 11 från 1968 som huvudväg på samma linje som i dag, utom vid Kroken, där kartans väg går i en båge omkring 60 m österut (inte daterad här).'),
 'road:qgis:geta:finnovagen-100km4': (['geta'], [[1100.0, 'end']], (1984, [[590.0, 'end']]),
   'Finnövägen ritas på grundkartan 1021 05 från 1968 som huvudväg på samma linje som i dag från Långvik västerut; vid Danbo går kartans väg i en båge 40–60 m från dagens linje fram till utgåvan 1984, som ritar dagens linje därifrån. Vägens första del vid Gräggnäs ligger på annan linje på alla utgåvor.'),
}
E, basis, stagebasis = [], {}, {}
for oid, (sheets, r68, later, b) in SPEC.items():
    o = O[oid]; gp = o['geometryPeriods'][0]; g = G[gp['geometryId']]; line = metric(g['paths'][0]); n = round(line.length, 1)
    first = o['states'][0]['from']; assert len(g['paths']) == 1 and gp['from'] == first, oid
    fix = lambda rs: [[0.0, n]] if rs == WHOLE else [[a, n if b == 'end' else b] for a, b in rs]
    maps = {f'1968-{s}': 'present' for s in sheets}
    for y in (1978, 1984):
        if y < first:
            for s in sheets:
                if f'{y}-{s}' in L: maps[f'{y}-{s}'] = 'present'
    e = dict(objectId=oid, inputHash=fingerprint(o), geometryId=g['id'], geometryHash=digest(g), lengthMeters=n, firstYear=1968, until=first, maps=maps, ranges=fix(r68))
    if later:
        e['laterStage'] = dict(firstYear=later[0], ranges=fix(later[1])); stagebasis[oid] = b
    E.append(e); basis[oid] = b
review = dict(schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:main-roads-saltvik:',
              source=dict(id='review:main-roads-saltvik', title='Huvudvägarna på grundkartorna i norra och västra Saltvik och i Geta · granskning', url='assets/main-roads-saltvik.json'),
              sources=[], maps=L,
              method='Grundkartorna 1021 04, 05, 08 och 11 (1968, 1978, 1984). Vägobjektens linje har jämförts med kartans röda huvudvägssymbol (inom 12 m, docs/reviews/main-roads-2026-11-23/scripts/match_editions.py) och granskats för ögat längs hela linjen.',
              early=E, earlyBasis=basis, laterStageBasis=stagebasis, laterStageNote='Del av objektets egen geometri (samma koordinater), där vägen är huvudvägen på den senare utgåvan.',
              geometryNote='Del av objektets egen geometri (samma koordinater), där dagens väg är den huvudväg grundkartan ritar.')
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_main_roads_saltvik(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
for e in E: print(e['objectId'][-38:], e['until'], e['ranges'], e.get('laterStage'))
print('trial ok')
