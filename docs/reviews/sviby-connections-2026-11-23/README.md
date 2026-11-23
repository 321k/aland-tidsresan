# Sviby connections review, 2026-11-23

The review behind `docs/sviby-connections.md`.

- `scripts/prepare.py`: writes the two review files and runs the step on a copy.
- Renders: in `docs/reviews/sviby-2026-11-23/renders/junction/` (the junction and the shore road) and in the Sviby
  review's renders.
- `scope-audit.json`: the change against the pre-step snapshot.
- `batch-sviby-connections.patch`: the changes to files that also hold other work. See `patch-verification.log`.
- `node-tests.log`: the full JS suite after the change.

The snapshot is in the local review cache:
`data/map-scan-cache/review/sviby-connections/before-sviby-connections-step.json.gz`. It is the catalogue built without
this step.
