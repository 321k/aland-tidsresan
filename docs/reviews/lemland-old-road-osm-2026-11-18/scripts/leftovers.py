"""Unowned OSM road parts (2014, 2021, 2025, 2026) that still run along an old-road object's surviving line, i.e. that
would be drawn as a second road beside it. Usage: leftovers.py CATALOGUE.json.gz [BUFFER_M] [MIN_M]"""
import json, gzip, sys
sys.path.insert(0, 'scripts')
from lemland_old_road_osm import metric
from mariehamn_lemlandsvagen_split import sub_path
c = json.load(gzip.open(sys.argv[1])); buf = float(sys.argv[2]) if len(sys.argv) > 2 else 10; least = float(sys.argv[3]) if len(sys.argv) > 3 else 30
G = {g['id']: g for g in c['geometries']}; own = {}
for o in c['objects']:
    for l in o.get('sourceLinks', []): own.setdefault((l['datasetId'], l['featureId']), []).append(l.get('sourceVertexRange'))
for y in (2014, 2021, 2025, 2026):
    F = json.load(gzip.open(f'dist/assets/roads-{y}.json.gz' if y < 2026 else 'dist/assets/modern.json.gz'))['features']
    for o in c['objects']:
        if 'lemlandOldRoadOsm' not in o: continue
        surv = [metric(p) for p in G[o['geometryPeriods'][-1]['geometryId']]['paths']]
        B = surv[0].buffer(buf)
        for s in surv[1:]: B = B.union(s.buffer(buf))
        for f in F:
            if f.get('kind') not in (None, 'road') or f.get('class') in ('footway', 'path', 'cycleway', 'steps') or len(f['paths']) != 1: continue
            p = f['paths'][0]
            if not metric(p).intersects(B): continue
            rs = own.get((f'osm-{y}', f['id']), [])
            if None in rs: continue
            at, rem = 0, []
            for a, b in sorted(rs):
                if a > at: rem.append((at, a))
                at = max(at, b)
            if at < len(p) - 1: rem.append((at, len(p) - 1))
            for a, b in rem:
                if b - a < 1e-6: continue
                seg = metric(sub_path(p, a, b)); ins = seg.intersection(B).length
                if ins > least: print(y, o['id'], f['id'], f.get('name'), f.get('class'), round(ins), 'of', round(seg.length))
