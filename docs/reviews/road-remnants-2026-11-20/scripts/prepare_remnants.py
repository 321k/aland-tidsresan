"""Write data/road-remnants.json: register road remnants on dated roads. Usage: prepare_remnants.py CATALOGUE.json.gz
(the build without the remnant step). Each match was checked on the parish maps (renders/*.jpg, remnant_window.py)."""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from shapely.geometry import LineString
from road_remnants import _outline

cat = json.load(gzip.open(sys.argv[1])); O = {o['id']: o for o in cat['objects']}; G = {g['id']: g for g in cat['geometries']}
outlines = {f['properties']['code']: f for f in json.load(open('dist/assets/heritage-boundaries.geojson'))['features']}
# code, object, year whose dated geometry the remnant is compared with, note (what the parish maps show)
MATCHES = [
    ('Lu 6.1', 'road:lumparland:gamla-landsvagen:skag', 1950,
     'Fornlämningsregistret: ett cirka 120 m långt fossilt vägavsnitt, del av landsvägen mellan Jomala och Föglö. Det är hörnet i Skag by på den gamla vägen som sockenkartan 1929 ritar; spåret följer det.'),
    ('Lu 2.1', 'road:qgis:lumparland:langnasvagen-100km3', 1920,
     'Fornlämningsregistret: två korta fossila vägavsnitt (cirka 20 och 35 m), del av landsvägen mellan Jomala och Föglö, omkring 10 m norr om dagens väg vid 1,45 km. Sockenkartan 1929 ritar vägen där; samma väg inom kartans lägesfel.'),
    ('Le 16.16', 'road:qgis:lumparland:lemlandsvagen-100km3', 1920,
     'Fornlämningsregistret: fossilt vägavsnitt från 1700-talets landsväg, omkring 30 m söder om dagens väg vid 3,4 km öster om kyrkbyn. Sockenkartan 1929 ritar vägen mellan dem; samma vägstråk, den gamla vägbanken låg något söder om dagens.'),
    ('Le 18.7', 'road:lemland:gamla-lemlandsvagen:mangard-soderby', 1920,
     'Fornlämningsregistret: ett cirka 60 m långt fossilt vägavsnitt, del av landsvägen mellan Jomala och Föglö. Det ligger på den gamla vägen genom Söderby som sockenkartan 1929 ritar.'),
    ('Ha 12.5', 'road:rural:hammarland-hammarlandsvagen-kattby-west', 1950,
     'Fornlämningsregistret: ett cirka 40 m långt vägavsnitt av den tidigmoderna postvägen, omkring 20 m söder om vägen väster om Kattby; samma vägstråk.'),
    ('Jo 23.6', 'road:emkarbyvagen', 1850,
     'Fornlämningsregistret: ett cirka 100 m långt fossilt vägavsnitt av den tidigmoderna postvägen vid Ringsböle (delvis undersökt arkeologiskt 2016), intill Emkarbyvägen.'),
    ('Jo 23.7', 'road:emkarbyvagen', 2026,
     'Fornlämningsregistret: ett cirka 70 m långt fossilt vägavsnitt av den tidigmoderna postvägen vid Ringsböle, intill Emkarbyvägen.'),
    ('Sa 10.14', 'road:qgis:saltvik:sundsvagen-haraldsby-kulla', 1850,
     'Fornlämningsregistret: ett 80 m långt fossilt vägavsnitt av den tidigmoderna postvägen vid Haraldsby, intill Sundsvägen.'),
    ('Su 13.16', 'road:qgis:saltvik:sundsvagen-haraldsby-kulla', 1850,
     'Fornlämningsregistret: ett 80 m långt fossilt vägavsnitt av den tidigmoderna postvägen vid Kulla, en 6–7 m bred jordvall intill Sundsvägen.'),
    ('Su 1.5', 'road:qgis:saltvik:sundsvagen-haraldsby-kulla', 1850,
     'Fornlämningsregistret: ett 80 m långt fossilt vägavsnitt av den tidigmoderna postvägen vid Berg, en 6–10 m bred jordvall intill Sundsvägen.'),
]
out = []
for code, oid, year, note in MATCHES:
    o = O[oid]; poly = _outline(outlines[code])
    lines = [LineString([TO_METRIC(*q) for q in p]) for gp in o['geometryPeriods'] if gp['from'] <= year < (gp['to'] or 9999)
             for p in G[gp['geometryId']]['paths'] if len(p) > 1]
    d = min(l.distance(poly) for l in lines); inside = sum(l.intersection(poly.buffer(5)).length for l in lines)
    sup = ['geometry', 'identity'] if inside >= 40 else ['identity']
    print(code, oid[-40:], year, 'distance', round(d, 1), 'inside', round(inside), sup)
    out.append(dict(code=code, sourceId='heritage-register:' + code, objectId=oid, inputHash=fingerprint(o), outlineHash=digest(outlines[code]['geometry']['coordinates']),
                    year=year, distanceMeters=round(d, 1), maxDistanceMeters=round(d, 1) + 5, supports=sup,
                    **({'minInsideMeters': round(inside * 0.9)} if sup[0] == 'geometry' else {}), note=note))
data = dict(schemaVersion=1, reviewedAt='2026-11-20',
            source=dict(id='review:road-remnants', title='Vägrester i fornlämningsregistret · granskning', url='assets/road-remnants.json'),
            remnants=out,
            notMatched={'Ha 17.8': 'Postad: används av data/hammarlandsvagen-postad.json för den gamla bågen.',
                        'Fi 8.17': 'Gamla färjvägen vid Godby, i bruk till 1761; ingen väg i katalogen för den.',
                        'Jo 18.11': 'Vägen till Kungsöbatteriet, anlagd 1916; inte en del av de granskade huvudvägarna.',
                        'Ma 33': 'Väg i Mariehamn belagd 1764; inte granskad här.', 'Ma 37': 'Väg från första världskriget; inte granskad här.',
                        'Ma 47': 'Väg från första världskriget; inte granskad här.'},
            method='Registrets avgränsningar jämförda med sockenkartorna 1929 och katalogens daterade vägar (docs/reviews/road-remnants-2026-11-20/renders/).')
json.dump(data, open('data/road-remnants.json', 'w'), ensure_ascii=False, indent=1)
