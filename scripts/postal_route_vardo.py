"""The postal route's end on Vårdö: Vårdövägen through Vargata on the base maps 1012 31/1023 01 (1971–1995)
(docs/postal-route-vardo.md).

The base maps 1971 and 1978 draw Vårdövägen from the Kumnäs landing north into Vargata, then in a bend north past the
"Post" farm at Västergård–Östergård (today's Drottning Kristinas gata, already dated from 1971) and east again. Today's
straight road through Vargata (OSM 296585218) is first on the 1985 map, which is why the object was dated from 1985.
This step gives the object an early period 1971–1984 without the straight, through the main-road helper (_apply) on
a copy of the catalogue. Map years are first evidence, not construction years.
"""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply

REVIEW = 'data/postal-route-vardo.json'


def apply_postal_route_vardo(read, catalog):
    trial = deepcopy(catalog)
    _apply(read, trial, REVIEW)
    catalog.clear(); catalog.update(trial)
