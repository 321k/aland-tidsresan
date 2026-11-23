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
