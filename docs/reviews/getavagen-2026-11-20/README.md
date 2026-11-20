# Getavägen · review 2026-11-20

The result for the Saltvik part is in `docs/getavagen.md`.

## Scripts (run from the repository root with `.venv-geo/bin/python`)

- `scripts/overview.py`, `scripts/grid_window.py`, `scripts/drawn_in_year.py`: as in the Långnäsvägen review, with the
  Saltvik, Tjudö and Geta sheets
- `scripts/ref_window.py`: like `grid_window.py`, with today's road drawn bold
- `scripts/candidates.py`: chosen catalogue roads in colour over a map window
- `scripts/prepare_saltvik.py CATALOGUE_BEFORE.json.gz`: writes `data/getavagen-saltvik.json`

`data/reference.json` is today's Getavägen: the three objects joined end to end, 21.0 km.

Snapshot (local review cache): `data/map-scan-cache/review/getavagen/before-getavagen-saltvik-step.json.gz`.

## Files

- `scope-audit-saltvik.json`
- `batch-getavagen-saltvik.patch` and `patch-verification.log`: the build hook and the loader card "1 av 99"
- `node-tests.log`, `python-tests.log`
