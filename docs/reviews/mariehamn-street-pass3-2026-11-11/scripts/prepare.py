"""Builds data/mariehamn-street-pass3.json from the visual review below (third Mariehamn street pass).

Retained for audit. It captures input hashes of the modern road, city-stage and snapshot records at
the time of review, so rerunning it after those inputs change silently re-baselines the review. The
compiler (scripts/mariehamn_street_pass3.py) rejects changed inputs instead.

Every decision was made by looking at the original-scan contact sheets ways-*.jpg made by
waysheet.py (one row per modern way: 1968 with the way outlined, then the unmarked 1968, 1978, 1985
and 1995 crops of the same ground) and, where needed, the area crops and zooms in this folder.

Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/mariehamn-major-roads/pass3/prepare.py
"""
import gzip, hashlib, json, sys
from pathlib import Path
from shapely.geometry import LineString, Point
from shapely.ops import substring
sys.path.insert(0, 'scripts')
from postwar_city import METRIC
from mariehamn_south_streets import digest

r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
HERE = Path('data/map-scan-cache/review/mariehamn-major-roads/pass3')
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
RED78 = 'Rödtryckt tunn linje i kompletteringen 1978 längs den senare gatan; kan vara en tomt- eller plangräns och räknas inte som gata.'
S68 = 'Visuellt följd i utgåvorna 1968, 1978, 1985 och 1995 i samma korridor. Kartåret är första granskade belägg, inte byggår. Modern detaljgeometri används för hela perioden.'
S85 = 'Saknas som gata 1968 och 1978. Ritad som gata 1985 och 1995 i samma läge. Kartåret är första granskade belägg, inte byggår.'
S95 = 'Saknas som gata 1968–1985. Ritad som gata först 1995. Kartåret är första granskade belägg, inte byggår.'


def obs(*rows):
    return [dict(year=y, outcome=o, coverage='unknown' if o != P else c, note=n) for y, (o, c, n) in zip(YEARS, rows)]


ALL68 = lambda n=N68: obs((P, 'full', n), (P, 'full', 'Grundkartan oförändrad.'), (P, 'full', ''), (P, 'full', ''))
def F85(y68=(A_, ABS), y78=(A_, ABS)):
    return obs((y68[0], None, y68[1]), (y78[0], None, y78[1]), (P, 'full', N85), (P, 'full', N95))
F95 = lambda: obs((A_, None, ABS), (A_, None, ABS), (A_, None, ABS), (P, 'full', N95))

D = []
def add(key, group, name, ways, first, observations, basis, kind='section', **extra):
    D.append(dict(id=key, group=group, name=name, ways=ways, first=first, observations=observations, basis=basis, kind=kind, **extra))


# --- Johannebo and the streets east of Godbyvägen (first reviewed 1968 unless noted) ------
for key, name, way in [('krokensvagen', 'Krokensvägen', 'way/121459479'), ('grantorpsvagen', 'Grantorpsvägen', 'way/69649474'),
                       ('angsvagen', 'Ängsvägen', 'way/214834445'), ('verkstadsvagen', 'Verkstadsvägen', 'way/214834444'),
                       ('fridhemsvagen', 'Fridhemsvägen', 'way/90673966'), ('johannebovagen', 'Johannebovägen', 'way/163848698'),
                       ('sanatorievagen', 'Sanatorievägen', 'way/44669181')]:
    add(key, 'johannebo', name, [way], 1968, ALL68(), S68)
add('nabbvagen', 'johannebo', 'Nabbvägen', ['way/34978285', 'way/158304925', 'way/626549151', 'way/626549152'], 1968,
    ALL68('Diagonal gata mot Lemlandsvägen med hus längs den sydvästra sidan.'), S68 + ' Fyra moderna OSM-delar bildar en sammanhängande sträckning.')
add('mellangardsvagen', 'johannebo', 'Mellangårdsvägen', ['way/69649466'], 1968,
    obs((P, 'partial', 'Den södra delen från Godbyvägen till Fridhemsvägen är ritad. Norr om Fridhemsvägen syns ingen säker gata.'),
        (P, 'partial', 'Som 1968.'), (P, 'full', 'Hela gatan ritad.'), (P, 'full', '')),
    'Den södra delen, från Godbyvägen upp till korsningen med Fridhemsvägen, finns 1968 och 1978. Den norra fortsättningen syns som gata först 1985. Samma objekt visar därför bara den södra delen 1968–1984 och hela gatan från 1985. Kartår är belägg, inte byggår.',
    kind='partial-section', partialTo=[19.944212, 60.11963])
add('strandhagsvagen', 'johannebo', 'Strandhagsvägen', ['way/84527342'], 1985,
    F85((A_, 'Ingen gata; husraderna står rygg mot rygg med en tomtgräns emellan. Vägen till fiskeriskolan ligger cirka 30 m söder om dagens gata och är i dag gångväg.'), (A_, 'Som 1968.')),
    S85 + ' Den äldre vägen till skolan söder om gatan är en annan sträckning och dateras inte här.')
add('dalgrand', 'johannebo', 'Dalgränd', ['way/163848719'], 1985,
    F85((U, 'En smal gång med streckad kant längs husen; inte säkert en gata.'), (U, 'Som 1968.')), S85.replace('Saknas som gata', 'Inte säkert ritad som gata'))
add('bastugrand', 'johannebo', 'Bastugränd', ['way/121739209'], 1985, F85(), S85)
add('doktorsvagen', 'johannebo', 'Doktorsvägen', ['way/88598408'], 1995,
    obs((A_, None, ABS), (A_, None, ABS), (A_, None, 'Endast en prickad gräns.'), (P, 'full', N95)), S95)

# --- Stenliden and Kråkbärsstigen, west of Nya Godbyvägen ---------------------------------
add('vastra-stenliden', 'stenliden', 'Västra Stenliden', ['way/61240349'], 1985, F85(), S85)

# --- Hindersböle residential grid ----------------------------------------------------------
add('ljungvagen', 'hindersbole', 'Ljungvägen', ['way/532052899'], 1968,
    ALL68('Smal gata med en streckad kant genom den äldre bebyggelsen norr om Hindersböle; samma läge som dagens Ljungvägen inom cirka 10 m.'),
    S68 + ' Gatan är den äldsta i området; resten av rutnätet kring den tillkommer först 1985.')
add('askuddsvagen', 'hindersbole', 'Askuddsvägen', ['way/86220899'], 1968,
    ALL68('Äldre väg från Hindersböle söderut till Lemlandsvägen, ritad med en hel och en streckad kant.'), S68)
for key, name, ways, red78, y68 in [
        ('solvandan', 'Solvändan', ['way/1537771232', 'way/251840730'], False, None),
        ('blomstervagen-north', 'Blomstervägen', ['way/245667778'], False, None),
        ('blomstervagen-south', 'Blomstervägen', ['way/527683413'], False, 'En äldre väg går cirka 30 m väster om dagens gata; sambandet är oklart.'),
        ('hogbackagatan-north', 'Högbackagatan', ['way/90673965'], True, None),
        ('hogbackagatan-south', 'Högbackagatan', ['way/47633550'], False, None),
        ('tussilagogrand', 'Tussilagogränd', ['way/162427750'], False, None),
        ('backavagen', 'Backavägen', ['way/143791605'], False, None),
        ('movagen', 'Movägen', ['way/228310365'], True, None),
        ('sandasvagen', 'Sandåsvägen', ['way/231045411'], True, None),
        ('lisebogrand', 'Lisebogränd', ['way/527683412'], False, None),
        ('konvaljegrand', 'Konvaljegränd', ['way/162427749'], False, None),
        ('gullvivegrand', 'Gullvivegränd', ['way/162427754'], False, None),
        ('vitsippsgrand', 'Vitsippsgränd', ['way/162427753'], False, None),
        ('blasippsgrand', 'Blåsippsgränd', ['way/162427752'], False, None),
        ('prastkragegrand', 'Prästkragegränd', ['way/532056364'], True, None),
        ('vallmogrand', 'Vallmogränd', ['way/532056363'], False, None),
        ('klovergrand', 'Klövergränd', ['way/532056361'], False, None),
        ('violgrand', 'Violgränd', ['way/532056359'], False, None),
        ('timotejgrand', 'Timotejgränd', ['way/47615741'], False, None),
        ('lillakersvagen-east-west', 'Lillåkersvägen', ['way/79138225'], True, None),
        ('lillakersvagen-north', 'Lillåkersvägen', ['way/532052897'], False, None),
        ('lillakersvagen-link', 'Lillåkersvägen', ['way/532052898'], False, None)]:
    add(key, 'hindersbole', name, ways, 1985, F85((U, y68) if y68 else (A_, ABS), (U, RED78) if red78 else (A_, ABS)), S85)
for key, name, way in [('odalvagen', 'Odalvägen', 'way/122072177'), ('riakersgrand-south', 'Riåkersgränd', 'way/136775754'),
                       ('riakersgrand-north', 'Riåkersgränd', 'way/493751672'), ('odalgrand', 'Odalgränd', 'way/493751675')]:
    add(key, 'hindersbole', name, [way], 1995,
        obs((A_, None, 'Åker.'), (A_, None, 'Åker.'), (A_, None, 'Åker (Ättehögar).'), (P, 'full', N95)), S95)

# --- Norrböle, north of Bolstavägen ----------------------------------------------------------
add('karlbergsvagen', 'norrbole', 'Karlbergsvägen', ['way/87088751'], 1985, F85((A_, 'Gårdarna Borstaberg och minkfarmen; ingen gata.'), (U, RED78)), S85)
add('skogshyddsvagen', 'norrbole', 'Skogshyddsvägen', ['way/45417659'], 1985, F85((U, 'En streckad stig i ungefär samma läge.'), (U, RED78)), S85)
add('dalkarbyvagen', 'norrbole', 'Dalkarbyvägen', ['way/44669185'], 1985, F85((U, 'Gårdsplanen vid Bolstan; ingen säker gata.'), (U, RED78)), S85)
add('norrbolevagen', 'norrbole', 'Norrbölevägen', ['way/44669186', 'way/45417661'], 1985,
    F85((U, 'En streckad gräns längs åkerkanten vid Backtorpet; ingen säker gata.'), (U, RED78)), S85 + ' Två moderna OSM-delar bildar en sammanhängande sträckning.')

# --- Västernäs -------------------------------------------------------------------------------
add('stenhuggarvagen', 'vasternas', 'Stenhuggarvägen', ['way/34995342'], 1968, ALL68('Diagonal dubbellinjerad gata med hus längs båda sidor.'), S68)
add('smedsgrand', 'vasternas', 'Smedsgränd', ['way/59319326'], 1968, ALL68(), S68 + ' Kartlinjen ligger 10–20 m från den moderna mittlinjen i samma riktning; avvikelsen är registreringsfel, inte en flytt.')
# --- Skarpans and Servicegatan, south of the centre -------------------------------------------
add('skarpansvagen', 'skarpans', 'Skarpansvägen', ['way/43519493', 'way/944017639', 'way/612335559', 'way/944025147'], 1968,
    ALL68('Röd huvudväg diagonalt längs industriområdet, i samma läge som i dag.'), S68 + ' Fyra moderna OSM-delar bildar en sammanhängande sträckning fram till korsningen i sydost.')
add('skeppargatan', 'skarpans', 'Skeppargatan', ['way/35432056', 'way/944013604', 'way/944013605', 'way/172276818'], 1968,
    ALL68('Gata genom industriområdet och vidare österut, korsar Skarpansvägen.'), S68 + ' Fyra moderna OSM-delar bildar en sammanhängande sträckning; de två korta delarna vid korsningen ligger i samma korridor.')
add('skiljevagen', 'skarpans', 'Skiljevägen', ['way/1423011513', 'way/40096180'], 1968, ALL68('Gata längs radhuskvarteren.'), S68)
add('gesallgatan', 'skarpans', 'Gesällgatan', ['way/627575720'], 1968, ALL68('Diagonal dubbellinjerad gata.'), S68)
add('servicegatan-north', 'skarpans', 'Servicegatan', ['way/37639417', 'way/61319836'], 1978,
    obs((A_, None, 'Endast prickad gräns och strand.'), (P, 'full', 'Rödtryckt väg i kompletteringen 1978, samma tjocka rödtryck som Österleden.'), (P, 'full', N85), (P, 'full', N95)),
    'Saknas 1968. Rödtryckt i kompletteringen 1978 och kvar 1985 och 1995 i samma läge. Kartåret är första granskade belägg, inte byggår.')


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
    return [dict(file=f'pass3/{p.name}', sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(HERE.glob('ways-*.jpg'))]


out = []
for d in D:
    rec = dict(id='road:mariehamn:street-pass3:' + d['id'], name=d['name'], routeId='road:' + d['name'], group=d['group'], kind=d['kind'])
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
        rec['phases'] = [dict(**{'from': d['first'], 'to': full_from}, geometry='substring:south', range=[0, t], paths=sub, basis='Den del av gatan som kartorna 1968 och 1978 visar: från Godbyvägen till korsningen med Fridhemsvägen.'),
                         dict(**{'from': full_from, 'to': None}, geometry='modern', basis='Hela gatan ritad från 1985.')]
    else:
        rec['phases'] = [dict(**{'from': d['first'], 'to': None}, geometry='modern', basis=d['basis'])]
    rec['observations'] = d['observations']
    rec['countRule'] = 'display'; rec['basis'] = d['basis']
    rec['lengthMeters'] = round(sum(m(modern[w]['paths'][0]).length for w in d['ways']), 2)
    out.append(rec)

ids = [w for d in D for w in d['ways']]
assert len(ids) == len(set(ids))
new = round(sum(d['lengthMeters'] for d in out), 2)
review = dict(schemaVersion=1, reviewedAt='2026-11-11',
              source=dict(id='review:mariehamn-street-pass3', title='Mariehamns gator · tredje granskningen mot kartorna 1968–1995', url='assets/mariehamn-street-pass3.json'),
              method='Varje modern gatudel jämfördes visuellt med originalkartornas utsnitt för 1968, 1978, 1985 och 1995 över samma markyta (kontaktark per gata med den moderna linjen inritad endast på 1968). Överlägg är hjälpmedel, inte belägg. Tunna röda linjer i kompletteringen 1978 räknas inte som gator. Kartår är första granskade belägg, inte byggår.',
              sheets=batch1['sheets'], decisions=out,
              deferred=[
                  dict(name='Myrstigen, Betesgränd, Bättringsvägen, Hälsostigen, Kasbrinken, Kärrstigen, Johannebovägens södra stump, Martallsvägen, Kråkbärsstigens västra del', basis='Ritade som smal väg eller gång 1985 och som svart linje, inte röd gata, 1995, eller anslutna i dag bara via gång- och cykelvägar. Väntar på en modell för väg som blir gångväg eller tvärtom.'),
                  dict(name='Mjölnargränd', basis='Bara den östvästliga delen syns 1968; den nordsydliga delen är oklar. Lämnas tills delningspunkten kan granskas.'),
                  dict(name='Lagervägen, Marielundsvägen, Bogränd, Snesgränd', basis='Läget eller utbredningen är oklar i minst en utgåva.'),
                  dict(name='Trädgårdsvägen och Åkervägen', basis='Ritade med enkla linjer 1968 och 1978. Åkervägen ansluter bara via Trädgårdsvägen, som 1995 är ritad som svart linje; ingen av dem dateras förrän anslutningen kan granskas.'),
                  dict(name='Uppgårdsvägen, Östra Stenliden, Kråkbärsstigens östra del, Varvsvägen, Framnäsvägen', basis='Uppgårdsvägen, Östra Stenliden och Kråkbärsstigen syns 1995 och Framnäsvägen och Varvsvägen 1985, men de når det daterade vägnätet bara via ännu odaterade korsningsdelar (Västra Utfartens körbanor, Doktorsvägens servicedel). De dateras tillsammans med de delarna för att inte rita fristående gator.'),
                  dict(name='Villagränd, Kilvägen, Servicegatans södra del', basis='Läget avviker eller anslutningen är oklar i 1968 års karta.'),
                  dict(name='Nygårdsvägen, Årsringen, Kärnveden, Torksprickan, Kummelgränd', basis='Saknas som gator till och med 1995.'),
                  dict(name='Äldre väg väster om Blomstervägen och Ljungvägens äldre bebyggelse vid Stentorpa', basis='Vägar på 1968 års karta som inte motsvarar en modern gata; inte rekonstruerade.'),
              ],
              reviewSheets=sheet_files())
review['totals'] = dict(newPersistentMeters=new, confirmedExistingMeters=0, reviewedMeters=new,
                        byGroup={g: round(sum(d['lengthMeters'] for d in out if d['group'] == g), 2) for g in dict.fromkeys(d['group'] for d in out)},
                        byFirstYear={str(y): round(sum(d['lengthMeters'] for d in out if d['firstYear'] == y), 2) for y in YEARS if any(d['firstYear'] == y for d in out)})
Path('data/mariehamn-street-pass3.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(len(out), new, review['totals']['byGroup'], review['totals']['byFirstYear'])
for d in out:
    print(d['id'].split(':')[-1], d['firstYear'], d['lengthMeters'], len(d['members']), len(d['modernLinks']), len(d['originals']))
