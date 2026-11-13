# Mariehamn buildings r2: the inconsistent-symbol recheck — 2026-11-13

The building-map review deferred a building as `inconsistent` when a symbol was matched in one edition but not in a
later one. Each such building of b1–b10 that still exists, is not modern-only and has no curated review (171) was
drawn in 1968 | 1985 | 1995 and judged by eye. Method and totals: `docs/mariehamn-building-maps.md`, section
*Recheck r2*.

| decision | buildings |
|---|---|
| E1968: 1968 and every later edition draw the same building | 41 |
| E1985: 1985 and 1995 draw it | 40 |
| deferred: a later edition lacks it or shows another building, hatched 1968 blocks, quays, unclear | 89 |
| deferred: overlaps a printed-map symbol object | 1 |

81 buildings are dated in batch `r2`, 1188 in all. The later symbol was usually present but missed, set aside by the
size rule, or drawn hatched or hollow; such editions are recorded with `visualReview`.

## What is committed directly

- `data/mariehamn-building-maps.json` and its copy in `dist/assets/`: 1188 decisions with batch `r2`; r1 decisions
  gain the label `recheck.verdict` and are otherwise unchanged.
- `tests/mariehamn-building-maps.test.cjs`: new totals and an r2 test; `tests/test_mariehamn_frame_1942.py`,
  `tests/test_mariehamn_symbols_1968.py`, `tests/test_mariehamn_museum_duplicates.py`,
  `tests/test_mariehamn_museum_offsets.py`: also leave the r2 buildings out of their snapshot comparison.
- `docs/mariehamn-building-maps.md`.

## What is in `batch.patch`

`dist/index.html`: the loader card "81 fler hus från kartorna", chained on the r1 patch.

## Evidence and checks

- `sheets/`, `data/` (buildings, decisions by cell, the symbol-object overlap), `scripts/` (`recheck.py`,
  `prepare.py` with the r1/r2 path).
- `scope-audit.json`: exactly the 81 r2 buildings changed against the previous publication.
- `logs/`, `publication/`: 514 of 514 JS tests and the affected Python tests; deployed as Cloudflare version
  eff60551, 295 files matched live byte for byte.
