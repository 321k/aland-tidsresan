"""Builds data/mariehamn-approaches-1942.json: review of the 1942 approach-road traces.

Retained for audit. It captures input hashes of the catalogue objects, city-stage trace features and
original traces at review time; rerunning it after those inputs change silently re-baselines the review.
The compiler (scripts/mariehamn_approaches_1942.py) rejects changed inputs instead.

Evidence: the official 25 July 1942 orthophoto (IMS layer "Ortofoto 1942"), fetched as z16 tiles
(2 m/px, EPSG:3874, tile x = E // 512, y = N // 512; tile-manifest.json), compared with the 1968 NLS
sheet 101208 and today's road lines. Review images: sodra-1942-pair.jpg, sodra-zoom*.jpg, sodra-1968.jpg,
ostra-label-*.jpg, ostra-zoom.jpg, vastra-label-*.jpg.

Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/trace-1942/prepare.py
"""
import gzip, hashlib, json
from pathlib import Path

r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
HERE = Path('data/map-scan-cache/review/trace-1942')
# Inputs are read from the catalogue as it was before this review (snapshot), not the rebuilt one.
catalog = r(str(HERE / 'before.json.gz'))
objects = {o['id']: o for o in catalog['objects']}
geoms = {g['id']: g for g in catalog['geometries']}
stages = {s['id']: s for s in catalog['cityStages']}
city = next(s for s in r('data/mariehamn-city-traces.json')['sets'] if s['id'] == 'city-1942')
photo = next(s for s in r('data/historical-road-traces.json')['sets'] if s['id'] == 'photo-1942')
digest = lambda v: hashlib.sha256(json.dumps(v, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def fingerprint(o):
    return digest({k: o.get(k) for k in ['id', 'kind', 'states', 'geometryPeriods', 'sourceLinks']})


def stage_features(trace_index):
    out = []
    for s in catalog['cityStages']:
        for f in s['features']:
            if f.get('traceId') == f'city-1942-trace-{trace_index}':
                out.append(dict(stageId=s['id'], featureId=f['id'], inputHash=digest(f), outside=':outside:' in f['id']))
    return out


def trace(trace_index, photo_id):
    t = city['roads'][trace_index]; p = next(f for f in photo['features'] if f['id'] == photo_id)
    assert t['traceId'] == f'city-1942-trace-{trace_index}' and t['pixels'] == p['pixels']
    return dict(traceId=t['traceId'], photoFeatureId=photo_id, name=t['name'], pixels=t['pixels'], inputHash=digest(t), stageFeatures=stage_features(trace_index))


NOTE = 'Vägkorridoren syns på originalfotot den 25 juli 1942 i samma läge som objektets mittlinje. Fotot daterar inte byggår, bredd eller beläggning.'


def member(oid):
    o = objects[oid]
    assert o['states'][0]['state'] == 'open' and o['states'][0]['from'] > 1942, oid
    return dict(objectId=oid, inputHash=fingerprint(o), originalFrom=o['states'][0]['from'], note=NOTE)


EAST = ['road:mariehamn:major-followup:godbyvagen-south-of-bolstavagen', 'road:mariehamn:major:way-930505693',
        'road:mariehamn:major-followup:godbyvagen-dual-north-of-158304921', 'road:mariehamn:major:way-158304921',
        'road:mariehamn:major:way-612701769', 'road:mariehamn:major:way-1298787834', 'road:mariehamn:street-pass3:johannebovagen',
        'road:mariehamn:major-followup:grindmattesvagen',
        'road:postwar:way-949213328', 'road:postwar:way-44950148', 'road:postwar:way-1057521575', 'road:postwar:way-345678687',
        'road:postwar:way-35052767', 'road:postwar:way-1082959128', 'road:postwar:way-1097579040', 'road:postwar:way-1097579039',
        'road:postwar:way-44950092']
WEST = ['road:qgis:mariehamn:svibyvagen-1-200km2',
        'road:mariehamn:street-pass4:klintvagen', 'road:mariehamn:street-pass4:klintgrand',
        'road:postwar:way-43518012', 'road:postwar:way-935167645',
        'road:postwar:way-77039253', 'road:postwar:way-346833252', 'road:postwar:way-652150733', 'road:postwar:way-652150732',
        'road:postwar:way-652150731', 'road:postwar:way-652150737', 'road:postwar:way-652158694', 'road:postwar:way-652158695']

RETRACE = 'Mittlinjen följer den ljusa vägytan på originalfotot (2 m/pixel) som en minsta-kostnadsväg mellan de två objektändarna, förenklad till 2 m och granskad visuellt (retrace-*.jpg).'


def retraced(key, from_id, to_id, basis):
    data = json.loads((HERE / f'{key}.json').read_text())
    return dict(fromObjectId=from_id, toObjectId=to_id, epsg3874=data['points'], method=data['method'], corridorMeters=data['corridorMeters'],
                sha256=hashlib.sha256((HERE / f'{key}.json').read_bytes()).hexdigest(), basis=basis + ' ' + RETRACE)


review = dict(
    schemaVersion=1, reviewedAt='2026-11-12',
    source=dict(id='review:mariehamn-approaches-1942', title='Infartsvägarna på flygfotot 1942 · granskning', url='assets/mariehamn-approaches-1942.json'),
    aerialSourceId='mariehamn-aerial-1942',
    method='De tre förenklade 1942-spåren (12–13 punkter vardera, ritade på en vy med 4 m/pixel) jämfördes med originalfotot den 25 juli 1942 som georefererade rutor med 2 m/pixel, med kartbladet 101208 från 1968 och med dagens vägar. Där fotot visar vägen i samma läge som ett beständigt vägobjekt får objektet fotot som belägg från 1942 och visas med sin egen mittlinje. Spåret visas bara i korta luckor där inget objekt motsvarar vägen, och bara 1942–1967. Från 1968 visar de daterade objekten vägarna.',
    rejected=[dict(**trace(4, 'photo-1942-5'),
        basis='Ingen väg syns på originalfotot 1942 längs spåret: söder om stadskanten går det genom sammanhängande skog och bergig mark, och längst i norr över mark som 1968 är bebyggda kvarter. Kartan 1968 visar ingen väg i läget. Halvöns verkliga väg 1942 är huvudvägen (Västra Ytternäsvägen) 100–330 m längre västerut. Spåret visas inte längre; originalpunkterna finns kvar i källfilen.')],
    approaches=[
        dict(**trace(1, 'photo-1942-2'), key='ostra', maxDeviationMeters=65, snapMeters=65, dropTail=True,
             basis='Den östra infarten syns tydligt på fotot 1942: Godbyvägen söderut, kurvan vid Johannebo, sträckan förbi dagens Grindmattesvägen och Strandgatan in mot staden. Spårets sista del följer Strandgatan, som redan visas från 1861, och visas därför inte. Spåret är en grov korda som skär av kurvorna med upp till 20–60 m mot objektens mittlinjer; avståndsgränsen mot spåret (65 m) är bara en identitetskontroll, belägget är den visuella granskningen.',
             members=[member(o) for o in EAST],
             retracedGaps=[retraced('retrace-ostra', 'road:mariehamn:major-followup:grindmattesvagen', 'road:postwar:way-949213328', 'Mellan Grindmattesvägen och Strandgatan går 1942 års väg i en båge väster om dagens gator; spåret avviker där 30–40 m.')],
             excluded=[dict(objectId='road:mariehamn:major:way-165358627', reason='Den norra änden ligger utanför fotots täckning.'),
                       dict(objectId='road:mariehamn:junction-review:godbyvagen-bolstavagen', reason='Korsningsdelar; korsningen 1942 granskas inte här.'),
                       dict(objectId='road:mariehamn:street-pass3:skiljevagen', reason='Bara den norra halvan följer 1942 års väg; den södra halvan saknas på fotot.'),
                       dict(objectId='road:postwar:way-35011592', reason='Ritas redan 1942 av stadskartans eget Strandgatans spår (Strandgatan · 1942); att förtidigarelägga objektet skulle ge en dubbel linje.'),
                       dict(objectId='road:mariehamn:major:way-40103454', reason='Nya Godbyvägen dateras från 1978; 1942 års väg vid Rökerirondellen motsvaras inte av ett eget objekt.')]),
        dict(**trace(0, 'photo-1942-1'), key='vastra', maxDeviationMeters=90, snapMeters=90, dropTail=True,
             basis='Den västra infarten syns tydligt på fotot 1942: från västra kanten österut till kröken, Svibyvägen söderut, diagonalen ned till Klintvägens raka norra del och Klintgränd, Västra Utfartens diagonal och Ålandsvägen söderut mot staden. Spårets sista del in i staden avviker 30–50 m och visas inte. Spåret är en grov korda; avståndsgränsen mot spåret (90 m) är bara en identitetskontroll, belägget är den visuella granskningen.',
             members=[member(o) for o in WEST],
             retracedGaps=[retraced('retrace-vastra', 'road:qgis:mariehamn:svibyvagen-1-200km2', 'road:mariehamn:street-pass4:klintvagen', 'Från Svibyvägen till Klintvägen går 1942 års väg som en jämn diagonal; inget objekt följer hela sträckan.')],
             excluded=[dict(objectId='road:qgis:mariehamn:svibyvagen-2-200km2', reason='Kort anslutningsdel vid den senare Västra rondellen.'),
                       dict(objectId='road:mariehamn:street-pass3:stenhuggarvagen', reason='Diagonalen följer 1942 års väg, men den norra änden kröker västerut där fotot inte visar någon väg; sträckan visas i stället med en ny mittlinje ritad efter fotot.'),
                       dict(objectId='road:postwar:way-345139187', reason='Västra Utfartens nordvästra stump vid Klintgränd syns inte på fotot; 1942 går vägen rakt söderut från Klintgränd och svänger sedan in i diagonalen.'),
                       dict(objectId='road:postwar:way-35432034', reason='Kort korsningsdel vid samma stump.'),
                       dict(objectId='road:postwar:way-1095723009', reason='Kort delad korsningsdel vid Ålandsplan.'),
                       dict(objectId='road:postwar:way-43519502', reason='Kort delad korsningsdel vid Ålandsplan.'),
                       dict(objectId='road:postwar:way-43519494', reason='Kort delad korsningsdel vid Ålandsplan.'),
                       dict(objectId='road:mariehamn:major-followup:vastra-rondellen', reason='Rondellen dateras från 1995.')]),
    ],
    reviewImages=[dict(file='trace-1942/' + p.name, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(HERE.glob('*.jpg'))],
    tileManifestSha256=hashlib.sha256((HERE / 'tile-manifest.json').read_bytes()).hexdigest())
Path('data/mariehamn-approaches-1942.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print('rejected', [x['name'] for x in review['rejected']], 'approaches', [(a['key'], len(a['members']), len(a['stageFeatures'])) for a in review['approaches']])
