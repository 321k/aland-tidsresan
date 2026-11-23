"""The postal route east of Kastelholm: the three short gaps in Sundsvägen at Lappböle and Klippan, on the base maps
(docs/postal-route-sund.md).

Sundsvägen is split into pieces by older reviews: the Saltvik piece ending at a sheet edge at Lappböle, and del 2, del 3
and del 1 from the Sundsvägen review (docs/sundsvagen.md). Three stretches of today's road between them were in no
object: 180 m at the Lappböle sheet edge, 265 m between del 2 and del 3 and 95 m between del 3 and del 1 at Klippan.
They become new objects of OSM pieces that no object owns, through the connections step of the Sviby review
(scripts/sviby_connections.py), on the same route as their neighbours. The Klippan pieces are dated with del 2 and
del 3 (1978); the 1968 sheet already draws the straight road, which the documentation records as an open item for the
Sundsvägen review. Everything runs on a copy of the catalogue. Map years are first evidence, not construction years.
"""
from copy import deepcopy
from sviby_connections import _check, _add

REVIEW = 'data/postal-route-sund.json'


def apply_postal_route_sund(read, catalog):
    review = read(REVIEW)
    trial = deepcopy(catalog)
    if review['source']['id'] in {s['id'] for s in trial['sources']}:
        raise ValueError('Postal route review already applied')
    _check(read, trial, review)
    _add(trial, review)
    catalog.clear(); catalog.update(trial)
