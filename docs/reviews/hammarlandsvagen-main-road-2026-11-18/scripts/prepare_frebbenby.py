"""Write data/hammarlandsvagen-frebbenby.json: Marsundsvägen from Frebbenby to the old ferry pier (0–1 040 m along it) is
the old road to the Marsund ferry on the 1929 Eckerö parish map and its 1956 edition, and a road on the base maps 1968,
1978 and 1985 (renders/marsundsvagen-*.jpg, marsundsvagen-base-maps.jpg, frebbenby-grid-*.jpg). The object was dated
from 1994 by the QGIS review. The Marsund connection's own Frebbenby stretch (0–472 m) is in the Marsund review.
Usage: prepare_frebbenby.py CATALOGUE_BEFORE_THE_STEP.json.gz"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from shapely.geometry import LineString, Point

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
MV, M, K = 'road:qgis:eckero:marsundsvagen-100km4', 'road:marsund:eckero-hammarland', 'road:rural:hammarland-hammarlandsvagen-kattby-west'
PIER = 1040.0           # metres along Marsundsvägen: the ferry pier on the 1929 and 1956 maps
o = O[MV]; gid = o['geometryPeriods'][0]['geometryId']; g = G[gid]; line = LineString([TO_METRIC(*p) for p in g['paths'][0]])
# the gap at the junction: Marsundsvägen's start and the end of the connection's Frebbenby stretch (a 27 m OSM link, way 125420159)
cut = [LineString([TO_METRIC(*q) for q in p]) for p in G[O[M]['geometryPeriods'][0]['geometryId']]['paths']]
gap = min(Point(line.coords[0]).distance(Point(c.coords[i])) for c in cut for i in (0, -1))
print(MV, o['states'][0]['from'], round(line.length, 1), 'gap', round(gap, 1))
maps = {'1929-eckero': dict(sourceId='nls:map-39091228', year=1929), '1956-eckero': dict(sourceId='nls:map-37971493', year=1956),
        '1968': dict(sourceId='nls:101203:1968', year=1968), '1978': dict(sourceId='nls:101203:1978', year=1978), '1985': dict(sourceId='nls:101203:1985', year=1985)}
early = [dict(objectId=MV, inputHash=fingerprint(o), geometryId=gid, geometryHash=digest(g), lengthMeters=round(line.length, 2),
              ranges=[[0.0, PIER]], firstYear=1929, until=o['states'][0]['from'], maps={k: 'present' for k in maps})]
data = dict(
    schemaVersion=1, reviewedAt='2026-11-19',
    source=dict(id='review:hammarlandsvagen-frebbenby', title='Vägen till Marsundsfärjan · granskning', url='assets/hammarlandsvagen-frebbenby.json'),
    sources=[], maps=maps, geometryPrefix='geometry:hammarlandsvagen-frebbenby:',
    geometryNote='Del av objektets egen geometri (samma koordinater) där Marsundsvägen är den gamla vägen till färjan över Marsund på sockenkartan 1929.',
    method='Marsundsvägen jämförd med sockenkartan 1012 03 Eckerö 1929 och utgåvan 1956 (karttiler 2,4 m/px, rutnät 50 m), grundkartorna 1968, 1978 och 1985 (blad 101203) och OpenStreetMap 2026 (renders/marsundsvagen-*.jpg, frebbenby-grid-*.jpg).',
    early=early,
    earlyBasis={MV: 'Marsundsvägens första 1 040 m, från Frebbenby västerut och längs stranden till den gamla färjebryggan, är vägen till färjan över Marsund som sockenkartan 1929 och utgåvan 1956 ritar; de ritar också färjeleden över sundet vid bryggan. Kartorna ritar vägen inom omkring 15 m från dagens, och i kröken vid Marsund inom omkring 25 m. Grundkartan 1968 ritar den fortfarande som landsväg, och 1978 och 1985 som väg. Söder om bryggan är Marsundsvägen yngre och visas som tidigare.'},
    route=dict(order=[K, M, MV], endObjects=[K, M], joinMeters=2.0, gaps=[dict(between=[M, MV], meters=round(gap, 1))]))
json.dump(data, open('data/hammarlandsvagen-frebbenby.json', 'w'), ensure_ascii=False, indent=1)
