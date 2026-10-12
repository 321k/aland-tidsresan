"""Offline alternative to Overpass: extract Åland from Geofabrik Finland PBF.
Requires osmium and shapely. The administrative boundary defines coverage.
Usage: .venv-geo/bin/python scripts/import_osm_extract.py /path/to/finland.osm.pbf
"""
import gzip
import json
import sys
import tempfile
from pathlib import Path
import osmium
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
from build_modern import join_rings

pbf = sys.argv[1]
relations, boundary = [], None
for r in osmium.FileProcessor(pbf, osmium.osm.RELATION).with_filter(osmium.filter.KeyFilter('building', 'ISO3166-1')):
    tags = dict(r.tags)
    if tags.get('ISO3166-1') == 'AX' or (tags.get('building') and tags.get('type') == 'multipolygon'):
        obj = {'type': 'relation', 'id': r.id, 'tags': tags,
               'members': [{'type': 'way', 'ref': m.ref, 'role': m.role} for m in r.members if m.type == 'w']}
        if tags.get('ISO3166-1') == 'AX': boundary = obj
        else: relations.append(obj)
assert boundary, 'Åland boundary missing'
border_ids = {m['ref'] for m in boundary['members']}
member_ids = {m['ref'] for r in relations for m in r['members']}
ways, coasts, borders = {}, [], {}
print('Reading regional geometry…', flush=True)
with tempfile.TemporaryDirectory(prefix='aland-osm-') as tmp:
    processor = osmium.FileProcessor(pbf).with_locations('sparse_file_array,' + tmp + '/nodes').with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))
    snapshot = processor.header.get('osmosis_replication_timestamp')
    for w in processor:
        t = dict(w.tags)
        if not (w.id in border_ids or w.id in member_ids or 'building' in t or 'highway' in t or t.get('natural') == 'coastline'): continue
        if not all(n.location.valid() for n in w.nodes): continue
        if not any(19 < n.lon < 21.5 and 59.3 < n.lat < 60.85 for n in w.nodes): continue
        geometry = [{'lon': n.lon, 'lat': n.lat} for n in w.nodes]
        e = {'type': 'way', 'id': w.id, 'tags': t, 'geometry': geometry}
        if w.id in border_ids: borders[w.id] = e
        if t.get('natural') == 'coastline': coasts.append(e)
        if 'building' in t or 'highway' in t or w.id in member_ids: ways[w.id] = e
assert border_ids <= borders.keys(), 'Incomplete Åland boundary'
rings = join_rings([[(p['lon'], p['lat']) for p in borders[m['ref']]['geometry']] for m in boundary['members'] if m['role'] in ('outer', '')])
assert rings, 'Could not assemble boundary'
area = unary_union([Polygon(r) for r in rings])
assert area.contains(Point(19.941, 60.103)) and area.contains(Point(21.04, 60.41))
features = [e for e in ways.values() if ('building' in e['tags'] or 'highway' in e['tags']) and len(e['geometry']) >= 2 and area.intersects(LineString([(p['lon'],p['lat']) for p in e['geometry']]))]
for r in relations:
    if not all(m['ref'] in ways for m in r['members']): continue
    if not any(area.intersects(LineString([(p['lon'],p['lat']) for p in ways[m['ref']]['geometry']])) for m in r['members'] if len(ways[m['ref']]['geometry']) > 1): continue
    for m in r['members']: m['geometry'] = ways[m['ref']]['geometry']
    features.append(r)
for n in osmium.FileProcessor(pbf, osmium.osm.NODE).with_filter(osmium.filter.KeyFilter('place')):
    t = dict(n.tags)
    if t.get('place') in ('town', 'village', 'hamlet') and area.contains(Point(n.lon, n.lat)):
        features.append({'type': 'node', 'id': n.id, 'tags': t, 'lon': n.lon, 'lat': n.lat})
assert snapshot, 'Missing source timestamp'
raw = {'osm3s': {'timestamp_osm_base': snapshot}, 'elements': features,
       'extract': {'area': 'Åland', 'boundary': 'relation/' + str(boundary['id']),
                   'url': 'https://download.geofabrik.de/europe/finland.html', 'license': 'ODbL 1.0',
                   'source': '© OpenStreetMap contributors / Geofabrik', 'method': 'Objects intersecting the Åland administrative boundary'}}
Path('data/aland-osm.json.gz').write_bytes(gzip.compress(json.dumps(raw, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0))
Path('data/aland-coast.json.gz').write_bytes(gzip.compress(json.dumps({'osm3s': raw['osm3s'], 'elements': coasts}, separators=(',', ':')).encode(), mtime=0))
print('Snapshot:', snapshot, 'Objects:', len(features), 'Coastlines:', len(coasts), flush=True)
