"""Hamngatan and Parkgatan before 1968: two unlinked streets of the museum's 1920s picture.

`data/mariehamn-museum-streets.json` records a visual review of the 1942, 1952, 1962, 1975, 1991 and 2021 orthophotos
and the 1968 and 1985 base maps (docs/reviews/mariehamn-hamngatan-parkgatan-2026-11-17/). The museum picture's
"Gata längs västra kvarteren" is a coarse drawing of Hamngatan and its "Gata söderut vid östra stranden" one of
Parkgatan. The photos show both streets in 1942, but the catalogue starts most of their parts at the 1968 base map,
and the northern stretch of Hamngatan (Norragatan to the junction) had no object at all.

* Every member keeps its own measured centre line. It gets the museum drawing (1920, decade precision,
  interpretation) as evidence and a state from 1920. A member that started in 1968 also gets the 1942 photo as evidence
  and a state 1942–1968. Its first geometry period starts in 1920. Where the drawing covers only the start of a member
  (`museumRange`, checked against `cutLatitude`), the 1920s period shows only that part (`coverage: partial`) and the
  whole line follows from the photo year.
* Hamngatan's northern stretch becomes one persistent object from today's four OSM pieces, which are identical in the
  2014–2026 street sets. The pieces become its source links, so the raw modern lines are no longer drawn separately.
  It gets the museum, 1942 photo and 1968/1985 base-map evidence.
* Each museum drawing becomes a source of one member (the longest match) and its original geometry. Its raw copies in
  the 1920 and 1927 city stages are removed.

Everything is validated before the catalogue changes. The museum, photo and map years are evidence, not construction
years.
"""
from copy import deepcopy
from shapely.geometry import LineString, Point
from shapely.ops import substring
from mariehamn_frame_1942 import digest, fingerprint, TO_METRIC, TO_GEO


def _line(path):
    return LineString([TO_METRIC(*p) for p in path])


def apply_museum_streets(read, catalog):
    review = read('data/mariehamn-museum-streets.json')
    objects = {o['id']: o for o in catalog['objects']}
    geometries = {g['id']: g for g in catalog['geometries']}
    stages = {s['id']: s for s in catalog['cityStages']}
    sources = {s['id'] for s in catalog['sources']}
    museum_year, photo_year = review['museumYear'], review['photoYear']
    needed = [review['aerialSourceId'], review['museumDatasetId'], review['modernSourceId']] + [m['sourceId'] for m in review['mapEvidence']]
    if review['schemaVersion'] != 1 or review['source']['id'] in sources or any(s not in sources for s in needed) or not museum_year < photo_year:
        raise ValueError('Museum street review already applied or missing a source')
    grid = {f['id']: f for s in read('dist/assets/mariehamn-city-grid.json')['sets'] for f in s['features']}
    owned = {(l['datasetId'], l['featureId']): o['id'] for o in catalog['objects'] for l in o.get('sourceLinks', [])}
    plans = []
    for street in review['streets']:
        raw = grid.get(street['featureId'])
        if raw is None or digest(raw) != street['inputHash'] or raw.get('traceId') != street['traceId'] or not street['basis']:
            raise ValueError('Changed museum drawing ' + street['featureId'])
        drawing = _line(raw['paths'][0])
        found = {(s['id'], f['id']) for s in catalog['cityStages'] for f in s['features'] if f.get('traceId') == street['traceId']}
        if found != {(x['stageId'], x['featureId']) for x in street['stageFeatures']}:
            raise ValueError('Unreviewed city-stage copy of ' + street['featureId'])
        for x in street['stageFeatures']:
            f = next(f for f in stages[x['stageId']]['features'] if f['id'] == x['featureId'])
            if digest(f) != x['inputHash'] or f.get('objectId'):
                raise ValueError('Changed city-stage copy ' + x['featureId'])
        if street['linkObjectId'] not in [m['objectId'] for m in street['members']]:
            raise ValueError('The museum drawing must belong to a member: ' + street['featureId'])
        members = []
        for m in street['members']:
            o = objects.get(m['objectId'])
            if (o is None or o.get('kind') != 'roadSegment' or fingerprint(o) != m['inputHash']
                    or o['states'][0]['from'] != m['originalFrom'] or o['geometryPeriods'][0]['from'] != m['originalFrom']
                    or any(s['state'] != 'open' for s in o['states']) or m['originalFrom'] not in (photo_year, 1968) or not m['note']):
                raise ValueError('Changed museum street member ' + m['objectId'])
            if m['originalFrom'] == photo_year and not any(e.get('observationType') == 'aerial' and e['describes']['from'] == photo_year for e in o['evidence']):
                raise ValueError('A member open from the photo year needs its photo evidence: ' + m['objectId'])
            g = geometries[o['geometryPeriods'][0]['geometryId']]
            part = None
            if 'museumRange' in m:
                a, b = m['museumRange']
                if len(g['paths']) != 1 or not (a == 0 and 0 < b < 1) or m['originalFrom'] <= photo_year:
                    raise ValueError('Invalid museum range ' + m['objectId'])
                line = _line(g['paths'][0])
                cut = TO_GEO(*line.interpolate(b, normalized=True).coords[0])
                if abs(cut[1] - m['cutLatitude']) > 0.00002:
                    raise ValueError('Museum range cut moved ' + m['objectId'])
                part = [[round(v, 7) for v in TO_GEO(x, y)] for x, y in substring(line, 0, b, normalized=True).coords]
            pts = part or [p for path in g['paths'] for p in path]
            far = max(drawing.distance(Point(TO_METRIC(*p))) for p in pts)
            if far > street['maxDistanceMeters']:
                raise ValueError(f"Member not near the museum drawing ({far:.0f} m): {m['objectId']}")
            members.append((o, m, part))
        new = []
        for n in street.get('newObjects', []):
            if n['id'] in objects:
                raise ValueError('New museum street object exists: ' + n['id'])
            for piece in n['pieces']:
                for x in piece['features']:
                    f = grid.get(x['featureId'])
                    if f is None or digest(f['paths']) != piece['pathHash'] or f.get('name') != n['name'] or (x['datasetId'], x['featureId']) in owned:
                        raise ValueError('Changed or owned modern piece ' + x['featureId'])
            paths = [grid[piece['features'][0]['featureId']]['paths'][0] for piece in n['pieces']]
            if any(a[-1] != b[0] for a, b in zip(paths, paths[1:])):
                raise ValueError('Modern pieces do not form one line: ' + n['id'])
            line = deepcopy(paths[0]) + [deepcopy(p) for path in paths[1:] for p in path[1:]]
            join = objects.get(n['joinsObjectId'])
            if join is None or Point(TO_METRIC(*line[0])).distance(_line(geometries[join['geometryPeriods'][-1]['geometryId']]['paths'][0])) > 1:
                raise ValueError('New object does not join its neighbour: ' + n['id'])
            new.append((n, line))
        plans.append((street, raw, members, new))

    # All checks passed. Change the catalogue.
    source_id = review['source']['id']
    catalog['sources'].append(deepcopy(review['source']))
    marker = dict(reviewedAt=review['reviewedAt'], constructionYear=None)
    for street, raw, members, new in plans:
        for x in street['stageFeatures']:
            stage = stages[x['stageId']]
            stage['features'] = [f for f in stage['features'] if f['id'] != x['featureId']]
        raw_gid = f"geometry:museum-streets:{street['key']}:museum-{museum_year}"
        catalog['geometries'].append(dict(id=raw_gid, paths=deepcopy(raw['paths']), representation='centerline',
                                          sourceIds=[review['museumDatasetId']], note='Museikartans ursprungliga avritning; ungefärligt inpassad.'))

        def museum_evidence(oid):
            return dict(id=oid + f':museum-{museum_year}', sourceId=review['museumDatasetId'],
                        describes={'from': museum_year, 'to': museum_year + 10}, supports=['identity', 'state'],
                        observationType='map', outcome='present', originalGeometryId=raw_gid, sourceFeatureId=raw['id'],
                        sourceTraceId=street['traceId'], interpretation=True, datePrecision='decade', constructionYear=None,
                        reviewId=source_id, note=street['basis'])

        def photo_evidence(oid, gid, note):
            return dict(id=oid + f':street-photo-{photo_year}', sourceId=review['aerialSourceId'],
                        describes={'from': photo_year, 'to': photo_year + 1}, supports=['geometry', 'state', 'identity'],
                        observationType='aerial', observedAt=review['photoObservedAt'], outcome='present',
                        imageCoverage='visible', matchedGeometryId=gid, interpretation=True, constructionYear=None,
                        reviewId=source_id, note=note)

        for o, m, part in members:
            first = o['geometryPeriods'][0]
            gid = first['geometryId']
            mus = museum_evidence(o['id'])
            o['evidence'].append(mus)
            if o['id'] == street['linkObjectId']:  # a source feature belongs to one object
                o['sourceLinks'].append(dict(datasetId=review['museumDatasetId'], featureId=raw['id']))
            early = [dict(state='open', **{'from': museum_year, 'to': photo_year}, evidenceIds=[mus['id']],
                          certainty='inferred', note=street['basis'])]
            ids = [mus['id']]
            if m['originalFrom'] > photo_year:
                ph = photo_evidence(o['id'], gid, m['note'])
                o['evidence'].append(ph)
                ids.append(ph['id'])
                early.append(dict(state='open', **{'from': photo_year, 'to': m['originalFrom']}, evidenceIds=[ph['id']],
                                  certainty='inferred', note=m['note'] + ' Fotoåret är belägg, inte byggår.'))
            o['states'][:0] = early
            if part:
                pid = f"geometry:museum-streets:{o['id'].split(':')[-1]}:museum-part"
                catalog['geometries'].append(dict(id=pid, paths=[part], representation='centerline', sourceIds=geometries[gid]['sourceIds'],
                                                  note='Den norra delen av den moderna mittlinjen, som museets avritning täcker.'))
                o['geometryPeriods'][:0] = [
                    dict(geometryId=pid, **{'from': museum_year, 'to': photo_year}, evidenceIds=[mus['id']], certainty='inferred',
                         basis=street['basis'], coverage='partial', canonicalRange=list(m['museumRange'])),
                    dict(geometryId=gid, **{'from': photo_year, 'to': m['originalFrom']}, evidenceIds=ids[1:], certainty='inferred',
                         basis=m['note'] + ' Fotoåret är belägg, inte byggår.', coverage='full', canonicalRange=[0, 1])]
            else:
                o['geometryPeriods'].insert(0, dict(geometryId=gid, **{'from': museum_year, 'to': m['originalFrom']},
                                                    evidenceIds=ids, certainty='inferred', basis=street['basis']))
                for k in ('coverage', 'canonicalRange'):
                    if k in first:
                        o['geometryPeriods'][0][k] = deepcopy(first[k])
            o['museumStreetReview'] = dict(marker, originalFrom=m['originalFrom'], featureId=raw['id'])
        for n, line in new:
            oid = n['id']
            gid = f'geometry:museum-streets:{oid.split(":")[-1]}'
            catalog['geometries'].append(dict(id=gid, paths=[line], representation='centerline', sourceIds=[review['modernSourceId']],
                                              note='Dagens OSM-mittlinje för gatans norra del, sammanfogad av fyra lika delar i 2014–2026 års gatunät. '
                                                   'Ingen historisk breddmätning.'))
            mus = museum_evidence(oid)
            ph = photo_evidence(oid, gid, n['photoNote'])
            maps = [dict(id=f"{oid}:map-{e['year']}", sourceId=e['sourceId'], describes={'from': e['year'], 'to': e['year'] + 1},
                         supports=['state', 'geometry', 'identity'], observationType='printed-map-review', interpretation=True,
                         constructionYear=None, reviewId=source_id, note=n['mapNote']) for e in review['mapEvidence']]
            modern = dict(id=oid + ':modern', sourceId=review['modernSourceId'], describes={'from': 2026, 'to': None},
                          supports=['geometry', 'identity'], note='Modern källa, inte ett historiskt öppningsdatum.')
            first_map = maps[0]['describes']['from']
            catalog['objects'].append(dict(
                id=oid, name=n['name'], kind='roadSegment', routeId=n['routeId'], independentRoad=True,
                modernRoadClass=n['modernRoadClass'], roadWidth=n['roadWidth'],
                states=[dict(state='open', **{'from': museum_year, 'to': photo_year}, evidenceIds=[mus['id']], certainty='inferred', note=street['basis']),
                        dict(state='open', **{'from': photo_year, 'to': first_map}, evidenceIds=[ph['id']], certainty='inferred',
                             note=n['photoNote'] + ' Fotoåret är belägg, inte byggår.'),
                        dict(state='open', **{'from': first_map, 'to': None}, evidenceIds=[e['id'] for e in maps] + [modern['id']],
                             certainty='inferred', note=n['mapNote'])],
                geometryPeriods=[dict(geometryId=gid, **{'from': museum_year, 'to': None}, evidenceIds=[mus['id'], ph['id'], maps[0]['id'], modern['id']],
                                      certainty='inferred', basis=n['basis'])],
                evidence=[mus, ph] + maps + [modern],
                sourceLinks=[dict(datasetId=x['datasetId'], featureId=x['featureId']) for piece in n['pieces'] for x in piece['features']],
                museumStreetReview=dict(marker, originalFrom=None, featureId=raw['id'], createdFromModern=True)))
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
