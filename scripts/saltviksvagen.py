"""Saltviksvägen from Tjudö to Kvarnbo, the old main road to Saltvik's church village, on the parish maps 1927 and 1929
(docs/saltviksvagen.md). Uses the main-road review helper of Hammarlandsvägen: today's road where it is the old road,
Kavelbrovägen (the old curve at Kavelbro), the first 200 m of Dåglösavägen and a new object for the vanished curve at
Andelsby. All checks run on a copy; the catalogue changes only if all pass."""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply


def apply_saltviksvagen_east(read, catalog):
    trial = deepcopy(catalog)
    _apply(read, trial, 'data/saltviksvagen-east.json')
    catalog.clear(); catalog.update(trial)
