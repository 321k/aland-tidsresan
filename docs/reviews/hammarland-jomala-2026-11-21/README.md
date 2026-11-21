# Södersundavägen towards Jomala · review 2026-11-21

The result is in `docs/sodersundavagen.md`.

## Scripts (run from the repository root with `.venv-geo/bin/python`)

- `scripts/grid_window.py`, `scripts/drawn_in_year.py`: as in the Saltviksvägen review. `data/reference.json` is
  Södersundavägen (way 86548779) from west to east; `CENTER=E,N` centres a window on a point. Map keys are the ids in
  `data/historical-map-sources.json` or base-map sheet ids (`nls:101209:1968`)
- `scripts/prepare.py CATALOGUE_BEFORE.json.gz`: writes `data/sodersundavagen.json` and `data/sodersundavagen-jomala.json`

Snapshot (local review cache): `data/map-scan-cache/review/sodersundavagen/before-sodersundavagen-step.json.gz`.
Before-copies for the patch: `data/map-scan-cache/review/sodersundavagen/before/`.

## Files

- `scope-audit.json`
- `batch-sodersundavagen.patch` and `patch-verification.log`: the build hook, the loader card and the object count (+1)
- `node-tests.log`, `python-tests.log`
