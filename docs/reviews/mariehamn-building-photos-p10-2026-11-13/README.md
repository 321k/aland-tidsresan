# Mariehamn buildings dated from the orthophotos: p10 (Östra Ytternäs) — 2026-11-13

The first photo-dating batch. Buildings with no symbol on the 1968–1995 base maps (`absent` in the building-map
review) in Östra Ytternäs (building-map batch b10) were drawn on Mariehamn's 1991, 1999, 2007 and 2015 orthophotos
(1 m/px) and judged by eye. Method, model changes and compiler checks: `docs/mariehamn-building-photos.md`.

| result | buildings |
|---|---|
| first seen on 1991 | 45 |
| first seen on 1999 | 17 |
| first seen on 2007 | 93 |
| first seen on 2015 | 5 |
| deferred: not on any photo (built after 2015), unclear, or under 40 m² | 74 |
| deferred: the 1985/1995 map is dark at the outline, so it may already draw the house (map ink guard) | 9 |
| deferred: earliest outline under 40 m² | 1 |

Most of the area was built between the 1999 and 2007 photos. The photo year is first evidence, not a construction year.

## What is committed directly

- `scripts/mariehamn_building_photos.py`: the new last build step.
- `data/mariehamn-building-photos.json` and its copy in `dist/assets/` (with every tile's sha256).
- `tests/mariehamn-building-photos.test.cjs`, `tests/test_mariehamn_building_photos.py` (pre-step snapshot
  `photos-before.json.gz` in the review cache); `tests/test_mariehamn_building_maps.py`,
  `tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_symbols_1968.py`,
  `tests/test_mariehamn_museum_duplicates.py`, `tests/test_mariehamn_museum_offsets.py`: also leave the
  photo-dated buildings out of their snapshot comparison.
- `docs/mariehamn-building-photos.md`.

## What is in `batch.patch`

`scripts/build_temporal_objects.py` (calls the step and copies the review), `dist/index.html` (loader card "Östra
Ytternäs från flygfotona") and `tests/test_reported_buildings_17_18.py` (leaves out the new source). See
`patch-verification.log`.

## Evidence and checks

- `sheets/p10-NN.jpg`: every building on the four photos; `data/`: the building list, decisions by cell and the map
  ink guard; `scripts/`: `fetch.py`, `sheets.py`, `guard.py`, `prepare.py`. The tiles themselves stay in the review
  cache; their sha256 values are in the review file.
- `scope-audit.json`: exactly the 160 buildings changed against the previous publication.
- `logs/`, `publication/`: 517 of 517 JS tests and the affected Python tests; deployed as Cloudflare version
  317edc02, 296 files matched live byte for byte.
