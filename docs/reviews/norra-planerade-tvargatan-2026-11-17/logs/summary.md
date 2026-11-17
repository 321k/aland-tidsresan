# Test summary — 2026-11-17

Full JS suite on the rebuilt catalogue (`js-tests.log`, before the two fixes below): 561 tests, 544 pass, 17 fail.
The same suite on the catalogue built just before this step (`js-tests-previous-build.log`, run in a scratch copy
without the new test file): 557 tests, 542 pass, 15 fail. The 15 failures are the same tests in both runs and come
from other uncommitted work.

Two failures were new with this step and are fixed:
- `startup-loader.test.cjs` "loom reads the entire actual catalogue": the embedded loader preview counted one source
  fewer. It was regenerated with `scripts/build_loader_preview.cjs` (in `../batch.patch`).
- `mariehamn-south-streets.test.cjs` "whole source traces remain evidence": the junction check compared the whole path
  of plan streets 2 and 5. It now compares the kept `sourcePaths` and checks that only the north end moved.
After the fixes, `plan-north-street`, `mariehamn-south-streets` and `startup-loader`: 21 of 21 pass.

Python (`python-tests.log`, `test_plan_north_street.log`):
- `test_plan_north_street`: 4 of 4 pass, including "matches the build" and "never overwrites existing source geometry".
- `test_mariehamn_church_road`: passes.
- `test_planned_city_streets`: 2 failures, the same against the previous build (22 founding features without
  `planned`; the museum-building set). Not caused by this step.
- `test_postwar_city`: setUpClass error "Changed rural building input: building:osm:way-1476351279". This step does
  not touch it.
- `test_plan_1860_buildings` "matches the build": the lasarett outlines differ in the 7th decimal, because this step
  moves the plan streets that step uses as control lines. Its before-snapshot predates this step and needs re-dumping
  (the planned-buildings session was told).
