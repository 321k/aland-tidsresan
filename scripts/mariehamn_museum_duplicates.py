"""Museum-map houses in Mariehamn that duplicate or were replaced by a later house.

The 1920 museum map's houses (`building:museum:*`) are provisional objects with assumed continued existence. Where one
overlaps a later house, `data/mariehamn-museum-duplicates.json` records a decision made on the 1942 orthophoto and the
1968 base map:

* merge: one physical house. The later object keeps its identity, outline, states and periods; it takes over the
  museum record's evidence, source links and aliases, and is shown from the museum map's 1920 with its own outline
  (a continuity assumption). The museum object is removed; references to it resolve through the aliases.
* replacement: different buildings on the plot. The museum house ends at the successor's first reviewed evidence (the
  latest replacement boundary, not a demolition year) and is linked to its successors.

A second pass, `data/mariehamn-museum-offsets.json`, reviews every museum house still open after the first one. The
museum map is often shifted about a house depth, so a museum house can stand in a street, front garden or yard next to
its house without overlapping it. That pass merges by adjacency (a gap of at most `maxGapMeters`), may merge two museum
houses into one longer building, and adds:

* ending: the house's own footprint is empty on the base map (1985, or 1968 where that edition is not hatched there)
  and no neighbour is clearly the same house. The museum house ends at that map's survey year, the latest boundary,
  not a demolition year; it may have gone earlier or have been misplaced on the museum map.

Every input is fingerprinted and validated before the catalogue changes; geometry is never moved.
"""
import hashlib
import json
from copy import deepcopy
from pyproj import Transformer
from shapely.geometry import Polygon

TO_METRIC = Transformer.from_crs(4326, 3874, always_xy=True).transform


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def fingerprint(o):
    return digest({k: o.get(k) for k in ['id', 'kind', 'states', 'geometryPeriods', 'sourceLinks', 'reconstruction', 'aliases', 'relationships']})


def outline(o, geometries):
    paths = geometries[o['geometryPeriods'][-1]['geometryId']]['paths']
    return Polygon([TO_METRIC(*p) for p in paths[0]], [[TO_METRIC(*p) for p in h] for h in paths[1:]]).buffer(0)


def apply_museum_duplicates(read, catalog):
    _apply(read, catalog, 'data/mariehamn-museum-duplicates.json')
    apply_museum_offsets(read, catalog)


def apply_museum_offsets(read, catalog):
    _apply(read, catalog, 'data/mariehamn-museum-offsets.json')


def _apply(read, catalog, path):
    review = read(path)
    adjacent = review.get('mergeRule') == 'adjacent'
    endings = review.get('endings', [])
    objects = {o['id']: o for o in catalog['objects']}
    geometries = {g['id']: g for g in catalog['geometries']}
    sources = {s['id'] for s in catalog['sources']}
    if review['schemaVersion'] != 1 or review['source']['id'] in sources or review['aerialSourceId'] not in sources:
        raise ValueError('Museum duplicate review already applied or missing its photo source')
    named = {d['keep'] for d in review['merges']} | {d['donor'] for d in review['merges']} | \
            {d['museum'] for d in review['replacements']} | {s for d in review['replacements'] for s in d['successors']} | \
            {d['museum'] for d in endings}
    if named != set(review['inputs']):
        raise ValueError('Incomplete museum duplicate inputs')
    for oid, expected in review['inputs'].items():
        if oid not in objects or fingerprint(objects[oid]) != expected:
            raise ValueError('Changed museum duplicate input: ' + oid)
    museums = [d['donor'] for d in review['merges']] + [d['museum'] for d in review['replacements']] + [d['museum'] for d in endings]
    if len(set(museums)) != len(museums) or {d['keep'] for d in review['merges']} & set(museums):
        raise ValueError('Conflicting museum duplicate decisions')
    for oid in museums:
        o = objects[oid]
        if (not oid.startswith('building:museum:') or len(o['states']) != 1 or o['states'][0]['state'] != 'standing'
                or o['states'][0]['to'] is not None or len(o['geometryPeriods']) != 1 or o['geometryPeriods'][0]['to'] is not None):
            raise ValueError('Museum house is not an open provisional object: ' + oid)
    keeps = [d['keep'] for d in review['merges']]
    if len(set(keeps)) != len(keeps) and not adjacent:
        raise ValueError('Two museum houses merged into one object')
    if adjacent and any(keeps.count(k) > 2 for k in keeps):
        raise ValueError('More than two museum houses merged into one object')
    for d in review['merges']:
        keep, donor = objects[d['keep']], objects[d['donor']]
        if (keep['id'].startswith('building:museum:') or keep.get('kind') != 'building' or not d['basis']
                or donor['states'][0]['from'] != d['fromYear'] or keep['states'][0]['from'] != d['keepFrom']
                or keep['states'][0]['state'] not in ('standing', 'occupied') or keep['geometryPeriods'][0]['from'] != d['keepFrom']
                or not keep.get('reconstruction') or keep['reconstruction']['from'] != d['keepFrom']):
            raise ValueError('Changed museum merge: ' + d['id'])
        a, b = outline(donor, geometries), outline(keep, geometries)
        if adjacent:
            if a.distance(b) > review['maxGapMeters'] or a.centroid.distance(b.centroid) > review['maxCentroidMeters']:
                raise ValueError('Museum merge partners are not neighbours: ' + d['id'])
        elif a.intersection(b).area < 4 or a.centroid.distance(b.centroid) > 25:
            raise ValueError('Museum merge partners do not overlap: ' + d['id'])
    for d in review['replacements']:
        old = objects[d['museum']]
        firsts = [objects[s]['states'][0]['from'] for s in d['successors']]
        if (not d['basis'] or d['endYear'] != min(firsts) or not old['states'][0]['from'] < d['endYear']
                or any(objects[s]['states'][0]['state'] not in ('standing', 'occupied', 'construction') for s in d['successors'])):
            raise ValueError('Changed museum replacement: ' + d['id'])
        a = outline(old, geometries)
        if any(a.intersection(outline(objects[s], geometries)).area < 4 for s in d['successors']):
            raise ValueError('Museum replacement successor does not overlap: ' + d['id'])
    sheets = {s['id'] for s in catalog['sources']}
    for d in endings:
        old = objects[d['museum']]
        if (not d['basis'] or d['sourceId'] not in sheets or not old['states'][0]['from'] < d['endYear'] <= 1985
                or d['darkShare'] > review['maxDarkShare']):
            raise ValueError('Changed museum ending: ' + d['id'])

    # All checks passed. Change the catalogue.
    sid = review['source']['id']
    catalog['sources'].append(deepcopy(review['source']))
    aliases, removed = {}, set()
    marker = review.get('marker', 'museumDuplicateReview')
    for d in review['merges']:
        keep, donor = objects[d['keep']], objects[d['donor']]
        previous = deepcopy(keep)
        eid = keep['id'] + ':museum-duplicate-review' + ('' if marker == 'museumDuplicateReview' else ':' + donor['id'].split(':')[-1])
        museum_ids = [e['id'] for e in donor['evidence']]
        for key in ['evidence', 'sourceLinks']:
            for item in donor.get(key, []):
                if item not in keep.setdefault(key, []):
                    keep[key].append(deepcopy(item))
        keep['evidence'].append(dict(id=eid, sourceId=sid, describes={'from': d['fromYear'], 'to': None}, supports=['identity', 'state'],
                                     observationType='interpretation', interpretation=True, constructionYear=None, note=d['basis'],
                                     aerialSourceId=review['aerialSourceId'], offsetMeters=d['offsetMeters']))
        keep['sourceYears'] = sorted(set(keep['sourceYears'] + donor['sourceYears']))
        names = [donor['id'], *donor.get('aliases', [])]
        aliases.update({n: keep['id'] for n in names})
        keep['aliases'] = sorted(set(keep.get('aliases', []) + names))
        ids = [eid, *museum_ids]
        if keep['states'][0]['from'] > d['fromYear']:
            first = keep['states'][0]
            keep['states'].insert(0, dict(state=first['state'], **{'from': d['fromYear'], 'to': d['keepFrom']}, evidenceIds=ids,
                                          certainty='inferred', note=d['basis']))
            period = keep['geometryPeriods'][0]
            keep['geometryPeriods'][0] = {**period, 'from': d['fromYear'], 'evidenceIds': period['evidenceIds'] + ids,
                                          'previousFrom': period['from'],
                                          'basis': (period.get('basis') or '') + ' Visas från museikartans 1920-tal som samma hus; '
                                                   'formen är den senare uppmätta konturen, inte museikartans ritning.'}
            rec = keep['reconstruction']
            keep['reconstruction'] = {**rec, 'from': d['fromYear'], 'evidenceIds': rec['evidenceIds'] + ids,
                                      'previous': {'from': rec['from'], 'firstObserved': rec['firstObserved'], 'basis': rec['basis']}}
        else:
            keep['states'][0]['evidenceIds'] = keep['states'][0]['evidenceIds'] + ids
            rec = keep['reconstruction']
            keep['reconstruction'] = {**rec, 'evidenceIds': rec['evidenceIds'] + ids,
                                      'previous': {'from': rec['from'], 'firstObserved': rec['firstObserved'], 'basis': rec['basis']}}
        # The museum map is now the first source of this house's existence.
        keep['reconstruction']['firstObserved'] = keep['sourceYears'][0]
        record = dict(reviewedAt=review['reviewedAt'], decision='merge', donorId=donor['id'], fromYear=d['fromYear'],
                      previousFrom=d['keepFrom'], constructionYear=None, mergedObject=deepcopy(donor), previousFingerprint=fingerprint(previous))
        if marker == 'museumDuplicateReview':
            keep[marker] = record
        else:  # the second pass may merge two museum houses into one longer building
            keep.setdefault(marker, []).append(record)
        removed.add(donor['id'])
    for d in review['replacements']:
        old = objects[d['museum']]
        eid = old['id'] + ':museum-duplicate-review'
        old['evidence'].append(dict(id=eid, sourceId=sid, describes={'from': d['endYear'], 'to': None}, supports=['identity', 'state'],
                                    observationType='interpretation', interpretation=True, constructionYear=None, note=d['basis'],
                                    aerialSourceId=review['aerialSourceId']))
        state = old['states'][0]
        state['to'] = d['endYear']; state['evidenceIds'] = state['evidenceIds'] + [eid]
        old['states'].append(dict(state='demolished', **{'from': d['endYear'], 'to': None}, evidenceIds=[eid], certainty='inferred', note=d['basis']))
        for period in old['geometryPeriods']:
            period['evidenceIds'] = period['evidenceIds'] + [eid]
        old['reconstruction'] = {**old['reconstruction'], 'evidenceIds': old['reconstruction']['evidenceIds'] + [eid]}
        old['replacementReview'] = dict(recordedAt=review['reviewedAt'], assumedEnd=d['endYear'], successorIds=d['successors'],
                                        changeWindow=[old['states'][0]['from'], d['endYear']], basis=d['basis'], reviewId=sid)
        if 'sourceMigration' in old:
            old['sourceMigration'] = {**old['sourceMigration'], 'decision': 'replacement', 'basis': d['basis'], 'interpretedAt': review['reviewedAt']}
        for s in d['successors']:
            old.setdefault('relationships', []).append(dict(type='replaced-by', objectId=s, **{'from': d['endYear']}, certainty='inferred'))
            objects[s].setdefault('relationships', []).append(dict(type='replaces', objectId=old['id'], **{'from': d['endYear']}, certainty='inferred'))
        old['museumDuplicateReview'] = dict(reviewedAt=review['reviewedAt'], decision='replacement', successorIds=d['successors'], endYear=d['endYear'])
    for d in endings:
        old = objects[d['museum']]
        eid, aid = old['id'] + ':museum-offset-review', old['id'] + ':map-absent-' + str(d['mapYear'])
        old['evidence'].append(dict(id=aid, sourceId=d['sourceId'], describes={'from': d['mapYear'], 'to': d['mapYear'] + 1},
                                    supports=['state'], observationType='printed-map', outcome='absent', interpretation=True,
                                    darkShare=d['darkShare'], constructionYear=None, note=d['basis']))
        old['evidence'].append(dict(id=eid, sourceId=sid, describes={'from': d['endYear'], 'to': None}, supports=['state'],
                                    observationType='interpretation', interpretation=True, constructionYear=None, note=d['basis']))
        state = old['states'][0]
        state['to'] = d['endYear']; state['evidenceIds'] = state['evidenceIds'] + [eid]
        old['states'].append(dict(state='demolished', **{'from': d['endYear'], 'to': None}, evidenceIds=[eid, aid], certainty='inferred', note=d['basis']))
        for period in old['geometryPeriods']:
            period['evidenceIds'] = period['evidenceIds'] + [eid]
        old['reconstruction'] = {**old['reconstruction'], 'evidenceIds': old['reconstruction']['evidenceIds'] + [eid]}
        if 'sourceMigration' in old:
            old['sourceMigration'] = {**old['sourceMigration'], 'decision': 'ending', 'basis': d['basis'], 'interpretedAt': review['reviewedAt']}
        old[marker] = [dict(reviewedAt=review['reviewedAt'], decision='ending', endYear=d['endYear'], mapYear=d['mapYear'], constructionYear=None)]
    catalog['objects'][:] = [o for o in catalog['objects'] if o['id'] not in removed]
    for o in catalog['objects']:
        for rel in o.get('relationships', []):
            rel['objectId'] = aliases.get(rel['objectId'], rel['objectId'])
    for s in catalog['cityStages']:
        for f in s['features'] + s.get('printedBuildings', []):
            if f.get('objectId') in aliases:
                f['objectId'] = aliases[f['objectId']]
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
