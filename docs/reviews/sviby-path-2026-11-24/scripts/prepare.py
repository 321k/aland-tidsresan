"""Write data/sviby-paths.json. Usage: prepare.py CATALOGUE_BEFORE.json.gz

Read on renders/photos-all.jpg, photos-plain-zoom*.jpg (the east–west road, 1942–2021) and norra-delen-photos.jpg (the
north piece of Norra Möckelövägen, 1952–2021), aerial tiles from Mariehamn's IMS service at 1 m/px."""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from copy import deepcopy
from mariehamn_frame_1942 import fingerprint, TO_METRIC
from shapely.geometry import LineString
from sviby_paths import apply_sviby_paths, REVIEW, MODERN

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
M = {f['id']: f for f in json.load(gzip.open(MODERN))['features']}
EW, NP = 'road:jomala:sviby:vagen-mot-svibyvagen', 'road:jomala:norra-mockelovagen:norra-delen'
L = lambda p: LineString([TO_METRIC(*q) for q in p]).length
WEST = ['way/1193557303', 'way/1108057940', 'way/1108057939', 'way/1180462200']
ew_path = G[O[EW]['geometryPeriods'][0]['geometryId']]['paths'][0]
f = round(sum(L(M[w]['paths'][0]) for w in WEST) / L(ew_path), 4)
print('east–west road', round(L(ew_path), 1), 'm; cycleway part', round(f * L(ew_path), 1), 'm =', f)
R = 'review:sviby-paths'
SRC = [dict(id=f'{R}:osm-{y}', title=f'OpenStreetMap · utdrag {y} · vägarna vid Sviby', url='https://www.openstreetmap.org/way/35304978/history', issuedAt=str(y)) for y in (2014, 2021, 2025)]
def snap(oid, y, note, rng=None):
    return dict(id=f'{oid}:osm-{y}', sourceId=f'{R}:osm-{y}', describes={'from': y, 'to': y + 1}, observationType='snapshot', supports=['state'], reviewId=R,
                coverage='partial' if rng else 'full', canonicalRange=rng or [0, 1], note=note)
def photo(oid, y, date, outcome, note):
    return dict(id=f'{oid}:photo-{y}', sourceId=f'mariehamn-aerial-{y}', describes={'from': y, 'to': y + 1}, observationType='aerial', observedAt=date,
                imageCoverage='visible', outcome=outcome, interpretation=True, supports=['state'], reviewId=R, note=note)
EVEN = 'En jämn grusväg i samma bredd i hela längden, från Norra Svibyvägen till Svibyvägen. När den västra delen stängdes för biltrafik syns inte på fotona.'
ew_ev = [snap(EW, 2014, 'Hela vägen är en väg (35304978) av klassen residential, en vanlig väg.'),
         snap(EW, 2021, 'Hela vägen är fortfarande en väg (35304978) av klassen residential.'),
         snap(EW, 2025, f'De västra {round(f * L(ew_path))} metrarna, från Norra Svibyvägen, är nu fyra vägar av klassen cycleway, en gång- och cykelväg; resten fram till Svibyvägen är residential.', [0, f]),
         photo(EW, 2007, '2007-06-04', 'present', EVEN), photo(EW, 2015, '2015-05-20', 'present', EVEN), photo(EW, 2021, '2021-06-06', 'present', EVEN)]
np_ev = [photo(NP, 1999, '1999-06-10', 'present', 'En grusväg i full bredd från korsningen vid Norra Svibyvägen söderut, som på flygfotona 1952–1991.'),
         photo(NP, 2007, '2007-06-04', 'different-structure', 'Norra Svibyvägen svänger nu åt sydväst i en ny kurva; den gamla vägen söderut från korsningen är en smal stig.'),
         snap(NP, 2014, 'Vägen är en gångväg (footway); 2025 en gång- och cykelväg (cycleway).')]
maps = [e['id'] for e in O[NP]['evidence'] if e['outcome'] == 'present']
review = dict(
    schemaVersion=1, reviewedAt='2026-11-24',
    source=dict(id=R, title='Vägarna vid Sviby som blivit gång- och cykelvägar · granskning', url='assets/sviby-paths.json'), sources=SRC,
    method='OpenStreetMap-utdragen 2014, 2021, 2025 och 2026 och Mariehamns flygfoton 1942–2021 (1 m per pixel) jämförda för ögat.',
    targets=[
        dict(objectId=EW, inputHash=fingerprint(O[EW]), evidence=ew_ev, roadClassPeriods=[dict(
            **{'from': 2025, 'to': None}, **{'class': 'cycleway'}, canonicalRange=[0, f], rangeWays=WEST, evidenceIds=[f'{EW}:osm-2025'],
            basis=f'Den västra delen, {round(f * L(ew_path))} m från Norra Svibyvägen, är en gång- och cykelväg i OpenStreetMap från utdraget 2025; 2014 och 2021 var hela vägen en vanlig väg. Flygfotona 2007–2021 visar samma grusväg i hela längden, så när den stängdes för biltrafik är inte känt; 2025 är första belägg.')]),
        dict(objectId=NP, inputHash=fingerprint(O[NP]), evidence=np_ev, roadClassPeriods=[dict(
            **{'from': 1929, 'to': 2007}, **{'class': 'residential'}, evidenceIds=maps + [f'{NP}:photo-1999'],
            basis='En väg på kartorna 1929–1995 och flygfotona 1952–1999. Flygfotot 2007 visar den som en smal stig, sedan Norra Svibyvägen fått en ny kurva åt sydväst; i OpenStreetMap är den en gångväg från utdraget 2014 och en gång- och cykelväg 2025. Från 2007 visas den som gång- och cykelväg.')])])
json.dump(review, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
trial = deepcopy(cat)
apply_sviby_paths(lambda p: review if p == REVIEW else (json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))), trial)
print('trial ok')
