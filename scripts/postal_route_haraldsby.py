"""The postal route from Godby over Färjsundet through Haraldsby on the Saltvik parish maps 1929 and 1944
(docs/postal-route-haraldsby.md).

One review file, data/postal-route-haraldsby.json, applied with the main-road helper (_apply in
scripts/hammarlandsvagen_main_road.py) on a copy of the catalogue, which replaces it only if every check passes. Road
objects dated from the base map 1968 that the parish maps already draw on the same course get an earlier open period on
their own geometry (whole, or a cut where only part of today's object is the old road): Hamnvägen on the west side of
Färjsundet, the road from the far landing to Vårsundet, Haraldsbyvägen through the village and Gamla Sundsvägen past
Östergård and Högbacka. A second review file, data/postal-route-farjsundet-shore.json, adds the road along the shore to
the old ferry landing as a new object of an OSM track (the connections step of scripts/sviby_connections.py). The ferry
itself is not a road object; the postal-route builder crosses it until the bridge of 1937
(data/postal-route-stations.json). Map years are first evidence, not construction years.
"""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply
from sviby_connections import _check, _add

REVIEW = 'data/postal-route-haraldsby.json'
SHORE = 'data/postal-route-farjsundet-shore.json'


def apply_postal_route_haraldsby(read, catalog):
    trial = deepcopy(catalog)
    _apply(read, trial, REVIEW)
    shore = read(SHORE)
    _check(read, trial, shore)
    _add(trial, shore)
    catalog.clear(); catalog.update(trial)
