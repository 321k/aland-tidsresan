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
- An earlier photo that covers the spot without the building is `absent`; one that does not cover it is
  `not-covered`. The photo year is first evidence, not a construction year.

## Batches

| batch | area | dated | 1991 | 1999 | 2007 | 2015 | deferred |
|---|---|---|---|---|---|---|---|
| p10 | Östra Ytternäs (building-map batch b10) | 160 | 45 | 17 | 93 | 5 | 84: 74 no photo evidence or under 40 m², 9 map ink, 1 earliest outline under 40 m² |

Most of Östra Ytternäs was built between the 1999 and 2007 photos; the 1991 dates are mostly garages and terraced
rows that the map matching missed.

## Model changes per building

- Evidence `{id}:photo-{year}` for every photo from the first one: `observationType: aerial`, the photo's capture
  date, `outcome: present`, `constructionYear: null`, a link to the photo in the town's map service.
- A new first `standing` state from the first photo year to the previous start; the first geometry period (the
  earliest measured outline) is extended back with `previousFrom`; `reconstruction` starts at the photo year with
  `photoDated: true` and the previous start kept. A modern-only outline gets a reconstruction first
  (`createdByBuildingPhotoReview`). `buildingPhotoReview` marks the object.

## Compiler checks

The review is rejected as a whole, leaving the catalogue unchanged, if a building's fingerprint changed, it repeats,
it has a review that decides its dates (curated reviews, the building-map, symbol or museum reviews), it has more than
one open phase or its start is not after the first photo year, a photo source is missing, the chronology is
inconsistent (the start is not the first `present` photo or a later photo does not show it), or its earliest outline
is under 40 m².

Tests: `tests/mariehamn-building-photos.test.cjs`, `tests/test_mariehamn_building_photos.py` (pre-step snapshot
`photos-before.json.gz` in the review cache). The scope audit finds exactly the 160 buildings changed, one new
source and no geometry or city-stage changes.
