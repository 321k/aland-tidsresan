"""Mattas: the road from the old bend at Mattas to Södersundavägen, 1929–1995 (docs/mattas-link.md).

The parish map 1012 06 Hammarby (1929), its 1944 print and the base maps 1968–1985 draw the road from Mattas round the
old bend (ways 495221553 and 160987689) and straight on north-east to Södersundavägen, which it meets about 170 m east
of where Södersundavägen's pre-1995 geometry began. That westernmost 170 m is the line of the 1995 bypass, 40–60 m to
the north-west; no map before 1995 draws a road there.

Two steps on one copy of the catalogue, which replaces it only if both pass:
- the main-road helper (_apply): the two bend ways from 1929 (whole), and the vanished link as an old-road object
  until the 1995 map;
- the coverage step of the Södersundavägen review (_coverage): Södersundavägen's 1929–1995 periods end at the junction.
Map years are first evidence, not construction years.
"""
from copy import deepcopy
from hammarlandsvagen_main_road import _apply
from sodersundavagen import _coverage

REVIEW = 'data/mattas-link.json'


def apply_mattas_link(read, catalog):
    trial = deepcopy(catalog)
    _apply(read, trial, REVIEW)
    _coverage(read, trial, REVIEW)
    catalog.clear(); catalog.update(trial)
