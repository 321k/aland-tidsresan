# Mariehamn buildings dated from the orthophotos (1991–2015)

Review: `data/mariehamn-building-photos.json` (source `review:mariehamn-building-photos`), applied at build time by
`scripts/mariehamn_building_photos.py` as the last step of `scripts/build_temporal_objects.py`. Reviewed 2026-11-13.

## Why

The building-map review (`docs/mariehamn-building-maps.md`) dates houses from the 1968, 1985 and 1995 base maps.
About 1,950 Mariehamn buildings have no symbol on any of them (`absent`); most were built after 1995 and are shown
only from their first OpenStreetMap year (2012–2026). The town's orthophotos give earlier first evidence.

## Method

- Tiles of the 1991, 1999, 2007 and 2015 orthophotos (`Ortofoto YYYY`, 1 m/px, 256 m tiles in EPSG:3874) are fetched
  from Mariehamn's map service (`data/map-scan-cache/review/photo-dating/fetch.py`; every tile's sha256 is recorded
  in the review). An empty answer means the photo does not cover the tile; the 1991 photo does not cover the
  southern edge of Östra Ytternäs.
- Every `absent` building of a building-map batch is drawn on the four photos with its outline (`sheets.py`) and
  judged by eye: the first photo that shows it, with every later photo showing it too, or no decision (not on any
  photo, i.e. built after 2015; unclear; or under 40 m², too small to judge at 1 m/px).
- Map ink guard (`guard.py`): a building first seen on the 1991 (1999) photo whose outline is dark on the 1985 (1995)
  map, after the local registration shift, may already be drawn there; it is deferred so that no date is set too late.
  The dark share misses open and hatched symbols (sheds, halls), so since p2 the map crops are also inspected by eye:
  `KEY-visual.json` lists buildings whose outline contains or touches a map symbol, and `guard.py` defers them too.
  From p11 the enlarged crops include the 1978 map, and a filled symbol there defers the building too.
- An earlier photo that covers the spot without the building is `absent`; one that does not cover it is
  `not-covered`. The photo year is first evidence, not a construction year.

## Batches

| batch | area | dated | 1991 | 1999 | 2007 | 2015 | deferred |
|---|---|---|---|---|---|---|---|
| p10 | Östra Ytternäs (building-map batch b10) | 160 | 45 | 17 | 93 | 5 | 84: 74 no photo evidence or under 40 m², 9 map ink, 1 earliest outline under 40 m² |
| p9 | Västra Ytternäs (building-map batch b9) | 112 | 47 | 9 | 13 | 43 | 193: 187 no photo evidence or under 40 m², 4 map ink, 2 start not after the first photo year |
| p4 | Övernäs (building-map batch b4) | 79 | 17 | 3 | 10 | 49 | 94: 62 no photo evidence or under 40 m², 30 map ink, 2 start not after the first photo year |
| p3 | blocks south of Norrböle and the marina (building-map batch b3) | 37 | 12 | 0 | 16 | 9 | 81: 62 no photo evidence or under 40 m², 5 map ink, 14 dated by an earlier curated review |
| p7 | Västernäs and the northern centre (building-map batch b7) | 77 | 35 | 5 | 28 | 9 | 86: 77 no photo evidence, unclear, overlapping outlines or under 40 m², 8 map ink, 1 dated by an earlier curated review |
| p6 | Södra and the southern centre (building-map batch b6) | 70 | 39 | 3 | 21 | 7 | 105: 101 no photo evidence, unclear, overlapping outlines or under 40 m², 4 map ink |
| p2 | the western strip from Klinten and the yard past Notgrundet (building-map batch b2) | 100 | 6 | 6 | 51 | 37 | 80: 69 no photo evidence, unclear, overlapping outlines or under 40 m², 10 map ink (8 by eye: open or hatched symbols), 1 start not after the first photo year |
| p11 | Dalen and Espholm, the peninsula south of Lervik (building-map batch b11) | 8 | 0 | 5 | 2 | 1 | 55: 48 no photo evidence, unclear or under 40 m² (many allotment cabins), 7 map ink (all by eye: 3 open symbols, 2 touching, 2 with a filled symbol on the 1978 map) |
| p1 | Johannebo, Stenliden, Hindersböle and Norrböle with their industrial blocks (building-map batch b1) | 214 | 35 | 34 | 94 | 51 | 277: 197 no photo evidence, unclear, overlapping or rebuilt outlines or under 40 m², 76 map ink (48 by eye: 14 open or hatched symbols, 32 touching, 2 with a filled symbol on the 1978 map), 1 earliest outline under 40 m², 3 start not after the first photo year |
| total | | 857 | 236 | 82 | 328 | 211 | 1055 |

Most of Östra Ytternäs was built between the 1999 and 2007 photos; the 1991 dates are mostly garages and terraced
rows that the map matching missed.

## Model changes per building

- Evidence `{id}:photo-{year}` for every photo from the first one: `observationType: aerial`, the photo's capture
  date, `outcome: present`, `constructionYear: null`, a link to the photo in the town's map service.
- A new first `standing` state from the first photo year to the previous start; the first geometry period (the
  earliest measured outline) is extended back with `previousFrom`; `reconstruction` starts at the photo year with
  `photoDated: true` and the previous start kept. A modern-only outline gets a reconstruction first
  (`createdByBuildingPhotoReview`). `buildingPhotoReview` marks the object.

Since p3, `prepare.py` defers a building whose dates an earlier curated review decides (`curated-review`), such as the
waterfront boathouse merges and church dating, before the compiler would reject it; p10, p9 and p4 had none.

## Compiler checks

The review is rejected as a whole, leaving the catalogue unchanged, if a building's fingerprint changed, it repeats,
it has a review that decides its dates (curated reviews, the building-map, symbol or museum reviews), it has more than
one open phase or its start is not after the first photo year, a photo source is missing, the chronology is
inconsistent (the start is not the first `present` photo or a later photo does not show it), or its earliest outline
is under 40 m².

Tests: `tests/mariehamn-building-photos.test.cjs`, `tests/test_mariehamn_building_photos.py` (pre-step snapshot
`photos-before.json.gz` in the review cache). The scope audit finds exactly the 160 buildings changed (p10), one new
source and no geometry or city-stage changes; for p9, against the p10 release, exactly the 112 p9 buildings changed
and nothing else; for p4, against the p9 release, exactly the 79 p4 buildings; for p3, against the p4 release, exactly the 37 p3 buildings; for p7, against the p3 release, exactly the 77 p7 buildings; for p6, against the p7 release, exactly the 70 p6 buildings; for p2, against the p6 and street release, exactly the 100 p2 buildings; for p11, against the p2 release, exactly the 8 p11 buildings; for p1, against the p11 release, exactly the 214 p1 buildings.

Open in p2: the yard halls `building:osm:way-165914218` (1,143 m²) and `way-165914225` (2,516 m²) and the shed
`way-165914206` are `absent` in the building-map review, but the 1985 map draws hatched or open symbols inside their
outlines. They are deferred here; the building-map matching should be revisited for hatched symbols. p1 (the
industrial blocks of b1) shows the same pattern for 14 more buildings with an open or hatched symbol inside.

Open in p7: `building:osm:relation-2315517` and `building:osm:way-162298851` are two objects for the same 713 m²
building (identical outlines, starts 2012 and 2025). Both are left undated here; they need a duplicate review.
