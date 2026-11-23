"""The postal route's start at Storby, Eckerö: from the post and customs house to the dated main road at Labbas, on the
base maps (docs/postal-route-storby.md).

The harbour lies on base-map sheet 1012 15, which the project had not registered. The review registers it on its
printed KKJ grid from the cached scans (docs/reviews/postal-route-2026-11-23/data/registrations-101215.json) and adds
those editions as map sources. The roads are new objects made of OSM pieces that no object owns, through the
connections step of the Sviby review (scripts/sviby_connections.py), with stated free ends where a road leads on to
something not reviewed here. Everything runs on a copy of the catalogue. Map years are first evidence, not
construction years.
"""
from copy import deepcopy
from sviby_connections import _check, _add

REVIEW = 'data/postal-route-storby.json'


def apply_postal_route_storby(read, catalog):
    review = read(REVIEW)
    trial = deepcopy(catalog)
    sources = {s['id'] for s in trial['sources']}
    if review['source']['id'] in sources or any(m['id'] in sources for m in review['mapSources']):
        raise ValueError('Postal route review already applied')
    trial['sources'] += [deepcopy(m) for m in review['mapSources']]
    _check(read, trial, review)
    _add(trial, review)
    catalog.clear(); catalog.update(trial)
