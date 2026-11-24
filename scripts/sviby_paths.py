"""Roads at Sviby that became paths (docs/sviby-paths.md).

Two roads from the Sviby connections (docs/sviby-connections.md) are cycle and foot paths today:
- the west part of the road from Norra Svibyvägen east to Svibyvägen (OSM: cycleway from the 2025 extract; the 2014
  and 2021 extracts have the whole road as one residential way);
- the north piece of Norra Möckelövägen (OSM: footway in 2014 and 2021, cycleway in 2025 and 2026), a road on the maps
  1929–1995 and the aerial photos 1952–1999, a narrow path on the photo of 2007.

One review file, data/sviby-paths.json, gives each object dated road classes ('roadClassPeriods': at most one period
in a year, over the whole line or over 'canonicalRange' of it; the object's modernRoadClass applies outside them) and the
evidence for them. The map draws the class in force each year (dist/city-grid.js). The objects keep their identity,
geometry and open state: the physical way is the same, only its use changed.
"""
from copy import deepcopy
from mariehamn_frame_1942 import fingerprint, TO_METRIC
from shapely.geometry import LineString

REVIEW = 'data/sviby-paths.json'
MODERN = 'dist/assets/modern.json.gz'


def _length(path):
    return LineString([TO_METRIC(*q) for q in path]).length


def apply_sviby_paths(read, catalog):
    review = read(REVIEW)
    trial = deepcopy(catalog)
    objects = {o['id']: o for o in trial['objects']}; geometries = {g['id']: g for g in trial['geometries']}
    sources = {s['id'] for s in trial['sources']}
    if review['schemaVersion'] != 1 or review['source']['id'] in sources:
        raise ValueError('Sviby paths review already applied')
    modern = None
    for t in review['targets']:
        o = objects.get(t['objectId'])
        if not o or fingerprint(o) != t['inputHash'] or o.get('roadClassPeriods'):
            raise ValueError('Changed Sviby paths target: ' + t['objectId'])
        first = o['states'][0]['from']
        ev = {e['id'] for e in o['evidence']} | {e['id'] for e in t['evidence']}
        for e in t['evidence']:
            if e['sourceId'] not in sources | {s['id'] for s in review['sources']}:
                raise ValueError('Missing evidence source: ' + e['id'])
        for i, p in enumerate(t['roadClassPeriods']):
            if p['from'] < first or (p['to'] is not None and p['to'] <= p['from']) or not p['basis'] or not p['evidenceIds'] or not set(p['evidenceIds']) <= ev \
                    or any(q['from'] < (p['to'] or 9999) and p['from'] < (q['to'] or 9999) for q in t['roadClassPeriods'][:i]):
                raise ValueError('Invalid road class period: ' + t['objectId'])
            if p.get('canonicalRange'):
                # A ranged period: the line's first ways, by their OSM 2026 lengths, on an object of one path.
                gp = [g for g in o['geometryPeriods'] if g['from'] <= p['from'] < (g['to'] or 9999)]
                paths = geometries[gp[0]['geometryId']]['paths'] if len(gp) == 1 else []
                linked = {l['featureId'] for l in o['sourceLinks'] if l['datasetId'] == 'osm-2026'}
                if modern is None:
                    modern = {f['id']: f for f in read(MODERN)['features']}
                if len(paths) != 1 or not set(p['rangeWays']) <= linked or p['canonicalRange'][0] != 0 \
                        or abs(sum(_length(modern[w]['paths'][0]) for w in p['rangeWays']) / _length(paths[0]) - p['canonicalRange'][1]) > 0.002 \
                        or any(modern[w]['class'] != p['class'] for w in p['rangeWays']):
                    raise ValueError('The class range is not the listed ways: ' + t['objectId'])
        o['evidence'] += deepcopy(t['evidence'])
        o['roadClassPeriods'] = [{k: v for k, v in p.items() if k != 'rangeWays'} for p in t['roadClassPeriods']]
        o['roadClassReview'] = dict(reviewedAt=review['reviewedAt'], review=review['source']['id'])
    trial['sources'] += [deepcopy(review['source'])] + deepcopy(review['sources'])
    trial['recordedAt'] = max(trial['recordedAt'], review['reviewedAt'])
    catalog.clear(); catalog.update(trial)
