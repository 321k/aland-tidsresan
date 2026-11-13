# Mariehamn buildings dated from the orthophotos: p9 (Västra Ytternäs) — 2026-11-13

The second photo-dating batch. Buildings with no symbol on the 1968–1995 base maps (`absent` in the building-map
review) in Västra Ytternäs (building-map batch b9) were drawn on Mariehamn's 1991, 1999, 2007 and 2015 orthophotos
(1 m/px) and judged by eye, with the same method and scripts as p10. Method, model changes and compiler checks:
`docs/mariehamn-building-photos.md`.

| result | buildings |
|---|---|
| first seen on 1991 | 47 |
| first seen on 1999 | 9 |
| first seen on 2007 | 13 |
| first seen on 2015 | 43 |
| deferred: not on any photo (built after 2015), unclear, or under 40 m² | 187 |
| deferred: the 1985/1995 map is dark at the outline, so it may already draw the house (map ink guard) | 4 |
| deferred: the photo year is not earlier than the building's current start | 2 |

Much of the area was built after the 2007 photo, and many plots are still forest in 2015. Where an earlier photo
was ambiguous the building was left undated rather than given a later first year. With p10 the review now holds
272 buildings. The photo year is first evidence, not a construction year.

Unlike p10, some of these buildings already had a reconstruction from their archived OpenStreetMap mapping date.
The compiler keeps that date as `reconstruction.previous.from`, as the building-map step does.

## What is committed directly

- `data/mariehamn-building-photos.json` and its copy in `dist/assets/` (p10 and p9 decisions, every tile's sha256).
- `tests/mariehamn-building-photos.test.cjs` (new totals); `tests/test_mariehamn_building_maps.py`,
  `tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_symbols_1968.py`,
  `tests/test_mariehamn_museum_duplicates.py`, `tests/test_mariehamn_museum_offsets.py`: 112 more photo-dated
  buildings left out of their snapshot comparison.
- `docs/mariehamn-building-photos.md` (batch table).

## What is in `batch.patch`

`dist/index.html` (loader card "Västra Ytternäs från flygfotona") and `tests/temporal-objects.test.cjs` (the
archived-mapping-date test treats photo-dated buildings like map-dated ones). See `patch-verification.log`.

## Evidence and checks

- `sheets/p9-NN.jpg`: every building on the four photos; `data/`: the building list, decisions by cell and the map
  ink guard. The scripts (`fetch.py`, `sheets.py`, `guard.py`, `prepare.py`) are unchanged and are in the p10
  folder `docs/reviews/mariehamn-building-photos-p10-2026-11-13/scripts/`. The tiles stay in the review cache;
  their sha256 values are in the review file.
- `scope-audit.json`: exactly the 112 p9 buildings changed against the p10 publication; no geometry or source changes.
- `logs/`, `publication/`: JS tests and the affected Python tests; deployed as Cloudflare version 4ab78bca,
  296 files matched live byte for byte.
