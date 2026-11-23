"""Write data/postal-route-storby.json. Usage: prepare_storby.py CATALOGUE_BEFORE.json.gz

Read on ../renders/harbour-101215-sheet.jpg (sheet 1012 15 registered on its printed grid, 1968, 1978, 1985, 1994; OSM
in green) and storby-sheet.jpg (1012 03, 1968–1985): the main road runs from Labbas south-west past Krogarviken to a
junction (E 20 474 752 N 6 678 848). From there one road leads south past the post and customs house ("Post Tull",
"Post Posti") and another on north-west to Berghamn harbour. Today: Eckerövägen (OSM 25208185, its first 17 vertices,
and four junction pieces to the Marsund connection at Labbas) and Sandmovägen (1066815068 and the first vertices of
25208110)."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import digest
from hammarlandsvagen_main_road import metric, SNAPSHOTS
from sviby_connections import _piece
from postal_route_storby import apply_postal_route_storby, REVIEW

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; S = {s['id'] for s in cat['sources']}
F = {ds: {x['id']: x for x in json.load(gzip.open(f))['features']} for ds, (f, _) in SNAPSHOTS.items()}
MARSUND = 'road:marsund:eckero-hammarland'
REG = json.load(open('docs/reviews/postal-route-2026-11-23/data/registrations-101215.json'))['sources']
map_sources = [{k: v for k, v in r.items() if k not in ('registration', 'sheet', 'imageSize', 'originalSha256')} | {'url': r['originalUrl'], 'issuedAt': str(r['year'])} for r in REG]
for m in map_sources: m.pop('originalUrl', None)
L = {f'{y}-storby': dict(sourceId=f'nls:101215:{y}', year=y) for y in (1968, 1978, 1985, 1994)}
L |= {f'{y}-eckero': dict(sourceId=f'nls:101203:{y}', year=y) for y in (1968, 1978, 1985)}
assert all(l['sourceId'] in S for k, l in L.items() if k.endswith('eckero'))
OWNED = {(l['datasetId'], l['featureId']) for o in cat['objects'] for l in o.get('sourceLinks', [])}

def links(spec, basis):
    out = []
    for fid, rng, rev, *extra in spec:
        for ds, pre in (('osm-2026', 'way/'), ('osm-2025', 'road-2025-'), ('osm-2021', 'road-2021-'), ('osm-2014', 'road-2014-')):
            f = F[ds].get(pre + fid)
            if not f or len(f['paths']) != 1: continue
            if ds != 'osm-2026':
                if rng or (ds, f['id']) in OWNED or metric(f['paths'][0]).hausdorff_distance(metric(F['osm-2026']['way/' + fid]['paths'][0])) > 5: continue
            p = f['paths'][0]; a, b = rng if rng else (0, len(p) - 1)
            out.append(dict(datasetId=ds, featureId=f['id'], sourceVertexRange=[a, b], sourceVertexCount=len(p), input=digest(f['paths']), basis=basis,
                            **({'reverse': True} if rev else {}), **(extra[0] if extra else {})))
    return out

def path2026(ls):
    built = []
    for l in [x for x in ls if x['datasetId'] == 'osm-2026']:
        part = _piece(F['osm-2026'][l['featureId']]['paths'][0], *l['sourceVertexRange'], l.get('reverse', False))
        built += part[1:] if built and built[-1] == part[0] else part
    return [built]

EK, SM = 'road:eckero:eckerovagen:storby-hamn', 'road:eckero:sandmovagen:posthuset'
ek_links = links([('25208185', [0, 16], True, {'partialBasis': 'Resten av vägen (vertex 16–28) är vägen vidare mot Berghamns hamn, som inte granskas här.'}),
                  ('174570487', None, True), ('174570484', None, False), ('172716458', None, False), ('174570483', None, False), ('1182793512', None, True)],
                 'Huvudvägen från Labbas till vägskälet vid Krogarviken i Storby, som den kartlagts detta år.')
sm_links = links([('1066815068', None, False), ('25208110', [0, 2], False, {'partialBasis': 'Resten av vägen är Sandmovägens slinga österut, som inte granskas här.'})],
                 'Vägen från vägskälet vid Krogarviken förbi post- och tullhuset, som den kartlagts detta år.')
present = lambda *ks: {k: 'present' for k in ks}
review = dict(
    schemaVersion=1, reviewedAt='2026-11-23', maps=L, stagePrefix='postal-route-storby', mapSources=map_sources,
    source=dict(id='review:postal-route-storby', title='Postvägens början vid post- och tullhuset i Storby på grundkartorna · granskning', url='assets/postal-route-storby.json'),
    method='Grundkartbladet 1012 15 är registrerat på sitt tryckta KKJ-rutnät (kilometerkryss, största avvikelse 4 m; docs/reviews/postal-route-2026-11-23/data/registrations-101215.json) och lagt över dagens vägar med ett rutnät på 100 m, tillsammans med bladet 1012 03.',
    surveySources=[dict(id=EK + ':survey', title='OpenStreetMap · Eckerövägen i Storby', url='https://www.openstreetmap.org/way/25208185', issuedAt='2026'),
                   dict(id=SM + ':survey', title='OpenStreetMap · Sandmovägen vid post- och tullhuset', url='https://www.openstreetmap.org/way/1066815068', issuedAt='2026')],
    newRoads=[
        dict(id=EK, name='Eckerövägen · Storby hamn–Labbas', routeId='road:route:postvagen', modernRoadClass='primary', roadWidth=6, firstYear=1968, surveySourceId=EK + ':survey',
             maps=present('1968-storby', '1978-storby', '1985-storby', '1994-storby', '1968-eckero', '1978-eckero', '1985-eckero'),
             start=None, freeStartBasis='Vägskälet vid Krogarviken, där vägen till post- och tullhuset tar av och huvudvägen fortsätter mot Berghamns hamn (inte granskad här).',
             end=MARSUND, joinMeters=1, paths=path2026(ek_links), sourceLinks=ek_links,
             basis='Huvudvägen i Storby från Labbas sydväst förbi Krogarviken till vägskälet vid post- och tullhuset. Grundkartorna 1012 15 och 1012 03 ritar den 1968, 1978, 1985 och 1994. Den saknades i katalogen eftersom bladet 1012 15 inte var registrerat.',
             geometryNote='Mittlinjen i OpenStreetMap 2026 (Eckerövägen, way 25208185 till vägskälet, och fyra anslutningsbitar), använd som stabilt läge från 1968.'),
        dict(id=SM, name='Sandmovägen · vid post- och tullhuset', routeId='road:route:postvagen', modernRoadClass='tertiary', roadWidth=4, firstYear=1968, surveySourceId=SM + ':survey',
             maps=present('1968-storby', '1978-storby', '1985-storby', '1994-storby'),
             start=EK, end=None, freeEndBasis='Post- och tullhuset i Storby (building:osm:way-342899630), postvägens början på Åland; vägen fortsätter som Sandmovägens slinga (inte granskad här).',
             joinMeters=1, paths=path2026(sm_links), sourceLinks=sm_links,
             basis='Vägen från vägskälet vid Krogarviken söderut förbi post- och tullhuset ("Post Tull", "Post Posti"). Grundkartorna 1012 15 ritar den 1968–1994.',
             geometryNote='Mittlinjen i OpenStreetMap 2026 (Sandmovägen, way 1066815068 och början av way 25208110), använd som stabilt läge från 1968.')],
    stageFeatures=[])
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
for nr in review['newRoads']: print(nr['name'], round(metric(nr['paths'][0]).length, 1), 'm,', len(nr['sourceLinks']), 'links')
trial = deepcopy(cat)
apply_postal_route_storby(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok:', len(trial['objects']) - len(cat['objects']), 'objects added')
