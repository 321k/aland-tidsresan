"""The road from Hammarland through Sviby towards Mariehamn on the parish maps 1928/1929 (docs/svibyvagen.md).

The visual review (docs/reviews/sviby-2026-11-23) compared today's roads with the parish maps 1012 05 Hammarudda–Kungsö
(1928; Kungsö 1944 and 1953) and 1012 08 Maarianhamina (1929; Mariehamn 1948) and the base maps 1012 05 (1978) and
1012 08 (1968–1995). Three review files, applied in order on one copy of the catalogue, which replaces it only if all
pass:
- data/svibyvagen.json (_apply and the new-road helpers): Norra Svibyvägen from 1928 and Svibyvägen from 1929, whole;
  Kasbergsgatan, a new object from its OSM way, from 1929;
- data/svibyvagen-kasberg.json (_apply): Kasbergsvägen from 1929 except at Talläsen, and the old corner there as an
  old-road object until the 1985 map;
- data/svibyvagen-old.json (_old_roads): the 1928 road from Utängsvägen through Sviby to Norra Svibyvägen, the main road
  until the airport (1978 map), afterwards only its surviving first part.
Map years are first evidence, not construction years.
"""
from copy import deepcopy
from shapely.geometry import Point
from hammarlandsvagen_main_road import _apply, _old_roads, _new_road_check, _new_road_add, metric, END_LIMIT
from mariehamn_frame_1942 import TO_METRIC

MAIN, KASBERG, OLD = 'data/svibyvagen.json', 'data/svibyvagen-kasberg.json', 'data/svibyvagen-old.json'


def apply_svibyvagen(read, catalog):
    review = read(MAIN)
    trial = deepcopy(catalog)
    _new_road_check(read, trial, review)
    _apply(read, trial, MAIN)
    _new_road_add(trial, review)
    _apply(read, trial, KASBERG)
    # The new road's ends rest (within 1 m) on roads open in its first year (Kasbergsvägen and Svibyvägen from 1929),
    # so the road from Kasberget to the town is one connected line.
    nr = review['newRoad']; y = nr['firstYear']
    geometries = {g['id']: g for g in trial['geometries']}
    open_lines = [metric(p) for o in trial['objects'] if o['kind'] == 'roadSegment' and o['id'] != nr['id']
                  for gp in o['geometryPeriods'] if gp['from'] <= y < (gp['to'] or 9999)
                  for p in geometries[gp['geometryId']]['paths'] if len(p) > 1]
    for p in nr['paths']:
        for q in (p[0], p[-1]):
            if min(l.distance(Point(TO_METRIC(*q))) for l in open_lines) > END_LIMIT:
                raise ValueError('The new road does not join a road open in its first year: ' + nr['id'])
    _old_roads(read, trial, OLD)
    catalog.clear(); catalog.update(trial)
