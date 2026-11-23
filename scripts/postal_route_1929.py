"""The postal route from Emkarby through Gölby and Godby on the parish maps 1928 and 1929 (docs/postal-route-1929.md).

One review file, data/postal-route-1929.json, applied on a copy of the catalogue, which replaces it only if every check
passes:
- 'early' (the main-road helper _apply in scripts/hammarlandsvagen_main_road.py): road pieces dated from the base map
  1968 that the parish maps already draw on the same line get an earlier open period on their own geometry: Postgårdsvägen,
  the Godbyvägen pieces at Gölby, Björkäng and the Godby crossroads, von Knorringsvägen and a short piece of Emkarbyvägen
  in Hammarland.
- 'split' and 'extend' (as in scripts/postal_route_godby.py): Emkarbyvägen's period 1894–1968 ended at Tingsbacka. It is
  split at 1928, and the part from 1928 gets the stretch round the old bend to Bergens that the 1928 map draws (the same
  path as its 1968 period). 1894–1927 is unchanged.
Map years are first evidence, not construction years.
"""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply
from postal_route_godby import _extend

REVIEW = 'data/postal-route-1929.json'


def _split(review, catalog):
    """'split': a geometry period [from, to) becomes [from, at) and [at, to) on the same geometry, so that an extension
    from the map year 'at' does not reach back to the period's start (the 1894 atlas does not show where the road ran)."""
    objects = {o['id']: o for o in catalog['objects']}
    for x in review.get('split', []):
        o = objects[x['objectId']]
        gp = next((p for p in o['geometryPeriods'] if p['from'] == x['from'] and p['to'] == x['to'] and p['geometryId'] == x['geometryId']), None)
        if not gp or not (x['from'] < x['at'] < x['to']):
            raise ValueError('Changed period to split ' + x['objectId'])
        later = deepcopy(gp); later['from'] = x['at']; gp['to'] = x['at']
        o['geometryPeriods'].insert(o['geometryPeriods'].index(gp) + 1, later)


def apply_postal_route_1929(read, catalog):
    review = read(REVIEW)
    trial = deepcopy(catalog)
    _apply(read, trial, REVIEW)            # adds the review source; refuses a second run
    _split(review, trial)
    _extend(review, trial)
    catalog.clear(); catalog.update(trial)
