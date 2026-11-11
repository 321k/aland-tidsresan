# Mariehamn larger roads, second pass — 2026-11-11

Junction reconstruction at Strandnäs, Nya Godbyvägen's 1985 curve, Åsvägen, northern Ålandsvägen, separately dated roundabouts and further streets: 7,641.79 m newly dated in 37 persistent objects. The full write-up is the "Second pass" section added to `docs/mariehamn-major-roads.md` by `batch.patch`.

## What is committed directly

These files belong only to this batch:

- `data/mariehamn-major-road-followups.json`, the review data
- `dist/assets/mariehamn-major-road-followups.json`, its published copy
- `scripts/mariehamn_major_road_followups.py`, the build-time compiler
- `tests/mariehamn-major-road-followups.test.cjs` and `tests/test_mariehamn_major_road_followups.py`

## What is in `batch.patch`

The batch also edits files that are still uncommitted or untracked because they belong to earlier work: the catalogue build, the first-pass road docs, the temporal-object tests and the loader page. Committing those files would stage that earlier work, so this batch's edits to them are kept in `batch.patch` instead:

- `scripts/build_temporal_objects.py`: calls the compiler after the first pass and copies the review JSON to `dist`.
- `tests/temporal-objects.test.cjs`: two assertions updated, one for the global identity count and one for the Österleden ramps that are now owned by the Rökerirondellen approach object.
- `dist/index.html`: the new recent-changes card, with the others renumbered from 38 to 39.
- `docs/mariehamn-major-roads.md`: replaces the first pass's follow-up list and adds the second-pass section.

`patch-verification.log` records that the patch applies to reconstructed pre-edit copies, reproduces the working-tree files exactly, and reverse-applies cleanly.

## Not committed

- Generated outputs: `dist/assets/temporal-objects.json.gz` and the cache-version stamps in `dist/`. The rebuilt catalogue also contains unrelated, uncommitted `data/rural-map-review.json` changes.
- Original-scan crops (219 MB) in `data/map-scan-cache/review/mariehamn-major-roads/followups/`, which is git-ignored. `crops/*.json` keeps each crop's bbox, pixel box, scale and scan SHA-256, and `scripts/crop.py` recreates the crops from the cached scans. `sequences/` holds JPEG copies of the key four-edition comparisons.
- The 3.4 MB full Python log and the pre-change catalogue snapshot, which stay in the review cache. `logs/python-tests-summary.log` lists the 19 failures. None are caused by this batch: 17 trace to the unrelated rural-review and building changes, and two tests were already failing for earlier passes.

## Scripts

- `scripts/prepare.py` captures input hashes. It is kept for audit; do not rerun it blindly.
- `scripts/trace.py` produced the raw centre-line samples.
- `scripts/audit.py` rebuilds a baseline without this pass and writes `scope-audit.json`.

## Publication

Deployed with Wrangler on 2026-11-11 as version `82982643-8c44-41dd-8842-a69babacd39c`. See `publication/`.
