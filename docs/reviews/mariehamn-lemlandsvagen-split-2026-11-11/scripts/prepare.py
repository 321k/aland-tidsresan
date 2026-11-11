"""Builds data/mariehamn-lemlandsvagen-split.json: splits the rural Lemlandsvägen object at Strandnäs.

Retained for audit. It captures hashes of the catalogue objects, modern ways, city-stage records and
scan crops as reviewed; rerunning after those inputs change would silently re-baseline the review.
Run from the project root after the larger-road follow-up pass has been built.
"""
import gzip, hashlib, json, subprocess, sys
from pathlib import Path
from shapely.geometry import LineString, Point
sys.path.insert(0, 'scripts')
from postwar_city import METRIC
from mariehamn_south_streets import digest

r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
HERE = Path('data/map-scan-cache/review/mariehamn-major-roads/lemlandsvagen')
catalog = r('dist/assets/temporal-objects.json.gz')
objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
modern = {f['id']: f for f in r('dist/assets/modern.json.gz')['features']}
stages = r('dist/assets/mariehamn-city-grid.json')['sets']
snap = {y: {f['id']: f for f in r(f'dist/assets/roads-{y}.json.gz')['features']} for y in [2014, 2021, 2025]}
owners = {(l['datasetId'], l['featureId']) for o in catalog['objects'] for l in o['sourceLinks']}
Q2, Q3 = 'road:qgis:mariehamn:lemlandsvagen-2-100km3', 'road:qgis:mariehamn:lemlandsvagen-3-100km3'
q2, q3 = objects[Q2], objects[Q3]
geo = geometries[q2['geometryPeriods'][0]['geometryId']]
WAYS = ['way/43377949', 'way/43448261', 'way/172865119', 'way/172865116', 'way/158304919', 'way/88582791', 'way/88582713', 'way/45478276', 'way/44108121', 'way/45478307', 'way/146899081', 'way/376582772']
SPLIT_WAY, SPLIT_VERTEX = 'way/45478307', 5
APPROACH, WEST = ['way/43377949'], WAYS[1:9]
# Vertex index of each way start in the rural geometry (ways share end vertices).
starts, i = {}, 0
for w in WAYS:
    starts[w] = i; i += len(modern[w]['paths'][0]) - 1
assert i + 1 == len(geo['paths'][0])
split_index = starts[SPLIT_WAY] + SPLIT_VERTEX
split_point = geo['paths'][0][split_index]
assert split_point == modern[SPLIT_WAY]['paths'][0][SPLIT_VERTEX]
slices = dict(approach=[0, starts['way/43448261']], west=[starts['way/43448261'], split_index], remainder=[split_index, len(geo['paths'][0]) - 1])
num = lambda fid: 'way/' + fid.rsplit('-', 1)[1] if fid.startswith('road-') else fid


def fractional_index(path, point):
    line = LineString([METRIC(*p) for p in path]); d = line.project(Point(METRIC(*point))); run = 0
    for k in range(len(path) - 1):
        seg = LineString([METRIC(*path[k]), METRIC(*path[k + 1])]).length
        if run + seg >= d:
            return round(k + (d - run) / seg, 8)
        run += seg
    return float(len(path) - 1)


links = dict(approach=[], west=[], remainder=[])
for l in q2['sourceLinks']:
    w = num(l['featureId']); base = {k: l[k] for k in ['datasetId', 'featureId', 'sourceVertexRange', 'sourceVertexCount']}
    if w == SPLIT_WAY:
        path = modern[w]['paths'][0] if l['datasetId'] == 'osm-2026' else snap[int(l['datasetId'][-4:])][l['featureId']]['paths'][0]
        t = SPLIT_VERTEX + 0.0 if l['datasetId'] == 'osm-2026' else fractional_index(path, split_point)
        a, b = l['sourceVertexRange']; assert a < t < b
        links['west'].append(dict(base, sourceVertexRange=[a, t], splitAt=t)); links['remainder'].append(dict(base, sourceVertexRange=[t, b], splitAt=t))
    elif w in APPROACH or w == 'way/43912432':
        links['approach'].append(base)
    elif w in WEST:
        links['west'].append(base)
    else:
        links['remainder'].append(base)


def stage_links(ways):
    out = []
    for w in ways:
        for s in stages:
            for sf in s['features']:
                if sf['kind'] == 'street' and sf['paths'] == modern[w]['paths']:
                    assert (s['id'], sf['id']) not in owners
                    out.append(dict(datasetId=s['id'], featureId=sf['id'], inputHash=digest(sf), modernFeatureId=w))
    return out


def traces():
    """Centre-line samples from the original-scan crops; the compiler judges them, nothing is pre-filtered."""
    runs = [('west', 'h 20 1040 6 120 500'), ('east', 'h 10 700 6 0 520')]
    out = {}
    for year in [1968, 1978, 1985, 1995]:
        pts = []
        for key, args in runs:
            res = subprocess.run([sys.executable, str(HERE / 'trace.py'), key, str(year), *args.split()], capture_output=True, text=True, check=True)
            pts += [p[:2] for p in json.loads(res.stdout)]
        crops = {k: dict(crop=f'lemlandsvagen/{k}-{year}.png', cropSha256=hashlib.sha256((HERE / f'{k}-{year}.png').read_bytes()).hexdigest(),
                         **{x: json.loads((HERE / f'{k}-{year}.json').read_text())[x] for x in ['bbox', 'box', 'scale', 'sourceId', 'sha256']}) for k, _ in runs}
        out[str(year)] = dict(method=[f'trace.py {k} {year} {a}' for k, a in runs], crops=crops, points=pts)
    return out


first = r('data/mariehamn-major-roads.json')
west_path = geo['paths'][0][slices['west'][0]:slices['west'][1] + 1]
review = dict(
    schemaVersion=1, reviewedAt='2026-11-11',
    source=dict(id='review:mariehamn-lemlandsvagen-split', title='Lemlandsvägen vid Strandnäs · delning av landsbygdsenheten 1968–1995', url='assets/mariehamn-lemlandsvagen-split.json'),
    method='Mittlinjen spårades på originalkartornas utsnitt för 1968, 1978, 1985 och 1995 och jämfördes med den moderna vägen i EPSG:3874. Punkter längre än 40 m från vägen är andra röda kartsymboler. Delen räknas som samma korridor när medianavvikelsen i varje 150-metersavsnitt är högst 12 m. Kartår är belägg, inte byggår.',
    sheets=first['sheets'],
    target=dict(objectId=Q2, inputHash=digest(q2), geometryId=geo['id'], geometryHash=digest(geo), ways=WAYS, wayHashes={w: digest(modern[w]) for w in WAYS},
                splitWay=SPLIT_WAY, splitVertex=SPLIT_VERTEX, splitPoint=split_point, slices=slices),
    pairedLane=dict(objectId=Q3, inputHash=digest(q3), modernFeatureId='way/43912432', firstYear=1978, stageLinks=stage_links(['way/43912432']),
                    basis='Rondellens östra tillfart har två körfält. Rödtrycket 1978 visar rondellen och tillfarten; refugen syns först 1985 men körfältet ligger i samma läge. Det tidigare 1985-belägget och dess geometri behålls.'),
    objects=[
        dict(part='west', id='road:mariehamn:lemlandsvagen:strandnas-sodergard', name='Lemlandsvägen · Strandnäs–Södergård', firstYear=1968,
             sourceLinks=links['west'], stageLinks=stage_links(WEST),
             basis='Lemlandsvägen följer 1968, 1978, 1985 och 1995 samma korridor från den gamla korsningen vid Strandnäs förbi Nabben och Kalmsta till strax öster om Södergård. Mätta avvikelser är 0–11 m, inom kartornas registreringsfel. Modern detaljgeometri används för hela perioden. Kartåret är första granskade belägg, inte byggår.'),
        dict(part='approach', id='road:mariehamn:lemlandsvagen:rokeri-approach', name='Lemlandsvägen · tillfart till Rökerirondellen', firstYear=1978,
             sourceLinks=links['approach'], stageLinks=stage_links(APPROACH),
             basis='Tillfarten från Rökerirondellen österut saknas 1968, då vägen gick rakt genom den senare rondellplatsen. Rödtryckt med rondellen 1978. Kartåret är inte invigningsår.'),
    ],
    remainder=dict(sourceLinks=links['remainder'],
                   basis='Öster om delningspunkten går vägen 1968 och 1978 i en äldre båge 12–30 m söder om dagens väg, i läget för dagens gång- och cykelväg (way 119232835). Den nuvarande sträckningen syns först 1985. Den återstående enheten behåller därför sin identitet, sitt startår 1985 och alla tidigare belägg; den äldre bågen är uppskjuten tills väg-till-gångväg kan modelleras.'),
    traces=traces(),
    visualChecks=[dict(year=1995, bin=b, crop=f'lemlandsvagen/{k}-1995.png', cropSha256=hashlib.sha256((HERE / f'{k}-1995.png').read_bytes()).hexdigest(), outcome='same-corridor', note=n)
                  for b, k, n in [(1, 'check1995a', '1995 ritar korsande gator och en rödstreckad gång- och cykelväg tätt intill vägen; spårningen fastnar på dem. Vägen ligger i samma läge som 1985 och idag.'),
                                  (6, 'check1995b', 'Spårningen ger inga punkter här eftersom korsande gator och tomtlinjer bryter den röda vägytan. Vägen ligger visuellt i samma läge som 1985 och idag.')]],
    curveDeviation=dict(note='Radvis spårning av bågen öster om delningspunkten: 1968 och 1978 avviker 12–31 m från 1560 m längs vägen, 1985 5–13 m och 1995 4–7 m. Underlag för att inte bakdatera resten.',
                        method='trace.py east {year} v 150 940 30 600 1560'),
)
Path('data/mariehamn-lemlandsvagen-split.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print({k: len(v) for k, v in links.items()}, 'west vertices', len(west_path), 'samples', {y: len(t['points']) for y, t in review['traces'].items()})
