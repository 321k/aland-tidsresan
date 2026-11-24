"""Write data/main-roads-new.json (batch 4: main roads no object has). Usage: prepare_new.py CATALOGUE_BEFORE.json.gz

Each road is today's OSM ways in order (unowned main-road ways, batch4-unowned.json), dated by the base-map editions
on which match_editions.py finds the red main-road symbol under at least half of it (batch4-match.json) and that were
checked by eye (renders/b4-*.jpg). The same ways in the older OSM extracts are owned too where their coordinates are
identical. Ends rest on the road they join (within 1 m) or are stated free ends."""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from copy import deepcopy
from mariehamn_frame_1942 import digest
from hammarlandsvagen_main_road import metric, SNAPSHOTS

D = 'docs/reviews/main-roads-2026-11-23/'
REVIEW = 'data/main-roads-new.json'
cat = json.load(gzip.open(sys.argv[1]))
match = json.load(open(D + 'batch4-match.json'))
snap = {d: {x['id']: x for x in json.load(gzip.open(f))['features']} for d, (f, p) in SNAPSHOTS.items()}
FREE_STUB = 'Vägen fortsätter här på en kort bit (under 50 m) fram till korsningen, som ingen väg i katalogen har.'

ROADS = [
    dict(slug='kumlinge:kungshamnsvagen', name='Kungshamnsvägen · Kumlinge', route='road:route:kumlinge:kungshamnsvagen', match='cand:way/1291807287',
         ways=[('1291807287', False), ('142810130', False), ('738205660', True)],
         start='road:qgis:kumlinge:kumlingevagen-200km2', end='road:qgis:kumlinge:vasterviksvagen-200km2',
         note='Grundkartan 1023 07 (1971) ritar vägen från Kumlingevägen österut förbi Skålberg och Bäckängen till Västerviksvägen i rött, som huvudväg, liksom utgåvorna 1985 och 1991. Vid Skålberg går den röda vägen på alla tre utgåvorna omkring 30 m norr om dagens linje, på omkring 200 m (1991 på omkring 150 m).'),
    dict(slug='saltvik:odkarbyvagen-haga', name='Ödkarbyvägen · Ödkarby–Haga', route='road:route:saltvik:odkarbyvagen-haga', match='cand:way/65617754',
         ways=[('54052710', False), ('65617754', False)],
         start=None, freeStart=FREE_STUB.replace('kort bit (under 50 m) fram till korsningen', 'kort bit fram till korsningen med Saltviksvägen'), end='road:qgis:saltvik:hagavagen',
         note='Grundkartan 1021 07 (1968) ritar vägen från Ödkarby genom byn och över Haga slätten till Haga i rött, som huvudväg, liksom utgåvorna 1978, 1985 och 1993.'),
    dict(slug='lumparland:bistorpvagen', name='Bistorpvägen', route='road:route:lumparland:bistorpvagen', match='cand:way/349909843',
         ways=[('349909843', False)], start='road:qgis:lumparland:lemlandsvagen-100km3', end='road:qgis:lumparland:bistorpberget-100km4',
         note='Grundkartan 1012 11 (1968) ritar vägen från Lemlandsvägen norrut genom Bistorp förbi Hinders och Västergård i rött, som huvudväg, liksom utgåvorna 1978, 1985 och 1995.'),
    dict(slug='sund:sonrodavagen', name='Sonrödavägen', route='road:route:sund:sonrodavagen', match='cand:way/38810657',
         ways=[('38810657', False), ('71083924', False)], start='road:qgis:sund:bjorbyvagen-rosenberg', end=None, freeEnd=FREE_STUB,
         note='Grundkartan 1021 10 (1968) ritar vägen från Björbyvägen västerut förbi Karlsro och norr om Sonröda träsk i rött, som huvudväg, liksom utgåvorna 1978, 1985 och 1993. Vid Karlsro, på omkring 100 m, går den röda vägen genom korsningen söder om dagens kurva.'),
    dict(slug='jomala:klockargrand', name='Klockargränd', route='road:route:jomala:klockargrand', match='cand:way/1423016201',
         ways=[('1423016201', False), ('143791594', False), ('963760099', False)], start=None, freeStart=FREE_STUB, end=None, freeEnd=FREE_STUB,
         note='Grundkartan 1012 09 (1968) ritar vägen från Godbyvägen vid posten sydväst mot Uppgård i rött, som huvudväg, liksom utgåvorna 1978, 1985 och 1995.'),
    dict(slug='brando:langang-farjfastet', name='Vägen till färjfästet · Långäng', route='road:route:brando:langang-farjfastet', match='cand:way/37711324',
         ways=[('37711324', False)], start='road:qgis:brando:brandovagen-1-200km2', end=None,
         freeEnd='Färjfästet vid Norrviken, som grundkartan 1969 ritar vid vägens ände.',
         note='Grundkartan 1041 02 (1969) ritar vägen från Långäng norrut till färjfästet vid Norrviken i rött, som huvudväg, liksom utgåvorna 1984 och 1991.'),
    dict(slug='svartsmara:bovikvagen', name='Bovikvägen', route='road:route:svartsmara:bovikvagen', match='cand:way/1067038810',
         ways=[('1067038810', False)], start='road:qgis:svartsmara:skarpnatovagen-5', end='road:qgis:svartsmara:mellanakersvagen-2',
         note='Grundkartan 1021 04 (1968) ritar vägen från Skarpnåtövägen västerut förbi Nybonds i rött, som huvudväg, liksom utgåvorna 1978, 1984 och 1993.'),
    dict(slug='kokar:pavals', name='Vägen vid Påvals · Kökar', route='road:route:kokar:pavals', match='cand:way/672386484',
         ways=[('672386484', False), ('745671649', False)], start='road:qgis:kokar:kokarvagen-200km2', end='road:qgis:kokar:valovagen-200km2',
         note='Grundkartan 1013 12 (1971) ritar vägen från Kökarvägen vid Påvals norrut till Valövägen i rött, som huvudväg, liksom utgåvorna 1985 och 1995.'),
    dict(slug='sund:bjorbyvagen-trygghem', name='Björbyvägen · Strömsborg–Trygghem', route='road:route:bjorbyvagen-rosenberg', match='cand:way/70574479',
         ways=[('70574479', False)], start='road:qgis:sund:bjorbyvagen-rosenberg', end=None, freeEnd=FREE_STUB,
         note='Grundkartan 1021 10 (1968) ritar vägen från Trygghem söderut till Strömsborg i rött, som huvudväg, liksom utgåvorna 1978, 1985 och 1993.'),
    dict(slug='sund:eliasvagen', name='Eliasvägen', route='road:route:sund:eliasvagen', match='cand:way/355197649',
         ways=[('355197649', False)], start=None, freeStart=FREE_STUB, end='road:qgis:sund:bjorbyvagen-rosenberg',
         note='Grundkartan 1021 10 (1968) ritar vägen från Trygghem längs Björby träsk till Nybonds i rött, som huvudväg, liksom utgåvorna 1978, 1985 och 1993.'),
]

labels, roads, survey = {}, [], []
for r in ROADS:
    m = match[r['match']]
    total = sum(x['length'] for x in m['editions'][0])
    present = []
    for e in m['editions']:
        if sum(x['matched'] for x in e) >= 0.5 * total:
            for y, sid in sorted({t for x in e for t in map(tuple, x['editions'])}):
                k = f"{y}-{sid.split(':')[1]}"
                labels[k] = dict(sourceId=sid, year=y); present.append(k)
    present = sorted(set(present))
    first = min(labels[k]['year'] for k in present)
    links, built = [], []
    for w, rev in r['ways']:
        f = snap['osm-2026']['way/' + w]; p = f['paths'][0]
        for d, (file, prefix) in SNAPSHOTS.items():
            x = snap[d].get(prefix + w)
            if x and digest(x['paths']) == digest(f['paths']):
                links.append(dict(datasetId=d, featureId=prefix + w, sourceVertexRange=[0, len(p) - 1], sourceVertexCount=len(p), input=digest(f['paths']),
                                  basis='Hela vägen i detta utdrag, med samma koordinater som 2026.', **({'reverse': True} if rev else {})))
        part = [list(q) for q in (p[::-1] if rev else p)]
        built += part[1:] if built and built[-1] == part[0] else part
    links.sort(key=lambda l: (list(SNAPSHOTS).index(l['datasetId']), [w for w, _ in r['ways']].index(l['featureId'].rsplit('-', 1)[-1].split('/')[-1])))
    oid = 'road:main-roads-new:' + r['slug']
    sv = oid + ':survey'
    survey.append(dict(id=sv, title='OpenStreetMap · ' + r['name'], url='https://www.openstreetmap.org/way/' + r['ways'][0][0], issuedAt='2026'))
    nr = dict(id=oid, name=r['name'], routeId=r['route'], modernRoadClass=snap['osm-2026']['way/' + r['ways'][0][0]]['class'], roadWidth=3, firstYear=first,
              surveySourceId=sv, maps={k: 'present' for k in present}, start=r['start'], end=r['end'], joinMeters=1,
              sourceLinks=links, paths=[built], lengthMeters=round(metric(built).length, 1), basis=r['note'],
              geometryNote=f"Mittlinjen i OpenStreetMap 2026 ({len(r['ways'])} {'väg' if len(r['ways']) == 1 else 'vägar i följd'}), använd som stabilt läge från {first}.")
    if r.get('freeStart'): nr['freeStartBasis'] = r['freeStart']
    if r.get('freeEnd'): nr['freeEndBasis'] = r['freeEnd']
    roads.append(nr)
    print(oid, first, present, nr['lengthMeters'], len(links), 'links')
review = dict(schemaVersion=1, reviewedAt='2026-11-24',
              method='Huvudvägar i OpenStreetMap 2026 (primary, secondary, tertiary) som inget objekt i katalogen har, jämförda med grundkartornas röda huvudvägssymbol i alla registrerade utgåvor och granskade för ögat.',
              maps=dict(sorted(labels.items())),
              source=dict(id='review:main-roads-new', title='Huvudvägar som saknades i katalogen · granskning', url='assets/main-roads-new.json'),
              surveySources=survey, newRoads=roads, stageFeatures=[])
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
from main_roads_new import apply_main_roads_new
trial = deepcopy(cat)
apply_main_roads_new(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok', len(trial['objects']) - len(cat['objects']), 'objects added')
