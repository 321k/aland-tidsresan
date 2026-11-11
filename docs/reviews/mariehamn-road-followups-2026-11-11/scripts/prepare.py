"""Builds data/mariehamn-major-road-followups.json from the visual review below.

Retained for audit. It captures input hashes of the modern road, city-stage and
snapshot records at the time of review, so rerunning it after those inputs change
silently re-baselines the review. The compiler rejects changed inputs instead.

Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/mariehamn-major-roads/followups/prepare.py
"""
import gzip, hashlib, json, sys
from pathlib import Path
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, substring
sys.path.insert(0, 'scripts')
from postwar_city import METRIC
from mariehamn_south_streets import digest

r = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
HERE = Path('data/map-scan-cache/review/mariehamn-major-roads/followups')
modern = {f['id']: f for f in r('dist/assets/modern.json.gz')['features']}
stages = r('dist/assets/mariehamn-city-grid.json')['sets']
snapshots = {y: r(f'dist/assets/roads-{y}.json.gz')['features'] for y in [2014, 2021, 2025]}
by_osm = {y: {f.get('osmId'): f for f in fs if f.get('osmId')} for y, fs in snapshots.items()}
catalog = r('dist/assets/temporal-objects.json.gz')
occupied = {(l['datasetId'], l['featureId']) for o in catalog['objects'] for l in o['sourceLinks']}
batch1 = r('data/mariehamn-major-roads.json')
m = lambda pts: LineString([METRIC(*p) for p in pts])
YEARS = [1968, 1978, 1985, 1995]


def crop_ref(key, year):
    meta = json.loads((HERE / f'{key}-{year}.json').read_text())
    png = HERE / f'{key}-{year}.png'
    return dict(crop=f'followups/{key}-{year}.png', cropSha256=hashlib.sha256(png.read_bytes()).hexdigest(),
                sourceId=meta['sourceId'], sourceSha256=meta['sha256'], box=meta['box'], scale=meta['scale'])


def on_line(way, lon, lat):
    """Nearest point on a modern way, rounded to the 7-decimal precision used by the scans."""
    line = LineString(modern[way]['paths'][0]); p = line.interpolate(line.project(Point(lon, lat)))
    return [round(p.x, 7), round(p.y, 7)]


# Raw centre-line samples from trace.py on the original-scan crops. Rejected samples
# (property numerals or crossing roads inside the search window) are kept separately.
TRACES = {
    'A': dict(year=1968, ref=crop_ref('strandnas-detail', 1968), method='trace.py strandnas-detail 1968 v 0 600 40 330 500',
              points=[[19.9422436, 60.1168428], [19.9422246, 60.1166404], [19.9422005, 60.1164381], [19.9421966, 60.1162359],
                      [19.9421876, 60.1160336], [19.9421585, 60.1158312], [19.9421064, 60.1152242], [19.9420773, 60.1150218],
                      [19.9420482, 60.1148193], [19.9420744, 60.1146173]],
              rejected=[[19.941843, 60.1156266], [19.9417084, 60.1154234]],
              note='Rak söderut från Godbyvägen till fyrvägskorsningen vid Lemlandsvägen. Två punkter vid röda fastighetssiffror är bortvalda.'),
    'B': dict(year=1968, ref=crop_ref('strandnas-detail', 1968), method='trace.py strandnas-detail 1968 h 150 420 10 420 520',
              points=[[19.9394635, 60.1143779], [19.9395638, 60.1143837], [19.9396649, 60.1143642], [19.9398656, 60.1143758],
                      [19.940066, 60.114395], [19.9401656, 60.1144261], [19.9402659, 60.1144319], [19.940367, 60.1144125],
                      [19.9404673, 60.1144183], [19.9405675, 60.1144291], [19.9406678, 60.1144349], [19.9407681, 60.1144433],
                      [19.9408677, 60.1144718], [19.940968, 60.1144776], [19.941069, 60.1144632], [19.9411693, 60.114469],
                      [19.9412696, 60.1144748], [19.9413699, 60.1144832], [19.9414702, 60.114489], [19.9415695, 60.1145301],
                      [19.941669, 60.1145638], [19.9417712, 60.1145064]],
              rejected=[[19.9397568, 60.1146505], [19.939961, 60.1145434], [19.9418703, 60.1145526], [19.9419734, 60.1144675], [19.9420738, 60.1144682], [19.9421711, 60.1145776]],
              note='Rak öst–västlig huvudväg genom den senare rondellplatsen. Två punkter vid röda fastighetssiffror och fyra i själva korsningen är bortvalda.'),
    'C': dict(year=1985, ref=crop_ref('ngv-merge', 1985), method='trace.py ngv-merge 1985 v 300 800 20 230 600',
              points=[[19.9349885, 60.1304889], [19.9350412, 60.1305903], [19.9352399, 60.1308947], [19.9353231, 60.1309963],
                      [19.9354163, 60.131098], [19.9354944, 60.1311996], [19.9355877, 60.1313013], [19.935686, 60.131403],
                      [19.9358047, 60.1315048], [19.9360216, 60.1317084], [19.9361504, 60.1318104], [19.936269, 60.1319122],
                      [19.9363775, 60.132014], [19.936486, 60.1321158], [19.9366046, 60.1322177], [19.9367181, 60.1323195],
                      [19.9368317, 60.1324214], [19.9369503, 60.1325232], [19.9370638, 60.1326251], [19.9374126, 60.1328296]],
              rejected=[[19.9348962, 60.1306902], [19.9343305, 60.1307869], [19.9373426, 60.1316173], [19.9367668, 60.1327238]],
              note='Nya Godbyvägens båge mot Godbyvägen 1985. Bortvalda punkter ligger på korsande vägar och Godbyvägen.'),
}

# Reconstructed display lines: modern junction nodes as anchors, scan trace between them.
crossing = on_line('way/43448261', 19.9420744, 60.1146173)
split = on_line('way/70750975', *TRACES['C']['points'][0])
RECON = {
    'A': dict(paths=[[[19.9422, 60.11605], crossing]], anchors=[dict(way='way/1298787802', point=[19.9422, 60.11605]), dict(way='way/43448261', point=crossing)]),
    'B': dict(paths=[[[19.93922, 60.11427], [19.94138, 60.11445]]], anchors=[dict(way='way/44108106', point=[19.93922, 60.11427]), dict(way='way/43448261', point=[19.94138, 60.11445])]),
    'C': dict(paths=[[split] + TRACES['C']['points'][1:-1] + [[19.93762, 60.13295]]], anchors=[dict(way='way/70750975', point=split), dict(way='way/77082297', point=[19.93762, 60.13295])]),
}

P, A_, U = 'present', 'absent', 'unclear'
def obs(*rows):
    return [dict(year=y, outcome=o, coverage=c, note=n) for y, (o, c, n) in zip(YEARS, rows)]
ALL68 = lambda n: obs((P, 'full', n), (P, 'full', n), (P, 'full', n), (P, 'full', n))
OVERPRINT = 'Rödtryckt komplettering 1978 visar rondellen och anslutningarna; grundkartans äldre korsning är ännu inte borttagen.'
ABS = (A_, 'unknown', 'Inte på kartan.')

S68 = 'Visuellt följd på grundkartan 1968 och i utgåvorna 1978, 1985 och 1995 i samma korridor. Kartåret är första granskade belägg, inte byggår. Modern detaljgeometri används där vägen bedöms ligga kvar.'
S78 = 'Saknas 1968. Rödtryckt i kompletteringen 1978 och kvar 1985 och 1995 i samma korridor. Kartåret är första granskade belägg, inte byggår.'
S85 = 'Saknas på kartorna 1968 och 1978 (endast fält, skog, höjdkurvor och tomtgränser). Ritad som gata 1985 och 1995 i samma läge. Kartåret är första granskade belägg, inte byggår.'
S95 = 'Saknas 1968–1985. Ritad som genomgående väg först 1995. Kartåret är första granskade belägg, inte byggår.'

D = []
def add(**k): D.append(k)

# --- 1. Godbyvägen's southern junction at Strandnäs ---------------------------------
add(id='godbyvagen-old-south-approach', group='strandnas', name='Godbyvägen · äldre södra infart', routeId='road:Godbyvägen', kind='realigned-section',
    members=['way/34984271'], display=['way/34984271'],
    phases=[dict(**{'from': 1968, 'to': 1985}, geometry='reconstructed:A', basis='Godbyvägen gick 1968 och 1978 rakt söderut till en fyrvägskorsning med Sjukhusvägen–Lemlandsvägen. Linjen är avritad ur 1968 års karta mellan två moderna knutpunkter.'),
            dict(**{'from': 1985, 'to': None}, geometry='modern', basis='Från 1985 leds trafiken i en båge till rondellen. Den södra delen av den gamla raksträckan finns kvar som återvändsgata (dagens Godbyvägen, way 34984271) med ny anslutning i norr.')],
    states=[dict(state='open', **{'from': 1968, 'to': None})],
    observations=obs((P, 'full', 'Rak infart till fyrvägskorsningen.'), (P, 'full', 'Grundkartans raka infart kvar; ' + OVERPRINT), (P, 'full', 'Endast den södra stumpen kvar, ansluten till den nya bågen.'), (P, 'full', 'Stumpen kvar som 1985.')),
    count='reconstructed', basis='Den äldre infartens kvarvarande stump bär samma identitet. Ändringen mellan 1978 och 1985 är en verklig omläggning; 1985 är första utgåva som visar den, inte ombyggnadsår.')
add(id='strandnas-old-straight-crossing', group='strandnas', name='Sjukhusvägen–Lemlandsvägen · äldre rak sträckning vid Strandnäs', routeId='road:Sjukhusvägen', kind='abandoned-section',
    members=[], display=[],
    phases=[dict(**{'from': 1968, 'to': 1985}, geometry='reconstructed:B', basis='Den raka huvudvägen genom den senare rondellplatsen, avritad ur 1968 års karta mellan Sjukhusvägens och Lemlandsvägens moderna knutpunkter.')],
    states=[dict(state='open', **{'from': 1968, 'to': 1985}), dict(state='abandoned', **{'from': 1985, 'to': None})],
    observations=obs((P, 'full', 'Rak genomfart.'), (P, 'full', 'Grundkartans genomfart kvar; ' + OVERPRINT), (A_, 'unknown', 'Ersatt av Rökerirondellen.'), (A_, 'unknown', 'Ersatt av Rökerirondellen.')),
    count='reconstructed', basis='Försvunnen sträckning. Visas inte efter 1985. Lemlandsvägens anslutande 40 m (del av en annan granskningsenhet med första belägg 1985) skapas inte som dubblett här.')
add(id='sjukhusvagen-west-link', group='strandnas', name='Sjukhusvägen', routeId='road:Sjukhusvägen', kind='section', members=['way/40388607'], display=['way/40388607'],
    first=1968, observations=ALL68('Del av Sjukhusvägens raka huvudväg.'), count='display', basis=S68 + ' Fyller luckan mellan två redan daterade delar.')
add(id='godbyvagen-strandnas-curve', group='strandnas', name='Godbyvägen · båge till Rökerirondellen', routeId='road:Godbyvägen', kind='section',
    members=['way/43448260', 'way/1033525982'], display=['way/43448260', 'way/1033525982'], first=1978,
    observations=obs(ABS, (P, 'full', 'Rödtryckt diagonal anslutning.'), (P, 'full', ''), (P, 'full', '')), count='display', basis=S78)
add(id='rokerirondellen', group='strandnas', name='Rökerirondellen', routeId='road:Rökerirondellen', kind='roundabout',
    members=['way/40096482', 'way/23103970', 'way/44108100', 'way/40096578', 'way/40096577', 'way/44108120', 'way/161453837', 'way/160422223', 'way/626556105', 'way/40096521', 'way/44108116', 'way/161453835'],
    display='all', first=1978, observations=obs(ABS, (P, 'full', 'Rödtryckt rondell.'), (P, 'full', 'Femvägsrondell med refuger.'), (P, 'full', '')),
    count='display', basis='Rondellen saknas 1968 och är rödtryckt i kompletteringen 1978. Daterad separat från sina tillfarter. Kartåret är inte invigningsår.')
for key, name, route, ways in [('godbyvagen-rokeri-approach', 'Godbyvägen · tillfart till Rökerirondellen', 'road:Godbyvägen', ['way/107295226', 'way/43378002']),
                               ('nya-godbyvagen-rokeri-approach', 'Nya Godbyvägen · tillfart till Rökerirondellen', 'road:Nya Godbyvägen', ['way/161453836', 'way/44108119']),
                               ('osterleden-rokeri-approach', 'Österleden · tillfart till Rökerirondellen', 'road:osterleden', ['way/43377918', 'way/86552381'])]:
    add(id=key, group='strandnas', name=name, routeId=route, kind='approach', members=ways, display='all', first=1978,
        observations=obs(ABS, (P, 'full', 'Rödtryckt anslutning.'), (P, 'full', 'Refug ritad.'), (P, 'full', '')), count='longest',
        basis='Rondellens tillfart med två körfält kring en refug. Anslutningen finns från 1978; refugen syns först 1985 men tillfarten ligger i samma läge. Räknas en gång.')
add(id='sjukhusvagen-rokeri-lane', group='strandnas', name='Sjukhusvägen · norra körfältet mot Rökerirondellen', routeId='road:Sjukhusvägen', kind='approach',
    members=['way/40385841'], display='all', first=1978, observations=obs(ABS, (P, 'full', 'Rödtryckt anslutning.'), (P, 'full', ''), (P, 'full', '')), count='parallel',
    basis='Separat körfält vid rondellens västra tillfart, parallellt med den redan daterade Sjukhusvägen. Räknas inte som ny väglängd.')

# --- 2. Nya Godbyvägen north ------------------------------------------------------------
add(id='nya-godbyvagen-junction-south', group='ngv-north', name='Nya Godbyvägen', routeId='road:Nya Godbyvägen', kind='section', members=['way/49360041'], display=['way/49360041'],
    first=1978, observations=obs(ABS, (P, 'full', 'Rödtryckt.'), (P, 'full', ''), (P, 'full', '')), count='display', basis=S78 + ' Den kanaliserade korsningen norr om delen är senare än 1995 och ingår inte.')
add(id='nya-godbyvagen-junction-north', group='ngv-north', name='Nya Godbyvägen', routeId='road:Nya Godbyvägen', kind='section', members=['way/175130453'], display=['way/175130453'],
    first=1978, observations=obs(ABS, (P, 'full', 'Rödtryckt.'), (P, 'full', ''), (P, 'full', '')), count='display', basis=S78 + ' Det parallella svängfältet (way 40103274) hör till den senare kanaliseringen och ingår inte.')
for key, ways in [('nya-godbyvagen-kasgrand-south', ['way/70750970', 'way/70750983']), ('nya-godbyvagen-kasgrand-north', ['way/70750977', 'way/70750978'])]:
    add(id=key, group='ngv-north', name='Nya Godbyvägen', routeId='road:Nya Godbyvägen', kind='carriageways', members=ways, display='all', first=1978,
        observations=obs(ABS, (P, 'full', 'Rödtryckt.'), (P, 'full', ''), (P, 'full', '')), count='longest', basis=S78 + ' Två körbanor vid en korsning; räknas en gång.')
add(id='nya-godbyvagen-kasberg', group='ngv-north', name='Nya Godbyvägen · vid Kasberg', routeId='road:Nya Godbyvägen', kind='partial-section',
    members=['way/70750975'], display=['way/70750975'],
    phases=[dict(**{'from': 1978, 'to': 1995}, geometry='substring:0:split', basis='1978 och 1985 följer vägen samma korridor endast fram till grenpunkten där den äldre bågen mot Godbyvägen tar av. Den nordligaste delen visas inte före 1995.'),
            dict(**{'from': 1995, 'to': None}, geometry='modern', basis='Från 1995 fortsätter vägen rakt norrut i hela den moderna sträckningen.')],
    states=[dict(state='open', **{'from': 1978, 'to': None})],
    observations=obs(ABS, (P, 'partial', 'Rödtryckt; den norra delen avviker mot öster.'), (P, 'partial', 'Bågen mot Godbyvägen tar av vid grenpunkten.'), (P, 'full', 'Rak genomfart.')),
    count='display', basis=S78 + ' Täckningen är partiell 1978 och 1985.')
add(id='nya-godbyvagen-old-godbyvagen-link', group='ngv-north', name='Nya Godbyvägen · äldre båge mot Godbyvägen', routeId='road:Nya Godbyvägen', kind='abandoned-section',
    members=[], display=[],
    phases=[dict(**{'from': 1985, 'to': 1995}, geometry='reconstructed:C', basis='Nya Godbyvägens norra ände svängde 1985 i en båge in i Godbyvägen. Linjen är avritad ur 1985 års karta.')],
    states=[dict(state='open', **{'from': 1985, 'to': 1995}), dict(state='abandoned', **{'from': 1995, 'to': None})],
    observations=obs(ABS, (U, 'unknown', 'Kompletteringen 1978 visar en anslutning till Godbyvägen längre norrut i ett annat läge. Den används inte som geometri.'), (P, 'full', 'Båge in i Godbyvägen.'), (A_, 'unknown', 'Ersatt av den raka norra fortsättningen.')),
    count='reconstructed', basis='Försvunnen sträckning mellan 1985 och 1995. 1995 är första utgåva utan bågen, inte rivningsår. Den smala förbindelse som 1995 leder till Godbyvägen är i dag gång- och cykelväg och ingår inte.')
for key, ways in [('nya-godbyvagen-michaels-south', ['way/645414165', 'way/645414164']), ('nya-godbyvagen-michaels-north', ['way/645414162', 'way/35304990'])]:
    add(id=key, group='ngv-north', name='Nya Godbyvägen', routeId='road:Nya Godbyvägen', kind='carriageways', members=ways, display='all', first=1995,
        observations=obs(ABS, ABS, (A_, 'unknown', 'Bågen mot Godbyvägen används i stället.'), (P, 'full', 'Rak genomfart; ingen rondell.')), count='longest',
        basis=S95 + ' Körbanorna kring den senare lilla rondellen räknas en gång; själva rondellen (way 40103437) är senare än 1995 och ingår inte.')
add(id='nya-godbyvagen-north-continuation', group='ngv-north', name='Nya Godbyvägen · norra fortsättningen', routeId='road:Nya Godbyvägen', kind='section',
    members=['way/645414161', 'way/515072596'], display=['way/645414161', 'way/515072596'], first=1995,
    observations=obs(ABS, ABS, (A_, 'unknown', 'Endast tomtgränser och stigar.'), (P, 'full', 'Rak genomfart.')), count='display', basis=S95)

# --- 3. Åsvägen and northern Ålandsvägen --------------------------------------------------
add(id='asvagen-north', group='asvagen', name='Åsvägen', routeId='road:Åsvägen', kind='section', members=['way/61240337', 'way/117232838'], display=['way/61240337', 'way/117232838'],
    first=1985, observations=obs((A_, 'unknown', 'Endast höjdkurvor och tomtgränser.'), (A_, 'unknown', 'Som 1968.'), (P, 'full', 'Gata öster om huvudvägen.'), (P, 'full', '')), count='display',
    basis=S85 + ' Huvudvägens parallella gång- och cykelstråk är inte Åsvägen.')
add(id='asvagen-south', group='asvagen', name='Åsvägen', routeId='road:Åsvägen', kind='section', members=['way/54446888'], display=['way/54446888'],
    first=1985, observations=obs((A_, 'unknown', 'Endast en kort gårdsväg i kvarteret.'), (A_, 'unknown', 'Som 1968.'), (P, 'full', 'Gata längs husraden.'), (P, 'full', '')), count='display',
    basis=S85 + ' Den korta gårdsvägen 1968 ligger inte i samma läge och används inte för att bakdatera gatan.')
add(id='alandsvagen-north', group='alandsvagen', name='Ålandsvägen · norra delen', routeId='road:Ålandsvägen', kind='section', members=['way/536065733', 'way/161722653'], display=['way/536065733', 'way/161722653'],
    first=1968, observations=ALL68('Dubbellinjerad gata från rondellen till kvarteret i norr.'), count='display',
    basis=S68 + ' Den parallella gatan öster om delen syns först 1995 och ingår inte.')
add(id='alandsvagen-roundabout-approach', group='alandsvagen', name='Ålandsvägen · tillfart till rondellen', routeId='road:Ålandsvägen', kind='approach', members=['way/43519495', 'way/43519496'], display='all',
    first=1968, observations=ALL68('Anslutning till den redan daterade rondellen.'), count='longest', basis=S68 + ' Två körfält kring en refug räknas en gång.')

# --- Additional sections -------------------------------------------------------------------
add(id='norra-mockelovagen', group='west', name='Norra Möckelövägen', routeId='road:Norra Möckelövägen', kind='section', members=['way/35072932', 'way/35072925'], display=['way/35072932', 'way/35072925'],
    first=1968, observations=obs((P, 'full', 'Huvudväg "t. flygstationen" längs kartbladets ram.'), (P, 'full', 'Som 1968.'), (P, 'full', 'Vägsymbolen skärs av ramlinjen i väster men hela längden syns.'), (P, 'full', '')),
    count='display', basis=S68 + ' Vägen ligger vid bladets västra ram. Den västliga Flygfältsvägen och norra Möckelövägen ligger utanför bladen 1968–1985 och ingår inte.')
add(id='hammarlandsvagen-east', group='west', name='Hammarlandsvägen', routeId='road:Hammarlandsvägen', kind='section',
    members=['way/1077608821', 'way/34667564', 'way/1077608714', 'way/35402486'], display=['way/1077608821', 'way/34667564', 'way/1077608714', 'way/35402486'],
    first=1968, observations=ALL68('Huvudväg över vattnet.'), count='display', basis=S68)
add(id='vastra-utfarten-north', group='west', name='Västra Utfarten', routeId='road:Västra Utfarten', kind='section',
    members=['way/345140944', 'way/935167644', 'way/43518791'], display=['way/345140944', 'way/935167644', 'way/43518791'],
    first=1968, observations=ALL68('Huvudväg norrut mot Hammarlandsvägen.'), count='display',
    basis=S68 + ' Den andra körbanan (way 43378155) är senare tillfartsutformning och ingår inte.')
add(id='vastra-rondellen', group='west', name='Västra rondellen', routeId='road:Västra rondellen', kind='roundabout',
    members=['way/44108099', 'way/44108109', 'way/345139188', 'way/345139186', 'way/44108108', 'way/44108098'], display='all', first=1995,
    observations=obs((A_, 'unknown', 'Y-korsning med refug.'), (A_, 'unknown', 'Som 1968.'), (A_, 'unknown', 'Som 1968.'), (P, 'full', 'Rondell.')), count='display',
    basis='Rondellen ersätter den äldre Y-korsningen och syns först 1995. Den äldre korsningens geometri är inte rekonstruerad.')
add(id='hammarlandsvagen-rondell-approach', group='west', name='Hammarlandsvägen · tillfart till Västra rondellen', routeId='road:Hammarlandsvägen', kind='approach',
    members=['way/35402484', 'way/34667559', 'way/40095250'], display='all', first=1995,
    observations=obs((A_, 'unknown', 'Y-korsningens gren i annat läge.'), (A_, 'unknown', ''), (A_, 'unknown', ''), (P, 'full', '')), count='stem-plus-longest',
    basis='Tillfartens refugkörfält hör till rondellen 1995. Räknas en gång.')
add(id='sjukhusvagen-vastra-lane', group='west', name='Sjukhusvägen · körfält vid Västra rondellen', routeId='road:Sjukhusvägen', kind='approach',
    members=['way/43518792'], display='all', first=1995, observations=obs(ABS, ABS, ABS, (P, 'full', '')), count='parallel',
    basis='Separat körfält parallellt med den redan daterade Sjukhusvägen. Räknas inte som ny väglängd.')
add(id='knappelstensvagen', group='central', name='Knappelstensvägen', routeId='road:Knappelstensvägen', kind='section',
    members=['way/119232832', 'way/1298840608', 'way/1298840555'], display=['way/119232832', 'way/1298840608', 'way/1298840555'],
    first=1985, observations=obs((A_, 'unknown', 'Fält och skog.'), (A_, 'unknown', 'Fält; motellet.'), (P, 'full', 'Ny bostadsgata.'), (P, 'full', '')), count='display', basis=S85)
add(id='bastuvagen', group='central', name='Bastuvägen', routeId='road:Bastuvägen', kind='section', members=['way/50540399'], display=['way/50540399'],
    first=1985, observations=obs((A_, 'unknown', 'Fält.'), (A_, 'unknown', 'Fält; motellet.'), (P, 'full', 'Slinga i bostadsområdet.'), (P, 'full', '')), count='display', basis=S85)
for key, name, ways in [('doktorsvagen', 'Doktorsvägen', ['way/1097429115', 'way/61240338', 'way/345656232']),
                        ('vedhuggsvagen-west', 'Vedhuggsvägen', ['way/964530567', 'way/50540394']),
                        ('vedhuggsvagen-east', 'Vedhuggsvägen', ['way/61240347']),
                        ('klintvagen-north', 'Klintvägen', ['way/61240341']),
                        ('grindmattesvagen', 'Grindmattesvägen', ['way/44108123', 'way/345679408'])]:
    add(id=key, group='southwest', name=name, routeId='road:' + name, kind='section', members=ways, display=ways, first=1968,
        observations=ALL68('Dubbellinjerad gata.'), count='display', basis=S68)
add(id='godbyvagen-dual-north-of-158304921', group='godbyvagen', name='Godbyvägen', routeId='road:Godbyvägen', kind='carriageways',
    members=['way/612701762', 'way/612701725', 'way/612701730', 'way/612701732', 'way/612701734', 'way/612701727', 'way/612701724'],
    display=['way/612701762', 'way/612701725', 'way/612701730', 'way/612701732'], first=1968, observations=ALL68('Enkel huvudväg.'), count='display',
    basis=S68 + ' Två nära parallella senare körbanor delar en vägidentitet och en visningslinje. Fyller luckan mellan två redan daterade delar.')
add(id='godbyvagen-south-of-bolstavagen', group='godbyvagen', name='Godbyvägen', routeId='road:Godbyvägen', kind='section', members=['way/165914527', 'way/930505692'], display=['way/165914527', 'way/930505692'],
    first=1968, observations=ALL68('Enkel huvudväg.'), count='display', basis=S68 + ' Den senare lilla rondellen vid Bolstavägen (efter 1995) och dess körfält ingår inte.')


def stage_links(way):
    f = modern[way]; out = []
    for s in stages:
        for sf in s['features']:
            if sf['kind'] == 'street' and sf['paths'] == f['paths']:
                key = (s['id'], sf['id'])
                assert key not in occupied, (way, key)
                out.append(dict(datasetId=s['id'], featureId=sf['id'], inputHash=digest(sf), modernFeatureId=way))
    return out


out = []
for d in D:
    rec = dict(id='road:mariehamn:major-followup:' + d['id'], name=d['name'], routeId=d['routeId'], group=d['group'], kind=d['kind'])
    rec['members'] = [dict(feature=modern[w], inputHash=digest(modern[w])) for w in d['members']]
    rec['display'] = d['members'] if d['display'] == 'all' else d['display']
    rec['modernLinks'] = [l for w in d['members'] for l in stage_links(w)]
    rec['originals'] = [dict(year=y, datasetId=f'city-{y}', feature=by_osm[y][w], inputHash=digest(by_osm[y][w])) for w in d['members'] for y in [2014, 2021, 2025] if w in by_osm[y]]
    rec['unobservedOriginals'] = [dict(modernFeatureId=w, years=[y for y in [2014, 2021, 2025] if w not in by_osm[y]]) for w in d['members'] if any(w not in by_osm[y] for y in [2014, 2021, 2025])]
    first = d.get('first') or d['phases'][0]['from']
    rec['firstYear'] = first
    rec['states'] = d.get('states') or [dict(state='open', **{'from': first, 'to': None})]
    phases = d.get('phases') or [dict(**{'from': first, 'to': None}, geometry='modern', basis=d['basis'])]
    for ph in phases:
        g = ph['geometry']
        if g.startswith('reconstructed:'):
            k = g.split(':')[1]; ph['paths'] = RECON[k]['paths']; ph['anchors'] = RECON[k]['anchors']; ph['trace'] = TRACES[k]
        elif g.startswith('substring:'):
            line = LineString(modern[d['members'][0]]['paths'][0]); t = line.project(Point(*split), normalized=True)
            ph['range'] = [0, round(t, 6)]; ph['paths'] = [[list(map(lambda v: round(v, 7), c)) for c in substring(line, 0, ph['range'][1], normalized=True).coords]]
    rec['phases'] = phases
    rec['observations'] = d['observations']
    rec['countRule'] = d['count']; rec['basis'] = d['basis']
    # Lengths in EPSG:3874, as in the first pass.
    disp = [m(modern[w]['paths'][0]) for w in rec['display']]
    if d['count'] == 'display':
        L = sum(g.length for g in disp)
    elif d['count'] == 'longest':
        L = max(g.length for g in disp)
    elif d['count'] == 'stem-plus-longest':
        L = disp[0].length + max(g.length for g in disp[1:])
    elif d['count'] == 'parallel':
        L = 0
    else:
        L = m(phases[0]['paths'][0]).length
    rec['lengthMeters'] = round(L, 2)
    out.append(rec)

sheets = batch1['sheets']
crops = sorted(p.name for p in HERE.glob('*.png'))
review = dict(schemaVersion=1, reviewedAt='2026-11-11',
              source=dict(id='review:mariehamn-major-road-followups', title='Mariehamns större vägar · uppföljning av korsningar och fler gator 1968–1995', url='assets/mariehamn-major-road-followups.json'),
              method='Manuell visuell jämförelse av originalkartornas utsnitt för 1968, 1978, 1985 och 1995 med moderna mittlinjer. Överläggen är hjälpmedel, inte belägg. Försvunna sträckningar är avritade ur originalskanningarna mellan moderna knutpunkter; de råa avritningspunkterna sparas som källgeometri. Kartår är första granskade belägg, inte byggår.',
              sheets=sheets, decisions=out,
              deferred=[
                  dict(name='Lemlandsvägen vid Strandnäs 1968–1984', basis='Lemlandsvägens befintliga landsbygdsenhet börjar 1985. Den raka korsningen 1968 möter därför en 40 m lucka mot öster tills den enheten delas och bakdateras i sin egen granskning.'),
                  dict(name='Rak väg söder om den gamla Strandnäskorsningen 1968', basis='Vägen söderut mot Strandnäs 1968 motsvarar delvis senare Österleden och stigar; den behöver en egen granskning.'),
                  dict(name='Äldre Y-korsning vid Västra rondellen', basis='Korsningen 1968–1985 är inte rekonstruerad; Hammarlandsvägen, Sjukhusvägen och Västra Utfarten möts med en lucka före 1995.'),
                  dict(name='Kanaliserade korsningar efter 1995', basis='Nya Godbyvägen/Bolstavägen, Godbyvägen/Bolstavägen och den lilla rondellen vid Michaelsvägen syns inte 1995. Genomfarten över korsningarna visas därför inte före de moderna källorna.'),
                  dict(name='Vedhuggsvägens mittdel', basis='Den diagonala gatan är sammanhängande 1968–1995, men 53 m i mitten är i dag gång- och cykelväg (way 50540398). Delen väntar på samma tillståndsmodell som förbindelsen vid Nya Godbyvägen.'),
                  dict(name='Förbindelsen Nya Godbyvägen–Godbyvägen 1995', basis='Vägen som 1995 förbinder vägarna är i dag gång- och cykelväg (way 162459763). En tillståndsändring från bilväg till gångväg behöver en egen modell.'),
                  dict(name='Flygfältsvägen, norra Möckelövägen, västra Hammarlandsvägen', basis='Ligger väster om bladens ram 1968–1985 och kan inte dateras med denna serie.'),
                  dict(name='Uppgårdsvägen, Vikingagränd, Lövdalsvägen, Blomstringevägen, Örnvägen, Falkvägen', basis='Saknas som gator 1985 och/eller är oklara 1995; ingen datering i denna serie.'),
                  dict(name='Klintvägens södra böj och Västra Utfartens andra körbana', basis='Ligger inte i samma läge på alla utgåvor och lämnas odaterade.'),
              ],
              crops=crops)
new = round(sum(d['lengthMeters'] for d in out), 2)
review['totals'] = dict(newPersistentMeters=new, confirmedExistingMeters=0, reviewedMeters=new,
                        byGroup={g: round(sum(d['lengthMeters'] for d in out if d['group'] == g), 2) for g in dict.fromkeys(d['group'] for d in out)})
Path('data/mariehamn-major-road-followups.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(len(out), new, review['totals']['byGroup'])
for d in out:
    print(d['id'].split(':')[-1], d['firstYear'], d['lengthMeters'], len(d['members']), len(d['modernLinks']), len(d['originals']))
