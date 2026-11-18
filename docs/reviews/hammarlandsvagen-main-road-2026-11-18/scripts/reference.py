"""Today's Hammarlandsvägen as one reference line from Västra rondellen (Mariehamn) to Kattby (Hammarland), from the
catalogue objects named Hammarlandsvägen (latest geometry). Writes data/reference.json: the line (EPSG:3874 and WGS84)
and each object's range along it. The short dual-carriageway pieces at the Mariehamn end are listed but not merged.
Usage: reference.py CATALOGUE.json.gz OUT.json"""
import sys, json, gzip
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import TO_METRIC, TO_GEO
from shapely.geometry import LineString, Point
from shapely.ops import linemerge
c = json.load(gzip.open(sys.argv[1])); G = {g['id']: g for g in c['geometries']}
objs = [o for o in c['objects'] if o.get('kind') == 'roadSegment' and (o.get('name', '').startswith('Hammarlandsvägen') or 'hammarlandsvagen' in o['id'])]
parts = [(o['id'], LineString([TO_METRIC(*q) for q in p])) for o in objs for p in G[o['geometryPeriods'][-1]['geometryId']]['paths'] if len(p) > 1]
merged = linemerge([l for _, l in parts]); main = max(merged.geoms, key=lambda g: g.length)
if main.coords[0][0] < main.coords[-1][0]:      # east to west
    main = LineString(main.coords[::-1])
ranges = []
for oid, l in parts:
    if l.within(main.buffer(0.5)):
        a, b = sorted([main.project(Point(l.coords[0])), main.project(Point(l.coords[-1]))])
        ranges.append(dict(objectId=oid, range=[round(a, 1), round(b, 1)]))
    else:
        ranges.append(dict(objectId=oid, range=None, note='not on the merged main line (junction carriageway)'))
ranges.sort(key=lambda r: r['range'][0] if r['range'] else -1)
json.dump(dict(lengthMeters=round(main.length, 1), metric=[list(map(lambda v: round(v, 2), p)) for p in main.coords],
               wgs84=[list(map(lambda v: round(v, 7), TO_GEO(*p))) for p in main.coords], objects=ranges), open(sys.argv[2], 'w'), indent=0)
for r in ranges: print(r['objectId'], r['range'])
print(round(main.length))
