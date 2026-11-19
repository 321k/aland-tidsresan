# Långnäsvägen · review 2026-11-19

The result and the reasoning are in `docs/langnasvagen.md`. This folder holds the evidence and the scripts.

## Scripts (run from the repository root with `.venv-geo/bin/python`)

- `scripts/overview.py`, `scripts/grid_window.py`, `scripts/drawn_in_year.py`: as in the Lemlandsvägen east review
- `scripts/prepare.py CATALOGUE_BEFORE.json.gz`: writes `data/langnasvagen.json` and `data/langnasvagen-skag.json`.
  The pixel waypoints are read on `renders/skag-close-1929.jpg` and `renders/sodergard-close-1929.jpg`.

`data/reference.json` is today's road (`road:qgis:lumparland:langnasvagen-100km3`), extended along OSM Långnäsvägen to
Långnäs, in EPSG:3874.

The catalogue before the step is kept in the local review cache:
`data/map-scan-cache/review/langnasvagen/before-langnasvagen-step.json.gz`.

## Patch

`batch-langnasvagen.patch` holds the changes to files that also hold other uncommitted work:
- `scripts/build_temporal_objects.py`: the hook and the asset copies
- `dist/index.html`: the loader card "1 av 96"
- `tests/temporal-objects.test.cjs`: the object count, +2
- `tests/qgis-roads.test.cjs`: reads `mainRoadReview`

`patch-verification.log` records how it was checked.

## Test logs

- `python-tests.log`: the replay test, and the Hammarlandsvägen and Lemland replay tests that use the two changed helpers
- `node-tests.log`: the new, loader, QGIS-road and object-count JS tests
