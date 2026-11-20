"""Road remnants in the heritage register as evidence on the roads they belong to (docs/road-remnants.md).

The register (Ålands landskapsregering, fornlämningsregistret) records fossil road sections ("Väglämning") with a
surveyed outline. Each one reviewed in data/road-remnants.json lies on, or within a stated distance of, a road object
that the catalogue already dates from the parish maps or earlier. This step adds the register entry to that object as
evidence (identity, and geometry where the road runs inside the outline). It changes no states or geometries: the
register's dating ("Sentid", 1500–) is too broad to set a first year. The remnant at Postad (Ha 17.8) is handled by
apply_hammarlandsvagen_postad, where it locates the old curve.

All checks run before any change: the review applies once, each object and outline is unchanged (fingerprint, digest),
and each outline still lies within its stated distance of the object's dated geometry.
"""
from copy import deepcopy
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC


def _outline(feature):
    g = feature['geometry']
    polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
    return unary_union([Polygon([TO_METRIC(*q) for q in p[0]]) for p in polys])


def apply_road_remnants(read, catalog):
    review = read('data/road-remnants.json')
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}; src = review['source']['id']
    if review['schemaVersion'] != 1 or src in sources or any(r['sourceId'] in sources for r in review['remnants']):
        raise ValueError('Road remnant review already applied')
    outlines = {f['properties']['code']: f for f in read('dist/assets/heritage-boundaries.geojson')['features']}
    register = {f['code']: f for f in read('dist/assets/heritage.json')['features']}
    seen = set()
    for r in review['remnants']:
        o = objects.get(r['objectId']); f = outlines.get(r['code'])
        if r['code'] in seen or r['code'] not in register or 'Väglämning' not in register[r['code']]['name']:
            raise ValueError('Not a single register road remnant: ' + r['code'])
        seen.add(r['code'])
        if not o or fingerprint(o) != r['inputHash']:
            raise ValueError('Changed road ' + r['objectId'])
        if not f or digest(f['geometry']['coordinates']) != r['outlineHash']:
            raise ValueError('Changed register outline ' + r['code'])
        poly = _outline(f)
        lines = [LineString([TO_METRIC(*q) for q in p]) for gp in o['geometryPeriods'] if gp['from'] <= r['year'] < (gp['to'] or 9999)
                 for p in geometries[gp['geometryId']]['paths'] if len(p) > 1]
        if not lines or min(l.distance(poly) for l in lines) > r['maxDistanceMeters'] or not r.get('note'):
            raise ValueError(f"Register remnant {r['code']} is not on {r['objectId']} in {r['year']}")
        inside = sum(l.intersection(poly.buffer(5)).length for l in lines)
        if (r['supports'] == ['geometry', 'identity']) != (inside >= r.get('minInsideMeters', 1e9)):
            raise ValueError('Changed overlap with the register outline: ' + r['code'])

    # All checks passed. Change the catalogue.
    catalog['sources'] += [dict(id=r['sourceId'], title=f"Ålands landskapsregering · fornlämningsregistret · {r['code']} {register[r['code']]['name']}",
                                url=register[r['code']]['sourceUrl'], issuedAt='2026') for r in review['remnants']] + [deepcopy(review['source'])]
    for r in review['remnants']:
        o = objects[r['objectId']]
        o['evidence'].append(dict(id=f"{o['id']}:register-{r['code'].replace(' ', '-')}", sourceId=r['sourceId'], describes={'from': 2026, 'to': 2027},
                                  observationType='heritage-register', interpretation=True, outcome='present', supports=list(r['supports']),
                                  constructionYear=None, reviewId=src, note=r['note']))
        o.setdefault('registerRemnants', []).append(dict(code=r['code'], review=src, distanceMeters=r['distanceMeters']))
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
