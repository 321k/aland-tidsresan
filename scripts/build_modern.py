"""Build compact, reusable modern map data from the complete Åland OSM extract."""
import collections
import gzip
import json
from pathlib import Path


def join_rings(paths):
    remaining = [list(p) for p in paths if len(p) > 1]
    result = []
    while remaining:
        ring = remaining.pop(0)
        while ring[0] != ring[-1]:
            for i, part in enumerate(remaining):
                if ring[-1] == part[0]: ring += part[1:]
                elif ring[-1] == part[-1]: ring += part[-2::-1]
                elif ring[0] == part[-1]: ring = part[:-1] + ring
                elif ring[0] == part[0]: ring = part[:0:-1] + ring
                else: continue
                remaining.pop(i)
                break
            else: break
        if len(ring) >= 4 and ring[0] == ring[-1]: result.append(ring)
    return result


def points(geometry):
    return [[round(p['lon'], 6), round(p['lat'], 6)] for p in geometry if p]


def build(raw):
    features, places, member_ways = [], [], set()
    # Only suppress a member when its parent polygon was actually assembled.
    for e in sorted(raw['elements'], key=lambda e: e['type'] != 'relation'):
        t = e.get('tags', {})
        if e['type'] == 'node':
            name = t.get('name:sv') or t.get('name')
            if name: places.append({'name': name, 'lon': e['lon'], 'lat': e['lat'], 'type': t['place']})
            continue
        building = t.get('building') not in (None, 'no', 'proposed', 'construction', 'demolished', 'razed')
        road = t.get('highway') not in (None, 'proposed', 'construction', 'abandoned', 'razed', 'platform')
        if not building and not road: continue
        kind = 'building' if building else 'road'
        if e['type'] == 'relation':
            if not building or t.get('type') != 'multipolygon': continue
            members = [m for m in e.get('members', []) if m['type'] == 'way' and m.get('geometry')]
            outer = join_rings([points(m['geometry']) for m in members if m.get('role', '') in ('', 'outer')])
            inner = join_rings([points(m['geometry']) for m in members if m.get('role') == 'inner'])
            if not outer: continue
            paths = outer + inner
            member_ways.update(m['ref'] for m in members if m.get('role', '') in ('', 'outer'))
        else:
            if building and e['id'] in member_ways: continue
            path = points(e.get('geometry', []))
            if len(path) < 2: continue
            if building and (len(path) < 4 or path[0] != path[-1]): continue
            paths = [path]
        name = t.get('name:sv') or t.get('name') or ' '.join(filter(None, [t.get('addr:street'), t.get('addr:housenumber')]))
        features.append({'id': e['type'] + '/' + str(e['id']), 'kind': kind,
                         'name': name or ('Byggnad' if building else 'Väg eller stig'),
                         'class': t.get('building') if building else t['highway'],
                         'paths': paths, 'start_date': t.get('start_date'), 'wiki': t.get('wikipedia')})
    coords = [p for f in features for path in f['paths'] for p in path]
    return {'source': '© OpenStreetMap contributors', 'license': 'ODbL 1.0',
            'url': 'https://www.openstreetmap.org/copyright',
            'snapshot': raw['osm3s']['timestamp_osm_base'], 'area': 'Åland',
            'bbox': [min(p[0] for p in coords), min(p[1] for p in coords), max(p[0] for p in coords), max(p[1] for p in coords)],
            'counts': dict(collections.Counter(f['kind'] for f in features)),
            'places': sorted(places, key=lambda p: p['name']), 'features': features}


if __name__ == '__main__':
    raw = json.loads(gzip.decompress(Path('data/aland-osm.json.gz').read_bytes()))
    data = build(raw)
    target = Path('dist/assets/modern.json.gz')
    target.write_bytes(gzip.compress(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0))
    print(data['counts'], 'Places:', len(data['places']), 'Bytes:', target.stat().st_size)
