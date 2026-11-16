"""The shore road on Västerhamn (today's Sjöpromenaden) before 1968.

`data/mariehamn-shore-road.json` records a visual review of the 1942, 1952 and 1962 orthophotos and the museum's
1920s picture. The photos show a road along the west shore from the harbour north to about latitude 60.1004 that
no object covered before the 1968 base map; the museum picture's "Västra strandens gata" is a coarse drawing of the
same road (its north end lies up to 40 m out in the water). The persistent Sjöpromenaden objects are shown from the
museum decade with their own measured centre lines:

* each member gets the museum drawing (1920, decade precision, interpretation) and the 1942 photo as evidence, a
  state 1920–1942 and 1942–original start, and one earlier geometry period. The long northern member only covers
  its southern part before its original start (`coverage: partial`, `canonicalRange`), since the photos show no
  road on the rocky shore north of the cut until later;
* every raw city-stage copy of the museum drawing is removed and the members are drawn in the 1920–1952 stages;
  the drawing itself stays in the source dataset and as each member's original geometry. Its southern remainder,
  past the harbour towards Lotsberget, has no road on the 1942 photo and is not drawn.

Everything is validated before the catalogue changes. The photo and museum years are evidence, not construction years.
"""
from copy import deepcopy
from pyproj import Transformer
from shapely.geometry import LineString, Point
from mariehamn_frame_1942 import digest, fingerprint, TO_METRIC

TO_GEO = Transformer.from_crs(3874, 4326, always_xy=True).transform


def apply_shore_road(read, catalog):
    review = read('data/mariehamn-shore-road.json')
    objects = {o['id']: o for o in catalog['objects']}
    geometries = {g['id']: g for g in catalog['geometries']}
    stages = {s['id']: s for s in catalog['cityStages']}
    sources = {s['id'] for s in catalog['sources']}
    museum = review['museum']
    if (review['schemaVersion'] != 1 or review['source']['id'] in sources or review['aerialSourceId'] not in sources
            or museum['datasetId'] not in sources):
        raise ValueError('Shore road review already applied or missing a source')
    grid = read('dist/assets/mariehamn-city-grid.json')
    raw = next((f for s in grid['sets'] for f in s['features'] if f['id'] == museum['featureId']), None)
    if raw is None or digest(raw) != museum['inputHash'] or raw.get('traceId') != museum['traceId'] or not review['basis']:
        raise ValueError('Changed museum shore drawing')
    drawing = LineString([TO_METRIC(*p) for p in raw['paths'][0]])
    found = {(s['id'], f['id']) for s in catalog['cityStages'] for f in s['features'] if f.get('traceId') == museum['traceId']}
    if found != {(x['stageId'], x['featureId']) for x in museum['stageFeatures']}:
        raise ValueError('Unreviewed city-stage copy of the museum shore drawing')
    for x in museum['stageFeatures']:
        f = next(f for f in stages[x['stageId']]['features'] if f['id'] == x['featureId'])
        if digest(f) != x['inputHash'] or f.get('objectId'):
            raise ValueError('Changed city-stage shore drawing ' + x['featureId'])
    draw = review['drawInStages']
    if any(s not in stages or not museum['year'] <= stages[s]['from'] < min(m['originalFrom'] for m in review['members']) for s in draw):
        raise ValueError('Unknown or late stage for the shore road')
    plans = []
    for m in review['members']:
        o = objects.get(m['objectId'])
        if (o is None or o.get('kind') != 'roadSegment' or fingerprint(o) != m['inputHash'] or len(o['states']) != 1
                or o['states'][0]['state'] != 'open' or o['states'][0]['from'] != m['originalFrom']
                or len(o['geometryPeriods']) != 1 or o['geometryPeriods'][0]['from'] != m['originalFrom']
                or not m['originalFrom'] > review['photoYear'] > museum['year'] or not m['note']):
            raise ValueError('Changed shore road object ' + m['objectId'])
        full = geometries[o['geometryPeriods'][0]['geometryId']]['paths']
        if len(full) != 1:
            raise ValueError('Shore road object must be one line: ' + m['objectId'])
        line = LineString([TO_METRIC(*p) for p in full[0]])
        a, b = m['canonicalRange']
        if not 0 <= a < b <= 1 or b != 1:
            raise ValueError('Invalid shore road extent ' + m['objectId'])
        if a > 0:
            cut = TO_GEO(*line.interpolate(a, normalized=True).coords[0])
            if abs(cut[1] - m['cutLatitude']) > 0.00002:
                raise ValueError('Shore road cut moved ' + m['objectId'])
            start = line.project(Point(line.interpolate(a, normalized=True)))
            part = [[round(v, 7) for v in TO_GEO(*line.interpolate(start).coords[0])]] + \
                   [p for p in full[0] if line.project(Point(TO_METRIC(*p))) > start + 0.01]
        else:
            part = deepcopy(full[0])
        if max(drawing.distance(Point(TO_METRIC(*p))) for p in part) > museum['maxDistanceMeters']:
            raise ValueError('Shore road object is not near the museum drawing: ' + m['objectId'])
        plans.append((o, m, part, a))

    # All checks passed. Change the catalogue.
    source_id = review['source']['id']
    catalog['sources'].append(deepcopy(review['source']))
    for x in museum['stageFeatures']:
        stage = stages[x['stageId']]
        stage['features'] = [f for f in stage['features'] if f['id'] != x['featureId']]
    raw_gid = 'geometry:shore-road:museum-1920'
    catalog['geometries'].append(dict(id=raw_gid, paths=deepcopy(raw['paths']), representation='centerline',
                                      sourceIds=[museum['datasetId']], note='Museikartans ursprungliga avritning; ungefärligt inpassad.'))
    for o, m, part, a in plans:
        first = o['geometryPeriods'][0]
        gid = first['geometryId']
        if a > 0:
            gid = f"geometry:shore-road:{o['id'].split(':')[-1]}:early"
            catalog['geometries'].append(dict(id=gid, paths=[part], representation='centerline', sourceIds=['city-2026'],
                                              note='Södra delen av den moderna mittlinjen, som flygfotot 1942 visar.'))
        mid, pid = o['id'] + ':museum-1920', o['id'] + ':shore-photo-1942'
        o['evidence'].append(dict(id=mid, sourceId=museum['datasetId'], describes={'from': museum['year'], 'to': museum['year'] + 10},
                                  supports=['identity', 'state', 'geometry'], observationType='map', outcome='present',
                                  originalGeometryId=raw_gid, sourceFeatureId=raw['id'], sourceTraceId=museum['traceId'],
                                  interpretation=True, datePrecision='decade', constructionYear=None, reviewId=source_id,
                                  note=museum['basis']))
        o['evidence'].append(dict(id=pid, sourceId=review['aerialSourceId'], describes={'from': review['photoYear'], 'to': review['photoYear'] + 1},
                                  supports=['geometry', 'state', 'identity'], observationType='aerial', observedAt=review['photoObservedAt'],
                                  outcome='present', imageCoverage='visible', matchedGeometryId=gid, interpretation=True,
                                  constructionYear=None, reviewId=source_id, note=m['note']))
        if o is plans[0][0]:  # a source feature belongs to one object: the long northern part owns the drawing
            o['sourceLinks'].append(dict(datasetId=museum['datasetId'], featureId=raw['id']))
        o['states'][:0] = [dict(state='open', **{'from': museum['year'], 'to': review['photoYear']}, evidenceIds=[mid],
                                certainty='inferred', note=museum['basis']),
                           dict(state='open', **{'from': review['photoYear'], 'to': m['originalFrom']}, evidenceIds=[pid],
                                certainty='inferred', note=m['note'] + ' Fotoåret är belägg, inte byggår.')]
        early = dict(geometryId=gid, **{'from': museum['year'], 'to': m['originalFrom']}, evidenceIds=[mid, pid],
                     certainty='inferred', basis=review['basis'])
        if a > 0:
            early.update(coverage='partial', canonicalRange=[a, 1])
            first.update(coverage='full', canonicalRange=[0, 1])
        o['geometryPeriods'].insert(0, early)
        for stage_id in draw:
            fid = f"{stage_id}:shore-road:{o['id']}"
            stages[stage_id]['features'].append(dict(id=fid, objectId=o['id'], name=o['name'], kind='street', width=8,
                                                     sourceFeatureId=raw['id'], paths=[deepcopy(part)]))
            o['sourceLinks'].append(dict(datasetId=stage_id, featureId=fid))
        o['shoreRoadReview'] = dict(reviewedAt=review['reviewedAt'], originalFrom=m['originalFrom'], constructionYear=None)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
