"""Fifth and final Mariehamn street pass: gap and junction pieces of dated streets, the Stenliden block and Lotsby.

Dated against the 1968, 1978, 1985 and 1995 sheets. The review file (data/mariehamn-street-pass5.json)
holds exact modern members, city-stage links, snapshot originals and the per-edition observations from
the visual review. Validation and the catalogue changes are the shared street-pass compiler's: every
input hash, ownership, continuity, chronology and length is checked before any object is added, and no
existing object is modified.
"""
from mariehamn_major_road_followups import apply_reviewed_streets

PASS5 = dict(path='data/mariehamn-street-pass5.json', idPrefix='road:mariehamn:street-pass5:',
             geometryPrefix='geometry:city-street-pass5:', marker='mariehamnStreetPass5', requires='mariehamnStreetPass4')


def apply_street_pass5(read, catalog):
    apply_reviewed_streets(read, catalog, PASS5)
