"""Printed-map symbol objects in central Mariehamn dated back to the 1968 edition of sheet 101208.

The `map-building:nls-symbol-*` objects start at the 1985 edition's survey year (1983, or 1982). Where
`data/mariehamn-symbols-1968.json` records the same symbol on the 1968 edition, outside the hatched built-up areas,
the object gets the 1968 map as evidence and is shown from 1968. Everything is validated before the catalogue
changes: the input fingerprint, the start, the position of the recorded 1968 symbol against the object's first
outline, and that the symbol lies outside every 1968 built-up area object. The first state and the first geometry
period are extended back with their previous start kept; later states and periods are unchanged.
"""
import hashlib
import json
from pyproj import Transformer
from shapely.geometry import Point, Polygon
from mariehamn_building_maps import pixel_converters

TO_METRIC = Transformer.from_crs(4326, 3874, always_xy=True).transform


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def fingerprint(o):
    return digest({k: o.get(k) for k in ['id', 'kind', 'states', 'geometryPeriods', 'sourceLinks', 'reconstruction']})


def apply_symbols_1968(read, catalog):
    review = read('data/mariehamn-symbols-1968.json')
    objects = {o['id']: o for o in catalog['objects']}
    geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}
    rules = review['rules']
    if review['schemaVersion'] != 1 or review['source']['id'] in sources or review['sheet1968'] not in sources:
        raise ValueError('1968 symbol review already applied or missing its sheet')
    to_metric = pixel_converters(read)[review['sheet1968']]
    areas = [Polygon([TO_METRIC(*p) for p in geometries[gp['geometryId']]['paths'][0]])
             for o in catalog['objects'] if o.get('printedMapArea') for gp in o['geometryPeriods'][:1]]
    seen, prepared = set(), []
    for d in review['decisions']:
        o = objects.get(d['objectId'])
        if (o is None or d['objectId'] in seen or not o.get('printedMapSymbol') or o.get('kind') != 'building'
                or fingerprint(o) != d['input'] or not d['note']):
            raise ValueError('Changed or repeated 1968 symbol object: ' + d['objectId'])
        seen.add(d['objectId'])
        first, period, rec = o['states'][0], o['geometryPeriods'][0], o.get('reconstruction')
        if (first['state'] not in ('occupied', 'standing') or first['from'] != d['originalFrom'] or not 1968 < d['originalFrom'] <= 1985
                or period['from'] != d['originalFrom'] or not rec or rec['from'] != d['originalFrom']):
            raise ValueError('1968 symbol object crosses unreviewed phases: ' + d['objectId'])
        point = Point(*to_metric(d['pixel']))
        if any(a.contains(point) for a in areas):
            raise ValueError('1968 symbol lies in a hatched built-up area: ' + d['objectId'])
        poly = Polygon([TO_METRIC(*p) for p in geometries[period['geometryId']]['paths'][0]])
        shifted = Polygon([(x + d['shiftMeters'][0], y + d['shiftMeters'][1]) for x, y in poly.exterior.coords])
        raw = poly.distance(point)
        if raw > rules['maxRawSymbolDistanceMeters'] or shifted.distance(point) > rules['matchLimitMeters'] + 0.5:
            raise ValueError('1968 symbol does not match object ' + d['objectId'])
        prepared.append((o, d, round(raw, 1)))

    # All checks passed. Change the catalogue.
    source_id = review['source']['id']
    catalog['sources'].append(dict(review['source']))
    for o, d, raw in prepared:
        eid = o['id'] + ':map-101208-1968'
        o['evidence'].append(dict(id=eid, sourceId=review['sheet1968'], describes={'from': 1968, 'to': 1969},
                                  supports=['state', 'identity'], observationType='printed-map', outcome='present',
                                  interpretation=True, constructionYear=None, reviewId=source_id, note=d['note'],
                                  sourcePixels=dict(sourceId=review['sheet1968'], pixel=d['pixel']), deviationMeters=raw,
                                  localShiftMeters=d['shiftMeters'], matchedGeometryId=o['geometryPeriods'][0]['geometryId']))
        first = o['states'][0]
        o['states'].insert(0, dict(state=first['state'], **{'from': 1968, 'to': d['originalFrom']}, evidenceIds=[eid],
                                   certainty='inferred', note=d['note']))
        period = o['geometryPeriods'][0]
        o['geometryPeriods'][0] = {**period, 'from': 1968, 'evidenceIds': period['evidenceIds'] + [eid], 'previousFrom': period['from'],
                                   'basis': (period.get('basis') or '') + ' Visas från 1968 efter samma hussymbol på grundkartan 1968; '
                                            'formen är inte kartans ritning.'}
        rec = o['reconstruction']
        o['reconstruction'] = {**rec, 'from': 1968, 'evidenceIds': rec['evidenceIds'] + [eid], 'mapDated': True,
                               'previous': {'from': rec['from'], 'basis': rec['basis']}}
        o['symbolMap1968'] = dict(reviewedAt=review['reviewedAt'], originalFrom=d['originalFrom'], batch=d['batch'], constructionYear=None)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
