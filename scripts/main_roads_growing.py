"""Main roads on the base maps, batch 5: roads whose geometry grows over time (docs/main-roads-growing.md).

Objects of the Hammarland rural review (road:rural:hammarland-*) have early geometry periods that cover only what that
review read on its sheet, 1012 06; the rest of today's line appears only with the full OSM geometry (2014–2025). Where
the first edition of the neighbouring sheets (1021 04, 1021 07, 1012 03, 1012 09) already draws the road as a main
road, in red, on today's line, each early period gets those stretches added: pieces of the object's latest geometry
(its own coordinates), cut to the reviewed ranges, beside the period's existing paths. A later stage (an edition that
draws more) starts a new period at its year. Map years are first evidence, not construction years.

One review file, data/main-roads-growing.json. For each object:
- 'inputHash': the object's fingerprint before the step;
- 'stages': [{year, sources, ranges}] on the latest geometry (metres);
- 'periods': the new geometry periods [{from, to, baseGeometryId, ranges}]; 'ranges' is the stage ranges in force
  from 'from', less what the base geometry already has (within 5 m). Each existing period before the latest is
  replaced by one or more of these, with the same years overall.
"""
from copy import deepcopy
from mariehamn_frame_1942 import fingerprint, TO_METRIC
from shapely.geometry import LineString, Point
from shapely.ops import substring
from lemlandsvagen_main_road import cut

REVIEW = 'data/main-roads-growing.json'
OWN = 5


def _met(p):
    return LineString([TO_METRIC(*q) for q in p])


def _uncovered(line, ranges, base, step=5):
    """The parts of ranges whose points lie more than OWN m from every base line."""
    out = []
    for a, b in ranges:
        cur = None; d = a
        while d <= b + 1e-6:
            pt = line.interpolate(min(d, b))
            if all(l.distance(pt) > OWN for l in base):
                cur = [cur[0], min(d, b)] if cur else [min(d, b), min(d, b)]
            elif cur:
                out.append(cur); cur = None
            d += step
        if cur: out.append(cur)
    return [[round(x, 1), round(y, 1)] for x, y in out if y - x >= 20]


def apply_main_roads_growing(read, catalog):
    review = read(REVIEW)
    trial = deepcopy(catalog)
    objects = {o['id']: o for o in trial['objects']}; geometries = {g['id']: g for g in trial['geometries']}
    sources = {s['id'] for s in trial['sources']}
    if review['schemaVersion'] != 1 or review['source']['id'] in sources:
        raise ValueError('Growing main-road review already applied')
    src = review['source']['id']
    for t in review['objects']:
        o = objects.get(t['objectId'])
        if not o or fingerprint(o) != t['inputHash'] or 'mainRoadReview' in o:
            raise ValueError('Changed growing main-road target: ' + t['objectId'])
        latest = o['geometryPeriods'][-1]; lp = [p for p in geometries[latest['geometryId']]['paths'] if len(p) > 1]
        if len(lp) != 1:
            raise ValueError('The latest geometry must be one path: ' + o['id'])
        line = _met(lp[0])
        early = o['geometryPeriods'][:-1]
        # the stages: ordered, within the line, at or after the object's first open year, before the latest period
        years = [s['year'] for s in t['stages']]
        if years != sorted(set(years)) or years[0] < o['states'][0]['from'] or years[-1] >= latest['from'] \
                or any(not (0 <= a < b <= line.length + 0.5) for s in t['stages'] for a, b in s['ranges']) \
                or any(x not in sources for s in t['stages'] for x in s['sources']):
            raise ValueError('Invalid stages: ' + o['id'])
        # the new periods cover the early periods' years exactly, each on one early period's geometry
        if [p['from'] for p in t['periods']][0] != early[0]['from'] or t['periods'][-1]['to'] != latest['from'] \
                or any(a['to'] != b['from'] for a, b in zip(t['periods'], t['periods'][1:])):
            raise ValueError('The new periods do not cover the early periods: ' + o['id'])
        new_periods, ev = [], []
        for s in t['stages']:
            for sid in s['sources']:
                ev.append(dict(id=f"{o['id']}:main-roads-growing:{sid}", sourceId=sid, describes={'from': s['year'], 'to': s['year'] + 1},
                               observationType='printed-map-review', interpretation=True, outcome='present', supports=['geometry', 'state'],
                               constructionYear=None, reviewId=src, rangesMeters=s['ranges'], note=s['note']))
        for p in t['periods']:
            base = next((g for g in early if g['from'] <= p['from'] < g['to']), None)
            if not base or base['geometryId'] != p['baseGeometryId'] or p['to'] > base['to']:
                raise ValueError('A new period is not within its early period: ' + o['id'])
            stage = [s for s in t['stages'] if s['year'] <= p['from']]
            want = _uncovered(line, stage[-1]['ranges'], [_met(q) for q in geometries[base['geometryId']]['paths'] if len(q) > 1]) if stage else []
            if want != p['ranges']:
                raise ValueError(f"The period's ranges are not the stage less its base geometry: {o['id']} {p['from']}")
            g = deepcopy(base)
            g.update({'from': p['from'], 'to': p['to']})
            if p['ranges']:
                gid = f"geometry:main-roads-growing:{o['id'].split(':', 1)[1]}:{p['from']}"
                pieces = [cut(lp[0], line, a, b) for a, b in p['ranges']]
                trial['geometries'].append(dict(id=gid, representation='centerline', paths=deepcopy(geometries[base['geometryId']]['paths']) + [[list(q) for q in x] for x in pieces],
                                                sourceIds=sorted(set(geometries[base['geometryId']].get('sourceIds', [])) | set(stage[-1]['sources'])),
                                                note=f"{geometries[base['geometryId']].get('note', '')} Med de sträckor av dagens linje som grundkartan {stage[-1]['year']} ritar som huvudväg ({review['source']['id']})."))
                g['geometryId'] = gid
                g['evidenceIds'] = g['evidenceIds'] + [e['id'] for e in ev if e['describes']['from'] <= p['from']]
                g['basis'] = (g.get('basis') or '') + ' ' + stage[-1]['note']
            new_periods.append(g)
        o['geometryPeriods'] = new_periods + [latest]
        o['evidence'] += ev
        o['mainRoadReview'] = dict(reviewedAt=review['reviewedAt'], review=src, growing=True, stages=[dict(year=s['year'], ranges=s['ranges']) for s in t['stages']], constructionYear=None)
    trial['sources'].append(deepcopy(review['source']))
    trial['recordedAt'] = max(trial['recordedAt'], review['reviewedAt'])
    catalog.clear(); catalog.update(trial)
