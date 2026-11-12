"""Reviewed 1942 approach-road traces: reject an unsupported trace and move real roads onto their objects.

The three hand traces of the 1942 orthophoto are coarse (12–13 points over 2–3 km, drawn at 4 m/px).
`data/mariehamn-approaches-1942.json` records the visual review against the original photo:

* a rejected trace is removed from every city stage (its original pixels stay in the source files);
* for a real approach, each persistent road object that the photo shows in the same place gets the
  photo as 1942 evidence and is shown from 1942 with its own centre line. The raw trace is kept only in
  short gaps where no object corresponds to the 1942 road, and only in the 1942 and 1952 stages. From
  1968 the dated objects show the roads, so the trace's carried-over parts are removed.

Everything is validated before the catalogue is touched; no earlier date is moved later.
"""
from copy import deepcopy
import hashlib
import json
from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import substring

TO_METRIC = Transformer.from_crs(4326, 3874, always_xy=True).transform
TO_GEO = Transformer.from_crs(3874, 4326, always_xy=True).transform
EARLY_STAGES = {'city-reconstruction-1942', 'city-reconstruction-1952'}
MIN_REMAINDER = 20  # metres; shorter trace leftovers between objects are not shown


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def fingerprint(o):
    return digest({k: o.get(k) for k in ['id', 'kind', 'states', 'geometryPeriods', 'sourceLinks']})


def geo(points):
    return [[round(x, 7), round(y, 7)] for x, y in (TO_GEO(*p) for p in points)]


def trace_line(entry, reference):
    return LineString([(reference['west'] + x * reference['metersPerViewPixel'],
                        reference['north'] - y * reference['metersPerViewPixel']) for x, y in entry['pixels']])


def remainders(trace, intervals, retraced, snap_limit, drop_tail):
    """Trace pieces outside the object intervals, with ends moved onto the adjoining object ends.

    Where the review retraced a gap from the photo (both ends on the adjoining object ends), the
    retraced centre line replaces the coarse trace for that gap."""
    intervals = sorted(intervals)
    merged = []
    for a, b, ea, eb in intervals:
        if merged and a <= merged[-1][1] + 1:
            if b > merged[-1][1]:
                merged[-1] = (merged[-1][0], b, merged[-1][2], eb)
        else:
            merged.append((a, b, ea, eb))
    gaps, cursor, start_point = [], 0.0, None
    for a, b, ea, eb in merged:
        gaps.append((cursor, a, start_point, ea))
        cursor, start_point = b, eb
    if not drop_tail:
        gaps.append((cursor, trace.length, start_point, None))
    out, used = [], set()
    for a, b, pa, pb in gaps:
        match = [i for i, r in enumerate(retraced) if pa is not None and pb is not None
                 and Point(r[0]).distance(Point(pa)) < 1 and Point(r[-1]).distance(Point(pb)) < 1]
        if match:
            used.add(match[0]); out.append([pa, *retraced[match[0]][1:-1], pb]); continue
        if b - a < MIN_REMAINDER:
            continue
        coords = list(substring(trace, a, b).coords)
        for index, point in [(0, pa), (-1, pb)]:
            if point is None:
                continue
            if Point(coords[index]).distance(Point(point)) > snap_limit:
                raise ValueError('1942 remainder does not reach the adjoining object')
            coords[index] = point
        out.append(coords)
    if used != set(range(len(retraced))):
        raise ValueError('Retraced 1942 gap does not join its reviewed objects')
    return out


def apply_approaches_1942(read, catalog):
    review = read('data/mariehamn-approaches-1942.json')
    objects = {o['id']: o for o in catalog['objects']}
    geometries = {g['id']: g for g in catalog['geometries']}
    stages = {s['id']: s for s in catalog['cityStages']}
    sources = {s['id'] for s in catalog['sources']}
    city = next(s for s in read('data/mariehamn-city-traces.json')['sets'] if s['id'] == 'city-1942')
    photo = next(s for s in read('data/historical-road-traces.json')['sets'] if s['id'] == 'photo-1942')
    if review['schemaVersion'] != 1 or review['source']['id'] in sources or review['aerialSourceId'] not in sources:
        raise ValueError('1942 approach review already applied or missing its aerial source')
    reference = city['reference']
    if photo['reference'] != reference:
        raise ValueError('Changed 1942 trace georeferencing')

    def check_trace(entry):
        raw = next((t for t in city['roads'] if t['traceId'] == entry['traceId']), None)
        feature = next((f for f in photo['features'] if f['id'] == entry['photoFeatureId']), None)
        if (raw is None or feature is None or digest(raw) != entry['inputHash'] or raw['pixels'] != entry['pixels']
                or feature['pixels'] != entry['pixels'] or raw['name'] != entry['name']):
            raise ValueError('Changed original 1942 trace ' + entry['traceId'])
        found = {(s['id'], f['id']) for s in catalog['cityStages'] for f in s['features'] if f.get('traceId') == entry['traceId']}
        listed = {(x['stageId'], x['featureId']) for x in entry['stageFeatures']}
        if found != listed:
            raise ValueError('Unreviewed city-stage copy of ' + entry['traceId'])
        for x in entry['stageFeatures']:
            f = next(f for f in stages[x['stageId']]['features'] if f['id'] == x['featureId'])
            if digest(f) != x['inputHash'] or f.get('objectId') or (':outside:' in f['id']) != x['outside'] \
                    or (not x['outside'] and x['stageId'] not in EARLY_STAGES):
                raise ValueError('Changed city-stage trace ' + x['featureId'])

    for entry in review['rejected']:
        check_trace(entry)
        if not entry['basis']:
            raise ValueError('Rejected trace needs a basis')

    plans, seen = [], set()
    for entry in review['approaches']:
        check_trace(entry)
        trace = trace_line(entry, reference)
        intervals, members = [], []
        for m in entry['members']:
            o = objects.get(m['objectId'])
            if (o is None or m['objectId'] in seen or fingerprint(o) != m['inputHash'] or o.get('kind') != 'roadSegment'
                    or o['states'][0]['state'] != 'open' or o['states'][0]['from'] != m['originalFrom']
                    or m['originalFrom'] <= 1942 or o['geometryPeriods'][0]['from'] != m['originalFrom'] or not m['note']):
                raise ValueError('Changed or repeated 1942 approach object ' + m['objectId'])
            seen.add(m['objectId'])
            first = o['geometryPeriods'][0]
            paths = geometries[first['geometryId']]['paths']
            if len(paths) != 1:
                raise ValueError('1942 approach object must be one line: ' + m['objectId'])
            line = LineString([TO_METRIC(*p) for p in paths[0]])
            ends = [line.coords[0], line.coords[-1]]
            (a, pa), (b, pb) = sorted((trace.project(Point(p)), p) for p in ends)
            observed = substring(trace, a, b)
            if b - a < 1 or line.hausdorff_distance(observed) > entry['maxDeviationMeters']:
                raise ValueError('1942 trace does not follow object ' + m['objectId'])
            intervals.append((a, b, pa, pb))
            members.append((o, m, first, paths))
        ends = {m['objectId']: [tuple(p) for p in (lambda q: [q[0], q[-1]])([TO_METRIC(*c) for c in geometries[objects[m['objectId']]['geometryPeriods'][0]['geometryId']]['paths'][0]])] for m in entry['members']}
        retraced = []
        for gap in entry.get('retracedGaps', []):
            line = LineString(gap['epsg3874'])
            if (not gap['basis'] or gap['fromObjectId'] not in ends or gap['toObjectId'] not in ends or not line.is_simple
                    or min(Point(gap['epsg3874'][0]).distance(Point(p)) for p in ends[gap['fromObjectId']]) > 1
                    or min(Point(gap['epsg3874'][-1]).distance(Point(p)) for p in ends[gap['toObjectId']]) > 1
                    or line.hausdorff_distance(substring(trace, *sorted(trace.project(Point(p)) for p in [line.coords[0], line.coords[-1]]))) > entry['maxDeviationMeters']):
                raise ValueError('Invalid retraced 1942 gap')
            retraced.append([tuple(p) for p in gap['epsg3874']])
        pieces = remainders(trace, intervals, retraced, entry['snapMeters'], entry['dropTail'])
        plans.append((entry, members, pieces))

    # All checks passed. Change the catalogue.
    source_id = review['source']['id']
    catalog['sources'].append(deepcopy(review['source']))
    for entry in review['rejected']:
        for x in entry['stageFeatures']:
            stage = stages[x['stageId']]
            stage['features'] = [f for f in stage['features'] if f['id'] != x['featureId']]
    for entry, members, pieces in plans:
        early = [x for x in entry['stageFeatures'] if not x['outside']]
        for x in entry['stageFeatures']:
            stage = stages[x['stageId']]
            index = next(i for i, f in enumerate(stage['features']) if f['id'] == x['featureId'])
            original = stage['features'].pop(index)
            if x['outside']:
                continue  # Dated objects show the road from 1968.
            for k, coords in enumerate(pieces):
                stage['features'].insert(index + k, {**{key: original[key] for key in ['kind', 'name', 'width', 'traceId'] if key in original},
                                                     'id': f"{x['featureId']}:approach-gap:{k}",
                                                     'approachGap': True, 'paths': [geo(coords)]})
            # (retraced gaps carry the photo centre line; the others are the reviewed trace remainder)
        for o, m, first, paths in members:
            aid = o['id'] + ':approach-photo-1942'
            o['evidence'].append(dict(id=aid, sourceId=review['aerialSourceId'], describes={'from': 1942, 'to': 1943},
                                      supports=['geometry', 'state', 'identity'], observationType='aerial', observedAt='1942-07-25',
                                      outcome='present', imageCoverage='visible', matchedGeometryId=first['geometryId'],
                                      interpretation=True, constructionYear=None, note=m['note'],
                                      reviewId=source_id, sourceTraceId=entry['traceId']))
            o['states'].insert(0, dict(state='open', **{'from': 1942, 'to': m['originalFrom']}, evidenceIds=[aid],
                                       certainty='inferred', note=m['note'] + ' Kartåret är belägg, inte byggår.'))
            period = {k: deepcopy(v) for k, v in first.items() if k in ['geometryId', 'coverage', 'canonicalRange']}
            o['geometryPeriods'].insert(0, dict(**period, **{'from': 1942, 'to': m['originalFrom']}, evidenceIds=[aid],
                                                certainty='inferred', basis=entry['basis']))
            for x in early:
                stage = stages[x['stageId']]
                fid = f"{x['stageId']}:approach-1942:{o['id']}"
                stage['features'].append(dict(id=fid, objectId=o['id'], name=o['name'], kind='street', width=8,
                                              sourceFeatureId=entry['traceId'], paths=deepcopy(paths)))
                o['sourceLinks'].append(dict(datasetId=x['stageId'], featureId=fid))
            o['approach1942'] = dict(reviewedAt=review['reviewedAt'], traceId=entry['traceId'], originalFrom=m['originalFrom'], constructionYear=None)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
