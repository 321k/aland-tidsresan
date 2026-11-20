# Road remnants and Postad · review 2026-11-20

The results are in `docs/road-remnants.md` and `docs/hammarlandsvagen-postad.md`. This folder holds the evidence and
the scripts.

## Scripts (run from the repository root with `.venv-geo/bin/python`)

- `scripts/remnant_window.py CODE TILE_KEY HALF YEAR OUT.jpg`: a register outline over a parish map, with the
  catalogue's roads for that year
- `scripts/prepare_postad.py CATALOGUE.json.gz`: writes `data/hammarlandsvagen-postad.json`
- `scripts/prepare_remnants.py CATALOGUE.json.gz`: writes `data/road-remnants.json`

The main-road review's `prepare.py` (in `docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/`) now has the
`postad-curve` and `postad-rejoin` boundaries.

Snapshots in the local review cache, `data/map-scan-cache/review/road-remnants/`:
- `before-postad-step.json.gz`: the build with the main-road change, without the Postad step
- `before-remnants-step.json.gz`: the build with the Postad step, without the remnant step

## Files

- `scope-audit.json`: the scope against the build before this batch. Nine objects changed, no objects added or removed;
  one geometry added and Postad's 1929 geometry changed; 13 sources added.
- `batch-road-remnants.patch` and `patch-verification.log`
- `node-tests.log`, `python-tests.log`, `python-tests-earlier.log`: the last of these is the first run, before five
  earlier replay tests were taught to ignore the remnant step's evidence
