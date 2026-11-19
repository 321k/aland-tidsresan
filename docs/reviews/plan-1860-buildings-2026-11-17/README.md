# Planned buildings of the 1860 town plan: 2026-11-17

The plan's 18 named building outlines and 35 pink house rows, traced by eye and shown as planned in 1860. Method: `docs/plan-1860-buildings.md`.

- `crops/`: plan crops used for tracing (the `s-*` strips and the block crops for the house rows; `streets-*` for the corrected Norragatan and Storagatan lines).
- `renders/plan-traces.jpg`: the street traces over the scan (scaled to 2048 px).
- `renders/ovl-w.jpg`, `renders/ovl-e.jpg`: the traced rows over the scan.
- `renders/trace-check.jpg`: the street traces (blue) against the rows (red); two east–west traces run through the blocks.
- `renders/placed-rows-1860.png`: buildings and rows placed on the 1860 stage.
- `data/`: the traced pixels (`house-rows-px.json` for the rows), the prototype's 35 control crossings and placements (the build now finds 40 of 48 crossings) and `scope-audit.json`, which
  compares the catalogue with the pre-batch snapshot: +53 objects, +53 geometries, +1 source, nothing else.
- `scripts/`: the crop, stage-dump and prototype placement scripts. The build step `scripts/plan_1860_buildings.py`
  is authoritative.
- `logs/`: test runs on 2026-11-19: 619 of 619 JS tests and the Python test pass.

Shared files touched: `scripts/build_temporal_objects.py` (hook and dist copy) and `dist/index.html` (loader card
"Stadsplanens hus 1860" and the regenerated loader preview). Both hold other uncommitted work, so their hunks are in `batch.patch` (verified both ways, `patch-verification.log`).

Since the batch, the re-trace session corrected the two misdrawn traces in `data/mariehamn-city-traces.json`
(`docs/plan-street-traces.md`, its own review) and the step reads them directly instead of its own `planLineCorrections`.
That traces change is not part of this commit.

Published 2026-11-19 as Cloudflare version c8ea9327-66a4-443a-adf6-b5964a97afaa (publication/).
