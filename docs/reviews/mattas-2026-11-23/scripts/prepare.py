"""Write data/mattas-link.json. Usage: prepare.py CATALOGUE_BEFORE.json.gz

Read on ../renders/m-sheet.jpg (1929 Hammarby, 1944 print, base maps 101206 1968, 1978, 1985, 1995; grid 100 m,
EPSG:3874, OSM green): the road leaves Mattas north round the old bend (ways 495221553 and 160987689, on the line in
every edition) and runs straight on north-east. On the 1968 map it passes E 20 493 297 N 6 671 573, 3 354/1 626 and
3 424/1 675 and meets Södersundavägen at about 3 515/1 732. The 1929 and 1944 maps draw the same line and nothing on
Södersundavägen's line west of the junction. The 1995 map draws today's road through Mattas (the bypass) as the main
road."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from hammarlandsvagen_main_road import metric
from mattas_link import apply_mattas_link, REVIEW
from shapely.geometry import Point, LineString

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
SV, B1, B2 = 'road:rural:hammarland-way-86548779', 'road:rural:hammarland-way-495221553', 'road:rural:hammarland-way-160987689'
OLD = 'road:hammarland:gamla-sodersundavagen:mattas'
r = lambda x: round(x, 1); togeo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
local = lambda x, y: (20490000 + x, 6670000 + y)

whole = next(G[gp['geometryId']] for gp in O[SV]['geometryPeriods'] if gp['to'] is None)
wl = metric(whole['paths'][0])
mj = wl.project(Point(local(3515, 1732))); junction = wl.interpolate(mj)
bend_end = G[O[B2]['geometryPeriods'][0]['geometryId']]['paths'][0][-1]
trace = [local(3297, 1573), local(3354, 1626), local(3424, 1675)]
path = [list(bend_end)] + [togeo(q) for q in trace] + [togeo(junction.coords[0])]
pl = metric(path)
first = O[SV]['geometryPeriods'][0]; old_range = None
for rv in (json.load(open('data/sodersundavagen.json'))['early'][0]['ranges'][0],):
    old_range = rv
print('link', r(pl.length), 'm; junction on Södersundavägen at', r(mj), 'm of', r(wl.length), '; the periods were', old_range)

L = {'1929-hammarby': dict(sourceId='nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08', year=1929), '1944-nafsby': dict(sourceId='nls:9c72a692-bae4-473d-93bb-7bcdee1222e7', year=1944),
     '1968-hammarby': dict(sourceId='nls:101206:1968', year=1968), '1978-hammarby': dict(sourceId='nls:101206:1978', year=1978),
     '1985-hammarby': dict(sourceId='nls:101206:1985', year=1985), '1995-hammarby': dict(sourceId='nls:101206:1995', year=1995)}
def whole_early(oid):
    g = G[O[oid]['geometryPeriods'][0]['geometryId']]; line = metric(g['paths'][0])
    return dict(objectId=oid, inputHash=fingerprint(O[oid]), geometryId=g['id'], geometryHash=digest(g), lengthMeters=r(line.length), firstYear=1929,
                until=O[oid]['states'][0]['from'], maps={'1929-hammarby': 'present', '1944-nafsby': 'present'}, ranges=[[0.0, r(line.length)]])
keep = [old_range[0], r(mj)]
basis_cut = 'Vägen från Södersunda genom Ulvsby fram till bågen mot kyrkan, från korsningen med den gamla vägen från Mattas. De västligaste 170 m av objektets linje är förbifarten från 1995; ingen karta före 1995 ritar en väg där.'
periods = []
for gp in O[SV]['geometryPeriods']:
    if gp['to'] is not None and gp['to'] <= 1995:
        y = gp['from']; k = {1929: '1929-hammarby', 1968: '1968-hammarby', 1978: '1978-hammarby', 1985: '1985-hammarby'}[y]
        periods.append(dict(**{'from': gp['from'], 'to': gp['to']}, geometryId=gp['geometryId'], range=keep, maps={k: 'present'}, basis=basis_cut))
review = dict(
    schemaVersion=1, reviewedAt='2026-11-23', reviewProperty='mainRoadReview', geometryPrefix='geometry:mattas-link:',
    source=dict(id='review:mattas-link', title='Vägen från Mattas till Södersundavägen på sockenkartan 1929 och grundkartorna · granskning', url='assets/mattas-link.json'),
    sources=[], maps=L,
    method='Kartorna har lagts över varandra och över dagens vägar med ett rutnät på 100 m. Bågens vägar (OSM 495221553 och 160987689) ligger på kartornas väg i alla utgåvor, vilket visar att registreringen stämmer här.',
    early=[whole_early(B1), whole_early(B2)],
    earlyBasis={B1: 'Den gamla vägens båge norrut från Mattas, på sockenkartan 1929 och 1944 års tryck av samma kartläggning. Objektet var daterat först från grundkartan 1968.',
                B2: 'Den gamla vägens båge norrut från Mattas och början av den raka sträckan mot nordost, på sockenkartan 1929 och 1944 års tryck. Objektet var daterat först från grundkartan 1968.'},
    geometryNote='Objektets egen geometri (samma koordinater), där vägen är vägen på sockenkartan 1929.',
    oldRoad=dict(id=OLD, name='Gamla Södersundavägen · Mattas', routeId='road:Gamla Södersundavägen', modernRoadClass='secondary', roadWidth=4, firstYear=1929, until=1995,
                 maps={'1929-hammarby': 'present', '1944-nafsby': 'present', '1968-hammarby': 'present', '1978-hammarby': 'present', '1985-hammarby': 'present', '1995-hammarby': 'unclear'},
                 untilBasis='Grundkartan 1995 ritar dagens väg genom Mattas (förbifarten) som huvudväg; om den gamla sträckan ännu ritas som mindre väg går inte att avgöra säkert, och den finns inte i OpenStreetMap.',
                 path=path, lengthMeters=r(pl.length), referenceRange=[0, None], endSnapMeters=[0.0, 0.0], endSnapLimit=1, endObjects=[B2, SV], todayRoadName='Södersundavägen',
                 basis='Den gamla vägen från bågen vid Mattas rakt mot nordost till Södersundavägen. Sockenkartan 1929, 1944 års tryck och grundkartorna 1968, 1978 och 1985 ritar den. Grundkartan 1995 ritar förbifarten genom Mattas som huvudväg. Inget av den finns i OpenStreetMap.',
                 traceBasis='Mittlinjen är avläst för hand på grundkartan 1968 (rutnät 100 m), som stämmer med sockenkartan 1929. Den västra änden är bågens ände (way 160987689), den östra en punkt på Södersundavägen.',
                 afterNote='Grundkartan 1995 ritar förbifarten som huvudväg. Exakt när den gamla sträckan togs ur bruk är inte känt.'),
    coverage=[dict(objectId=SV, wholeGeometryId=whole['id'], wholeGeometryHash=digest(whole), periods=periods,
                   geometryNote='Del av objektets egen geometri (samma koordinater), från korsningen med den gamla vägen från Mattas genom Ulvsby fram till bågen mot Jomala kyrka.')])
# the coverage step checks the object after _apply (which leaves it unchanged): its fingerprint now
review['coverage'][0]['inputHash'] = fingerprint(O[SV])
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_mattas_link(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
T = {o['id']: o for o in trial['objects']}
print('trial ok:', len(trial['objects']) - len(cat['objects']), 'object added; Södersundavägen periods', [(g['from'], g['to'], g.get('canonicalRange')) for g in T[SV]['geometryPeriods']])
