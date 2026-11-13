"""Writes data/mariehamn-frame-1942.json: the 14 coarse 1942 city traces reviewed against the 1942 orthophoto.

Retained for audit; it fingerprints the catalogue as it was before this step (frame-before.json.gz in this folder),
so rerunning it after inputs change re-baselines the review. The compiler (scripts/mariehamn_frame_1942.py) rejects changed inputs instead.
Evidence: frame-*-pair.jpg, map1968-*.jpg, frame-w2-havsgatan.jpg, frame-e-connector.jpg, retrace-strand.jpg, south-*.jpg.
Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/trace-1942/frame_prepare.py
"""
import gzip, hashlib, json
from pathlib import Path

P = Path('data/map-scan-cache/review/trace-1942')
r = lambda p: json.loads(gzip.decompress(open(p, 'rb').read()) if p.endswith('.gz') else open(p, 'rb').read())
digest = lambda v: hashlib.sha256(json.dumps(v, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
fingerprint = lambda o: digest({k: o.get(k) for k in ['id', 'kind', 'states', 'geometryPeriods', 'sourceLinks']})
c = r(str(P / 'frame-before.json.gz')); O = {o['id']: o for o in c['objects']}
city = next(s for s in r('data/mariehamn-city-traces.json')['sets'] if s['id'] == 'city-1942')
PHOTO = 'Flygfotot 25 juli 1942 visar gatan i samma läge som objektets mittlinje.'

TRACES = [
    dict(traceId='city-1942-trace-23', decision='rejected', maxDistanceMeters=None, members=[],
         basis='Spåret är en rak linje med två punkter över 870 meter. Flygfotot 1942 visar stadens södra gata, Skillnadsgatan, '
               '60–70 meter längre norrut; den visas redan från 1871 i dagens läge. Under spåret finns skog och trädgårdstäppor, '
               'ingen väg. Restbitarna visas inte längre, varken 1942–1967 eller 1968–1985. Originalpunkterna bevaras i källfilen.'),
    dict(traceId='city-1942-trace-5', decision='replaced', maxDistanceMeters=40,
         members=[('road:postwar:way-1081061710', 'Havsgatans anslutning vid kvarterens norra kant.'),
                  ('road:postwar:way-59319322', 'Havsgatan, norra delen.'), ('road:postwar:way-1081056142', 'Havsgatan vid esplanaden.'),
                  ('road:postwar:way-685474023', 'Havsgatan, mellersta delen.'), ('road:postwar:way-685473994', 'Havsgatan fram till Mariegatan.')],
         basis='Spåret är grovt (sex punkter över 1,1 kilometer) och skär snett genom tomterna; 76 procent ligger mer än 15 meter från '
               'en väg och den södra delen går genom skog ned mot Lotsbergets klippa, där fotot inte visar någon väg. Den västra '
               'gatan genom kvarteren är Havsgatan, som fotot visar från kvarterens norra kant till Mariegatan. Havsgatans delar '
               'visas från 1942 med egna mittlinjer. Söder om Mariegatan följde 1942 års väg ett äldre läge än dagens Havsgatan '
               '(den nya sträckningen från 1985 ligger upp till 28 meter österut) och den dateras inte om.'),
    dict(traceId='city-1942-trace-13', decision='replaced', maxDistanceMeters=35,
         members=[('road:postwar:way-122594160', 'Köpmansgatan, västra delen.'), ('road:postwar:way-1057534808', 'Köpmansgatan, mellersta delen.'),
                  ('road:postwar:way-1057534807', 'Köpmansgatan, östra delen.'), ('road:postwar:way-626549150', 'Köpmansgatan mot Strandgatan.')],
         basis='Spåret är en rak linje med två punkter över 845 meter. Den östra halvan ligger 20–30 meter söder om Köpmansgatan, '
               'som flygfotot 1942 visar med hus längs båda sidor. Den västra halvan går genom skog och öppen mark där fotot inte visar '
               'någon väg; det fanns alltså ingen genomgående tvärgata som skolan senare bröt. Köpmansgatan visas från 1942 med egna '
               'mittlinjer; den tidigare tolkningen från 1952 och senare belägg behålls.'),
    dict(traceId='city-1942-trace-11', decision='replaced', maxDistanceMeters=30,
         members=[('road:postwar:way-35011592', 'Strandgatan norr om den granskade kärnan.'),
                  ('road:postwar:way-39585442', 'Den södra fortsättningen längs stranden, i dag Parkgatan.')],
         basis='Spårets kärna mellan Stora gatan och Nygatan ersattes tidigare av Strandgatans granskade objekt. Restbitarna följer '
               'verkliga gator: den norra delen Strandgatan (cirka 7 meter från spåret) och den södra Parkgatan (cirka 23 meter). '
               'Båda visas från 1942 med egna mittlinjer. Mellan kärnans södra ände och Parkgatan går vägen på fotot först österut '
               'längs tvärgatan och sedan rakt söderut; spåret skar i stället snett genom husen. Den sträckan har ritats om från fotot '
               'och visas bara 1942–1967.'),
]
NEPT = [('44108104', 'Neptunigatan vid Norragatan.'), ('951311473', 'Neptunigatan norr om kvarteren.'), ('1081062879', 'Neptunigatan norr om kvarteren.'),
        ('44108105', 'Neptunigatan fram till Badhusgatan.'), ('889004816', 'Neptunigatan söder om kärnan.'), ('889004817', 'Neptunigatan söder om kärnan.'),
        ('889004818', 'Neptunigatan söder om kärnan.'), ('889004819', 'Neptunigatan fram till Skillnadsgatan.')]
ALAND = [('610024474', 'Ålandsvägen norr om kärnan.'), ('209112218', 'Ålandsvägen norr om kärnan.'), ('653434349', 'Ålandsvägen norr om kärnan.'),
         ('346833254', 'Ålandsvägen norr om kärnan.'), ('1077608078', 'Ålandsvägen vid korsningen.'), ('172865147', 'Ålandsvägen söder om kärnan.')]
TORG = [(i, 'Kort del av Torggatan vid en korsning.') for i in ['44108087', '392187946', '601830158', '601830161', '613969827', '862194715', '862194716', '1051656049', '1082966161']]
STYR = [(i, 'Styrmansgatan.') for i in ['1097428367', '652150725', '652150726', '944013585', '944013586']]
NORR = [(i, 'Kort del av Norragatan vid en korsning.') for i in ['1081062022', '862198311', '951311472', '951311474']]
way = lambda xs: [('road:postwar:way-' + i, n) for i, n in xs]
CORE = ('Spårets mittdel ersattes tidigare av gatans granskade kärna; de kvarvarande grova bitarna ligger {d} från gatans egna '
        'objekt, som flygfotot 1942 visar. De objekten visas från 1942 med egna mittlinjer, och spårbitarna tas bort.')
TRACES += [
    dict(traceId='city-1942-trace-2', decision='rejected', maxDistanceMeters=None, members=[],
         basis='Spåret har sju punkter över 1,1 kilometer. Den nordöstra delen följer en rak gata genom skogen som 1968 års grundkarta '
               'visar som kraftledning, inte väg; den västra delen går över åkrar och skog cirka 25 meter norr om huvudvägen. Varken spåret '
               'eller dagens Elverksgatan syns som väg på fotot. Spåret visas inte längre, varken 1942–1967 eller 1968–1985.'),
    dict(traceId='city-1942-trace-3', decision='rejected', maxDistanceMeters=None, members=[],
         basis='Spåret går över industritomten och skogen på Badhusberget. Varken flygfotot 1942 eller grundkartan 1968 visar någon väg där. '
               'Spåret visas inte längre.'),
    dict(traceId='city-1942-trace-6', decision='replaced', maxDistanceMeters=25, members=way(NEPT), basis=CORE.format(d='3–17 meter') +
         ' Gatan är Neptunigatan; dess nya kurva från 1985 och den långa vägen mot nordväst dateras inte om.'),
    dict(traceId='city-1942-trace-9', decision='replaced', maxDistanceMeters=25, members=way(ALAND), basis=CORE.format(d='6–19 meter') +
         ' Gatan är Ålandsvägen.'),
    dict(traceId='city-1942-trace-10', decision='replaced', maxDistanceMeters=10, members=way(TORG), basis=CORE.format(d='0–5 meter') +
         ' Bitarna är korta delar av Torggatan vid korsningarna.'),
    dict(traceId='city-1942-trace-12', decision='replaced', maxDistanceMeters=25, members=way(STYR),
         basis='Spåret är en rak linje med två punkter över 566 meter. Den östra delen ligger 13–18 meter söder om Styrmansgatan, som '
               'flygfotot 1942 visar med hus längs gatan; den västra delen går in i skogen där fotot inte visar någon väg. Styrmansgatans '
               'delar visas från 1942 med egna mittlinjer.'),
    dict(traceId='city-1942-trace-15', decision='replaced', maxDistanceMeters=10, members=way(NORR), basis=CORE.format(d='0–1 meter') +
         ' Bitarna är korta delar av Norragatan vid korsningarna.'),
    dict(traceId='city-1942-trace-17', decision='rejected', maxDistanceMeters=None, members=[],
         basis='Bara en kvarlämnad bit på 34 meter visas 1968–1985, bredvid Storagatans granskade kärna. Gatan visas av sina objekt; '
               'biten tas bort.'),
    dict(traceId='city-1942-trace-22', decision='rejected', maxDistanceMeters=None, members=[],
         basis='Spåret är en rak linje med två punkter över 593 meter mitt i kvarteren, genom tomterna mellan två gator som redan visas. '
               'Flygfotot 1942 visar ingen gata där. Spåret visas inte längre.'),
    dict(traceId='city-1942-trace-24', decision='rejected', maxDistanceMeters=None, members=[],
         basis='Spåret går genom trädgårdstäppor cirka 35 meter väster om den väg fotot visar, och den vägen visas redan av sina objekt. '
               'Spåret visas inte längre, varken 1942–1967 eller 1968–1985.'),
]
retrace = json.load(open(P / 'retrace-strand.json'))
GAPS = {'city-1942-trace-11': [dict(fromObjectId='road:postwar:way-78489469', toObjectId='road:postwar:way-39585442', epsg3874=retrace['points'],
                                    basis='Minsta-kostnadsväg över vägytans ljusare ton på flygfotot 1942 (2 m/pixel), förenklad till 2 meter och '
                                          'kontrollerad visuellt; ingen persistent väg motsvarar sträckan.')]}

entries = []
for t in TRACES:
    raw = next(x for x in city['roads'] if x['traceId'] == t['traceId'])
    stage_features = [dict(stageId=s['id'], featureId=f['id'], inputHash=digest(f), outside=':outside:' in f['id'])
                      for s in c['cityStages'] for f in s['features'] if f.get('traceId') == t['traceId'] and not f.get('objectId')]
    members = []
    for oid, note in t['members']:
        o = O[oid]
        members.append(dict(objectId=oid, name=o['name'], inputHash=fingerprint(o), originalFrom=o['states'][0]['from'], note=f'{PHOTO} {note}'))
    entries.append(dict(traceId=t['traceId'], name=raw['name'], pixels=raw['pixels'], inputHash=digest(raw), decision=t['decision'],
                        basis=t['basis'], maxDistanceMeters=t['maxDistanceMeters'], stageFeatures=stage_features, members=members,
                        retracedGaps=GAPS.get(t['traceId'], [])))
review = dict(schemaVersion=1, reviewedAt='2026-11-12',
              source=dict(id='review:mariehamn-frame-1942', title='Mariehamns stadsspår 1942 · granskade mot flygfotot', url='assets/mariehamn-frame-1942.json'),
              aerialSourceId='mariehamn-aerial-1942',
              method=('Stadsspåren ritades på 1942 års ortofoto i en vy med 4 meter per pixel, två till femton punkter per gata. De fyra första bildar '
                      'en grov ram runt staden. Alla spår utan objekt har jämförts med originalfotot i 2 meter per pixel, med varje persistent väg märkt ut. Ett spår som '
                      'inte följer någon väg tas bort. För de övriga får de vägobjekt som fotot visar i spårets ställe fotot som belägg för 1942 '
                      'och visas med egna mittlinjer; varje objekt måste ligga nära det spår det ersätter. Fotoåret är belägg, inte byggår.'),
              traces=entries,
              reviewImages=[dict(file=p.name, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(P.glob('frame-*.jpg')) + sorted(P.glob('map1968-*.jpg')) + sorted(P.glob('south-*.jpg')) + [P / 'retrace-strand.jpg']])
Path('data/mariehamn-frame-1942.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print({e['name']: (e['decision'], len(e['stageFeatures']), len(e['members'])) for e in entries})
