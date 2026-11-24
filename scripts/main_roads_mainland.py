"""Main roads on the base maps, batch 3: Lemland, Lumparland, Jomala, Eckerö and Sund (docs/main-roads-mainland.md).

Road objects dated from a later base-map edition that the first edition (1968) already draws as a main road, in red, on
the same line get an earlier open period on their own geometry, cut to the stretches where it does, with a second stage
from the 1978 edition where that map draws more of it. Same method and helper as batch 1 (scripts/main_roads_saltvik.py).
Map years are first evidence, not construction years.
"""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply
from main_roads_saltvik import _whole_stages

REVIEW = 'data/main-roads-mainland.json'


def apply_main_roads_mainland(read, catalog):
    trial = deepcopy(catalog)
    _apply(read, trial, REVIEW)
    _whole_stages(read(REVIEW), trial)
    catalog.clear(); catalog.update(trial)
