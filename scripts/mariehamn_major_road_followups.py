"""Second Mariehamn larger-road pass: changed junctions, removed alignments, roundabouts and more streets.

All reconciliation happens here at build time. The review file stores exact modern members,
city-stage links, snapshot originals and, for vanished alignments, the raw scan trace together
with the reconstructed display line. Nothing is mutated before every check has passed.
"""
from copy import deepcopy
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, substring
from shapely.geometry import MultiLineString
from historical_map_observations import load_review
from mariehamn_south_streets import digest
from postwar_city import METRIC

YEARS = [1968, 1978, 1985, 1995]
KINDS = {'section', 'carriageways', 'approach', 'roundabout', 'partial-section', 'realigned-section', 'abandoned-section'}
TRACE_LIMIT = 25      # metres between a reconstructed line and its raw scan samples
ANCHOR_LIMIT = 1.0    # metres between a reconstructed end and the modern junction it joins
PARALLEL_LIMIT = 60   # metres between members of one approach or carriageway pair


def metric(path):
    return LineString([METRIC(*p) for p in path])


def merged(paths):
    line = linemerge(MultiLineString([[METRIC(*p) for p in path] for path in paths]))
    if line.geom_type != 'LineString' or not line.is_simple:
        raise ValueError('Reviewed section is not one continuous line')
    return line


FOLLOWUPS = dict(path='data/mariehamn-major-road-followups.json', idPrefix='road:mariehamn:major-followup:',
                 geometryPrefix='geometry:city-major-followup:', marker='majorRoadFollowup', requires='majorRoadReview')


def apply_major_road_followups(read, catalog):
    apply_reviewed_streets(read, catalog, FOLLOWUPS)


def apply_reviewed_streets(read, catalog, cfg):
    """Shared validator and writer for the reviewed Mariehamn street passes (second pass and later)."""
    review = read(cfg['path'])
    first_pass = read('data/mariehamn-major-roads.json')
    modern = {f['id']: f for f in read('dist/assets/modern.json.gz')['features']}
    stages = read('dist/assets/mariehamn-city-grid.json')['sets']
    stage_features = {(s['id'], f['id']): f for s in stages for f in s['features']}
    snapshots = {y: {f['id']: f for f in read(f'dist/assets/roads-{y}.json.gz')['features']} for y in [2014, 2021, 2025]}
    objects = {o['id']: o for o in catalog['objects']}
    sources = {s['id'] for s in catalog['sources']}
    occupied = {(l['datasetId'], l['featureId']) for o in objects.values() for l in o['sourceLinks']}
    if review['schemaVersion'] != 1 or review['sheets'] != first_pass['sheets'] or any(s['sourceId'] not in sources for s in review['sheets']):
        raise ValueError('Follow-up review must use the verified first-pass map sheets')
    if not any(o.get(cfg['requires']) for o in objects.values()):
        raise ValueError('Earlier larger-road pass must be applied first')
    sheet_ids = {s['year']: s['sourceId'] for s in review['sheets']}
    _, registrations = load_review(read)
    used, owned_modern, total = set(objects), set(), 0
    for d in review['decisions']:
        if d['id'] in used or not d['id'].startswith(cfg['idPrefix']) or d['kind'] not in KINDS or not d['basis']:
            raise ValueError('Duplicate or unclassified follow-up road')
        used.add(d['id'])
        ids = [m['feature']['id'] for m in d['members']]
        if len(set(ids)) != len(ids) or set(ids) & owned_modern or not set(d['display']) <= set(ids):
            raise ValueError('Modern road member owned twice')
        owned_modern.update(ids)
        if bool(ids) == (d['kind'] == 'abandoned-section'):
            raise ValueError('Removed alignment cannot own modern roads, and kept roads must')
        expected = set()
        for member in d['members']:
            f = modern[member['feature']['id']]
            if f != member['feature'] or digest(f) != member['inputHash'] or f['kind'] != 'road' or len(f['paths']) != 1:
                raise ValueError('Changed modern road input')
            expected.update(k for k, sf in stage_features.items() if sf['kind'] == 'street' and sf['paths'] == f['paths'])
        links = {(l['datasetId'], l['featureId']) for l in d['modernLinks']}
        if links != expected or len(links) != len(d['modernLinks']) or links & occupied:
            raise ValueError('Missing or duplicate normalized road ownership')
        for l in d['modernLinks']:
            if digest(stage_features[(l['datasetId'], l['featureId'])]) != l['inputHash']:
                raise ValueError('Changed city-stage source')
        occupied.update(links)
        keys = set()
        for o in d['originals']:
            raw = snapshots[o['year']].get(o['feature']['id'])
            if raw != o['feature'] or digest(raw) != o['inputHash'] or raw.get('osmId') not in ids or (o['year'], raw['id']) in keys or o['datasetId'] != 'city-' + str(o['year']):
                raise ValueError('Changed original source record')
            keys.add((o['year'], raw['id']))
        seen = {(o['year'], o['feature']['osmId']) for o in d['originals']}
        missing = {(y, u['modernFeatureId']) for u in d['unobservedOriginals'] for y in u['years']}
        if seen | missing != {(y, w) for w in ids for y in [2014, 2021, 2025]} or seen & missing:
            raise ValueError('Missing original-source uncertainty')
        display_paths = [modern[w]['paths'][0] for w in d['display']]
        if d['kind'] in {'section', 'partial-section', 'realigned-section'}:
            modern_line = merged(display_paths)
        elif display_paths:
            modern_line = None
            for w in ids:
                if min(metric(modern[w]['paths'][0]).distance(metric(p)) for p in display_paths) > (0 if w in d['display'] else PARALLEL_LIMIT):
                    raise ValueError('Parallel member is not part of the same junction')
            if d['kind'] in {'carriageways', 'approach'} and any(metric(modern[a]['paths'][0]).hausdorff_distance(metric(modern[b]['paths'][0])) > PARALLEL_LIMIT for a in ids for b in ids if a < b and a in d['display'] and b in d['display'] and d['countRule'] == 'longest'):
                raise ValueError('Carriageways diverge beyond one junction')
        # Chronology. Map years are evidence; states and geometry periods are explicit.
        obs = d['observations']
        if [o['year'] for o in obs] != YEARS or any(o['outcome'] not in {'present', 'absent', 'unclear'} or o['coverage'] not in {'full', 'partial', 'unknown'} or (o['outcome'] == 'present') == (o['coverage'] == 'unknown') for o in obs):
            raise ValueError('Incomplete map chronology')
        present = [o['year'] for o in obs if o['outcome'] == 'present']
        if not present or d['firstYear'] != present[0] or any(o['outcome'] == 'present' for o in obs if o['year'] < d['firstYear']):
            raise ValueError('Road start is not its first reviewed map evidence')
        states, phases = d['states'], d['phases']
        for seq in (states, phases):
            if seq[0]['from'] != d['firstYear'] or any(a['to'] != b['from'] for a, b in zip(seq, seq[1:])):
                raise ValueError('Gapped or undated road periods')
        if states[0]['state'] != 'open' or any(s['state'] not in {'open', 'abandoned'} for s in states):
            raise ValueError('Unsupported road state')
        open_until = next((s['from'] for s in states if s['state'] == 'abandoned'), None)
        if phases[-1]['to'] != open_until or (open_until is not None and (states[-1] != {'state': 'abandoned', 'from': open_until, 'to': None}
                                                                         or any(o['outcome'] == 'present' for o in obs if o['year'] >= open_until)
                                                                         or not any(o['outcome'] == 'absent' and o['year'] == open_until for o in obs))):
            raise ValueError('Removal must follow the first edition without the road')
        if open_until is None and any(o['outcome'] == 'absent' for o in obs if o['year'] >= d['firstYear']):
            raise ValueError('Kept road is missing from a later edition')
        for ph in phases:
            g = ph['geometry']
            if not ph['basis']:
                raise ValueError('Undocumented geometry period')
            if g == 'modern':
                if not display_paths:
                    raise ValueError('Removed alignment has no modern geometry')
            elif g.startswith('reconstructed:'):
                line = metric(ph['paths'][0]); trace = ph['trace']
                if len(ph['paths']) != 1 or not line.is_simple or trace['year'] != ph['from'] or trace['ref']['sourceId'] != sheet_ids[trace['year']]:
                    raise ValueError('Reconstructed alignment lacks its dated scan trace')
                year_sheet = registrations.get(f"nls-mariehamn-{trace['year']}")
                if year_sheet and year_sheet[0]['originalSha256'] != trace['ref']['sourceSha256']:
                    raise ValueError('Changed scan behind reconstructed alignment')
                # Samples beyond the junction anchors belong to the neighbouring roads.
                samples = [s for s in (Point(METRIC(*p)) for p in trace['points']) if 0 < line.project(s) < line.length]
                if len(samples) < 5 or max(line.distance(s) for s in samples) > TRACE_LIMIT:
                    raise ValueError('Reconstructed line departs from its scan trace')
                ends = [ph['paths'][0][0], ph['paths'][0][-1]]
                if [a['point'] for a in ph['anchors']] != ends or any(metric(modern[a['way']]['paths'][0]).distance(Point(METRIC(*a['point']))) > ANCHOR_LIMIT for a in ph['anchors']):
                    raise ValueError('Reconstructed alignment is not anchored to the modern junctions')
            elif g.startswith('substring:'):
                base = LineString(modern[ids[0]]['paths'][0]); a, b = ph['range']
                expected_paths = [[list(map(lambda v: round(v, 7), c)) for c in substring(base, a, b, normalized=True).coords]]
                if len(ids) != 1 or ph['paths'] != expected_paths or not 0 <= a < b < 1:
                    raise ValueError('Partial extent does not follow its modern road')
                if not any(o['coverage'] == 'partial' and ph['from'] <= o['year'] < (ph['to'] or 9999) for o in obs):
                    raise ValueError('Partial geometry needs a partial map observation')
            else:
                raise ValueError('Unknown geometry kind')
        for o in obs:
            ph = next((p for p in phases if p['from'] <= o['year'] and (p['to'] is None or o['year'] < p['to'])), None)
            if (o['outcome'] == 'present') != (ph is not None) or (o['coverage'] == 'partial') != (ph is not None and ph['geometry'].startswith('substring:')):
                raise ValueError('Map observation and displayed geometry disagree')
        # Counted length; parallel lanes are reported but never counted twice.
        rule = d['countRule']; disp = [metric(p) for p in display_paths]
        length = (sum(x.length for x in disp) if rule == 'display' else max(x.length for x in disp) if rule == 'longest'
                  else disp[0].length + max(x.length for x in disp[1:]) if rule == 'stem-plus-longest' else 0 if rule == 'parallel'
                  else metric(phases[0]['paths'][0]).length if rule == 'reconstructed' else None)
        if length is None or round(length, 2) != d['lengthMeters'] or (rule == 'reconstructed') != any(p['geometry'].startswith('reconstructed:') for p in phases):
            raise ValueError('Incorrect reviewed road length')
        total += d['lengthMeters']
    t = review['totals']
    if round(total, 2) != t['newPersistentMeters'] or t['confirmedExistingMeters'] != 0 or t['reviewedMeters'] != t['newPersistentMeters']:
        raise ValueError('Incorrect review totals')

    # All checks passed. Add objects; earlier objects are never modified.
    if review['source']['id'] in sources:
        raise ValueError('Follow-up review already applied')
    catalog['sources'].append(deepcopy(review['source']))
    src = review['source']['id']
    for d in review['decisions']:
        oid = d['id']; prefix = cfg['geometryPrefix'] + oid.rsplit(':', 1)[1]
        interp = oid + ':interpretation'
        evidence = [dict(id=interp, sourceId=src, describes={'from': d['firstYear'], 'to': None}, supports=['identity', 'state'], observationType='interpretation', interpretation=True, constructionYear=None, note=d['basis'])]
        geometry_ids = {}
        for i, ph in enumerate(d['phases']):
            gid = f'{prefix}:phase-{i}'
            paths = display_geometry([modern[w]['paths'][0] for w in d['display']]) if ph['geometry'] == 'modern' else ph['paths']
            kind = ph['geometry'].split(':')[0]
            note = {'modern': 'Stabil modern detaljgeometri i den visuellt granskade vägkorridoren. Ingen historisk körfälts- eller breddmätning.',
                    'reconstructed': 'Avritad historisk sträckning mellan moderna knutpunkter. Den råa avritningen sparas separat som källgeometri.',
                    'substring': 'Den del av den moderna vägen som kartan visar i samma korridor.'}[kind]
            catalog['geometries'].append(dict(id=gid, representation='centerline', paths=deepcopy(paths), sourceIds=[ph['trace']['ref']['sourceId']] if kind == 'reconstructed' else ['city-2026'], note=note))
            geometry_ids[i] = gid
            if ph['geometry'].startswith('reconstructed:'):
                tid = f'{prefix}:trace-{i}'
                catalog['geometries'].append(dict(id=tid, representation='centerline', paths=[deepcopy(ph['trace']['points'])], sourceIds=[ph['trace']['ref']['sourceId']], note='Oförändrade avritningspunkter ur originalskanningen. ' + ph['trace']['note']))
                evidence.append(dict(id=f'{oid}:trace-{i}', sourceId=ph['trace']['ref']['sourceId'], describes={'from': ph['trace']['year'], 'to': ph['trace']['year'] + 1}, supports=['geometry', 'location'], observationType='printed-map-review', outcome='present', coverage='full', canonicalRange=[0, 1], interpretation=True, originalGeometryId=tid, matchedGeometryId=gid, note=ph['basis']))
        for o in d['observations']:
            y = o['year']; ph = next((i for i, p in enumerate(d['phases']) if p['from'] <= y and (p['to'] is None or y < p['to'])), None)
            e = dict(id=f'{oid}:map-{y}', sourceId=sheet_ids[y], describes={'from': y, 'to': y + 1}, observationType='printed-map-review', outcome=o['outcome'], coverage=o['coverage'], interpretation=True,
                     note=o['note'] or (d['basis'] if o['outcome'] == 'present' else 'Inte belagd i denna utgåva.'))
            if o['outcome'] == 'present':
                e.update(supports=['geometry', 'identity', 'state'], matchedGeometryId=geometry_ids[ph], canonicalRange=d['phases'][ph].get('range', [0, 1]))
            else:
                e['supports'] = ['state'] if o['outcome'] == 'absent' else ['location']
            evidence.append(e)
        for i, original in enumerate(d['originals']):
            ogid = f'{prefix}:original-{i}'
            catalog['geometries'].append(dict(id=ogid, representation='centerline', paths=deepcopy(original['feature']['paths']), sourceIds=[original['datasetId']], note='Oförändrad ursprunglig OSM-geometri.'))
            evidence.append(dict(id=f'{oid}:original-{i}', sourceId=original['datasetId'], describes={'from': original['year'], 'to': original['year'] + 1}, supports=['identity', 'geometry'], originalGeometryId=ogid, sourceFeatureId=original['feature']['id'], note='Ursprungligt namn och sträckning bevaras som källa.'))
        for i, member in enumerate(d['members']):
            ogid = f'{prefix}:modern-original-{i}'
            catalog['geometries'].append(dict(id=ogid, representation='centerline', paths=deepcopy(member['feature']['paths']), sourceIds=['city-2026'], note='Oförändrad modern källform.'))
            evidence.append(dict(id=f'{oid}:modern-{i}', sourceId='city-2026', describes={'from': 2026, 'to': None}, supports=['identity', 'geometry'], originalGeometryId=ogid, sourceFeatureId=member['feature']['id'], note='Modern källa, inte ett historiskt öppningsdatum.'))

        def refs(start):
            return [interp] + [f'{oid}:map-{o["year"]}' for o in d['observations'] if o['year'] == start] + [f'{oid}:trace-{i}' for i, p in enumerate(d['phases']) if p['from'] == start and p['geometry'].startswith('reconstructed:')]
        first = d['members'][0]['feature'] if d['members'] else None
        obj = dict(id=oid, name=d['name'], kind='roadSegment', routeId=d['routeId'], independentRoad=True,
                   modernRoadClass=first['class'] if first else 'secondary', roadWidth=8 if first and first['class'] in ['primary', 'secondary'] else 6,
                   states=[dict(state=s['state'], **{'from': s['from'], 'to': s['to']}, certainty='inferred', evidenceIds=refs(s['from']),
                                note=d['basis'] if s['state'] == 'open' else 'Första granskade utgåva utan sträckningen. Inget exakt rivningsår antas.') for s in d['states']],
                   geometryPeriods=[dict(geometryId=geometry_ids[i], **{'from': p['from'], 'to': p['to']}, certainty='inferred', evidenceIds=refs(p['from']), coverage='partial' if 'range' in p else 'full', canonicalRange=p.get('range', [0, 1]), basis=p['basis']) for i, p in enumerate(d['phases'])],
                   evidence=evidence, sourceLinks=[dict(datasetId=l['datasetId'], featureId=l['featureId']) for l in d['modernLinks']],
                   **{cfg['marker']: dict(reviewedAt=review['reviewedAt'], constructionYear=None, group=d['group'], kind=d['kind'], lengthMeters=d['lengthMeters'], countRule=d['countRule'], modernMembers=[m['feature']['id'] for m in d['members']])})
        catalog['objects'].append(obj)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])


def display_geometry(paths):
    """One line where the members join end to end; otherwise the members as drawn (ring arcs, refuge lanes)."""
    line = linemerge(MultiLineString(paths))
    if line.geom_type == 'LineString':
        return [[list(c) for c in line.coords]]
    return [deepcopy(p) for p in paths]
