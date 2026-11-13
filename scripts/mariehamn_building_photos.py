"""Mariehamn buildings with no symbol on sheet 101208, dated from the town's orthophotos (1991, 1999, 2007, 2015).

`data/mariehamn-building-photos.json` records, per building, the photo years judged by eye on 1 m/px tiles: the first
photo that shows it (every later reviewed photo shows it too) and the earlier ones that show the site without it.
Before anything changes the compiler checks the input fingerprint, that the building has one open phase starting
after the first photo year, that every photo source exists, and that the chronology is consistent. Each building
gets aerial evidence for the photo years that show it and a new first state from the first photo year; its first
geometry period (the earliest measured outline) is extended back with its previous start kept. A modern-only outline
without a reconstruction gets one first, as in the building-map step. The photo year is first evidence, not a
construction year.
"""
import hashlib
import json
from aerial_observations import photo_url
from pyproj import Transformer
from shapely.geometry import Polygon

TO_METRIC = Transformer.from_crs(4326, 3874, always_xy=True).transform


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def fingerprint(o):
    return digest({k: o.get(k) for k in ['id', 'kind', 'states', 'geometryPeriods', 'sourceLinks', 'reconstruction']})


CURATED = ['historicalReview', 'museumReview', 'printedMapSymbol', 'neighborhoodReviews', 'buildingMapReview', 'symbolMap1968',
           'museumDuplicateReview', 'museumOffsetReview']


def apply_building_photos(read, catalog):
    review = read('data/mariehamn-building-photos.json')
    objects = {o['id']: o for o in catalog['objects']}
    geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id']: s for s in catalog['sources']}
    photos = {p['year']: p for p in read('data/mariehamn-aerial-review.json')['sources']}
    if review['schemaVersion'] != 1 or review['source']['id'] in sources:
        raise ValueError('Building photo review already applied')
    years = review['photoYears']
    if any(y not in photos or photos[y]['id'] not in sources for y in years):
        raise ValueError('Missing reviewed photo source')
    seen, prepared = set(), []
    for d in review['decisions']:
        o = objects.get(d['objectId'])
        if o is None or d['objectId'] in seen or o.get('kind') != 'building' or fingerprint(o) != d['input'] or not d['basis']:
            raise ValueError('Changed or repeated photo-dated building: ' + d['objectId'])
        if any(o.get(k) for k in CURATED):
            raise ValueError('Building has a review that decides its dates: ' + d['objectId'])
        seen.add(d['objectId'])
        states, periods = o['states'], o['geometryPeriods']
        rec = o.get('reconstruction')
        create = rec is None
        if (len(states) != 1 or states[0]['state'] != 'standing' or states[0]['to'] is not None or states[0]['from'] != d['originalFrom']
                or periods[0]['from'] != d['originalFrom'] or periods[0]['geometryId'] != d['referenceGeometryId']
                or not d['firstYear'] < d['originalFrom']
                or (create and not (o.get('externalModern') and o['sourceYears'] == [2026] and len(periods) == 1))
                or (not create and (rec['from'] != d['originalFrom'] or rec['firstObserved'] != o['sourceYears'][0]))):
            raise ValueError('Photo-dated building crosses unreviewed phases: ' + d['objectId'])
        obs = d['observations']
        if [x['year'] for x in obs] != sorted(x['year'] for x in obs) or any(x['year'] not in years for x in obs):
            raise ValueError('Invalid photo chronology: ' + d['objectId'])
        present = [x['year'] for x in obs if x['outcome'] == 'present']
        if (not present or present[0] != d['firstYear'] or any(x['outcome'] not in ('present', 'absent', 'not-covered') for x in obs)
                or any(x['outcome'] != 'present' for x in obs if x['year'] >= d['firstYear'])
                or not any(x['outcome'] in ('absent', 'not-covered') for x in obs if x['year'] < d['firstYear']) and d['firstYear'] != years[0]):
            raise ValueError('Building start is not its first photo evidence: ' + d['objectId'])
        if Polygon([TO_METRIC(*p) for p in geometries[d['referenceGeometryId']]['paths'][0]]).area < review['minAreaSquareMeters']:
            raise ValueError('Building below the reviewed size: ' + d['objectId'])
        prepared.append((o, d, create))

    # All checks passed. Change the catalogue.
    source_id = review['source']['id']
    catalog['sources'].append(dict(review['source']))
    for o, d, create in prepared:
        s = o['states'][0]
        if create:
            o['reconstruction'] = dict(**{'from': s['from']}, firstObserved=o['sourceYears'][0], basis=s['note'], dateClaims={},
                                       evidenceIds=list(s['evidenceIds']), createdByBuildingPhotoReview=True)
        center = Polygon(geometries[d['referenceGeometryId']]['paths'][0]).centroid
        ids = []
        for x in d['observations']:
            if x['outcome'] != 'present':
                continue
            photo = photos[x['year']]; eid = f"{o['id']}:photo-{x['year']}"
            o['evidence'].append(dict(id=eid, sourceId=photo['id'], describes={'from': x['year'], 'to': x['year'] + 1},
                                      supports=['state', 'identity'], observationType='aerial', observedAt=photo['capturedAt'],
                                      outcome='present', imageCoverage='visible', matchedGeometryId=d['referenceGeometryId'],
                                      interpretation=True, constructionYear=None, reviewId=source_id, note=x['note'],
                                      sourceUrl=photo_url(x['year'], list(TO_METRIC(center.x, center.y)))))
            o['sourceLinks'].append(dict(datasetId=photo['id'], featureId=o['id']))
            ids.append(eid)
        o['states'].insert(0, dict(state='standing', **{'from': d['firstYear'], 'to': d['originalFrom']}, evidenceIds=ids,
                                   certainty='inferred', note=d['basis']))
        first = o['geometryPeriods'][0]
        o['geometryPeriods'][0] = {**first, 'from': d['firstYear'], 'evidenceIds': first['evidenceIds'] + ids, 'certainty': 'inferred',
                                   'previousFrom': first['from'],
                                   'basis': (first.get('basis') or '') + f" Visas från flygfotot {d['firstYear']}; formen är den först inmätta konturen."}
        rec = o['reconstruction']
        o['reconstruction'] = {**rec, 'from': d['firstYear'], 'basis': d['basis'], 'evidenceIds': rec['evidenceIds'] + ids, 'photoDated': True,
                               'previous': {'from': rec['from'], 'basis': rec['basis']}}
        o['buildingPhotoReview'] = dict(reviewedAt=review['reviewedAt'], firstYear=d['firstYear'], originalFrom=d['originalFrom'],
                                        batch=d['batch'], constructionYear=None)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
