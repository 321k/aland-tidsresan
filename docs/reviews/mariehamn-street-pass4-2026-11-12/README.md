# Fourth Mariehamn street pass — 2026-11-12

This pass dates 63 streets against the 1968, 1978, 1985 and 1995 editions of NLS sheet 101208. They are in Västernäs, Klinten, southern Mariehamn, Ytternäs and Norrböle north/Dalkarby. Together they add 10,696.10 m of newly dated streets:

- 1968: 3,431.26 m
- 1978: 36.63 m
- 1985: 4,906.59 m
- 1995: 2,321.62 m

Nothing already reviewed is counted again, and no existing object changes. Each street starts at the first edition that shows it and keeps one stable geometry through 2026. That is first map evidence, not a construction year.

- **Klintvägen** shows its straight northern part from 1968 and the whole street from 1978, when the bend to Västra Utfarten first appears. **Mjölnargränd** shows its east–west part from 1968 and the whole street from 1995.
- **Västra Utfarten's west carriageway** shows from 1995 and counts 0 m, because earlier editions draw a single road.
- **Klintvägen's 1978 connection** (two lanes and the crossing pieces) counts once.

The full write-up is the "Fourth pass" section that `batch.patch` adds to `docs/mariehamn-major-roads.md`. It includes the deferred streets: the 1995 Stenliden block, Bergshöjden, Mästargränd, Knipgränd, Alfågelgränd, Tibastvägen, Framnäsvägen and Varvsvägen, among others.

## What is committed directly

These files belong only to this pass:

- `data/mariehamn-street-pass4.json`: the review data, with 63 decisions, the per-edition observations, the deferred list and the review-sheet hashes.
- `dist/assets/mariehamn-street-pass4.json`: its published copy.
- `scripts/mariehamn_street_pass4.py`: the build-time compiler. It uses the shared `apply_reviewed_streets` unchanged.
- `tests/mariehamn-street-pass4.test.cjs` and `tests/test_mariehamn_street_pass4.py`.

## What is in `batch.patch`

The pass also edits files that are still uncommitted or untracked because they belong to earlier work. Committing them would stage that work, so this pass's edits are kept in `batch.patch`:

- `scripts/build_temporal_objects.py` runs the pass after the third pass and copies the review JSON to `dist`.
- `tests/temporal-objects.test.cjs` includes the new decisions in the global identity count.
- `dist/index.html` gets the new recent-changes card, "Ytterligare 10,7 kilometer gator i Mariehamn", with the other cards renumbered to 42. The previous street-pass card is hidden. Generated preview bins and cache stamps are left out.
- `docs/mariehamn-major-roads.md` gets the fourth-pass section and its publication note.

The patch applies on top of the third pass's `batch.patch`. `patch-verification.log` records three checks:

- the patch applies to the pre-edit copies;
- applied, it reproduces the working-tree files, apart from the generated lines;
- it reverse-applies cleanly against the working tree.

## Evidence

- `sheets/ways-*.jpg` are the per-way contact sheets. Each shows the modern way outlined on 1968, then the unmarked 1968, 1978, 1985 and 1995 crops of the same ground. `sheets/ways-*.json` hold their pixel boxes and scan hashes.
- `crops/*.json` record the area crops' bbox, pixel box, scale and scan SHA-256 for `klint` (the Klinten gränder), `klintbend` (Klintvägen's bend), `sten` (the Stenliden block in 1995) and `vik` (Vikingagränd, Lövdalsvägen and Fallgärdsvägen). `scripts/crop.py` recreates them.
- `overlays/*.jpg` are recompressed copies of the area overlays and comparison strips.

The original-size images and the pre-change catalogue snapshot `before.json.gz` stay in the git-ignored `data/map-scan-cache/review/mariehamn-major-roads/pass4/`.

## Scripts

- `scripts/prepare.py` writes the review JSON and captures input hashes. It checks ownership against `before.json.gz`. It is kept for audit; do not rerun it blindly.
- `scripts/waysheet.py` and `scripts/crop.py` produced the sheets and crops.
- `scripts/audit.py` checks the build against the snapshot and writes `scope-audit.json`. Objects go from 36,126 to 36,189 and geometries from 46,450 to 46,839. All 389 new geometries have the pass-4 prefix, and no existing object changes.

## Tests

- `logs/js-tests.log`: the full JavaScript suite, 474/474 passed.
- `logs/python-tests.log`: the street-pass, major-road, Lemlandsvägen and QGIS reconciliation Python modules, 71 tests, all passed.
- `publication/release-tests.log`: the 137 relevant JavaScript tests, run against the release tree.

## Publication

Deployed with Wrangler on 2026-11-12 as version `e9000b11-534f-4a4e-b00a-8a86403cec36`. The release tree was built from the live version `167275da` plus only this pass. All 287 live files were checked byte for byte against the release. See `publication/deployment.json`.
