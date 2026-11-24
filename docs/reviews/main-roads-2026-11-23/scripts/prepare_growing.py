"""Write data/main-roads-growing.json (batch 5). Usage: prepare_growing.py CATALOGUE_BEFORE.json.gz

Ranges from match_growing.py (batch5-growing.json), checked by eye on renders/b5-*.jpg. A stage's sources are the
editions whose frame holds at least 50 m of its ranges."""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from copy import deepcopy
from mariehamn_frame_1942 import fingerprint, TO_METRIC
from shapely.geometry import LineString, Polygon
from shapely.ops import substring
from pyproj import Transformer
from main_roads_growing import apply_main_roads_growing, REVIEW, _uncovered, _met

D = 'docs/reviews/main-roads-2026-11-23/'
cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
M = json.load(open(D + 'batch5-growing.json'))
rev = json.load(open('data/rural-map-review.json')); frames = {}
for s in rev['sources']:
    r = s.get('registration') or {}
    if 'metricFrame' in r:
        t = Transformer.from_crs(r['crs'], 'EPSG:3874', always_xy=True).transform; frames[s['id']] = Polygon([t(*p) for p in r['metricFrame']])
SPEC = {  # object: [(edition index, note)]
    'road:rural:hammarland-way-71082200': [(0, 'Grundkartorna 1021 04 och 1021 07 (1968) ritar Svartsmaravägen som huvudväg, i rött, på dagens linje från Bjärström över Bamböle, Grönalund och Mossberg till Svartsmara, utom de äldre kurvorna vid Svedals, Hammarbacka och Fågelholm och vid Breidablick.')],
    'road:rural:hammarland-skarpnatovagen-south': [(0, 'Grundkartan 1021 04 (1968) ritar Skarpnåtövägen som huvudväg, i rött, på dagens linje förbi Berglund, Lugnet, Karslund och Lillbolstad, utom den äldre vägen vid Norrgård.'),
                                                   (2, 'Utgåvan 1984 av 1021 04 ritar hela den södra delen på dagens linje, också den rätade sträckan vid Norrgård.')],
    'road:rural:hammarland-way-557084450': [(0, 'Grundkartan 1012 09 (1968) ritar Ringsbölevägen som huvudväg, i rött, på dagens linje genom Buskböle, förbi Västergård, Nedergård och Grins till Mellangård.')],
    'road:rural:hammarland-bovikvagen-east': [(0, 'Grundkartorna 1012 03 och 1021 01 (1968) ritar Bovikvägen som huvudväg, i rött, på dagens linje förbi Lugnet, Frihem och Stenbacka, men inte vid Furulund.')],
    'road:rural:hammarland-way-350331479': [(0, 'Grundkartan 1012 03 (1968) ritar Tellholmsvägen som huvudväg, i rött, på dagens linje från Karlgård förbi Aftonsol.')],
}
out = []
for oid, stages in SPEC.items():
    o = O[oid]; latest = o['geometryPeriods'][-1]; lp = [p for p in G[latest['geometryId']]['paths'] if len(p) > 1][0]; line = _met(lp)
    st, prev = [], []
    for k, note in stages:
        e = M[oid]['editions'][k]; ranges = e['ranges']
        # a later stage keeps what the earlier one has
        allr = sorted(ranges + prev); merged = []
        for a, b in allr:
            if merged and a <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], b)
            else: merged.append([a, b])
        srcs = sorted({sid for _, sid in e['years'] if sum(substring(line, a, b).intersection(frames[sid]).length for a, b in merged) >= 50})
        year = min(int(s.split(':')[2]) for s in srcs)
        st.append(dict(year=year, sources=srcs, ranges=merged, note=note)); prev = merged
    periods = []
    for g in o['geometryPeriods'][:-1]:
        cuts = sorted({g['from'], g['to']} | {s['year'] for s in st if g['from'] < s['year'] < g['to']})
        base = [_met(q) for q in G[g['geometryId']]['paths'] if len(q) > 1]
        for a, b in zip(cuts, cuts[1:]):
            stage = [s for s in st if s['year'] <= a]
            periods.append({'from': a, 'to': b, 'baseGeometryId': g['geometryId'], 'ranges': _uncovered(line, stage[-1]['ranges'], base) if stage else []})
    out.append(dict(objectId=oid, name=o['name'], inputHash=fingerprint(o), stages=st, periods=periods))
    print(o['name'], [(s['year'], s['sources'], round(sum(b - a for a, b in s['ranges']))) for s in st], [(p['from'], p['to'], round(sum(b - a for a, b in p['ranges']))) for p in periods])
review = dict(schemaVersion=1, reviewedAt='2026-11-24',
              source=dict(id='review:main-roads-growing', title='Huvudvägarna på grundkartorna intill Hammarlandsbladet · granskning', url='assets/main-roads-growing.json'),
              method='Dagens linje för vägobjekt vars tidiga perioder bara täcker kartbladet 1012 06, jämförd med den röda huvudvägssymbolen på grannbladens utgåvor (inom 12 m), och granskad för ögat.',
              objects=out)
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_main_roads_growing(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok')
