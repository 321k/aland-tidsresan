"""Write data/postal-route-godby.json: the postal route's leg from Emkarby through Gölby and Godby to Färjsundet on the
base maps 1012 09 Jomala and 1021 07 Godby (1968–1995). Usage: prepare_godby.py CATALOGUE_BEFORE.json.gz

Read on ../renders (grid 100 m, EPSG:3874):
- extg-sheet.jpg, bend-sheet.jpg, ext-sheet.jpg: Emkarbyvägen east of Tingsbacka. The 1968 map draws the main road
  from Tingsbacka east at N 6 676 760 and round today's Tingsgränd (OSM 1141053639) to Buskböle, then on today's line
  to Bergens, where it turned east along today's Postgårdsvägen. The 1978 map draws today's straight road at
  Tingsbacka and today's curve from Bergens to Godbyvägen at Gölby. Emkarbyvägen's own review stopped at the sheet edge
  at Tingsbacka (docs/emkarby-road-continuity.md); its geometry before 2021 ends there.
- golby-1968.jpg, h1-sheet.jpg: Postgårdsvägen is the 1968 main road from Bergens to Godbyvägen; the 1978 curve
  replaces it as the main road (it stays a local road).
- h2-sheet.jpg: Godbyvägen's piece at Björkäng (OSM 963762444) is the 1968 and 1978 road.
- gf-sheet.jpg, h3-sheet.jpg: from von Knorringsvägen's east end the 1968 main road runs north-east to the Färjsundet
  bridge on today's Sundsvägen ways.
- The two junction pieces (Godbyvägen at Gölby, 22 m; at the Godby crossroads, today a roundabout) close holes between
  dated objects; the 1968 maps draw the roads through them."""
import sys, json, gzip
from copy import deepcopy
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from hammarlandsvagen_main_road import metric, SNAPSHOTS
from sviby_connections import _piece
from postal_route_godby import apply_postal_route_godby, REVIEW
from shapely.geometry import Point, LineString

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
S = {s['id'] for s in cat['sources']}
F = {ds: {x['id']: x for x in json.load(gzip.open(f))['features']} for ds, (f, _) in SNAPSHOTS.items()}
EM, GB, VK2, VK1, SVH = 'road:emkarbyvagen', 'road:atlas1894:godbyvagen', 'road:qgis:saltvik:von-knorringsvagen-2-batch4', 'road:qgis:saltvik:von-knorringsvagen-1-batch4', 'road:qgis:saltvik:sundsvagen-varsundet-haraldsby'
SVH = next(k for k in O if k.startswith(SVH))
r = lambda x: round(x, 1); togeo = lambda q: [round(v, 7) for v in TO_GEO(*q)]; local = lambda x, y: (20490000 + x, 6670000 + y)

L = {'1968-jomala': dict(sourceId='nls:101209:1968', year=1968), '1978-jomala': dict(sourceId='nls:101209:1978', year=1978), '1985-jomala': dict(sourceId='nls:101209:1985', year=1985),
     '1995-jomala': dict(sourceId='nls:101209:1995', year=1995), '1968-godby': dict(sourceId='nls:102107:1968', year=1968), '1978-godby': dict(sourceId='nls:102107:1978', year=1978),
     '1985-godby': dict(sourceId='nls:102107:1985', year=1985), '1993-godby': dict(sourceId='nls:102107:1993', year=1993)}
assert all(l['sourceId'] in S for l in L.values()), [l for l in L.values() if l['sourceId'] not in S]

# --- Emkarbyvägen east of Tingsbacka -----------------------------------------------------------------------------------
em = O[EM]; whole = G['geometry:e76742ec1a46df8ce6ea']; wl = metric(whole['paths'][0])
old_end = Point(TO_METRIC(*G['geometry:1ed743bde36c0e86aeff']['paths'][0][-1])); a = r(wl.project(old_end))
bergens = r(wl.project(Point(20496439, 6675955)))
tg = F['osm-2026']['way/1141053639']['paths'][0]
leave = 8860.0; rejoin = r(wl.project(Point(TO_METRIC(*tg[-1]))))
bend_pts = [togeo(wl.interpolate(leave).coords[0])] + [togeo(local(*q)) for q in [(5460, 6765), (5550, 6760), (5650, 6756)]] + [list(q) for q in tg[:-1]] + [togeo(wl.interpolate(rejoin).coords[0])]
gp68 = next(p for p in em['geometryPeriods'] if p['from'] == 1968); gp78 = next(p for p in em['geometryPeriods'] if p['from'] == 1978)
extend = [dict(objectId=EM, inputHash=fingerprint(em), wholeGeometryId=whole['id'], wholeGeometryHash=digest(whole), periods=[
    dict(**{'from': 1968, 'to': 1978}, geometryId=gp68['geometryId'], geometryHash=digest(G[gp68['geometryId']]), range=[a, bergens], maps={'1968-jomala': 'present'},
         bend=dict(leaveAt=leave, rejoinAt=rejoin, points=bend_pts,
                   basis='Grundkartan 1968 ritar vägen från Tingsbacka österut längs N 6 676 760 och i en båge längs dagens Tingsgränd (OSM 1141053639) till Buskböle; dagens raka väg ritas först 1978. Bågen är avläst för hand på kartan 1968 fram till Tingsgränd och följer sedan dess koordinater.'),
         note='Österut från Tingsbacka till Bergens, där vägen 1968 svängde österut längs dagens Postgårdsvägen (grundkartan 1012 09, 1968).'),
    dict(**{'from': 1978, 'to': 2021}, geometryId=gp78['geometryId'], geometryHash=digest(G[gp78['geometryId']]), range=[a, r(wl.length)], maps={'1978-jomala': 'present', '1985-jomala': 'present', '1995-jomala': 'present'},
         note='Österut från Tingsbacka på dagens raka väg och i den nya kurvan från Bergens till Godbyvägen vid Gölby (grundkartorna 1012 09, 1978–1995).')])]
print('Emkarbyvägen extension from', a, 'to Bergens', bergens, '/ end', r(wl.length), '; bend', leave, '→', rejoin)

# --- new roads -------------------------------------------------------------------------------------------------------
OWNED = {(l['datasetId'], l['featureId']) for o in cat['objects'] for l in o.get('sourceLinks', [])}
def links(spec, basis):
    out = []
    for fid, rng, rev, *extra in spec:
        for ds, pre in (('osm-2026', 'way/'), ('osm-2025', 'road-2025-'), ('osm-2021', 'road-2021-'), ('osm-2014', 'road-2014-')):
            f = F[ds].get(pre + fid)
            if not f or len(f['paths']) != 1: continue
            if ds != 'osm-2026':                                    # an older extract only where the way is the same line
                p26 = metric(F['osm-2026']['way/' + fid]['paths'][0]); p = metric(f['paths'][0])
                if p.hausdorff_distance(p26) > 5 or rng or (ds, f['id']) in OWNED: continue
            p = f['paths'][0]; aa, bb = rng if rng else (0, len(p) - 1)
            out.append(dict(datasetId=ds, featureId=f['id'], sourceVertexRange=[aa, bb], sourceVertexCount=len(p), input=digest(f['paths']), basis=basis,
                            **({'reverse': True} if rev else {}), **(extra[0] if extra else {})))
    return out

def path2026(ls):
    built = []
    for l in [x for x in ls if x['datasetId'] == 'osm-2026']:
        part = _piece(F['osm-2026'][l['featureId']]['paths'][0], *l['sourceVertexRange'], l.get('reverse', False))
        built += part[1:] if built and built[-1] == part[0] else part
    return [built]

ring = F['osm-2026']['way/1193284948']['paths'][0]; rm = [TO_METRIC(*q) for q in ring]
i_in = min(range(len(rm)), key=lambda k: Point(rm[k]).distance(Point(TO_METRIC(*F['osm-2026']['way/1193284944']['paths'][0][0]))))
i_out = min(range(len(rm)), key=lambda k: Point(rm[k]).distance(Point(TO_METRIC(*F['osm-2026']['way/1193284946']['paths'][0][0]))))
print('roundabout arc from vertex', i_in, 'to', i_out, 'of', len(rm))
arc = (sorted([i_in, i_out]), i_in > i_out)
ARC_BASIS = 'Bågen av dagens rondell i Godby mellan Godbyvägen och von Knorringsvägen; rondellens övriga bågar hör till andra vägar och ägs inte här. 1968 var platsen en vägkorsning.'

specs = {
    'road:jomala:postgardsvagen': ('Postgårdsvägen', 'residential', 1968, EM, GB, [('1299708900', None, False), ('1299708897', None, False), ('162622255', None, False)],
                                   {'1968-jomala': 'present', '1978-jomala': 'present', '1985-jomala': 'present', '1995-jomala': 'present'},
                                   'Den gamla huvudvägen från Bergens österut till Godbyvägen vid Gölby. Grundkartan 1968 ritar den som huvudväg; från 1978 går huvudvägen i den nya kurvan söder om den, och Postgårdsvägen blir en lokal väg.'),
    'road:jomala:godbyvagen:golby-junction': ('Godbyvägen · vid Gölby', 'tertiary', 1968, GB, GB, [('731250732', None, False)],
                                   {'1968-jomala': 'present', '1978-jomala': 'present'}, 'En kort bit av Godbyvägen vid Gölby, mellan två delar av den daterade vägen. Grundkartorna ritar vägen här.'),
    'road:jomala:godbyvagen:bjorkang': ('Godbyvägen · vid Björkäng', 'tertiary', 1968, GB, GB, [('963762444', None, False)],
                                   {'1968-jomala': 'present', '1978-jomala': 'present'}, 'Godbyvägens bit vid Björkäng, mellan två delar av den daterade vägen. Grundkartorna 1968 och 1978 ritar huvudvägen här.'),
    'road:finstrom:godby-korsningen': ('Godbyvägen · korsningen i Godby', 'tertiary', 1968, GB, VK2,
                                   [('1133392114', None, True), ('1193284944', None, True), ('1193284948', [arc[0][0], arc[0][1]], arc[1], {'partialBasis': ARC_BASIS})],
                                   {'1968-godby': 'present', '1978-godby': 'present', '1985-godby': 'present', '1993-godby': 'present'},
                                   'Godbyvägens anslutning till von Knorringsvägen i Godby centrum. Grundkartorna ritar vägkorsningen; i dag ligger en rondell där, och linjen följer dess båge.'),
    'road:finstrom:sundsvagen:godby-farjsundet': ('Sundsvägen · Godby–Färjsundet', 'primary', 1968, VK1, SVH,
                                   [('35979864', None, True), ('118461526', None, False), ('172146731', None, False), ('35165557', None, False), ('172146730', None, False), ('65650237', None, False)],
                                   {'1968-godby': 'present', '1978-godby': 'present', '1985-godby': 'present', '1993-godby': 'present'},
                                   'Huvudvägen från von Knorringsvägens östra ände i Godby nordost till bron över Färjsundet. Grundkartorna 1968–1993 ritar den.'),
}
newRoads, surveys = [], []
for oid, (name, cls, fy, start, end, spec, mp, basis) in specs.items():
    ls = links(spec, basis.split('.')[0] + ', som den kartlagts detta år.')
    newRoads.append(dict(id=oid, name=name, routeId='road:route:postvagen', modernRoadClass=cls, roadWidth=6 if cls == 'primary' else 4, firstYear=fy, surveySourceId=oid + ':survey',
                         maps=mp, start=start, end=end, joinMeters=1, paths=path2026(ls), sourceLinks=ls, basis=basis,
                         geometryNote='Mittlinjen i OpenStreetMap 2026 (' + ', '.join(s[0] for s in spec) + '), använd som stabilt läge från ' + str(fy) + '.'))
    surveys.append(dict(id=oid + ':survey', title='OpenStreetMap · ' + name, url='https://www.openstreetmap.org/way/' + spec[0][0], issuedAt='2026'))
    print(name, round(metric(newRoads[-1]['paths'][0]).length, 1), 'm,', len(ls), 'links')

review = dict(schemaVersion=1, reviewedAt='2026-11-23', maps=L, geometryPrefix='geometry:postal-route-godby:', stagePrefix='postal-route-godby',
              source=dict(id='review:postal-route-godby', title='Postvägen från Emkarby genom Gölby och Godby till Färjsundet på grundkartorna · granskning', url='assets/postal-route-godby.json'),
              method='Grundkartorna 1012 09 och 1021 07 (1968–1995) har lagts över dagens vägar med ett rutnät på 100 m. Där katalogens vägar bryts längs postvägen har kartan avgjort vilken väg som ritas.',
              surveySources=surveys, extend=extend, newRoads=newRoads, stageFeatures=[])
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_postal_route_godby(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok:', len(trial['objects']) - len(cat['objects']), 'objects added')
