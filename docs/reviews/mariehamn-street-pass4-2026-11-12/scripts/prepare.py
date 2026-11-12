"""Builds data/mariehamn-street-pass4.json from the visual review below (fourth Mariehamn street pass).

Retained for audit. It captures input hashes of the modern road, city-stage and snapshot records at
the time of review, so rerunning it after those inputs change silently re-baselines the review. The
compiler (scripts/mariehamn_street_pass4.py) rejects changed inputs instead.

Every decision was made by looking at the original-scan contact sheets ways-*.jpg made by
waysheet.py (one row per modern way: 1968 with the way outlined, then the unmarked 1968, 1978, 1985
and 1995 crops of the same ground) and, where needed, the area crops in this folder (klint-*,
klintbend-*, sten-*).

Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/mariehamn-major-roads/pass4/prepare.py
"""
import gzip, hashlib, json, sys
from pathlib import Path
from shapely.geometry import LineString, Point
from shapely.ops import substring
sys.path.insert(0, 'scripts')
from postwar_city import METRIC
from mariehamn_south_streets import digest

r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
HERE = Path('data/map-scan-cache/review/mariehamn-major-roads/pass4')
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


# --- Västernäs, Klinten and the gränder east of Skarpansvägen ------------------------------
for key, name, ways, note in [
        ('parkstigen', 'Parkstigen', ['way/150528099'], 'Böjd dubbellinjerad gata genom villakvarteren.'),
        ('fabriksgatan', 'Fabriksgatan', ['way/54445946'], None),
        ('kapellvagen', 'Kapellvägen', ['way/44108122', 'way/54446882'], 'Dubbellinjerad gata från huvudgatan västerut och snett nedåt mot sydväst.'),
        ('backgatan', 'Backgatan', ['way/166291560'], None),
        ('arensgrand', 'Arensgränd', ['way/162379078'], 'Kort dubbellinjerad tvärgata mellan husraderna.'),
        ('bjorkmansgrand', 'Björkmansgränd', ['way/162379076'], 'Kort dubbellinjerad tvärgata mellan husraderna.'),
        ('gummerusgrand', 'Gummerusgränd', ['way/162379086'], 'Kort dubbellinjerad tvärgata mellan husraderna.'),
        ('sundblomsgrand', 'Sundblomsgränd', ['way/162379072'], 'Kort dubbellinjerad tvärgata mellan husraderna.'),
        ('knorringsgrand', 'Knorringsgränd', ['way/162379071'], 'Kort dubbellinjerad tvärgata mellan husraderna.'),
        ('klintgrand', 'Klintgränd', ['way/44108101'], 'Den raka nordsydliga gatan fortsätter söderut i samma läge.'),
        ('stenhuggarvagen-north', 'Stenhuggarvägen', ['way/50620751', 'way/166289519', 'way/50540395'], 'Dubbellinjerad gata snett norrut, där Backgatan ansluter.')]:
    add(key, 'vasternas', name, ways, 1968, ALL68(note or N68), S68 + ({2: ' Två moderna OSM-delar bildar en sammanhängande sträckning.', 3: ' Tre moderna OSM-delar bildar en sammanhängande sträckning.'}.get(len(ways), '')))
add('klintvagen', 'vasternas', 'Klintvägen', ['way/270240354'], 1968,
    obs((P, 'partial', 'Den raka nordsydliga gatan är ritad. Den sydvästra böjen mot Västra Utfarten saknas; gatan fortsätter i stället rakt söderut som dagens Klintgränd.'),
        (P, 'full', 'Böjen mot sydväst rödtryckt i kompletteringen 1978 med samma tjocka rödtryck som de nya vägarna.'), (P, 'full', 'Hela gatan ritad.'), (P, 'full', '')),
    'Den raka norra delen finns 1968. Böjen mot sydväst till Västra Utfarten syns först som tjockt rödtryck 1978. Samma objekt visar därför bara den norra delen 1968–1977 och hela gatan från 1978. Kartår är belägg, inte byggår.',
    kind='partial-section', partialTo=[19.934081, 60.10787],
    partialBasis='Den del av gatan som kartan 1968 visar: den raka sträckan norr om korsningen med Klintgränd.', fullBasis='Hela gatan ritad från 1978.')
add('klintvagen-approach', 'vasternas', 'Klintvägen', ['way/56396443', 'way/43519507', 'way/56131935', 'way/56396444', 'way/56396446', 'way/56396441', 'way/56396440'], 1978,
    obs((A_, None, 'Inte ritad; endast streckade tomtgränser. Gatan går 1968 rakt söderut.'), (P, 'full', 'Tjock rödtryckt väg i kompletteringen 1978 fram till Västra Utfarten.'), (P, 'full', 'Dubbellinjerad anslutning.'), (P, 'full', N95)),
    'Saknas 1968. Rödtryckt 1978 och kvar 1985 och 1995 i samma läge. Två körfält kring en refug och de korta korsningsbitarna där de möter Västra Utfarten (OSM-namn Västra Utfarten) hör till samma anslutning och räknas en gång, som det längsta körfältet. Kartåret är första granskade belägg, inte byggår.',
    kind='approach', count='longest')
add('mjolnargrand', 'vasternas', 'Mjölnargränd', ['way/59319327'], 1968,
    obs((P, 'partial', 'Den östvästliga delen är ritad som dubbellinjerad gata. Den nordsydliga fortsättningen syns inte.'),
        (P, 'partial', 'Som 1968.'), (P, 'partial', 'Fortfarande bara den östvästliga delen; norrut endast en tunn rödtryckt gräns.'), (P, 'full', 'Hela gatan röd.')),
    'Den östvästliga delen finns 1968–1985. Den nordsydliga fortsättningen ritas som gata först 1995. Samma objekt visar därför bara den östvästliga delen 1968–1994 och hela gatan från 1995. Kartår är belägg, inte byggår.',
    kind='partial-section', partialTo=[19.93576, 60.111086],
    partialBasis='Den del av gatan som kartorna 1968–1985 visar: den östvästliga sträckan fram till hörnet.', fullBasis='Hela gatan ritad från 1995.')
for key, name, ways, y68 in [
        ('cedersvagen', 'Cedersvägen', ['way/161756306', 'way/232451851'], (A_, ABS)),
        ('bagargrand', 'Bagargränd', ['way/99065928'], (U, SINGLE)),
        ('murargrand', 'Murargränd', ['way/40094417'], (U, SINGLE)),
        ('formansgrand', 'Formansgränd', ['way/45417658'], (U, SINGLE)),
        ('gjutargrand', 'Gjutargränd', ['way/161464239'], (U, SINGLE)),
        ('timmermansgrand', 'Timmermansgränd', ['way/161464242'], (A_, 'Inte ritad; endast en streckad tomtgräns mellan husraderna.')),
        ('skraddargrand', 'Skräddargränd', ['way/161464241'], (A_, ABS)),
        ('hagnasgrand', 'Hagnäsgränd', ['way/61240344'], (A_, ABS)),
        ('scheffersgrand', 'Scheffersgränd', ['way/35106990'], (A_, ABS)),
        ('gustaf-eriksonsgrand', 'Gustaf Eriksonsgränd', ['way/162379073'], (A_, ABS)),
        ('grindmattesvagen', 'Grindmattesvägen', ['way/1077608487', 'way/347964764'], (A_, ABS)),
        ('skraddargrand-west', 'Skräddargränd', ['way/536065734', 'way/1298942712'], (A_, 'Inte ritad; endast prickade tomtgränser.'))]:
    y78 = (y68[0], 'Som 1968.') if y68[0] == U else (A_, ABS)
    add(key, 'vasternas', name, ways, 1985, F85(y68, y78), S85.replace('Saknas som gata', 'Inte säkert ritad som gata') if y68[0] == U else S85)
add('vastra-utfarten-west', 'vasternas', 'Västra Utfarten', ['way/43378155', 'way/678798992', 'way/1064239367', 'way/678798993', 'way/1064239366'], 1995,
    obs((U, None, 'En enda röd vägsignatur. Den västra körbanan ligger 6–9 m från den redan daterade östra och kan inte skiljas ut.'), (U, None, 'Som 1968.'), (U, None, 'Som 1968.'),
        (P, 'full', 'Ritad som två skilda körbanor.')),
    'Västra Utfartens västra körbana, parallell med den redan daterade östra. Visas först 1995, då kartan ritar två körbanor; tidigare utgåvor visar en enda väg. Räknas inte som ny väglängd.',
    kind='carriageways', count='parallel')

# --- Southern Mariehamn ----------------------------------------------------------------------
for key, name, ways, note in [
        ('matrosgatan', 'Matrosgatan', ['way/96831630'], 'Dubbellinjerad gata med böj i norr, i samma läge som i dag.'),
        ('jungmansgatan', 'Jungmansgatan', ['way/96831828'], None),
        ('larlingsgrand', 'Lärlingsgränd', ['way/97111552'], 'Diagonal dubbellinjerad gata i det snedställda gatunätet.'),
        ('hantverkargatan', 'Hantverkargatan', ['way/96957253'], 'Diagonal dubbellinjerad gata i det snedställda gatunätet.'),
        ('berggatan', 'Berggatan', ['way/163490513'], 'Böjd dubbellinjerad gata med hus längs båda sidor.'),
        ('mockelobrinken', 'Möckelöbrinken', ['way/37913499', 'way/163487830', 'way/163490512'], 'Dubbellinjerad gata längs södra kanten av det skrafferade kvarteret.')]:
    add(key, 'sodra', name, ways, 1968, ALL68(note or N68), S68 + (f' {len(ways)} moderna OSM-delar bildar en sammanhängande sträckning.'.replace(' 2 ', ' Två ').replace(' 3 ', ' Tre ') if len(ways) > 1 else ''))
add('mangelgrand', 'sodra', 'Mangelgränd', ['way/186395790'], 1985, F85((A_, HATCH), (A_, HATCH)), S85)
add('hellmansgrand', 'sodra', 'Hellmansgränd', ['way/162302454'], 1985, F85((A_, HATCH), (A_, HATCH)), S85)
add('vastra-skolgatan', 'sodra', 'Västra Skolgatan', ['way/1081063268'], 1985, F85((A_, HATCH), (A_, HATCH)), S85)
for key, name, way in [('storbatsvagen', 'Storbåtsvägen', 'way/223194504'), ('skotbatsvagen', 'Skötbåtsvägen', 'way/223194518'),
                       ('galeasvagen', 'Galeasvägen', 'way/142807391'), ('galeasvagen-link', 'Galeasvägen', 'way/303193207')]:
    add(key, 'sodra', name, [way], 1995, F95(), S95)

# --- Ytternäs ----------------------------------------------------------------------------------
for key, name, ways, red78 in [
        ('tallvagen', 'Tallvägen', ['way/118247851'], True), ('alvagen', 'Alvägen', ['way/72843062', 'way/162297311', 'way/925579965'], True),
        ('granvagen', 'Granvägen', ['way/134294407'], True), ('lovstrandsvagen', 'Lövstrandsvägen', ['way/134416726'], False),
        ('askvagen-west', 'Askvägen', ['way/118247854'], True), ('askvagen-east', 'Askvägen', ['way/152020197', 'way/152020196'], True),
        ('tallvagen-south', 'Tallvägen', ['way/152068474'], True), ('videvagen', 'Videvägen', ['way/118247844'], True),
        ('granvagen-north', 'Granvägen', ['way/134294420'], True), ('granvagen-south', 'Granvägen', ['way/493781609'], True),
        ('salgstigen', 'Sälgstigen', ['way/222074035'], True), ('kallstigen', 'Källstigen', ['way/222074028'], False), ('solstrandsstigen', 'Solstrandsstigen', ['way/162997276'], False)]:
    add(key, 'ytternas', name, ways, 1985, F85((A_, ABS), (U, RED78) if red78 else (A_, ABS)), S85 + ({2: ' Två moderna OSM-delar bildar en sammanhängande sträckning.', 3: ' Tre moderna OSM-delar bildar en sammanhängande sträckning.'}.get(len(ways), '')))
add('genvagen', 'ytternas', 'Genvägen', ['way/525919669'], 1985,
    F85((U, 'En tunn linje med tvärstreck i ungefär samma läge; inte ritad som gata.'), (U, 'Som 1968.')), S85.replace('Saknas som gata', 'Inte säkert ritad som gata'))
add('svedgrand', 'ytternas', 'Svedgränd', ['way/161577062'], 1995, F95(), S95)
add('maringrand', 'ytternas', 'Maringränd', ['way/161577063'], 1995, F95((U, 'Tunna dubbla linjer vid strandtomterna; inte säkert en gata.')), S95)
add('skolstigen', 'ytternas', 'Skolstigen', ['way/134295153', 'way/925582182', 'way/935644590'], 1995, F95(), S95 + ' Tre moderna OSM-delar bildar en sammanhängande sträckning.')

# --- Norrböle north and Dalkarby ---------------------------------------------------------------
add('travvagen', 'norr', 'Travvägen', ['way/161756320'], 1968, ALL68('Röd väg förbi Norrgård i samma läge som i dag.'), S68)
add('dalvagen', 'norr', 'Dalvägen', ['way/35556563', 'way/166080097'], 1985, F85(), S85 + ' Två moderna OSM-delar bildar en sammanhängande sträckning.')
add('brinkvagen', 'norr', 'Brinkvägen', ['way/105033786'], 1995, F95(), S95)
add('vikingagrand', 'norr', 'Vikingagränd', ['way/35039424'], 1995,
    obs((A_, None, ABS), (U, None, RED78), (A_, None, 'Inte ritad; endast tomt- och områdesgränser.'), (P, 'full', N95)), S95)
add('fallgardsvagen', 'norr', 'Fallgärdsvägen', ['way/131007857'], 1995,
    obs((U, None, 'En prickad stig vid Granliden i ungefär samma läge; inte ritad som gata.'), (U, None, 'Som 1968.'), (U, None, 'Som 1968.'), (P, 'full', N95)), S95.replace('Saknas som gata', 'Inte säkert ritad som gata'))
add('lovdalsvagen', 'norr', 'Lövdalsvägen', ['way/44108111'], 1995, F95(), S95)


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
    return [dict(file=f'pass4/{p.name}', sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(HERE.glob('ways-*.jpg'))]


out = []
for d in D:
    rec = dict(id='road:mariehamn:street-pass4:' + d['id'], name=d['name'], routeId='road:' + d['name'], group=d['group'], kind=d['kind'])
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
              source=dict(id='review:mariehamn-street-pass4', title='Mariehamns gator · fjärde granskningen mot kartorna 1968–1995', url='assets/mariehamn-street-pass4.json'),
              method='Varje modern gatudel jämfördes visuellt med originalkartornas utsnitt för 1968, 1978, 1985 och 1995 över samma markyta (kontaktark per gata med den moderna linjen inritad endast på 1968). Överlägg är hjälpmedel, inte belägg. Tunna röda linjer i kompletteringen 1978 och enkla heldragna linjer 1968 räknas inte som gator; svarta linjer 1995 är gångväg eller mindre väg. Kartår är första granskade belägg, inte byggår. Parallella körbanor räknas en gång.',
              sheets=batch1['sheets'], decisions=out,
              deferred=[
                  dict(name='Framnäsvägen och Varvsvägen', basis='Ritade som gator 1985, men de ansluter till Västra Utfartens västra körbana, som kartorna skiljer ut först 1995. Daterade från 1985 skulle de sluta 6–9 m från den daterade körbanan under 1985–1994.'),
                  dict(name='Uppgårdsvägen, Östra Stenliden, Kråkbärsstigen, Blåbärsstigen, Hjortronstigen', basis='Ritade som röda gator först 1995 (Uppgårdsvägens norra del, way 88561577, inte ens då). Kvarteret når det daterade vägnätet bara via odaterade korsningsbitar av Nya Godbyvägen, Doktorsvägens servicedel och gång- och cykelvägar; de dateras tillsammans med de delarna.'),
                  dict(name='Bergshöjden', basis='Ritad som gata 1985, men dagens gata slutar i båda ändar utan anslutning till någon modern gata; anslutningen behöver granskas.'),
                  dict(name='Mästargränd och Ekogränd', basis='Slingan är ritad 1968, men dagens Ekogränd ligger längs en tunn genomgående linje och inte längs slingans norra sida, och Mästargrändens östra anslutning är i dag gångväg.'),
                  dict(name='Knipgränd, Alfågelgränd, Tibastvägen', basis='Ritade som gator 1985, men de når det daterade vägnätet bara via Skrakvägen och Roskarlsvägen utanför stadens gatuunderlag eller via gång- och cykelvägar.'),
                  dict(name='Michaelsvägen', basis='Rondellens tillfarter är senare än 1995 eller oklara.'),
                  dict(name='Björkvägen, Hagtornsvägen, Kottstigen, Syrengränd', basis='Läget är oklart 1985.'),
                  dict(name='Västra Utfartens korsningsdelar vid Klintvägen och Ålandsplan', basis='Korta korsningsbitar utan egen längd; lämnas tills korsningen granskas som helhet.'),
                  dict(name='Skönviksvägen, Nybondas, Snickerivägen, Sylgränd, Slantgränd', basis='Inte ritade som röd gata 1995 (svart linje, gräns eller ingenting).'),
                  dict(name='Bergsvägen, Tvärgränd, Hasselstigen, Kvarngränd, Kilvägen, Lagervägen, Strandgränd, Algotsgränd, Ekogränd', basis='Läget, utbredningen eller anslutningen är oklar i minst en utgåva.'),
                  dict(name='Kasbrinken, Åbrinken, Vikbrinken, Lekgränd, Krokvikgsgränd, Gnistvägen, Fyrvaktarvägen, Ångbåtsbryggan', basis='Ritade som svart linje, inte röd gata, 1995. Väntar på en modell för väg som blir gångväg eller tvärtom.'),
                  dict(name='Servicegatans södra del, Villagränd, Bäckvägen, Nybondasvägen', basis='Kartornas äldre väg följer en annan linje än dagens gata; sambandet behöver en egen omläggningsgranskning.'),
                  dict(name='Fågelberget (Fågellänken, Vråkvägen, Hökvägen m.fl.), Blomstringevägen, Skrapängsvägen, Juseliusvägen, Palett-, Akvarell- och Pastellgränd', basis='Saknas som gator till och med 1995.'),
              ],
              reviewSheets=sheet_files())
review['totals'] = dict(newPersistentMeters=new, confirmedExistingMeters=0, reviewedMeters=new,
                        byGroup={g: round(sum(d['lengthMeters'] for d in out if d['group'] == g), 2) for g in dict.fromkeys(d['group'] for d in out)},
                        byFirstYear={str(y): round(sum(d['lengthMeters'] for d in out if d['firstYear'] == y), 2) for y in YEARS if any(d['firstYear'] == y for d in out)})
Path('data/mariehamn-street-pass4.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(len(out), new, review['totals']['byGroup'], review['totals']['byFirstYear'])
for d in out:
    print(d['id'].split(':')[-1], d['firstYear'], d['lengthMeters'], len(d['members']), len(d['modernLinks']), len(d['originals']))
