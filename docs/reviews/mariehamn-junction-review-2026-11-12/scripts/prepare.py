"""Builds data/mariehamn-junction-review.json from the visual review below (Mariehamn junction review).

Retained for audit. It captures input hashes of the modern road, city-stage and snapshot records at
the time of review, so rerunning it after those inputs change silently re-baselines the review. The
compiler (scripts/mariehamn_junction_review.py) rejects changed inputs instead.

Every decision was made by looking at the original-scan contact sheets ways-*.jpg made by
waysheet.py (one row per modern way: 1968 with the way outlined, then the unmarked 1968, 1978, 1985
and 1995 crops of the same ground) and, where needed, the area crops in this folder (lotsby-*).

Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/mariehamn-major-roads/junctions/prepare.py
"""
import gzip, hashlib, json, sys
from pathlib import Path
from shapely.geometry import LineString, Point
from shapely.ops import substring
sys.path.insert(0, 'scripts')
from postwar_city import METRIC
from mariehamn_south_streets import digest

r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
HERE = Path('data/map-scan-cache/review/mariehamn-major-roads/junctions')
modern = {f['id']: f for f in r('dist/assets/modern.json.gz')['features']}
stages = r('dist/assets/mariehamn-city-grid.json')['sets']
snapshots = {y: r(f'dist/assets/roads-{y}.json.gz')['features'] for y in [2014, 2021, 2025]}
by_osm = {y: {f.get('osmId'): f for f in fs if f.get('osmId')} for y, fs in snapshots.items()}
# Ownership is checked against the catalogue as it was before this pass (snapshot), not the rebuilt one.
catalog = r(str(HERE / 'before.json.gz'))
occupied = {(l['datasetId'], l['featureId']) for o in catalog['objects'] for l in o['sourceLinks']}
batch1 = r('data/mariehamn-major-roads.json')
m = lambda pts: LineString([METRIC(*p) for p in pts])
YEARS = [1968, 1978, 1985, 1995]
P, A_, U = 'present', 'absent', 'unclear'

# Notes, in the catalogue's Swedish. Map years are evidence, never construction years.
N68 = 'Dubbellinjerad gata i samma läge som i dag.'
N85 = 'Ritad som gata med hus längs båda sidor.'
N95 = 'Röd gata i samma läge som i dag.'
ABS = 'Inte ritad; endast tomtgränser, åker, skog eller höjdkurvor.'
HATCH = 'Inte ritad; skrafferat bebyggelseområde utan gator.'
SINGLE = 'En enkel heldragen linje mellan husraderna, inte en dubbellinjerad gata; kan vara en gång eller tomtväg och räknas inte som gata.'
RED78 = 'Rödtryckt tunn linje i kompletteringen 1978 längs den senare gatan; kan vara en tomt- eller plangräns och räknas inte som gata.'
S68 = 'Visuellt följd i utgåvorna 1968, 1978, 1985 och 1995 i samma korridor. Kartåret är första granskade belägg, inte byggår. Modern detaljgeometri används för hela perioden.'
S85 = 'Saknas som gata 1968 och 1978. Ritad som gata 1985 och 1995 i samma läge. Kartåret är första granskade belägg, inte byggår.'
S95 = 'Saknas som gata 1968–1985. Ritad som gata först 1995. Kartåret är första granskade belägg, inte byggår.'


def obs(*rows):
    return [dict(year=y, outcome=o, coverage='unknown' if o != P else c, note=n) for y, (o, c, n) in zip(YEARS, rows)]


ALL68 = lambda n=N68: obs((P, 'full', n), (P, 'full', 'Grundkartan oförändrad.'), (P, 'full', ''), (P, 'full', ''))
def F85(y68=(A_, ABS), y78=(A_, ABS)):
    return obs((y68[0], None, y68[1]), (y78[0], None, y78[1]), (P, 'full', N85), (P, 'full', N95))
def F95(y85=(A_, ABS)):
    return obs((A_, None, ABS), (A_, None, ABS), (y85[0], None, y85[1]), (P, 'full', N95))

D = []
def add(key, group, name, ways, first, observations, basis, kind='section', count='display', **extra):
    D.append(dict(id=key, group=group, name=name, ways=ways, first=first, observations=observations, basis=basis, kind=kind, count=count, **extra))
ALLP = lambda n: obs((P, 'full', n), (P, 'full', 'Som 1968.'), (P, 'full', ''), (P, 'full', ''))

# --- Godbyvägen and Bolstavägen ----------------------------------------------------------------
add('godbyvagen-bolstavagen', 'godbyvagen-bolstavagen', 'Godbyvägen', [
        'way/165358622', 'way/158304927', 'way/165358620', 'way/34972009', 'way/165358625', 'way/165358624',
        'way/165358621', 'way/1298839735', 'way/165358623', 'way/158304929', 'way/165358619', 'way/165358618', 'way/158304928', 'way/165358626', 'way/1298839909',
        'way/165358629', 'way/165358630'], 1968,
    ALLP('Godbyvägen ritad som röd väg genom korsningen; Bolstavägens östra gren ansluter som dubbellinjerad gata.'),
    'Körbanor och svängfält där Godbyvägen korsar Bolstavägen, mellan Godbyvägens redan daterade delar norr och söder om korsningen (1968) och Bolstavägens daterade östra del (1968). Kartorna visar korsningen med en enda vägsignatur från 1968; de moderna delarna ligger inom den. Korsningsdelarna räknas inte som ny väglängd. Kartåret är första granskade belägg, inte byggår.',
    kind='approach', count='parallel')
add('bolstavagen-west-approach', 'godbyvagen-bolstavagen', 'Bolstavägen', ['way/165358617', 'way/1298822075', 'way/165358616', 'way/244377191'], 1978,
    obs((A_, None, 'Ingen väg västerut från korsningen.'), (P, 'full', 'Tjock rödtryckt väg västerut i kompletteringen 1978.'), (P, 'full', 'Röd väg.'), (P, 'full', N95)),
    'Bolstavägens två körfält mellan den redan daterade västra delen (1978) och Godbyvägen. Saknas 1968; rödtryckt 1978 och kvar 1985 och 1995. Räknas inte som ny väglängd. Kartåret är första granskade belägg, inte byggår.',
    kind='approach', count='parallel')

# --- Ålandsplan ---------------------------------------------------------------------------------
add('alandsplan-ring', 'alandsplan', 'Ålandsplan', ['way/35137575', 'way/346799406', 'way/347944803', 'way/347944802', 'way/612335560', 'way/612335561'], 1968,
    ALLP('Röd rondell med rund mittö, i samma läge som i dag.'),
    'Den södra halvan av rondellen vid Ålandsplan, mellan ringens redan daterade delar (1968). Rondellen ritad 1968, 1978, 1985 och 1995 i samma läge. Kartåret är första granskade belägg, inte byggår.',
    kind='roundabout')
add('skarpansvagen-alandsplan', 'alandsplan', 'Skarpansvägen', ['way/35038764', 'way/43519503'], 1968,
    ALLP('Röd väg från rondellen mot sydost.'),
    'Skarpansvägens två körfält kring en refug vid rondellen, mellan rondellen och den redan daterade Skarpansvägen (1968). Refugen syns 1985; vägen ligger i samma läge från 1968. Räknas en gång, som det längsta körfältet. Kartåret är första granskade belägg, inte byggår.',
    kind='approach', count='longest')
add('gesallgatan-alandsplan', 'alandsplan', 'Gesällgatan', ['way/56133994', 'way/1095723065', 'way/643036390', 'way/944013591', 'way/643036389', 'way/652159168'], 1968,
    ALLP('Dubbellinjerad gata från rondellen mot sydväst.'),
    'Gesällgatans anslutning till rondellen, med två körfält närmast ringen, mellan rondellen och den redan daterade Gesällgatan (1968). Ritad i samma läge 1968–1995. Räknas en gång, som den längsta delen. Kartåret är första granskade belägg, inte byggår.',
    kind='approach', count='longest')

# --- Västra Utfarten at the crossing south of Klintvägen ------------------------------------------
add('vastra-utfarten-crossing-east', 'vastra-utfarten', 'Västra Utfarten', ['way/56396449', 'way/56396447', 'way/56396442'], 1995,
    obs((U, None, 'En enda röd vägsignatur genom korsningen; den andra körbanan kan inte skiljas ut.'), (U, None, 'Som 1968.'), (U, None, 'Som 1968.'), (P, 'full', 'Ritad som två körbanor.')),
    'Västra Utfartens andra körbana vid korsningen söder om Klintvägen, parallell med de redan daterade delarna. Visas först 1995, då kartan ritar två körbanor, som den västra körbanan längre norrut. Räknas inte som ny väglängd.',
    kind='carriageways', count='parallel')


def stage_links(way):
    f = modern[way]; out = []
    for s in stages:
        for sf in s['features']:
            if sf['kind'] == 'street' and sf['paths'] == f['paths']:
                key = (s['id'], sf['id'])
                assert key not in occupied, (way, key)
                out.append(dict(datasetId=s['id'], featureId=sf['id'], inputHash=digest(sf), modernFeatureId=way))
    return out


def sheet_files():
    return [dict(file=f'junctions/{p.name}', sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(HERE.glob('*-seq.jpg'))]


out = []
for d in D:
    rec = dict(id='road:mariehamn:junction-review:' + d['id'], name=d['name'], routeId='road:' + d['name'], group=d['group'], kind=d['kind'])
    rec['members'] = [dict(feature=modern[w], inputHash=digest(modern[w])) for w in d['ways']]
    rec['display'] = d['ways']
    rec['modernLinks'] = [l for w in d['ways'] for l in stage_links(w)]
    rec['originals'] = [dict(year=y, datasetId=f'city-{y}', feature=by_osm[y][w], inputHash=digest(by_osm[y][w])) for w in d['ways'] for y in [2014, 2021, 2025] if w in by_osm[y]]
    rec['unobservedOriginals'] = [dict(modernFeatureId=w, years=[y for y in [2014, 2021, 2025] if w not in by_osm[y]]) for w in d['ways'] if any(w not in by_osm[y] for y in [2014, 2021, 2025])]
    rec['firstYear'] = d['first']
    rec['states'] = [dict(state='open', **{'from': d['first'], 'to': None})]
    if d['kind'] == 'partial-section':
        line = LineString(modern[d['ways'][0]]['paths'][0]); t = round(line.project(Point(*d['partialTo']), normalized=True), 6)
        sub = [[list(map(lambda v: round(v, 7), c)) for c in substring(line, 0, t, normalized=True).coords]]
        full_from = next(o['year'] for o in d['observations'] if o['coverage'] == 'full')
        rec['phases'] = [dict(**{'from': d['first'], 'to': full_from}, geometry='substring:start', range=[0, t], paths=sub, basis=d['partialBasis']),
                         dict(**{'from': full_from, 'to': None}, geometry='modern', basis=d['fullBasis'])]
    else:
        rec['phases'] = [dict(**{'from': d['first'], 'to': None}, geometry='modern', basis=d['basis'])]
    rec['observations'] = d['observations']
    rec['countRule'] = d['count']; rec['basis'] = d['basis']
    lengths = [m(modern[w]['paths'][0]).length for w in d['ways']]
    rec['lengthMeters'] = round(sum(lengths) if d['count'] == 'display' else max(lengths) if d['count'] == 'longest' else 0, 2)
    out.append(rec)

ids = [w for d in D for w in d['ways']]
assert len(ids) == len(set(ids))
new = round(sum(d['lengthMeters'] for d in out), 2)
review = dict(schemaVersion=1, reviewedAt='2026-11-12',
              source=dict(id='review:mariehamn-junction-review', title='Mariehamns korsningar · granskning mot kartorna 1968–1995', url='assets/mariehamn-junction-review.json'),
              method='Varje modern gatudel jämfördes visuellt med originalkartornas utsnitt för 1968, 1978, 1985 och 1995 över samma markyta (kontaktark per gata med den moderna linjen inritad endast på 1968). Överlägg är hjälpmedel, inte belägg. Tunna röda linjer i kompletteringen 1978 och enkla heldragna linjer 1968 räknas inte som gator; svarta linjer 1995 är gångväg eller mindre väg. Kartår är första granskade belägg, inte byggår. Parallella körbanor räknas en gång.',
              sheets=batch1['sheets'], decisions=out,
              deferred=[
                  dict(name='Framnäsvägen och Varvsvägen', basis='Ritade som gator 1985 men ansluter till Västra Utfartens västra körbana, som kartorna skiljer ut först 1995; daterade från 1985 skulle de sluta 6–9 m från vägnätet under 1985–1994.'),
                  dict(name='Doktorsvägens servicedel (way 77082300)', basis='Svart streckad stig 1995, inte röd gata; Uppgårdsvägen ansluter i stället norrut via Nya Godbyvägen.'),
                  dict(name='Kråkbärsstigens västra del och Hjortronstigens förbindelse', basis='Ansluter i dag bara via gång- och cykelvägar; väntar på en modell för väg som blir gångväg.'),
                  dict(name='Mästargränd och Ekogränd', basis='Slingan från 1968 följer inte dagens Ekogränd, och Mästargrändens östra anslutning är i dag gångväg.'),
                  dict(name='Michaelsvägens rondell vid Nya Godbyvägen', basis='Rondellen är senare än 1995.'),
              ],
              reviewSheets=sheet_files())
review['totals'] = dict(newPersistentMeters=new, confirmedExistingMeters=0, reviewedMeters=new,
                        byGroup={g: round(sum(d['lengthMeters'] for d in out if d['group'] == g), 2) for g in dict.fromkeys(d['group'] for d in out)},
                        byFirstYear={str(y): round(sum(d['lengthMeters'] for d in out if d['firstYear'] == y), 2) for y in YEARS if any(d['firstYear'] == y for d in out)})
Path('data/mariehamn-junction-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(len(out), new, review['totals']['byGroup'], review['totals']['byFirstYear'])
for d in out:
    print(d['id'].split(':')[-1], d['firstYear'], d['lengthMeters'], len(d['members']), len(d['modernLinks']), len(d['originals']))
