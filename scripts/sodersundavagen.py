"""Södersundavägen towards Jomala church, the old road from Hammarland to Jomala, on the parish maps 1928/1929
(docs/sodersundavagen.md). Three steps on one copy of the catalogue, which replaces it only if all pass:
- the main-road helper (_apply): Södersundavägen from Mattas to where the 1928 road leaves today's line, 1929–1968, cut
  from the object's whole geometry ('laterGeometry');
- the coverage step below: Södersundavägen's 1968–1995 periods drew only the part on the Hammarby base-map sheet; the
  Jomala sheets 1968–1985 draw the rest up to the same bend, and the 1995 sheet the whole road.;
- the old-road helper (_old_roads): the 1928 road round the loop through Ulvsby to the church, the main road until 1995
  and afterwards only its surviving parts (Drittel-Mattes Gränd, S:t Olofs vägen)."""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply, _old_roads, metric
from lemlandsvagen_main_road import cut
from mariehamn_frame_1942 import fingerprint, digest


def _coverage(read, catalog, path_):
    """Replace the geometry of listed periods by a cut ('range', metres along the whole geometry) or the whole geometry.
    Each period must still have its recorded geometry; the whole geometry must be unchanged; maps marked present give the
    evidence. Nothing else of the object changes."""
    review = read(path_); labels = review['maps']; src = review['source']['id']
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    todo = []
    for cv in review['coverage']:
        todo.append(_coverage_plan(cv, objects, geometries, labels))
    # All checks passed. Change the objects.
    for cv, o, full, line, plans in todo:
        _coverage_change(review, catalog, cv, o, full, line, plans, labels, src)


def _coverage_plan(cv, objects, geometries, labels):
    o = objects.get(cv['objectId'])
    if not o or fingerprint(o) != cv['inputHash']:
        raise ValueError('Changed coverage input ' + cv['objectId'])
    full = geometries.get(cv['wholeGeometryId'])
    if not full or digest(full) != cv['wholeGeometryHash'] or len(full['paths']) != 1 or full['id'] not in [gp['geometryId'] for gp in o['geometryPeriods']]:
        raise ValueError('Changed whole geometry ' + cv['objectId'])
    line = metric(full['paths'][0]); plans = []
    for p in cv['periods']:
        gp = next((x for x in o['geometryPeriods'] if x['from'] == p['from'] and x['to'] == p['to']), None)
        if not gp or gp['geometryId'] != p['geometryId']:
            raise ValueError(f"Changed period {p['from']}-{p['to']} of {cv['objectId']}")
        rng = p.get('range')
        if rng and not (0 <= rng[0] < rng[1] <= line.length + 0.1 and rng[1] - rng[0] >= 50):
            raise ValueError('Invalid coverage range ' + cv['objectId'])
        if not set(p['maps']) <= set(labels) or not any(v == 'present' and p['from'] <= labels[k]['year'] < (p['to'] or 9999) for k, v in p['maps'].items()):
            raise ValueError(f"No map draws the period {p['from']}-{p['to']} of {cv['objectId']}")
        plans.append((gp, p))
    return cv, o, full, line, plans


def _coverage_change(review, catalog, cv, o, full, line, plans, labels, src):
    made = {}
    for gp, p in plans:
        rng = p.get('range')
        if rng:
            key = tuple(rng)
            if key not in made:
                gid = review['geometryPrefix'] + o['id'].rsplit(':', 1)[1] + ':coverage-' + '-'.join(str(round(x)) for x in rng)
                catalog['geometries'].append(dict(id=gid, representation='centerline', paths=[cut(full['paths'][0], line, rng[0], min(rng[1], line.length))],
                                                  sourceIds=deepcopy(full['sourceIds']), note=cv['geometryNote']))
                made[key] = gid
            gid = made[key]; cov = dict(coverage='partial', canonicalRange=[round(rng[0] / line.length, 6), round(min(rng[1], line.length) / line.length, 6)])
        else:
            gid = full['id']; cov = dict(coverage='full', canonicalRange=[0, 1])
        ev = []
        for k, v in sorted(p['maps'].items(), key=lambda kv: labels[kv[0]]['year']):
            y = labels[k]['year']
            e = dict(id=f"{o['id']}:coverage-{k}", sourceId=labels[k]['sourceId'], describes={'from': y, 'to': y + 1}, observationType='printed-map-review', interpretation=True,
                     outcome=v, supports=['geometry', 'identity', 'state'] if v == 'present' else ['state'], constructionYear=None, reviewId=src, note=p['basis'])
            if v == 'present':
                e.update(matchedGeometryId=gid, **cov)
            if not any(x['id'] == e['id'] for x in o['evidence']):
                o['evidence'].append(e); ev.append(e['id'])
        gp.update(geometryId=gid, basis=p['basis'], **cov)
        gp['evidenceIds'] = list(gp.get('evidenceIds', [])) + [x for x in ev if next(e for e in o['evidence'] if e['id'] == x)['outcome'] == 'present']
    o.setdefault('coverageReviews', []).append(dict(review=src, reviewedAt=review['reviewedAt'], periods=[[p['from'], p['to'], p.get('range')] for _, p in plans]))


def apply_sodersundavagen(read, catalog):
    trial = deepcopy(catalog)
    _apply(read, trial, 'data/sodersundavagen.json')
    _coverage(read, trial, 'data/sodersundavagen.json')
    _old_roads(read, trial, 'data/sodersundavagen-jomala.json')
    catalog.clear(); catalog.update(trial)
