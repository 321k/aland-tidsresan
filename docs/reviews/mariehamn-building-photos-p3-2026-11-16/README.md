# Mariehamn buildings dated from the orthophotos: p3 (blocks south of Norrböle) — 2026-11-16

The fourth photo-dating batch. Buildings with no symbol on the 1968–1995 base maps (`absent` in the building-map
review) in the blocks just south of Norrböle, including the guest marina (building-map batch b3), were drawn on
Mariehamn's 1991, 1999, 2007 and 2015 orthophotos (1 m/px) and judged by eye. Method, model changes and compiler
checks: `docs/mariehamn-building-photos.md`.

| result | buildings |
|---|---|
| first seen on 1991 | 12 |
| first seen on 1999 | 0 |
| first seen on 2007 | 16 |
| first seen on 2015 | 9 |
| deferred: not on any photo (built after 2015), unclear, or under 40 m² (most marina cabins) | 62 |
| deferred: the 1985 map is dark at the outline, so it may already draw the house (map ink guard) | 5 |
| deferred: an earlier curated review decides its dates | 14 |

The first build stopped: the compiler rejected a decision for a building with a `historicalReview` (church dating).
Thirteen marina boathouses merged by the waterfront `neighborhoodReviews` were also among the decisions. `prepare.py`
now defers every such building as `curated-review` (the change is in `scripts/prepare.py` here; the other scripts
are unchanged from `docs/reviews/mariehamn-building-photos-p10-2026-11-13/scripts/`). The earlier batches p10, p9 and
p4 had none, and their 351 decisions are unchanged. The photo year is first evidence, not a construction year.

## What is committed directly

- `data/mariehamn-building-photos.json` and its copy in `dist/assets/` (p10, p9, p4 and p3 decisions).
- `tests/mariehamn-building-photos.test.cjs` (new totals and the `curated-review` count);
  `tests/test_mariehamn_building_maps.py`, `tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_symbols_1968.py`,
  `tests/test_mariehamn_museum_duplicates.py`, `tests/test_mariehamn_museum_offsets.py`: 37 more photo-dated
  buildings left out of their snapshot comparison.
- `docs/mariehamn-building-photos.md` (batch table and the new deferral).

## What is in `batch.patch`

`dist/index.html` (loader card "Kvarteren söder om Norrböle från flygfotona"). See `patch-verification.log`.

## Evidence and checks

- `sheets/p3-NN.jpg`: every building on the four photos; `data/`: the building list, decisions by cell and the map
  ink guard. The tiles stay in the review cache; their sha256 values are in the review file.
- `scope-audit.json`: exactly the 37 p3 buildings changed against the p4 publication; no geometry or source changes.
- `logs/`, `publication/`: 517 of 517 JS tests and the affected Python tests; deployed as Cloudflare version
  aa32b9ae, 296 files matched live byte for byte.
