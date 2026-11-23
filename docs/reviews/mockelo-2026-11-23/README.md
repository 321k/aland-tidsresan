# Möckelö review, 2026-11-23

The review behind `docs/mockelo-road.md`.

- `scripts/prepare.py`: writes the two review files and runs the step on a copy. Renders were made with the Sviby
  review's `window.py` and `sheet.py`.
- `renders/`:
  - `ov-*`: overviews;
  - `z-*` and `e-*`: the road past Lönnelund and the sheet seam;
  - `m-*`: Möckelövägen on the Kungsö sheets.
- `scope-audit.json`: the change against the pre-step snapshot.
- `batch-mockelo-road.patch`: the changes to files that also hold other work. See `patch-verification.log`.
- `node-tests.log`: the full JS suite after the change.

The snapshot is in the local review cache: `data/map-scan-cache/review/mockelo/before-mockelo-step.json.gz`.
