# Norra planerade tvärgatan — 2026-11-17

Visual review of the 1860 plan's northern cross street. Method, decisions and checks: `docs/plan-north-street.md`.

- `plan-traces-scaled.png`: the plan scan with the traces drawn at the scan's scale (view pixels × 1.1228). The cross
  street runs parallel to the Norragatan line, one 47 m block row north of it.
- `grid-proposal-1861.png`: the 1861 stage with the old trace and the proposed line.
- `before-after-1861.png`: the 1861 stage before and after the step (red: the street; blue: the moved plan streets;
  orange: the recomputed block).
- `app-1861.jpg`: the rebuilt app at 1861 (the dashed line is the planned street).
- `scripts/prepare.py`: writes `data/plan-north-street.json` with fingerprints from the catalogue dumped right after
  `apply_church_road`. That dump is kept in the ignored review cache, `data/map-scan-cache/review/plan-north-street/before.json.gz`.
- `scope-audit.json`: what changed against the catalogue built just before this step was added (15:01, with the
  planned-buildings step). The 6 features in each of the three stages and the new source changed; no object changed. Four
  planned-building geometries (the lasarett) moved by at most 0.01 m, because that later step extends the moved plan
  streets and their new ends are rounded to 7 decimals.
- `logs/`: test output; `logs/summary.md` explains every failure.
- `batch.patch`: the changes in files that also hold other uncommitted work, verified in `patch-verification.log`:
  - the build hook in the untracked `scripts/build_temporal_objects.py` (the step after `apply_church_road`, and a
    copy of `data/plan-north-street.json` to `dist/assets/`);
  - the regenerated loader preview in `dist/index.html` (only the preview block; the file also holds the
    planned-buildings loader card);
  - `tests/mariehamn-south-streets.test.cjs` (untracked): the junction check compares the kept `sourcePaths` of plan
    streets 2 and 5 when this review applies.
  The generated catalogue is rebuilt from the committed review.

An earlier render drew the traces without the 1.1228 scale and wrongly suggested the trace cut through blocks. It
was discarded.
