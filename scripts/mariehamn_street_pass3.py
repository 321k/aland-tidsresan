"""Third Mariehamn street pass: residential streets dated against the 1968, 1978, 1985 and 1995 sheets.

The review file (data/mariehamn-street-pass3.json) holds exact modern members, city-stage links,
snapshot originals and the per-edition observations from the visual review. Validation and the
catalogue changes are the second pass's: every input hash, ownership, continuity, chronology and
length is checked before any object is added, and no existing object is modified.
"""
from mariehamn_major_road_followups import apply_reviewed_streets

PASS3 = dict(path='data/mariehamn-street-pass3.json', idPrefix='road:mariehamn:street-pass3:',
             geometryPrefix='geometry:city-street-pass3:', marker='mariehamnStreetPass3', requires='majorRoadFollowup')


def apply_street_pass3(read, catalog):
    apply_reviewed_streets(read, catalog, PASS3)
