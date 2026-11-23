"""Main roads on the base maps, batch 1: Saltvik north and west and Geta (docs/main-roads-saltvik.md).

Road objects dated from a later base-map edition (1978, 1984 or 1993) that the first edition (1968) already draws as a
main road, in red, on the same line get an earlier open period on their own geometry: whole where the whole object is
the road the map draws, or the stretches where it is (a cut), with a second stage from a later edition where that map
draws more of it. The main-road helper (_apply in scripts/hammarlandsvagen_main_road.py) checks each object's input,
geometry, length and ranges, and that the first year is the first map marked present. Where the first edition draws the
road on another line (an old bend), that stretch is left out here and listed in the docs.
Map years are first evidence, not construction years.
"""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply

REVIEW = 'data/main-roads-saltvik.json'


def _whole_stages(review, catalog):
    """The helper marks a later stage as partial; where that stage covers the whole object (range [0, 1]) it is full."""
    ids = {e['objectId'] for e in review['early'] if e.get('laterStage')}
    for o in catalog['objects']:
        if o['id'] not in ids: continue
        for x in o['geometryPeriods'] + o['evidence']:
            if x.get('coverage') == 'partial' and x.get('canonicalRange') == [0, 1]:
                x['coverage'] = 'full'


def apply_main_roads_saltvik(read, catalog):
    trial = deepcopy(catalog)
    _apply(read, trial, REVIEW)
    _whole_stages(read(REVIEW), trial)
    catalog.clear(); catalog.update(trial)
