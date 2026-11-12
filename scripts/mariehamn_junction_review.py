"""Mariehamn junction review: the junctions deferred by the street passes.

Godbyvägen–Bolstavägen, Ålandsplan and Västra Utfarten's crossing south of Klintvägen, dated against the
1968, 1978, 1985 and 1995 sheets. The review file (data/mariehamn-junction-review.json) holds exact modern
members, city-stage links, snapshot originals and the per-edition observations from the visual review.
Validation and the catalogue changes are the shared street-pass compiler's: every input hash, ownership,
chronology and length is checked before any object is added, and no existing object is modified.
"""
from mariehamn_major_road_followups import apply_reviewed_streets

JUNCTIONS = dict(path='data/mariehamn-junction-review.json', idPrefix='road:mariehamn:junction-review:',
                 geometryPrefix='geometry:city-junction-review:', marker='mariehamnJunctionReview', requires='mariehamnStreetPass5')


def apply_junction_review(read, catalog):
    apply_reviewed_streets(read, catalog, JUNCTIONS)
