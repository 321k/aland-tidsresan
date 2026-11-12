"""Builds data/mariehamn-street-pass5.json from the visual review below (fifth and final Mariehamn street pass).

Retained for audit. It captures input hashes of the modern road, city-stage and snapshot records at
the time of review, so rerunning it after those inputs change silently re-baselines the review. The
compiler (scripts/mariehamn_street_pass5.py) rejects changed inputs instead.

Every decision was made by looking at the original-scan contact sheets ways-*.jpg made by
waysheet.py (one row per modern way: 1968 with the way outlined, then the unmarked 1968, 1978, 1985
and 1995 crops of the same ground) and, where needed, the area crops in this folder (lotsby-*).

Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/mariehamn-major-roads/pass5/prepare.py
"""
import gzip, hashlib, json, sys
from pathlib import Path
from shapely.geometry import LineString, Point
from shapely.ops import substring
sys.path.insert(0, 'scripts')
from postwar_city import METRIC
from mariehamn_south_streets import digest

r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
HERE = Path('data/map-scan-cache/review/mariehamn-major-roads/pass5')
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
TWO = ' Två moderna OSM-delar bildar en sammanhängande sträckning.'
GAP = ' Delen fyller en lucka mellan redan daterade delar av samma gata.'

# --- Junction and gap pieces of streets that are already dated ---------------------------------
add('sjukhusvagen-west-gap', 'luckor', 'Sjukhusvägen', ['way/1097429064', 'way/345398965'], 1968,
    ALL68('Inom den breda röda vägsignaturen med mittlinje.'), S68 + TWO + GAP)
add('sjukhusvagen-east-gap', 'luckor', 'Sjukhusvägen', ['way/35402539', 'way/35402537'], 1968,
    ALL68('Inom den breda röda vägsignaturen med mittlinje.'), S68 + TWO + GAP)
add('mariegatan-gap', 'luckor', 'Mariegatan', ['way/945223153', 'way/685473995'], 1968,
    ALL68('Vit gata mellan de skrafferade kvarteren, i samma läge som i dag.'), S68 + TWO + GAP)
add('skeppargatan-gap', 'luckor', 'Skeppargatan', ['way/35038799', 'way/944013606'], 1968, ALL68('Kort böj i korsningen.'), S68 + TWO + GAP)
add('ostra-esplanadgatan-gap', 'luckor', 'Östra Esplanadgatan', ['way/212860647', 'way/548191850'], 1968,
    ALL68('Vit gata längs det skrafferade kvarteret.'), S68 + TWO + GAP)
add('vastra-esplanadgatan-gap', 'luckor', 'Västra Esplanadgatan', ['way/626549147'], 1968, ALL68('Vit gata längs det skrafferade kvarteret.'), S68 + GAP)
add('sjopromenaden-gap', 'luckor', 'Sjöpromenaden', ['way/54445948'], 1968, ALL68('Inom den röda vägsignaturen.'), S68 + GAP)
add('sjopromenaden-harbour', 'luckor', 'Sjöpromenaden', ['way/1365314791', 'way/1081059573'], 1968,
    ALL68('Längs den röda vägen vid västra hamnen.'), S68 + TWO)
add('lotsgatan-island', 'luckor', 'Lotsgatan', ['way/968650930', 'way/968650932'], 1968,
    ALL68('Båda delarna ligger inom den röda vägsignaturen.'),
    'Två körbanor kring en refug mellan redan daterade delar av Lotsgatan. Vägen ritad 1968, 1978, 1985 och 1995 i samma läge. Räknas en gång, som den längsta körbanan. Kartåret är första granskade belägg, inte byggår.',
    kind='carriageways', count='longest')
add('havsgatan-new-section', 'luckor', 'Havsgatan', ['way/158304917', 'way/158304935', 'way/685473991'], 1985,
    F85((U, 'Kvarteret är skrafferat; endast den sydöstra delen följer en äldre vit gata.'), (U, 'Som 1968.')),
    'Inte säkert ritad som gata 1968 och 1978: gatan går där genom skrafferade kvarter. Ritad som röd gata 1985 och 1995 i samma läge. Tre moderna OSM-delar bildar en sammanhängande sträckning. Kartåret är första granskade belägg, inte byggår.')
add('neptunigatan-curve', 'luckor', 'Neptunigatan', ['way/37913504'], 1985,
    F85((U, 'Längs kanten av ett skrafferat kvarter; ingen säker gata.'), (U, 'Som 1968.')), S85.replace('Saknas som gata', 'Inte säkert ritad som gata'))
add('hindersbolevagen-link', 'luckor', 'Hindersbölevägen', ['way/345672833'], 1985,
    F85((A_, 'Inte ritad; åker.'), (U, RED78)), S85 + GAP)
add('hindersbolevagen-ditch', 'luckor', 'Hindersbölevägen', ['way/548983916', 'way/1097889372'], 1985,
    F85((A_, 'Inte ritad; endast diket.'), (U, RED78)), S85 + TWO)
add('grindmattesvagen-link', 'luckor', 'Grindmattesvägen', ['way/217254486', 'way/217254487'], 1985, F85(), S85 + TWO + GAP)

# --- Nya Godbyvägen at Bolstavägen and the Stenliden block --------------------------------------
add('nya-godbyvagen-bolstavagen-junction', 'stenliden', 'Nya Godbyvägen', ['way/40103274', 'way/626556101', 'way/626556102', 'way/40102862', 'way/158304933',
    'way/676049873', 'way/158304937', 'way/40103275', 'way/626556104', 'way/49360674', 'way/626556103', 'way/40103316', 'way/158304934'], 1978,
    obs((A_, None, 'Inte ritad; Nya Godbyvägen saknas.'), (P, 'full', 'Tjock rödtryckt väg med anslutning österut i kompletteringen 1978.'), (P, 'full', 'Röd korsning.'), (P, 'full', N95)),
    'Korsningsdelarna mellan Nya Godbyvägens redan daterade norra och södra korsningsdelar (1978) och Bolstavägens två körbanor fram till den daterade delen. Rödtryckt 1978 och kvar 1985 och 1995. Delarna är körbanor och svängfält i en korsning och räknas inte som ny väglängd. Kartåret är första granskade belägg, inte byggår.',
    kind='approach', count='parallel')
add('uppgardsvagen-link', 'stenliden', 'Uppgårdsvägen', ['way/676049877', 'way/676049878'], 1985,
    obs((A_, None, ABS), (A_, None, ABS), (P, 'full', 'Kort röd anslutning västerut från Nya Godbyvägen.'), (P, 'full', N95)),
    'Saknas 1968 och 1978. Kort röd anslutning västerut från Nya Godbyvägen 1985, som 1995 leder in till Uppgårdsvägen. Två körfält kring en refug räknas en gång. Kartåret är första granskade belägg, inte byggår.',
    kind='approach', count='longest')
add('uppgardsvagen', 'stenliden', 'Uppgårdsvägen', ['way/87088755', 'way/88561898', 'way/347964768', 'way/1298823939', 'way/347964766', 'way/1298823942', 'way/676049876'], 1995,
    F95((A_, 'Endast streckade stigar och tomtgränser.')), S95 + ' Sju moderna OSM-delar bildar en sammanhängande sträckning. Den nordligaste delen (way 88561577) är inte röd gata 1995 och ingår inte.')
for key, name, way in [('ostra-stenliden', 'Östra Stenliden', 'way/51356764'), ('krakbarsstigen-east', 'Kråkbärsstigen', 'way/87088754'),
                       ('blabarsstigen-north', 'Blåbärsstigen', 'way/87088753'), ('blabarsstigen-cross', 'Blåbärsstigen', 'way/87088766'),
                       ('blabarsstigen-south', 'Blåbärsstigen', 'way/87088764'), ('hjortronstigen', 'Hjortronstigen', 'way/51356763')]:
    add(key, 'stenliden', name, [way], 1995, F95((A_, 'Endast streckade stigar och tomtgränser.')), S95)

# --- Lotsby and Ytternäs south --------------------------------------------------------------------
add('fiskhamnsvagen', 'lotsby', 'Fiskhamnsvägen', ['way/945669422', 'way/35979829', 'way/930153951', 'way/1361467655', 'way/930153950'], 1968,
    ALL68('Röd väg från stranden österut till huvudvägen, i samma läge som i dag.'), S68 + ' Fem moderna OSM-delar bildar en sammanhängande sträckning.')
add('masvagen', 'lotsby', 'Måsvägen', ['way/134294425'], 1985, F85(), S85)
add('doppingvagen', 'lotsby', 'Doppingvägen', ['way/161722652', 'way/223197755'], 1985, F85(), S85 + ' Den korta namnlösa delen närmast huvudvägen (way 161722652) hör till samma gata.')


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
    return [dict(file=f'pass5/{p.name}', sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(HERE.glob('ways-*.jpg'))]


out = []
for d in D:
    rec = dict(id='road:mariehamn:street-pass5:' + d['id'], name=d['name'], routeId='road:' + d['name'], group=d['group'], kind=d['kind'])
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
              source=dict(id='review:mariehamn-street-pass5', title='Mariehamns gator · femte granskningen mot kartorna 1968–1995', url='assets/mariehamn-street-pass5.json'),
              method='Varje modern gatudel jämfördes visuellt med originalkartornas utsnitt för 1968, 1978, 1985 och 1995 över samma markyta (kontaktark per gata med den moderna linjen inritad endast på 1968). Överlägg är hjälpmedel, inte belägg. Tunna röda linjer i kompletteringen 1978 och enkla heldragna linjer 1968 räknas inte som gator; svarta linjer 1995 är gångväg eller mindre väg. Kartår är första granskade belägg, inte byggår. Parallella körbanor räknas en gång.',
              sheets=batch1['sheets'], decisions=out,
              deferred=[
                  dict(name='Kråkbärsstigens västra del och Hjortronstigens förbindelse', basis='Röda gator 1995, men i dag anslutna bara via gång- och cykelvägar.'),
                  dict(name='Bergshöjden', basis='Ritad som gata 1985, men dagens gata slutar i båda ändar utan anslutning till någon modern gata.'),
                  dict(name='Framnäsvägen och Varvsvägen', basis='Ansluter till Västra Utfartens västra körbana, som kartorna skiljer ut först 1995; daterade från 1985 skulle de sluta 6–9 m från vägnätet.'),
                  dict(name='Hamngatans delar vid västra hamnen, Havsgatans västra delar, Mariegatans diagonal, Styrmansgatan', basis='Hamnområdet byggdes om; läget eller färgen 1995 är oklar.'),
                  dict(name='Bolstavägens och Godbyvägens korsning, Ålandsplan, Gesällgatans delar', basis='Flerkörbanekorsningar som behöver en egen korsningsgranskning.'),
                  dict(name='Lotsbys gator (Skonertvägen, Briggstigen, Oséns, Wennströms och Nordströms gränd, Lotsbyvägen, Ekstocksvägen, Korrviksvägen, Notdragargränd, Fiskargränd) och Segelmakargatan', basis='Endast planlinjer 1995 (Segelmakargatan svart linje); senare än 1995.'),
                  dict(name='Fågelberget, Blomstringevägen, Skrapängsvägen, gatorna väster om Möckelö', basis='Saknas till och med 1995 eller ligger utanför kartbladet 101208.'),
              ],
              reviewSheets=sheet_files())
review['totals'] = dict(newPersistentMeters=new, confirmedExistingMeters=0, reviewedMeters=new,
                        byGroup={g: round(sum(d['lengthMeters'] for d in out if d['group'] == g), 2) for g in dict.fromkeys(d['group'] for d in out)},
                        byFirstYear={str(y): round(sum(d['lengthMeters'] for d in out if d['firstYear'] == y), 2) for y in YEARS if any(d['firstYear'] == y for d in out)})
Path('data/mariehamn-street-pass5.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(len(out), new, review['totals']['byGroup'], review['totals']['byFirstYear'])
for d in out:
    print(d['id'].split(':')[-1], d['firstYear'], d['lengthMeters'], len(d['members']), len(d['modernLinks']), len(d['originals']))
