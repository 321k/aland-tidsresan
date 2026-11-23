# Mattas review, 2026-11-23

The review behind `docs/mattas-link.md`.

- `scripts/prepare.py`: writes `data/mattas-link.json` and runs the step on a copy. Renders were made with the Sviby
  review's `window.py` and `sheet.py`.
- `renders/m-*.jpg`: Mattas on the 1929, 1944, 1968, 1978, 1985 and 1995 maps.
- `scope-audit.json`: the change against the pre-step snapshot.
- `batch-mattas-link.patch`: the changes to files that also hold other work. See `patch-verification.log`.
- `node-tests.log`: the full JS suite after the change.

The snapshot is in the local review cache: `data/map-scan-cache/review/mattas/before-mattas-step.json.gz`.
