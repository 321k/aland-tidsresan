"""The postal route from Emkarby through Gölby and Godby to Färjsundet on the base maps 1968–1995
(docs/postal-route-godby.md).

One review file, data/postal-route-godby.json, applied on a copy of the catalogue, which replaces it only if every check
passes:
- 'extend': periods of an existing object whose geometry stopped short of a stretch the base maps draw get that
  stretch added as an extra path. The path is the object's own latest geometry (a cut, same coordinates) except where
  the review traces an older bend ('bend': traced points and OSM vertices, stated basis). The old paths stay unchanged.
  Here: Emkarbyvägen east of Tingsbacka, which its own review left outside the reviewed sheet.
- 'newRoads' (and 'stageFeatures'): new objects made of OSM pieces that no object owns, by the connections step of the
  Sviby review (scripts/sviby_connections.py).
Map years are first evidence, not construction years.
"""
from copy import deepcopy
from shapely.geometry import Point, LineString
from hammarlandsvagen_main_road import metric, END_LIMIT, OVERLAP_BUFFER, OVERLAP_LIMIT
from lemlandsvagen_main_road import cut
from mariehamn_frame_1942 import fingerprint, digest, TO_METRIC
from sviby_connections import _check, _add

REVIEW = 'data/postal-route-godby.json'


def _extension_path(oid, e, full, line):
    """The added path: cut(s) of the whole geometry, with an optional traced bend between two cuts."""
    a, b = e['range']
    bend = e.get('bend')
    if not bend:
        return cut(full['paths'][0], line, a, b)
    leave, rejoin = bend['leaveAt'], bend['rejoinAt']
    if not (a < leave < rejoin < b) or not bend.get('basis') or len(bend['points']) < 2:
        raise ValueError('Invalid bend ' + oid)
    head, tail = cut(full['paths'][0], line, a, leave), cut(full['paths'][0], line, rejoin, b)
    pts = [list(q) for q in bend['points']]
    if Point(TO_METRIC(*head[-1])).distance(Point(TO_METRIC(*pts[0]))) > END_LIMIT or Point(TO_METRIC(*tail[0])).distance(Point(TO_METRIC(*pts[-1]))) > END_LIMIT:
        raise ValueError('The bend does not leave and rejoin the line: ' + oid)
    return head + pts[1:-1] + tail


def _extend(review, catalog):
    labels = review['maps']; src = review['source']['id']
    objects = {o['id']: o for o in catalog['objects']}; geometries = {g['id']: g for g in catalog['geometries']}
    plans = []
    for x in review['extend']:
        o = objects.get(x['objectId'])
        if not o or fingerprint(o) != x['inputHash']:
            raise ValueError('Changed extension input ' + x['objectId'])
        full = geometries.get(x['wholeGeometryId'])
        if not full or digest(full) != x['wholeGeometryHash'] or len(full['paths']) != 1 or full['id'] not in [gp['geometryId'] for gp in o['geometryPeriods']]:
            raise ValueError('Changed whole geometry ' + x['objectId'])
        line = metric(full['paths'][0])
        for e in x['periods']:
            gp = next((p for p in o['geometryPeriods'] if p['from'] == e['from'] and p['to'] == e['to']), None)
            g = geometries.get(gp['geometryId']) if gp else None
            if not g or g['id'] != e['geometryId'] or digest(g) != e['geometryHash']:
                raise ValueError(f"Changed period {e['from']}-{e['to']} of {x['objectId']}")
            a, b = e['range']
            if not (0 <= a < b <= line.length + 0.1 and b - a >= 50):
                raise ValueError('Invalid extension range ' + x['objectId'])
            if not set(e['maps']) <= set(labels) or not any(v == 'present' and e['from'] <= labels[k]['year'] < (e['to'] or 9999) for k, v in e['maps'].items()):
                raise ValueError(f"No map draws the extension {e['from']}-{e['to']} of {x['objectId']}")
            path = _extension_path(x['objectId'], e, full, line); new = metric(path)
            old = [metric(p) for p in g['paths'] if len(p) > 1]
            # the added path starts where an old path ends and does not run along the old geometry
            if min(Point(l.coords[i]).distance(Point(new.coords[0])) for l in old for i in (0, -1)) > END_LIMIT:
                raise ValueError('The extension does not continue the old geometry: ' + x['objectId'])
            for l in old:
                hit = l.intersection(new.buffer(OVERLAP_BUFFER))
                if max([h.length for h in getattr(hit, 'geoms', [hit])] + [0]) > OVERLAP_LIMIT:
                    raise ValueError('The extension runs along the old geometry: ' + x['objectId'])
            plans.append((o, gp, g, e, path))
    # All checks passed. Change the catalogue.
    for o, gp, g, e, path in plans:
        gid = f"{review['geometryPrefix']}{o['id'].rsplit(':', 1)[1]}:{e['from']}-{e['to'] or 'now'}"
        catalog['geometries'].append(dict(id=gid, representation='centerline', paths=deepcopy(g['paths']) + [path], sourceIds=deepcopy(g.get('sourceIds', [])),
                                          note=g.get('note', '') + ' ' + e['note']))
        ev = []
        for k, v in sorted(e['maps'].items(), key=lambda kv: labels[kv[0]]['year']):
            y = labels[k]['year']
            x = dict(id=f"{o['id']}:extension-{e['from']}-{k}", sourceId=labels[k]['sourceId'], describes={'from': y, 'to': y + 1}, observationType='printed-map-review',
                     interpretation=True, outcome=v, supports=['geometry', 'identity', 'state'] if v == 'present' else ['state'], constructionYear=None, reviewId=src, note=e['note'])
            if v == 'present':
                x.update(matchedGeometryId=gid)
            o['evidence'].append(x)
            if v == 'present':
                ev.append(x['id'])
        gp.update(geometryId=gid)
        gp['evidenceIds'] = list(gp.get('evidenceIds', [])) + ev
        o.setdefault('extensionReviews', []).append(dict(review=src, reviewedAt=review['reviewedAt'], period=[e['from'], e['to']], range=e['range'], bend=bool(e.get('bend'))))


def apply_postal_route_godby(read, catalog):
    review = read(REVIEW)
    trial = deepcopy(catalog)
    sources = {s['id'] for s in trial['sources']}
    if review['source']['id'] in sources:
        raise ValueError('Postal route review already applied')
    _extend(review, trial)
    _check(read, trial, review)
    _add(trial, review)
    catalog.clear(); catalog.update(trial)
