# Mariehamn buildings r1: the earlier-drawing recheck — 2026-11-13

The building-map review deferred a building as `earlier-unclear` when a 1985 or 1995 start was proposed but the
previous edition showed dark drawing inside the outline, so that no house got a too-late date. Each such building
of b1–b10 that still exists, is not modern-only and has no curated review (226) was drawn in 1968 | 1985 | 1995 and
judged by eye. Method, rules and totals: `docs/mariehamn-building-maps.md`, section *Recheck r1*.

| decision | buildings |
|---|---|
| E1968: the 1968 edition already draws the building | 16 |
| E1985: the 1985 edition draws it (mostly a symbol the detector missed) | 67 |
| P: the earlier ink is lettering, lines, an area fill or block hatching; the proposed edition stands | 97 |
| deferred: unclear, lettering, quays | 44 |
| deferred: overlaps a printed-map symbol object (the compiler's guard caught one; both are listed) | 2 |

180 buildings are dated in batch `r1`, 1107 in all. The 927 earlier decisions and all earlier rejections are
identical.

## What is committed directly

- `data/mariehamn-building-maps.json` and its copy in `dist/assets/`: 1107 decisions, now with batch `r1`
  (each with `recheck.code` and `recheck.sourceBatch`).
- `scripts/mariehamn_building_maps.py`: accepts an `unclear` 1968 edition before the start when the block is hatched
  (`reason: hatched-block`), and marks evidence confirmed by eye with `visualReview`.
- `tests/mariehamn-building-maps.test.cjs`: new totals and an r1 test; `tests/test_mariehamn_frame_1942.py`,
  `tests/test_mariehamn_symbols_1968.py`, `tests/test_mariehamn_museum_duplicates.py`,
  `tests/test_mariehamn_museum_offsets.py`: their pre-step snapshots predate r1, so the 180 r1 buildings are left
  out of their exact comparison.
- `docs/mariehamn-building-maps.md`.

## What is in `batch.patch`

`dist/index.html`: the loader card "180 fler hus från kartorna", chained on the museum offset review's patch.

## Evidence and checks

- `sheets/`: the recheck sheets; `data/`: the building list, the decisions by cell and the two symbol-object overlaps;
  `scripts/`: `recheck.py` and `prepare.py` (with the r1 path).
- `scope-audit.json`: exactly the 180 r1 buildings changed against the previous publication.
- `logs/`, `publication/`: 513 of 513 JS tests and the affected Python tests; deployed as Cloudflare version
  925c9d83, 295 files matched live byte for byte.
