# Lemlandsvägen split at Strandnäs — 2026-11-11

The rural Lemlandsvägen object `road:qgis:mariehamn:lemlandsvagen-2-100km3` is split at way 45478307. The unchanged western corridor (Strandnäs–Södergård) is shown from its 1968 evidence and the Rökerirondellen approach from 1978. The remainder keeps its identity and its 1985 start, because 1968 and 1978 show an older curve 12–31 m further south. The paired lane `lemlandsvagen-3` is dated from 1978. The full write-up is the "Lemlandsvägen split at Strandnäs" section that `batch.patch` adds to `docs/mariehamn-major-roads.md`.

## What is committed directly

These files belong only to this batch:

- `data/mariehamn-lemlandsvagen-split.json`, the review data
- `dist/assets/mariehamn-lemlandsvagen-split.json`, its published copy
- `scripts/mariehamn_lemlandsvagen_split.py`, the build-time compiler
- `tests/mariehamn-lemlandsvagen-split.test.cjs` and `tests/test_mariehamn_lemlandsvagen_split.py`

## What is in `batch.patch`

The batch also edits files that are still uncommitted or untracked because they belong to earlier work. Committing them would stage that work, so this batch's edits are kept in `batch.patch`:

- `scripts/build_temporal_objects.py`: runs the split after the follow-up pass and copies the review JSON to `dist`.
- `tests/temporal-objects.test.cjs`: the global identity count includes the two new objects.
- `tests/qgis-roads.test.cjs`: ranges moved by the split may belong to the split sections, and the lane's 1978 start is read from the object.
- `tests/test_qgis_road_reconciliation.py`: the QGIS replay starts from the catalogue without the split objects, since the split runs after the QGIS step.
- `dist/index.html`: the new recent-changes card, with the others renumbered from 39 to 40. Generated preview bins and cache stamps are left out.
- `docs/mariehamn-major-roads.md`: adds the split section and its publication note.

`patch-verification.log` records that the patch applies to reconstructed pre-edit copies, reproduces the working-tree files exactly, and reverse-applies cleanly against the working tree.

## Not committed

- Generated outputs: `dist/assets/temporal-objects.json.gz` and the cache stamps in `dist/`.
- Original-scan crops and full-size overlays in the git-ignored `data/map-scan-cache/review/mariehamn-major-roads/lemlandsvagen/`, plus the pre-change catalogue snapshot `before.json.gz`. `crops/*.json` keeps each crop's bbox, pixel box, scale and scan SHA-256, and `scripts/crop.py` recreates the crops. `sequences/` holds JPEG copies of the four-edition comparisons and the two 1995 visual checks.

## Scripts

- `scripts/prepare.py` captures input hashes. It is kept for audit; do not rerun it blindly.
- `scripts/trace.py` produced the centre-line samples, and `scripts/compare.py` the per-bin deviations.
- `scripts/audit.py` rebuilds a baseline without the split and writes `scope-audit.json`.

## Tests

- `logs/js-tests.log`: full JavaScript suite, 459/459 passed.
- `logs/python-tests.log`: the split and QGIS reconciliation Python tests, 38/38 passed.
- `publication/release-js-tests.log`: the 94 relevant JavaScript tests run against the release tree.

The wider Python suite still has failures in `test_rural_map_review` (4) and `test_rural_sectors` (1). They appear with and without this batch and come from unrelated uncommitted rural-review work.

## Publication

Deployed with Wrangler on 2026-11-11 as version `074f8450-e6bd-4e6b-ba4a-50420ecfdb4a`, from a release tree built from the live version plus only this batch. See `publication/deployment.json`.
