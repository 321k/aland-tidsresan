# Saltviksvägen · review 2026-11-21

The result is in `docs/saltviksvagen.md`.

## Scripts (run from the repository root with `.venv-geo/bin/python`)

- `scripts/reference.py CATALOGUE.json.gz`: writes `data/reference.json`, today's road from Laby to Kvarnbo (8.67 km)
- `scripts/overview.py`, `scripts/grid_window.py`, `scripts/drawn_in_year.py`, `scripts/ref_window.py`: as in the
  Getavägen review. `REF=data/reference-del1.json` points the grid window at Saltviksvägen del 1, and `CENTER=E,N`
  centres it on a point
- `scripts/prepare.py CATALOGUE_BEFORE.json.gz`: writes `data/saltviksvagen-east.json`. The Andelsby curve is traced on
  `renders/andelsby-tjudo-1927.jpg` (900 px for 900 m)

Snapshot (local review cache): `data/map-scan-cache/review/saltviksvagen/before-saltviksvagen-east-step.json.gz`.
Before-copies for the patch: `data/map-scan-cache/review/saltviksvagen/before/`.

## Files

- `scope-audit.json`
- `batch-saltviksvagen-east.patch` and `patch-verification.log`: the build hook, the loader card "1 av 101" and the
  object count (+1)
- `node-tests.log`, `python-tests.log`
