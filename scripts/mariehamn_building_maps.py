"""Mariehamn buildings dated from the house symbols on sheet 101208 (1968, 1985, 1995).

`data/mariehamn-building-maps.json` records, per building, the scan pixel of the matched symbol in each edition, the
local registration shift used for the match and the outcome per edition. Everything is validated before the catalogue
changes: the input fingerprint, the chronology (start at the first edition with the symbol, present in every later
one, 1985 only 'unclear' between 1968 and 1995), and the position of every recorded symbol, converted through the
sheet's registration, against the building outline. Each building gets the map evidence and an earlier standing
state; its first geometry period (the earliest measured outline) is extended back to the map year with its previous
start recorded, and the reconstruction starts at the map year and keeps its previous start. Source years stay the outline sources.
Later states and periods are kept unchanged.
"""
import hashlib
import json
import numpy as np
from pyproj import Transformer
from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree
from historical_map_observations import load_review, MERCATOR
from rural_registration import registration_pair

TO_METRIC = Transformer.from_crs(4326, 3874, always_xy=True).transform
FROM_MERCATOR = Transformer.from_crs(3857, 4326, always_xy=True).transform
YEARS = [1968, 1985, 1995]
# A curated history, museum, printed-symbol or neighbourhood (merge) review decides these buildings' dates; the map review never overrides it.
CURATED = ['historicalReview', 'museumReview', 'printedMapSymbol', 'neighborhoodReviews']
# The provisional first-source wording no longer applies once a map gives an earlier date.
PROVISIONAL = 'Första kartbelägget används tills en tidigare datering kan uppskattas; det är inte ett fastställt byggår.'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def fingerprint(o):
    return digest({k: o.get(k) for k in ['id', 'kind', 'states', 'geometryPeriods', 'sourceLinks', 'reconstruction']})


def pixel_converters(read):
    """sourceId -> function(pixel) -> EPSG:3874 point, for the editions of sheet 101208."""
    _, regs = load_review(read)
    out = {}
    for key, (sheet, convert, _) in regs.items():
        if key.startswith('nls-mariehamn-'):
            out['nls:' + sheet['id']] = lambda p, convert=convert: TO_METRIC(*FROM_MERCATOR(*MERCATOR(*convert(np.array([p]))[0])))
    sheet = next(s for s in read('data/rural-map-review.json')['sources'] if s['id'] == 'nls:101208:1995')
    fwd, _ = registration_pair(sheet)
    back = Transformer.from_crs(sheet['registration']['crs'], 3874, always_xy=True).transform
    out[sheet['id']] = lambda p: back(*fwd(tuple(p)))
    return out


def apply_building_maps(read, catalog):
    review = read('data/mariehamn-building-maps.json')
    objects = {o['id']: o for o in catalog['objects']}
    geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}
    rules = review['rules']
    if review['schemaVersion'] != 1 or review['source']['id'] in sources:
        raise ValueError('Building map review already applied')
    sheet_ids = {review['sheets'][str(y)] for y in YEARS}
    if not sheet_ids <= sources:
        raise ValueError('Missing building map source')
    to_metric = pixel_converters(read)
    seen, prepared = set(), []
    for d in review['decisions']:
        o = objects.get(d['objectId'])
        if o is None or d['objectId'] in seen or fingerprint(o) != d['input'] or o.get('kind') != 'building' or not d['basis']:
            raise ValueError('Changed or repeated building: ' + d['objectId'])
        if any(o.get(k) for k in CURATED):
            raise ValueError('Building has a curated review that decides its dates: ' + d['objectId'])
        seen.add(d['objectId'])
        states, periods = o['states'], o['geometryPeriods']
        if (len(states) != 1 or states[0]['state'] != 'standing' or states[0]['from'] != d['originalFrom']
                or periods[0]['from'] != d['originalFrom'] or periods[0]['geometryId'] != d['referenceGeometryId']
                or not d['firstYear'] < d['originalFrom'] or not o.get('reconstruction')
                or o['reconstruction']['from'] != d['originalFrom'] or o['reconstruction']['firstObserved'] != o['sourceYears'][0]):
            raise ValueError('Building crosses unreviewed phases: ' + d['objectId'])
        obs = d['observations']
        if [x['year'] for x in obs] != YEARS or any(x['sourceId'] != review['sheets'][str(x['year'])] for x in obs):
            raise ValueError('Incomplete building map chronology: ' + d['objectId'])
        present = [x['year'] for x in obs if x['outcome'] == 'present']
        if not present or present[0] != d['firstYear'] or any(x['outcome'] != 'absent' for x in obs if x['year'] < d['firstYear']):
            raise ValueError('Building start is not its first map evidence: ' + d['objectId'])
        for x in obs:
            if x['year'] > d['firstYear'] and x['outcome'] != 'present':
                # Only 1985 may be unclear, and only between symbols in 1968 and 1995.
                if not (x['outcome'] == 'unclear' and x['year'] == 1985 and d['firstYear'] == 1968 and obs[2]['outcome'] == 'present'):
                    raise ValueError('Building missing from a later edition: ' + d['objectId'])
        poly = Polygon([TO_METRIC(*p) for p in geometries[d['referenceGeometryId']]['paths'][0]])
        if poly.area < rules['minAreaSquareMeters']:
            raise ValueError('Building below the mapped size: ' + d['objectId'])
        for x in obs:
            if x['outcome'] != 'present':
                continue
            point = Point(*to_metric[x['sourceId']](x['pixel']))
            raw = poly.distance(point)
            shifted = Polygon([(px + x['shiftMeters'][0], py + x['shiftMeters'][1]) for px, py in poly.exterior.coords]).distance(point)
            limit = rules['fillLimitMeters'] if x.get('fillPass') else rules['matchLimitMeters']
            if raw > rules['maxRawSymbolDistanceMeters'] or shifted > limit + 0.5:
                raise ValueError(f"Symbol does not match building {d['objectId']} in {x['year']}")
            x['_deviation'] = round(raw, 1)
        prepared.append((o, d, poly))
    # In the centre, printed-map symbol objects already show houses from the same sheet. A dated outline must not
    # overlap any of them in any period, or the same house would be drawn twice.
    symbols = [Polygon([TO_METRIC(*p) for p in geometries[gp['geometryId']]['paths'][0]]).buffer(0)
               for s in catalog['objects'] if s.get('printedMapSymbol') for gp in s['geometryPeriods']
               if gp['geometryId'] in geometries and len(geometries[gp['geometryId']]['paths'][0]) >= 4]
    tree = STRtree(symbols)
    for o, d, poly in prepared:
        outline = poly.buffer(0)
        for i in tree.query(outline):
            if outline.intersection(symbols[i]).area > rules['symbolObjectOverlapSquareMeters'] or outline.contains(symbols[i].centroid):
                raise ValueError('Building overlaps a printed-map symbol object: ' + d['objectId'])

    # All checks passed. Change the catalogue.
    source_id = review['source']['id']
    catalog['sources'].append(dict(review['source']))
    for o, d, _ in prepared:
        ids = []
        for x in d['observations']:
            if x['year'] < d['firstYear']:
                continue
            eid = f"{o['id']}:map-101208-{x['year']}"
            e = dict(id=eid, sourceId=x['sourceId'], describes={'from': x['year'], 'to': x['year'] + 1},
                     supports=['state', 'identity'] if x['outcome'] == 'present' else ['assessment'],
                     observationType='printed-map', outcome=x['outcome'], interpretation=True, constructionYear=None,
                     reviewId=source_id, note=x['note'])
            if x['outcome'] == 'present':
                e.update(sourcePixels=dict(sourceId=x['sourceId'], pixel=x['pixel']), deviationMeters=x.pop('_deviation'),
                         localShiftMeters=x['shiftMeters'], matchedGeometryId=d['referenceGeometryId'])
                ids.append(eid)
            o['evidence'].append(e)
        note = d['basis']
        o['states'].insert(0, dict(state='standing', **{'from': d['firstYear'], 'to': d['originalFrom']}, evidenceIds=ids,
                                   certainty='inferred', note=note))
        # The map symbol dates existence, not shape: the first period, which shows the outline first measured in
        # firstObserved, is extended back to the map year and keeps its previous start.
        rec = o['reconstruction']; first = o['geometryPeriods'][0]
        basis = (first.get('basis') or '').replace(PROVISIONAL, '').strip()
        basis = (basis + ' ' if basis else '') + (f"Visas från {d['firstYear']} efter hussymbolen på grundkartan; formen är den först "
                                                  f"inmätta konturen från {rec['firstObserved']}, inte kartans ritning.")
        o['geometryPeriods'][0] = {**first, 'from': d['firstYear'], 'evidenceIds': first['evidenceIds'] + ids, 'certainty': 'inferred',
                                   'basis': basis, 'previousFrom': first['from'], 'previousBasis': first.get('basis')}
        o['reconstruction'] = {**rec, 'from': d['firstYear'], 'basis': note, 'evidenceIds': rec['evidenceIds'] + ids, 'mapDated': True,
                               'previous': {'from': rec['from'], 'basis': rec['basis']}}
        o['buildingMapReview'] = dict(reviewedAt=review['reviewedAt'], firstYear=d['firstYear'], originalFrom=d['originalFrom'],
                                      batch=d['batch'], constructionYear=None)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
