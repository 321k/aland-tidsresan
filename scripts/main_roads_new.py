"""Main roads on the base maps, batch 4: main roads that no catalogue object had (docs/main-roads-new.md).

Today's main roads (OSM primary, secondary, tertiary) that no object owns and that the first base-map edition already
draws as a main road, in red, on the same line become new road objects made of their OSM ways, dated by the editions
that draw them. One review file, data/main-roads-new.json, in the form of the Sviby connections ('newRoads', checked
and added by scripts/sviby_connections.py). Map years are first evidence, not construction years.
"""
from copy import deepcopy
from sviby_connections import _check, _add

REVIEW = 'data/main-roads-new.json'


def apply_main_roads_new(read, catalog):
    review = read(REVIEW)
    trial = deepcopy(catalog)
    _check(read, trial, review)
    _add(trial, review)
    catalog.clear(); catalog.update(trial)
