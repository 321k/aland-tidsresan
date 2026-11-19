"""Långnäsvägen from the sound at Bergören past Skag and Södergård (docs/langnasvagen.md).

The visual review (docs/reviews/langnasvagen-2026-11-19) compared today's road with the 1917 Senate atlas, the 1929
Lumparland parish map and the 1968–1995 base maps (sheet 101211). Today's road was dated only from 1968, but its first
3.2 km are the road on the 1929 map, except at two places:
- at Skag the old road ran straight north from the crossing to a sharp corner in the village; part of it survives as a
  track. Today's curve is first on the 1968 map;
- at Södergård the old road turned north-east through the village and rejoined today's line 600 m on. Today's line
  through the fields is first on the 1968 map, which still draws part of the old line as a lesser road.
The 1917 atlas draws the road from Skag east and north along Krokstadviken, but no crossing to Bergören. North of
Sjögård (3.2 km) today's road is new: the 1929 road ran north through Nyabonds instead.

Two reviews, both applied to a copy first:
- data/langnasvagen.json (`_apply`): today's road from 1917 (Skag–Sjögård), with a second stage from 1929 that adds the
  crossing; the old road at Södergård (vanished, open 1917–1968, then unknown);
- data/langnasvagen-skag.json (`_old_roads`): the old road at Skag, the main road 1929–1968, then its surviving track.
Map years are first evidence, not construction years.
"""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply, _old_roads


def apply_langnasvagen(read, catalog):
    trial = deepcopy(catalog)
    _apply(read, trial, 'data/langnasvagen.json')
    _old_roads(read, trial, 'data/langnasvagen-skag.json')
    catalog.clear(); catalog.update(trial)
