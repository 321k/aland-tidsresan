# Photo-dated buildings, batch p6: Södra and the southern centre — 2026-11-16

Building-map batch b6. 175 buildings without a map symbol were checked by eye on the 1991, 1999, 2007 and 2015
orthophotos (`sheets/p6-*.jpg`). Method: `docs/mariehamn-building-photos.md`. The photo year is the first evidence,
not the construction year.

* **Dated: 70** — 39 first seen in 1991, 3 in 1999, 21 in 2007, 7 in 2015.
* **Deferred: 105** — 101 with no photo evidence, unclear, overlapping or duplicate outlines, gone by 2015 or under
  40 m²; 4 where the 1985 or 1995 map is dark at the outline (`data/p6-guard.json`).

Decisions: `data/p6-decisions.json`; candidates: `data/p6.json`.

## Publication

Deployed as Cloudflare version 499222f1 together with the Nygatan / shore-road review
(`docs/reviews/mariehamn-nygatan-shore-road-2026-11-16`). The loader card "Södra från flygfotona" is in that review's
`batch.patch`, so there is no separate patch here. `scope-audit.json` separates the 70 p6 buildings from the 4 roads the
shore-road review changed.

## What is committed

`data/mariehamn-building-photos.json` and its `dist/assets/` copy as deployed (535 buildings), the p6 row in
`docs/mariehamn-building-photos.md`, and the p6 counts in `tests/mariehamn-building-photos.test.cjs`,
`tests/test_mariehamn_building_maps.py` (535), `tests/test_mariehamn_frame_1942.py` (1132),
`tests/test_mariehamn_symbols_1968.py`, `tests/test_mariehamn_museum_duplicates.py` and
`tests/test_mariehamn_museum_offsets.py` (892). The working tree already holds the next batch (p2), so these files are
committed in their p6 state, not as they are on disk.

## Checks

`logs/`: 517 of 517 JS tests and the eight affected Python test files pass.
