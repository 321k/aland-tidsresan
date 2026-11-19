"""Lemlandsvägen east of the church village, to the sound at Bergören (docs/lemlandsvagen-east.md).

The visual review (docs/reviews/lemlandsvagen-east-2026-11-19) compared today's road with the 1917 Senate atlas, the
1929 Lumparland parish map and the 1968–1995 base maps (sheet 101211). Today's road was dated only from 1968, but:
- from the church village through Norrböle, Rörstorp and Granboda it is the road on the 1917 and 1929 maps, except at
  Simons, where the old road is today's Skolsvängen, and east of Granboda, where it ran east along today's
  Klubbensvägen and then north along Fiskartorpsvägen. Today's straight road and diagonal are first on the 1968 map;
- the road across Bergören to the sound is first on the 1929 map. The 1917 atlas draws the road only to the shore at
  Delsviken.

The step uses the Hammarlandsvägen helpers: `_apply` for the early periods (today's road from 1917, with a second stage
from 1929 that adds Bergören; Skolsvängen and Klubbensvägen from 1917) and the new-road helpers for Fiskartorpsvägen, a
new object from its OSM way, from 1929. Everything runs on a copy first. Map years are first evidence, not construction
years.
"""
from copy import deepcopy
from shapely.geometry import Point
from hammarlandsvagen_main_road import _apply, _new_road_check, _new_road_add, metric, END_LIMIT
from mariehamn_frame_1942 import TO_METRIC

REVIEW = 'data/lemlandsvagen-east.json'


def apply_lemlandsvagen_east(read, catalog):
    review = read(REVIEW)
    trial = deepcopy(catalog)
    _new_road_check(read, trial, review)
    _apply(read, trial, REVIEW)
    _new_road_add(trial, review)
    # The new road's ends rest (within 1 m) on roads that are open in its first year: here today's road from 1929 and
    # Klubbensvägen, so the old route is one connected line.
    nr = review['newRoad']; y = nr['firstYear']
    geometries = {g['id']: g for g in trial['geometries']}
    open_lines = [metric(p) for o in trial['objects'] if o['kind'] == 'roadSegment' and o['id'] != nr['id']
                  for gp in o['geometryPeriods'] if gp['from'] <= y < (gp['to'] or 9999)
                  for p in geometries[gp['geometryId']]['paths'] if len(p) > 1]
    for p in nr['paths']:
        for q in (p[0], p[-1]):
            if min(l.distance(Point(TO_METRIC(*q))) for l in open_lines) > END_LIMIT:
                raise ValueError('The new road does not join a road open in its first year: ' + nr['id'])
    # 'statedGaps': an early piece's end that does not reach the road it joined; the distance is stated and checked.
    for sg in review.get('statedGaps', []):
        o = next(x for x in trial['objects'] if x['id'] == sg['objectId']); gp = o['geometryPeriods'][0]
        q = geometries[gp['geometryId']]['paths'][0][sg['end']]
        others = [metric(p) for x in trial['objects'] if x['kind'] == 'roadSegment' and x['id'] != o['id']
                  for g2 in x['geometryPeriods'] if g2['from'] <= gp['from'] < (g2['to'] or 9999)
                  for p in geometries[g2['geometryId']]['paths'] if len(p) > 1]
        if not sg.get('basis') or abs(min(l.distance(Point(TO_METRIC(*q))) for l in others) - sg['meters']) > 1:
            raise ValueError('Changed stated gap at ' + sg['objectId'])
    catalog.clear(); catalog.update(trial)
