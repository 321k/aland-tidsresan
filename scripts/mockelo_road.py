"""The road from Svibyviken to Möckelö on the parish maps 1928/1929 (docs/mockelo-road.md).

Uses the connections step of the Sviby review (scripts/sviby_connections.py) with two review files, on one copy of the
catalogue:
- data/mockelo-road-early.json (_apply): Möckelövägen from 1928, whole;
- data/mockelo-road.json: the road from Norra Möckelövägen along the shore and Lönnelundsgatan to Möckelövägen, a new
  object made of OSM pieces that no object owns.
Map years are first evidence, not construction years.
"""
from sviby_connections import apply_connections

EARLY, MAIN = 'data/mockelo-road-early.json', 'data/mockelo-road.json'


def apply_mockelo_road(read, catalog):
    apply_connections(read, catalog, EARLY, MAIN)


MJOLKDAL = 'data/mjolkdalsvagen.json'


def apply_mjolkdalsvagen(read, catalog):
    """Mjölkdalsvägen from 1928 (docs/mockelo-road.md): the main-road helper (_apply) on a copy, which replaces the
    catalogue only if every check passes."""
    from copy import deepcopy
    from hammarlandsvagen_main_road import _apply
    trial = deepcopy(catalog)
    _apply(read, trial, MJOLKDAL)
    catalog.clear(); catalog.update(trial)
