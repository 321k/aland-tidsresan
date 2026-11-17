# Norra planerade tvärgatan in the 1860 plan

Review: `data/plan-north-street.json` (source `review:plan-north-street`), applied at build time by
`scripts/plan_north_street.py` right after the church-road step. Reviewed 2026-11-17; evidence in
`docs/reviews/norra-planerade-tvargatan-2026-11-17/`.

## Why

The 1860 plan draws a northern cross street ("N o r r a … g a t a n") one block row north of the street that the plan
streets are aligned to the real Norragatan by (`scripts/planned_city_streets.py`). Its trace, `plan-1860-trace-8`, was
never aligned. Placed through the plan's affine registration, it ran 75 m north of the reconstructed Norragatan in the
west and 26 m in the east. So it crossed the city stages' grid at an angle and cut the plan streets ending on it short
or long by up to 24 m.

On the plan scan, at its true scale (view pixels × 1.1228, `plan-traces-scaled.png`), the block row between the two
streets is 47 m deep. Measured three times through the plan's own registration it was 47.0, 46.8 and 46.9 m. The plan
draws the two streets parallel.

## What changes

In `city-reconstruction-1860`, `-1861` and `-1871`:

| feature | change |
|---|---|
| `plan-1860-street-18` (the trace) | one straight line, parallel to a least-squares line through the stage's reconstructed Norragatan and 47 m north of it. It runs from the west shore street (`plan-1860-street-0`) to Strandgatan (`road:postwar:way-78489469`), about 1,009 m. |
| `plan-1860-street-0`, `-1`, `-2`, `-5` | the end on the old trace moves along the street's own direction onto the new line: 24 m, 10.6 m and 5.4 m shorter; street-5 is 8.9 m longer |
| `block:17` | recomputed between the streets with the early-city block rule (`docs/early-city-streets.md`): 1,599 → about 3,640 m² |

Each changed feature keeps its earlier geometry in `sourcePaths` and gets an `alignment` note naming the review. No
object, no other feature and no other stage changes. The later planned-buildings step (`scripts/plan_1860_buildings.py`)
uses the moved plan streets as control lines; its lasarett outlines shift by at most 0.01 m from rounding. Torggatan and Strandgatan cross the line and are untouched.

The reconstructed Norragatan is straight to within 1.6 m (the step stops above `straightnessMeters`, 3 m). Offsetting
the fitted line rather than the polyline keeps short end segments of the reconstruction from bending the planned
street. Norragatan's vertices lie 45.8–48.6 m from the new street.

## Checks in the step

Everything is validated before any stage changes:

- the input fingerprints of the trace, the four attached streets and the block;
- the straightness of Norragatan, and that the line lies north of it;
- each attached street ends within 3 m of the old trace and moves at most `maxMoveMeters` (40 m);
- the line meets Strandgatan;
- the recomputed block is enclosed, within a 1 m tolerance because the grid's joints miss by up to 0.6 m, and gives
  exactly one part between `minArea` and `maxArea`;
- the review applies only once.

Tests: `tests/plan-north-street.test.cjs` (built catalogue) and `tests/test_plan_north_street.py` (rejected inputs,
consistency with the build; needs the pre-step snapshot in the local review cache).

## Limits

The street's position is an interpretation of the plan, not evidence of a built street. The depth comes from the plan
itself, not from a survey.
