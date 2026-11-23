# Sviby review, 2026-11-23

The visual review behind `docs/svibyvagen.md`.

- `scripts/window.py`: draws a map window with a 100 m grid, the catalogue's roads for a year, and optionally OSM.
- `scripts/sheet.py`: tiles several renders into one sheet.
- `scripts/prepare.py`: writes the three review files and runs the step on a copy.
- `renders/`:
  - `t-*`, `s-*` and `nsv-*`: the Sviby road and Norra Svibyvägen;
  - `corner-sheet.jpg`: Kasbergsvägen at Talläsen, 1929–1995;
  - `z-*`, `v-*` and `w-*`: the junction and Svibyviken;
  - `result-sheet.jpg`: the catalogue in 1950, 1980, 1930 and 1990.
- `scope-audit.json`: the change against the pre-step snapshot.
- `batch-svibyvagen.patch`: the changes to files that also hold other work. See `patch-verification.log`.

The snapshot is in the local review cache: `data/map-scan-cache/review/sviby/before-sviby-step.json.gz`. It is the
catalogue built without this step.
