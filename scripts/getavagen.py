"""Getavägen in Saltvik and Finström (docs/getavagen.md): today's road where it is the road on the 1929 Saltvik parish
map, and the old main road around it (Kyrkvägen at Godby; Bartsgårdavägen, Kroklundsvägen and the western part of
Saltviksvägen between Bartsgårda and Avanåker; Gamla Getavägen). Uses the Hammarlandsvägen helper `_apply` on a copy;
the catalogue changes only if all checks pass. Map years are first evidence, not construction years."""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply


def apply_getavagen_saltvik(read, catalog):
    trial = deepcopy(catalog)
    _apply(read, trial, 'data/getavagen-saltvik.json')
    catalog.clear(); catalog.update(trial)


def apply_getavagen_tjudo_geta(read, catalog):
    """Getavägen through Tjudö and Geta (docs/getavagen.md): today's road from 1927 where it is the road on the 1927 parish
    maps, the diagonal at Fenell from 1968, the old loop past Lignell (1927–1984) and Skräddarsvägen, the old curve at
    Östergeta, from 1927. `_apply` on a copy."""
    trial = deepcopy(catalog)
    _apply(read, trial, 'data/getavagen-tjudo-geta.json')
    catalog.clear(); catalog.update(trial)
