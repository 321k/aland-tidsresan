"""Modern OSM roads and catalogue road objects that lie along a 1929 trace (what of the old road survives today).
Usage: survivors.py TRACE.json [BUFFER_M]"""
import sys, json, gzip
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from trace import TO_M
from shapely.geometry import LineString
T = LineString(json.load(open(sys.argv[1]))['trace']); buf = float(sys.argv[2]) if len(sys.argv) > 2 else 30
B = T.buffer(buf)
mod = json.loads(gzip.decompress(open('dist/assets/modern.json.gz', 'rb').read()))['features']
for f in mod:
    if f['kind'] != 'road' or f.get('class') in ('footway', 'path', 'cycleway', 'steps', 'corridor'): continue
    for p in f['paths']:
        l = LineString([TO_M(*c) for c in p])
        if not l.intersects(B): continue
        inside = l.intersection(B).length
        if inside > 40 and inside / l.length > 0.3:
            a, b = T.project(l.interpolate(0)), T.project(l.interpolate(l.length))
            print('osm', f['id'], f.get('class'), repr(f.get('name')), round(l.length), 'in', round(inside), 'along', round(min(a, b)), round(max(a, b)))
c = json.loads(gzip.decompress(open('dist/assets/temporal-objects.json.gz', 'rb').read())); G = {g['id']: g for g in c['geometries']}
for o in c['objects']:
    if o['kind'] != 'roadSegment': continue
    for gp in o['geometryPeriods'][-1:]:
        for p in G[gp['geometryId']]['paths']:
            l = LineString([TO_M(*q) for q in p])
            if l.length and l.intersects(B):
                inside = l.intersection(B).length
                if inside > 40:
                    print('obj', o['id'], repr(o['name']), o['states'][0]['from'], round(l.length), 'in', round(inside), 'along', round(T.project(l.interpolate(0))), round(T.project(l.interpolate(l.length))))
