"""The 1942 city traces reviewed against the 1942 orthophoto.

The hand traces of the 1942 city stage were drawn at 4 m/px with two to fifteen points per street; four of them form a
coarse frame around the town. `data/mariehamn-frame-1942.json` records the review of every trace that was still drawn
without an object, against the original photo (and the 1968 base map as a second witness):

* every raw city-stage copy of a reviewed trace is removed (original pixels stay in the source files; features of
  street objects that carry the trace id as their source are kept);
* where the photo shows the street the trace stood for, those persistent road objects get the photo as 1942 evidence
  and are shown from 1942 with their own centre lines. Each must lie near the trace it replaces;
* a gap the photo shows but no object covers is drawn from a centre line retraced on the photo, 1942–1967 only.

Everything is validated before the catalogue is touched; no existing state or date is moved.
"""
from copy import deepcopy
import hashlib
import json
from pyproj import Transformer
from shapely.geometry import LineString, Point

TO_METRIC = Transformer.from_crs(4326, 3874, always_xy=True).transform
TO_GEO = Transformer.from_crs(3874, 4326, always_xy=True).transform
EARLY_STAGES = ['city-reconstruction-1942', 'city-reconstruction-1952']


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def fingerprint(o):
    return digest({k: o.get(k) for k in ['id', 'kind', 'states', 'geometryPeriods', 'sourceLinks']})


def apply_frame_1942(read, catalog):
    review = read('data/mariehamn-frame-1942.json')
    objects = {o['id']: o for o in catalog['objects']}
    geometries = {g['id']: g for g in catalog['geometries']}
    stages = {s['id']: s for s in catalog['cityStages']}
    sources = {s['id'] for s in catalog['sources']}
    city = next(s for s in read('data/mariehamn-city-traces.json')['sets'] if s['id'] == 'city-1942')
    ref = city['reference']
    if review['schemaVersion'] != 1 or review['source']['id'] in sources or review['aerialSourceId'] not in sources:
        raise ValueError('1942 frame review already applied or missing its aerial source')
    seen, plans = set(), []
    for entry in review['traces']:
        raw = next((t for t in city['roads'] if t['traceId'] == entry['traceId']), None)
        if raw is None or digest(raw) != entry['inputHash'] or raw['pixels'] != entry['pixels'] or raw['name'] != entry['name'] or not entry['basis']:
            raise ValueError('Changed original 1942 trace ' + entry['traceId'])
        # Features of street objects may carry the trace id as their source; only the raw trace copies are reviewed here.
        found = {(s['id'], f['id']) for s in catalog['cityStages'] for f in s['features'] if f.get('traceId') == entry['traceId'] and not f.get('objectId')}
        if found != {(x['stageId'], x['featureId']) for x in entry['stageFeatures']}:
            raise ValueError('Unreviewed city-stage copy of ' + entry['traceId'])
        for x in entry['stageFeatures']:
            f = next(f for f in stages[x['stageId']]['features'] if f['id'] == x['featureId'])
            if digest(f) != x['inputHash'] or f.get('objectId') or (':outside:' in f['id']) != x['outside'] \
                    or (not x['outside'] and x['stageId'] not in EARLY_STAGES):
                raise ValueError('Changed city-stage trace ' + x['featureId'])
        if (entry['decision'] == 'rejected') != (not entry['members'] and not entry['retracedGaps']) or entry['decision'] not in ('rejected', 'replaced'):
            raise ValueError('Inconsistent 1942 frame decision ' + entry['traceId'])
        trace = LineString([(ref['west'] + x * ref['metersPerViewPixel'], ref['north'] - y * ref['metersPerViewPixel']) for x, y in raw['pixels']])
        members = []
        for m in entry['members']:
            o = objects.get(m['objectId'])
            if (o is None or m['objectId'] in seen or fingerprint(o) != m['inputHash'] or o.get('kind') != 'roadSegment'
                    or o['states'][0]['state'] != 'open' or o['states'][0]['from'] != m['originalFrom'] or m['originalFrom'] <= 1942
                    or o['geometryPeriods'][0]['from'] != m['originalFrom'] or not m['note']):
                raise ValueError('Changed or repeated 1942 frame object ' + m['objectId'])
            seen.add(m['objectId'])
            first = o['geometryPeriods'][0]; paths = geometries[first['geometryId']]['paths']
            if len(paths) != 1:
                raise ValueError('1942 frame object must be one line: ' + m['objectId'])
            if max(trace.distance(Point(TO_METRIC(*p))) for p in paths[0]) > entry['maxDistanceMeters']:
                raise ValueError('1942 frame object is not near the trace it replaces: ' + m['objectId'])
            members.append((o, m, first, paths))
        gaps = []
        for gap in entry['retracedGaps']:
            line = LineString(gap['epsg3874'])
            ends = []
            for oid in (gap['fromObjectId'], gap['toObjectId']):
                o = objects.get(oid)
                if o is None:
                    raise ValueError('Missing object at a retraced 1942 gap: ' + oid)
                path = geometries[o['geometryPeriods'][0]['geometryId']]['paths'][0]
                ends.append([Point(TO_METRIC(*path[0])), Point(TO_METRIC(*path[-1]))])
            if (not gap['basis'] or not line.is_simple or min(Point(line.coords[0]).distance(p) for p in ends[0]) > 1
                    or min(Point(line.coords[-1]).distance(p) for p in ends[1]) > 1
                    or max(trace.distance(Point(p)) for p in line.coords) > entry['maxDistanceMeters']):
                raise ValueError('Invalid retraced 1942 frame gap')
            gaps.append([[round(v, 7) for v in TO_GEO(*p)] for p in line.coords])
        plans.append((entry, members, gaps))

    # All checks passed. Change the catalogue.
    source_id = review['source']['id']
    catalog['sources'].append(deepcopy(review['source']))
    for entry, members, gaps in plans:
        early = {}
        for x in entry['stageFeatures']:
            stage = stages[x['stageId']]
            index = next(i for i, f in enumerate(stage['features']) if f['id'] == x['featureId'])
            original = stage['features'].pop(index)
            if not x['outside']:
                early[x['stageId']] = original
        for stage_id, original in early.items():
            for k, coords in enumerate(gaps):
                stages[stage_id]['features'].append({**{key: original[key] for key in ['kind', 'name', 'width', 'traceId'] if key in original},
                                                     'id': f"{original['id']}:frame-gap:{k}", 'frameGap': True, 'paths': [coords]})
        for o, m, first, paths in members:
            aid = o['id'] + ':frame-photo-1942'
            o['evidence'].append(dict(id=aid, sourceId=review['aerialSourceId'], describes={'from': 1942, 'to': 1943},
                                      supports=['geometry', 'state', 'identity'], observationType='aerial', observedAt='1942-07-25',
                                      outcome='present', imageCoverage='visible', matchedGeometryId=first['geometryId'],
                                      interpretation=True, constructionYear=None, note=m['note'], reviewId=source_id,
                                      sourceTraceId=entry['traceId']))
            o['states'].insert(0, dict(state='open', **{'from': 1942, 'to': m['originalFrom']}, evidenceIds=[aid],
                                       certainty='inferred', note=m['note'] + ' Fotoåret är belägg, inte byggår.'))
            period = {k: deepcopy(v) for k, v in first.items() if k in ['geometryId', 'coverage', 'canonicalRange']}
            o['geometryPeriods'].insert(0, dict(**period, **{'from': 1942, 'to': m['originalFrom']}, evidenceIds=[aid],
                                                certainty='inferred', basis=entry['basis']))
            for stage_id in EARLY_STAGES:
                stage = stages[stage_id]
                if any(f.get('objectId') == o['id'] for f in stage['features']):
                    continue  # already drawn there by an earlier review (Köpmansgatan from 1952)
                fid = f"{stage_id}:frame-1942:{o['id']}"
                stage['features'].append(dict(id=fid, objectId=o['id'], name=o['name'], kind='street', width=8,
                                              sourceFeatureId=entry['traceId'], paths=deepcopy(paths)))
                o['sourceLinks'].append(dict(datasetId=stage_id, featureId=fid))
            o['frame1942'] = dict(reviewedAt=review['reviewedAt'], traceId=entry['traceId'], originalFrom=m['originalFrom'], constructionYear=None)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
