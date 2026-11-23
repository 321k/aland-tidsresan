"""Write data/postal-route-sund.json. Usage: prepare_sund.py CATALOGUE_BEFORE.json.gz

Read on ../renders:
- lappbole-sheet.jpg (1021 10, 1968, 1978, 1985; OSM in green): Sundsvägen runs on today's line south-east across the
  sheet edge, between the Saltvik piece (owns way 71081797 to vertex 4.985) and del 2 (from vertex 6.677).
  lappbole-n-sheet.jpg (1012 09 and 1021 07) shows the same road west of the edge.
- klippan-sheet.jpg (1012 12, 1968, 1978, 1985, 1994) and klipp-we-sheet.jpg (1968 and 1978 enlarged): from 1978 the
  road runs straight along N 6 679 000 from del 2 to del 3 and on from del 3 to del 1. The 1968 sheet already draws the
  straight from the Svensböle junction eastwards (the road from Svensböle bends into it) and the Klippanvägen loop as a
  smaller road.
Two OSM ways run in parallel at each Klippan junction (615021063 beside 615021067, 613972000 beside 613971997); the
eastbound one is used and the other stays unowned."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import digest
from hammarlandsvagen_main_road import metric, SNAPSHOTS
from sviby_connections import _piece
from postal_route_sund import apply_postal_route_sund, REVIEW

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; S = {s['id'] for s in cat['sources']}
F = {ds: {x['id']: x for x in json.load(gzip.open(f))['features']} for ds, (f, _) in SNAPSHOTS.items()}
L = {f'{y}-lappbole': dict(sourceId=f'nls:102110:{y}', year=y) for y in (1968, 1978, 1985, 1993)}
L |= {f'{y}-klippan': dict(sourceId=f'nls:101212:{y}', year=y) for y in (1968, 1978, 1985, 1994)}
assert all(l['sourceId'] in S for l in L.values())
OWNED = {(l['datasetId'], l['featureId']) for o in cat['objects'] for l in o.get('sourceLinks', [])}
SALTVIK, DEL1, DEL2, DEL3 = ('road:qgis:saltvik:sundsvagen-lappbole-bladgransen', 'road:qgis:bomarsund:sundsvagen-1-100km5',
                             'road:qgis:bomarsund:sundsvagen-2-100km5', 'road:qgis:bomarsund:sundsvagen-3-100km5')

def rng(oid, fid):
    return next(l['sourceVertexRange'] for l in O[oid]['sourceLinks'] if l['featureId'] == fid)

def links(spec, basis):
    out = []
    for fid, r, rev in spec:
        for ds, pre in (('osm-2026', 'way/'), ('osm-2025', 'road-2025-'), ('osm-2021', 'road-2021-'), ('osm-2014', 'road-2014-')):
            f = F[ds].get(pre + fid)
            if not f or len(f['paths']) != 1: continue
            if ds != 'osm-2026':
                if r or (ds, f['id']) in OWNED or metric(f['paths'][0]).hausdorff_distance(metric(F['osm-2026']['way/' + fid]['paths'][0])) > 5: continue
            p = f['paths'][0]; a, b = r if r else (0, len(p) - 1)
            out.append(dict(datasetId=ds, featureId=f['id'], sourceVertexRange=[a, b], sourceVertexCount=len(p), input=digest(f['paths']), basis=basis,
                            **({'reverse': True} if rev else {})))
    return out

def path2026(ls):
    built = []
    for l in [x for x in ls if x['datasetId'] == 'osm-2026']:
        part = _piece(F['osm-2026'][l['featureId']]['paths'][0], *l['sourceVertexRange'], l.get('reverse', False))
        built += part[1:] if built and built[-1] == part[0] else part
    return [built]

W = 'way/71081797'
lap = links([('71081797', [rng(SALTVIK, W)[1], rng(DEL2, W)[0]], False)], 'Sundsvägen vid bladkanten i Lappböle, mellan Saltviksdelen och del 2, som den kartlagts detta år.')
kw = links([(w, None, False) for w in ('615021066', '615021068', '615021062', '615021067', '615021065', '613972003', '614875755')],
           'Sundsvägen raka sträckan vid Klippan mellan del 2 och del 3, som den kartlagts detta år.')
ke = links([(w, None, False) for w in ('614875759', '613971997')], 'Sundsvägen vid Klippan mellan del 3 och del 1, som den kartlagts detta år.')
present = lambda *ks: {k: 'present' for k in ks}
LAP, KW, KE = 'road:sund:sundsvagen:lappbole-bladkant', 'road:sund:sundsvagen:klippan-vast', 'road:sund:sundsvagen:klippan-ost'
osm = lambda oid, t, w: dict(id=oid + ':survey', title='OpenStreetMap · ' + t, url='https://www.openstreetmap.org/way/' + w, issuedAt='2026')
K1968 = (' Grundkartan 1968 ritar redan den raka vägen här, men katalogen följer Sundsvägsgranskningen, som låter den gamla'
         ' landsvägen förbi Klippan vara huvudvägen till 1978 och daterar del 2 och del 3 från 1978. Biten dateras därför här'
         ' från 1978, liksom grannarna; 1968 är en öppen fråga för Sundsvägsgranskningen (docs/postal-route-sund.md).')
review = dict(
    schemaVersion=1, reviewedAt='2026-11-23', maps=L, stagePrefix='postal-route-sund',
    source=dict(id='review:postal-route-sund', title='Sundsvägens luckor vid Lappböle och Klippan på grundkartorna · granskning', url='assets/postal-route-sund.json'),
    method='Grundkartbladen 1021 10 (Lappböle) och 1012 12 (Klippan), 1968–1994, med dagens vägar och ett rutnät på 100 m ovanpå.',
    surveySources=[osm(LAP, 'Sundsvägen vid Lappböle', '71081797'), osm(KW, 'Sundsvägen vid Klippan', '615021065'), osm(KE, 'Sundsvägen öster om Klippan', '614875759')],
    newRoads=[
        dict(id=LAP, name='Sundsvägen · Lappböle vid bladkanten', routeId='road:route:sundsvagen', modernRoadClass='primary', roadWidth=3, firstYear=1968, surveySourceId=LAP + ':survey',
             maps=present('1968-lappbole', '1978-lappbole', '1985-lappbole', '1993-lappbole'), start=SALTVIK, end=DEL2, joinMeters=1, paths=path2026(lap), sourceLinks=lap,
             basis='Sundsvägen sydost om Lappböle, mellan Saltviksdelen (som slutar vid en bladkant) och del 2. Grundkartan 1021 10 ritar vägen i dagens läge 1968, 1978, 1985 och 1993. Före 1968 är biten okänd; den lämnas tom.',
             geometryNote='Mittlinjen i OpenStreetMap 2026 (Sundsvägen, way 71081797 mellan de två ägda delarna), använd som stabilt läge från 1968.'),
        dict(id=KW, name='Sundsvägen · Klippan', routeId='road:route:sundsvagen', modernRoadClass='primary', roadWidth=3, firstYear=1978, surveySourceId=KW + ':survey',
             maps=present('1978-klippan', '1985-klippan', '1994-klippan'), start=DEL2, end=DEL3, joinMeters=1, paths=path2026(kw), sourceLinks=kw,
             basis='Den raka Sundsvägen vid Klippan mellan del 2 och del 3. Grundkartan 1012 12 ritar den 1978, 1985 och 1994.' + K1968,
             geometryNote='Mittlinjen i OpenStreetMap 2026 (sju bitar av Sundsvägen, de östgående vid korsningen med Svensbölevägen), använd som stabilt läge från 1978.'),
        dict(id=KE, name='Sundsvägen · öster om Klippan', routeId='road:route:sundsvagen', modernRoadClass='primary', roadWidth=3, firstYear=1978, surveySourceId=KE + ':survey',
             maps=present('1978-klippan', '1985-klippan', '1994-klippan'), start=DEL3, end=DEL1, joinMeters=1, paths=path2026(ke), sourceLinks=ke,
             basis='Sundsvägen från korsningen vid Klippanvägen österut till del 1. Grundkartan 1012 12 ritar den 1978, 1985 och 1994. Före 1978 hör sträckan till den gamla landsvägen Hallbacka–Klippan.',
             geometryNote='Mittlinjen i OpenStreetMap 2026 (två bitar av Sundsvägen, den östgående vid korsningen), använd som stabilt läge från 1978.')],
    stageFeatures=[])
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
for nr in review['newRoads']: print(nr['name'], round(metric(nr['paths'][0]).length, 1), 'm,', len(nr['sourceLinks']), 'links')
trial = deepcopy(cat)
apply_postal_route_sund(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok:', len(trial['objects']) - len(cat['objects']), 'objects added')
