"""Fourth Mariehamn street pass: Västernäs, Klinten, Stenliden, southern Mariehamn, Ytternäs and the north.

Dated against the 1968, 1978, 1985 and 1995 sheets. The review file (data/mariehamn-street-pass4.json)
holds exact modern members, city-stage links, snapshot originals and the per-edition observations from
the visual review. Validation and the catalogue changes are the shared street-pass compiler's: every
input hash, ownership, continuity, chronology and length is checked before any object is added, and no
existing object is modified.
"""
from mariehamn_major_road_followups import apply_reviewed_streets

PASS4 = dict(path='data/mariehamn-street-pass4.json', idPrefix='road:mariehamn:street-pass4:',
             geometryPrefix='geometry:city-street-pass4:', marker='mariehamnStreetPass4', requires='mariehamnStreetPass3')


def apply_street_pass4(read, catalog):
    apply_reviewed_streets(read, catalog, PASS4)
