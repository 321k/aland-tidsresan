# Mariehamn buildings dated from sheet 101208, batch b1 — 2026-11-12

444 buildings in Johannebo, Stenliden, Hindersböle and Norrböle are now shown from their first house symbol on the
1968, 1985 or 1995 base map (152, 199 and 93), instead of from their first modern outline source (2011–2026). Method,
rules, deferred buildings and the model changes are described in `docs/mariehamn-building-maps.md`. The map year is
first evidence, not a construction year, and the shape is still the earliest measured outline.

## What is committed directly

- `data/mariehamn-building-maps.json` and its published copy `dist/assets/mariehamn-building-maps.json`.
- `scripts/mariehamn_building_maps.py`: the build-time compiler. It runs after the reported-buildings step and
  validates every decision before changing the catalogue. It imports `historical_map_observations` and the still
  untracked `rural_registration` (the 1995 sheet registration).
- `tests/mariehamn-building-maps.test.cjs` and `tests/test_mariehamn_building_maps.py` (the Python tests need the
  pre-review snapshot in the git-ignored review cache and skip without it).
- `docs/mariehamn-building-maps.md`.

## What is in `batch.patch`

These files are untracked or carry other uncommitted work, so this batch's edits are kept as a patch:

- `scripts/build_temporal_objects.py`: runs the review and copies its JSON to `dist`.
- `tests/temporal-objects.test.cjs`: two tests about OSM-dated reconstructions leave out map-dated buildings, whose
  archived mapping date is checked as the previous start instead.
- `tests/test_reported_buildings_17_18.py`: ignores the later building-map source when rebuilding its baseline.
- `dist/index.html`: the loader card "444 hus i Mariehamn får äldre belägg" and the renumbering to 46. Generated
  preview bins and cache stamps are left out.

The two files shared with the 1942 review start from exactly the state its `batch.patch` produces. See
`patch-verification.log` for the three checks.

## Evidence and scripts

- `sheets/b1-sheet-*.jpg`: the 12 review tiles, 1968 | 1985 | 1995 side by side with today's outlines coloured by
  verdict (purple 1968, green 1985, blue 1995, red inconsistent, grey absent) and matched symbols in yellow. Every
  tile was inspected. `sheets/b1-review-*.jpg` are the closer checks of the hatched and lettered areas.
- `data/b1-verdict.json` (verdict per building), `b1-fills.json` (second-pass matches within 14 m),
  `b1-ink.json` (dark-ink fractions behind the deferral guard), `b1-mismatch.json`.
- `scripts/match.py` (symbol detection and matching), `verdict.py`, `sheets.py`, `conv.py`, `area.py`, and
  `prepare.py`, which writes the review from the snapshot. Kept for audit; do not rerun blindly. The scans, match
  overlays and the snapshot `before.json.gz` stay in `data/map-scan-cache/review/mariehamn-buildings/`.
- `scope-audit.json`: the snapshot equals the previously live catalogue (`6948f533…`); exactly the 444 reviewed
  objects changed, one source was added, no geometry changed, and every earlier state, period, evidence item and
  source year is kept.

## Tests

- `logs/js-tests.log`: full JavaScript suite, 494/494 passed.
- `logs/python-batch-tests.log`: this batch's Python tests and the reported-buildings tests, passed.
- `logs/python-full-suite-summary.log`: full Python suite (432 tests). The two failures this batch caused were fixed;
  the remaining 19 do not involve these buildings or the new source (rural review, parks, aerial years, city streets
  and older building reviews). That was judged from the failure output, not from a run without the batch.

## Publication

Deployed on 2026-11-12 as Cloudflare version `1354d66c-3a86-4a2e-94c5-341679f6ad9a`, built from the live release
`7c730ce9` plus only this batch. All 291 live files matched byte for byte; see `publication/deployment.json`.
