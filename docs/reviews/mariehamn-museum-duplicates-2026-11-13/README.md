# Museum-map duplicates and replacements — 2026-11-13

Started from overlapping houses along Storagatan: several 1920 museum-map houses sat about half a house from the same
building's later outline, so the map showed the house twice. A town-wide check found 53 pairs of a museum house
overlapping a later house. Each was judged on the 1942 orthophoto and the 1968 sheet 101208. Method, decision table,
model changes and compiler checks are in `docs/mariehamn-museum-duplicates.md`.

| decision | museum houses |
|---|---|
| merged into the later house, which is shown from 1920 | 15 |
| ended at the successor's first reviewed start (1942, 1975, 1983 or 2021) | 16 |
| deferred (sheds, unclear shape, map review records absence) | 16 houses, 18 pairs |

Town-wide overlapping pairs went from 104 to 69; museum pairs from 53 to the 18 deferred ones, and no new pair
appeared.

## What is committed directly

- `scripts/mariehamn_museum_duplicates.py`: the new last build step; validates every input before changing anything.
- `data/mariehamn-museum-duplicates.json` and its copy in `dist/assets/`: merges, replacements, deferred pairs and
  input fingerprints.
- `tests/mariehamn-museum-duplicates.test.cjs`, `tests/test_mariehamn_museum_duplicates.py`: new regression checks
  (the Python tests use the pre-step snapshot `museum-before.json.gz` in the review cache and skip without it).
- `tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_building_maps.py`, `tests/test_mariehamn_symbols_1968.py`:
  apply the new step after theirs before comparing with the build; `tests/mariehamn-symbols-1968.test.cjs`: a rejected
  symbol house may now start in 1920 when it was merged with a museum house.
- `docs/mariehamn-museum-duplicates.md`.

## What is in `batch.patch`

Files that are untracked or carry other uncommitted work (`patch-verification.log`):

- `scripts/build_temporal_objects.py`: calls `apply_museum_duplicates` after the 1968 symbol review and copies the
  review to `dist/assets`.
- `dist/index.html`: the loader card "Färre dubbla hus i centrum" and the renumbered cards.
- `tests/city-buildings.test.cjs`: the provisional museum-house count subtracts the merges, and the story check uses
  the first museum house that no review has ended.
- `tests/temporal-objects.test.cjs`: the provisional-building count and reviewed ends include this review; the
  street-alignment check reads a merged museum house from the record its merge keeps.
- `tests/test_reported_buildings_17_18.py`: also leaves out the new review source.

## Evidence and checks

- `sheets/museum-NN.jpg`: every pair on the 1942 photo (plain and with outlines) and the 1968 map;
  `storagatan-1942.jpg` and `storagatan-maps.jpg`: the Storagatan pairs that started the review.
- `data/`: the pairs with offsets and areas, and the overlap lists before and after (town-wide and Storagatan).
- `scripts/`: `sheets.py`, `prepare.py` (writes the review), and the two overlap checks.
- `scope-audit.json`: exactly the 15 merged museum objects removed and 44 objects changed; no geometry or city-stage
  changes.
- `logs/`: 508 of 508 JS tests and the affected Python tests; `publication/`: deployed as Cloudflare version 5e4fbc44
  from the live release plus only this batch, 294 files matched live byte for byte.
