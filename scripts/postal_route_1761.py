"""The old road down to the Färjsundet ferry, in use until 1761 (docs/postal-route-crossings.md).

Ålands kulturarvsregister, Fi 8.17 ("Väglämning – Godby"): a serpentine descent to the old ferry place south of
today's Färjsundsbron, with remains of the postal road west to today's main road; in use until 1761, when a new ferry
place was built north of the bridge (the landing of Färjvägen, docs/postal-route-haraldsby.md). Its start is not known.

One review file, data/postal-route-1761.json, applied with the main-road helper (_apply in
scripts/hammarlandsvagen_main_road.py) as an old road: a new object traced from the registry outline, open from the
postal route's opening (1638) until 1761, ending at the ferry place (a stated free end). The helper records every dated
source as a printed-map review; this step marks the two that are not maps for what they are.
"""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply

REVIEW = 'data/postal-route-1761.json'


def apply_postal_route_1761(read, catalog):
    review = read(REVIEW)
    trial = deepcopy(catalog)
    _apply(read, trial, REVIEW)
    kinds = review['observationTypes']
    for o in trial['objects']:
        if o['id'] == review['oldRoad']['id']:
            for e in o['evidence']:
                k = e['id'].rsplit(':parish-map-', 1)[-1] if ':parish-map-' in e['id'] else None
                if k in kinds:
                    e['observationType'] = kinds[k]
    catalog.clear(); catalog.update(trial)
