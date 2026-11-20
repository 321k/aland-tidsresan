"""Write data/hammarlandsvagen-postad.json: the old curve at Postad (Hammarland) as an early period of 'Äldre väg vid
Korsberg'. Usage: prepare_postad.py CATALOGUE.json.gz  (a build with data/hammarlandsvagen-main-road.json already cutting
the curve's span out of Postad–Korsängen, and without the Postad step).

The curve (renders/ha-17-8-1929.jpg, ha-17-8-1944.jpg): Korsberg's own vertices while they lie within 12 m of the
centre line of the register outline Ha 17.8, then that centre line to its south-east end, then today's road where the
main-road review's 1929 stretch resumes. The register outline is surveyed; the parish maps place the road within it."""
import sys, json, gzip, itertools
sys.path.insert(0, 'scripts')
import numpy as np
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point, Polygon

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
K_ID, M_ID = 'road:rural:hammarland-korsberg-old-road', 'road:rural:hammarland-hammarlandsvagen-postad-korsangen'
k = O[K_ID]; kg = G[k['geometryPeriods'][0]['geometryId']]; kp = kg['paths'][0]
m = O[M_ID]; m29 = [p for p in G[m['geometryPeriods'][0]['geometryId']]['paths']]
assert m['geometryPeriods'][0]['from'] == 1929 and len(m29) == 2, 'run with the main-road review already cutting the curve'
rem = next(f for f in json.load(open('dist/assets/heritage-boundaries.geojson'))['features'] if f['properties']['code'] == 'Ha 17.8')
poly = Polygon([TO_METRIC(*q) for q in rem['geometry']['coordinates'][0]])
ex = list(poly.exterior.coords)[:-1]
i, j = max(itertools.combinations(range(len(ex)), 2), key=lambda t: Point(ex[t[0]]).distance(Point(ex[t[1]])))
A, B = LineString(ex[i:j + 1]), LineString((ex[j:] + ex[:i + 1])[::-1])
C = LineString([((A.interpolate(t, normalized=True).x + B.interpolate(t, normalized=True).x) / 2, (A.interpolate(t, normalized=True).y + B.interpolate(t, normalized=True).y) / 2)
                for t in np.linspace(0, 1, 25)])
start = Point(TO_METRIC(*kp[0]))
if C.project(start) > C.length / 2: C = LineString(C.coords[::-1])          # from the Korsberg (north-west) end
keep = 0
while keep < len(kp) and C.distance(Point(TO_METRIC(*kp[keep]))) <= 12: keep += 1
assert keep >= 2 and kp[0] == m29[0][-1] or Point(TO_METRIC(*kp[0])).distance(Point(TO_METRIC(*m29[0][-1]))) < 1, 'Korsberg starts where the 1929 stretch ends'
last = C.project(Point(TO_METRIC(*kp[keep - 1])))
end = m29[1][0]                                                              # where the 1929 stretch resumes
geo = lambda q: [round(v, 7) for v in TO_GEO(*q)]
tail = [geo(q) for q in C.coords if last + 10 < C.project(Point(q)) < C.length - 5]
path = kp[:keep] + tail + [end]
L = LineString([TO_METRIC(*q) for q in path])
inside = L.intersection(poly.buffer(10)).length
print('keep', keep, 'of', len(kp), 'Korsberg vertices; curve', round(L.length, 1), 'm,', round(inside), 'm inside the outline')
H1929, H1944 = 'nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08', 'nls:9c72a692-bae4-473d-93bb-7bcdee1222e7'
REG = 'heritage-register:Ha 17.8'
h = next(f for f in json.load(open('dist/assets/heritage.json'))['features'] if f['code'] == 'Ha 17.8')
data = dict(
    schemaVersion=1, reviewedAt='2026-11-20',
    source=dict(id='review:hammarlandsvagen-postad', title='Gamla landsvägen vid Postad · granskning', url='assets/hammarlandsvagen-postad.json'),
    sources=[dict(id=REG, title='Ålands landskapsregering · fornlämningsregistret · Ha 17.8 Väglämning – Postad', url=h['sourceUrl'], issuedAt='2026')],
    maps={'1929': dict(sourceId=H1929, year=1929), '1944': dict(sourceId=H1944, year=1944)},
    objectId=K_ID, inputHash=fingerprint(k), geometryHash=digest(kg), connection=M_ID, connectionHash=fingerprint(m),
    outcomes={'1929': 'present', '1944': 'present'}, firstYear=1929, until=k['states'][0]['from'], survivingVertices=keep,
    path=path, lengthMeters=round(L.length, 1),
    remnant=dict(code='Ha 17.8', sourceId=REG, outlineHash=digest(rem['geometry']['coordinates']), minInsideMeters=round(inside * 0.95),
                 describes={'from': 2026, 'to': 2027},
                 note='Fornlämningsregistret: ett cirka 450 m långt vägavsnitt i NV–SO-riktning, del av den tidigmoderna postvägen genom Åland, varaktigt övergivet i NV. Registrets avgränsning följer bågen som sockenkartorna 1929 och 1944 ritar.'),
    basis='Den gamla landsvägen vid Postad gick i en båge upp till 70 m öster om dagens raka linje. Sockenkartan 1929 och utgåvan 1944 ritar den som landsvägen; fornlämningsregistret har den som en del av den tidigmoderna postvägen (Ha 17.8). Den raka linjen ritas första gången på grundkartan 1968; därefter finns bara bågens nordvästra del kvar, som Äldre väg vid Korsberg.',
    traceBasis='Vägens egna koordinater där den finns kvar (Äldre väg vid Korsberg), och därefter mittlinjen av fornlämningsregistrets avgränsning (inmätt), fram till dagens väg där 1929 års sträcka fortsätter.',
    method='Fornlämningsregistrets avgränsning jämförd med sockenkartan 1012 06 Hammarby 1929, dess utgåva 1944 och katalogens vägar (docs/reviews/road-remnants-2026-11-20/renders/ha-17-8-*).')
json.dump(data, open('data/hammarlandsvagen-postad.json', 'w'), ensure_ascii=False, indent=1)
