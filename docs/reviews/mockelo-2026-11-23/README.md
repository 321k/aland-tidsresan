# Möckelö review, 2026-11-23

The review behind `docs/mockelo-road.md`.

- `scripts/prepare.py`: writes the two review files and runs the step on a copy.
- `scripts/prepare_branches.py`: writes `data/mjolkdalsvagen.json` (the Gustavsberg branches). Renders were made with the Sviby
  review's `window.py` and `sheet.py`.
- `renders/`:
  - `ov-*`: overviews;
  - `z-*` and `e-*`: the road past Lönnelund and the sheet seam;
  - `m-*`: Möckelövägen on the Kungsö sheets;
  - `branches/`: Mjölkdalsvägen and Småholmavägen.
- `scope-audit.json`: the change against the pre-step snapshot.
- `batch-mockelo-road.patch`: the changes to files that also hold other work. See `patch-verification.log`.
- `node-tests.log` and `node-tests-branches.log`: the full JS suite after each change.
- `batch-mjolkdalsvagen.patch`: the branches step's changes to shared files.

The snapshot is in the local review cache: `data/map-scan-cache/review/mockelo/before-mockelo-step.json.gz`.
