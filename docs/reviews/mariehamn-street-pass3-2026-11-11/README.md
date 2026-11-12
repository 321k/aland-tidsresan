# Third Mariehamn street pass — 2026-11-11

53 residential streets in Johannebo, Stenliden, Hindersböle, Norrböle, Västernäs and Skarpans are dated against the 1968, 1978, 1985 and 1995 editions of NLS sheet 101208. Together they add 10,702.47 m of newly dated streets: 4,742.89 m from 1968, 192.10 m from 1978, 5,086.41 m from 1985 and 681.07 m from 1995. No already-reviewed road is counted again as a confirmation, and no existing object changes. Each street starts at the first edition that shows it and keeps one stable geometry through 2026. That is when it first appears on these maps, not a construction year. Mellangårdsvägen shows only its southern part, up to the Fridhemsvägen junction, before 1985. The full write-up is the "Third pass" section that `batch.patch` adds to `docs/mariehamn-major-roads.md`. It includes the streets deferred because they are path-like, partial, unclear or not yet joined to the dated network.

## What is committed directly

These files belong only to this pass:

- `data/mariehamn-street-pass3.json`, the review data: 53 decisions, the per-edition observations, a deferred list and the review-sheet hashes
- `dist/assets/mariehamn-street-pass3.json`, its published copy
- `scripts/mariehamn_street_pass3.py`, the build-time compiler
- `scripts/mariehamn_major_road_followups.py`, whose second-pass validator becomes the shared `apply_reviewed_streets`, configured by ID prefix, geometry prefix, marker and required earlier pass. The second pass's output is unchanged.
- `tests/mariehamn-street-pass3.test.cjs` and `tests/test_mariehamn_street_pass3.py`

## What is in `batch.patch`

The pass also edits files that are still uncommitted or untracked because they belong to earlier work. Committing them would stage that work, so this pass's edits are kept in `batch.patch`:

- `scripts/build_temporal_objects.py` runs the pass after the Lemlandsvägen split and copies the review JSON to `dist`.
- `tests/temporal-objects.test.cjs` adds the new decisions to the global identity count.
- `dist/index.html` gets the new recent-changes card, "Ytterligare 10 kilometer gator i Mariehamn", with the others renumbered from 40 to 41. Generated preview bins and cache stamps are left out.
- `docs/mariehamn-major-roads.md` gets the third-pass section and its publication note.

The patch applies on top of the Lemlandsvägen batch's `batch.patch`. `patch-verification.log` records three checks: the patch applies to the pre-edit copies, it reproduces the working-tree files apart from the generated lines, and it reverse-applies cleanly against the working tree.

## Evidence

- `crops/*.json` holds each area crop's bbox, pixel box, scale and scan SHA-256. `scripts/crop.py` recreates the crops from the git-ignored scan cache.
- `sheets/ways-*.jpg` are the per-way contact sheets that show each modern way against the four editions, and `sheets/ways-*.json` hold their boxes. `sheets/*-labels.jpg` and `sheets/*-sheet.jpg` are the labelled area crops. All are recompressed JPEG copies.
- `overlays/*.jpg` are recompressed copies of the full-size area overlays. The originals stay in the git-ignored `data/map-scan-cache/review/mariehamn-major-roads/pass3/`, together with the pre-change catalogue snapshot `before.json.gz`.

## Scripts

- `scripts/prepare.py` writes the review JSON and captures input hashes. Ownership is checked against `before.json.gz`. It is kept for audit; do not rerun it blindly.
- `scripts/trace.py`, `sheet.py`, `labels.py`, `zoom.py` and `waysheet.py` produced the crops, labels and contact sheets.
- `scripts/audit.py` checks the build against the snapshot and writes `scope-audit.json`. Objects go from 36,073 to 36,126 and geometries from 46,161 to 46,450. All 289 new geometries have the pass-3 prefix, and no existing object changes.

## Tests

- `logs/js-tests.log`: full JavaScript suite, 467/467 passed.
- `logs/python-tests.log`: the affected Python modules, 56 tests, all passed.
- `publication/release-tests.log`: the 95 relevant JavaScript tests run against the release tree.

## Publication

Deployed with Wrangler on 2026-11-11 as version `167275da-4c53-4517-a19b-fc820fcd773e`, from a release tree built from the live version `074f8450` plus only this pass. All 286 live files were checked byte for byte against the release. See `publication/deployment.json`.
