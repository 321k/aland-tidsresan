# Ytternäs modern-only houses dated from the maps — 2026-11-13

93 Ytternäs houses (b9, b10) passed the contact-sheet review but were deferred as `external-modern`: they are
`externalModern` objects, outlines that exist only in the 2026 OSM extract, with a single 2026 phase and no
reconstruction for the map evidence to extend. The review now marks them `createReconstruction`; the compiler checks
that each still has exactly one 2026 phase and no reconstruction, gives it a reconstruction starting at its first
source (marked `createdByBuildingMapReview`), and then extends it to the map year like any other building. The
outline and the 2026 evidence are unchanged. 2 start in 1968, 44 in 1985 and 47 in 1995; 1281 houses in all.
See `docs/mariehamn-building-maps.md`, section *Ytternäs*.

The contact sheets and decisions for these houses are those of `docs/reviews/mariehamn-building-maps-b910-2026-11-13`.

## What is committed directly

- `data/mariehamn-building-maps.json` and its copy in `dist/assets/`: 1281 decisions; earlier ones unchanged.
- `scripts/mariehamn_building_maps.py`: `createReconstruction` with its checks.
- `tests/mariehamn-building-maps.test.cjs`: new totals and a test of the created reconstructions (replacing the one
  that expected them deferred); `tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_symbols_1968.py`,
  `tests/test_mariehamn_museum_duplicates.py`, `tests/test_mariehamn_museum_offsets.py`: also leave these houses out
  of their snapshot comparison.
- `docs/mariehamn-building-maps.md`.

## What is in `batch.patch`

`dist/index.html`: the loader card "Resten av Ytternäs från kartorna", chained on the r2 patch.

## Checks

- `scope-audit.json`: exactly the 93 houses changed against the previous publication.
- `logs/`, `publication/`: 514 of 514 JS tests and the affected Python tests; deployed as Cloudflare version
  20511518, 295 files matched live byte for byte. `scripts/prepare.py` is the generator with the new path.
