# Main roads on the base maps, batch 1: northern and western Saltvik and Geta

Part of the main-road survey (`docs/reviews/main-roads-2026-11-23/README.md`).

Build step: `apply_main_roads_saltvik` in `scripts/main_roads_saltvik.py`, after the postal-route steps.

Review data: `data/main-roads-saltvik.json` (copied to `dist/assets/`), written by
`docs/reviews/main-roads-2026-11-23/scripts/prepare_saltvik.py`.

## Method

**Maps:** base-map sheets 1021 04, 05, 07, 08 and 11, editions 1968, 1978 and 1984.

1. `scripts/objects_for_gaps.py` lists the catalogue objects behind the survey's red candidates on these sheets
   (`batch1-objects.json`).
2. `scripts/match_editions.py` walks each object's line in 10 m steps on every edition before its current first year.
   It marks where the map's red main-road symbol lies within 12 m. The mask (`scripts/redmask.py`) keeps the strong red
   band and drops thin red lines and text. The output is `batch1-match.json`.
3. **Checking by eye.** Every object was checked along its whole line on the first edition, with the matched stretches
   in green and the rest in magenta (`renders/b1-*.jpg`, made by `scripts/along.py`).
   - Short unmatched gaps where the map draws the same road beside the line (at most 30 m off) are bridged.
   - Where the map draws the road on another line (an old bend), the stretch is left out.
4. `_apply` (the main-road helper) gives each object an earlier open period on its own geometry. It checks the input
   hashes, lengths and ranges, and that the first year is the first map marked present. A later stage is added where a
   later edition draws more of the object.

**The 40 m test.** A test with a 40 m tolerance was rejected. At Östergård it accepted a stretch where today's
Södravägen rides on another red road and then cuts through the village, where the 1968 map has no road
(`renders/b1-sodra-mid.jpg`).

## Result

| object | from | until (its first year before) | on the 1968 map |
|---|---|---|---|
| Tjudövägen | 1968 | 1984 | whole (sheets 1021 07, 08); at Backas within 30 m |
| Hamnsundsvägen · del 1 | 1968 | 1984 | whole |
| Hamnsundsvägen · del 2 | 1968 | 1984 | whole (1021 08, 11); two curves within 20 m |
| Hamnsundsvägen · del 3 | 1968; whole from 1978 | 1984 | the first 290 m |
| Skarpnåtövägen · del 3 | 1968 | 1984 | whole; the map's road follows some curves up to 30 m off today's straightened line |
| Södravägen · del 2 | 1968 | 1984 | all but Bolstaholm (0.4 km) and Östergård (0.4 km), where the map's road runs in older bends; at Tallbacka within 30 m |
| Tobölevägen | 1968 | 1978 | all but Norrgård (a bend to the west); the lakeside end at Skaffan is not on the 1968 map |
| Hamnsundsvägen (Hamnsund) | 1968 | 1993 | all but Kroken (a bend about 60 m east) |
| Finnövägen | 1968; more from 1984 | 1993 | from Långvik west. At Danbo the map's road bends 40–60 m off until the 1984 edition, which draws today's line from there |

Scope (`docs/reviews/main-roads-2026-11-23/scope-audit-saltvik.json`):
- objects: 9 changed;
- geometries: 11 added;
- sources: 1 added;
- the atlas roads file is unchanged.

**Effect on the survey:** on these sheets, the main roads not covered at the first edition fall from 63.9 km to
30.6 km. Part of what is left was not a red road in 1968.

**A fix in the step.** The helper marks a later stage as partial. Where the stage covers the whole object (Hamnsundsvägen
del 3 from 1978), this step marks it full, which the map model requires.

## Tests

- `tests/test_main_roads_saltvik.py`, the replay;
- `tests/main-roads-saltvik.test.cjs`:
  - each object is open from 1968, not 1967;
  - each 1968 geometry's length matches its reviewed ranges;
  - each has evidence from a 1021 sheet;
- `tests/qgis-roads.test.cjs` (untracked, in the patch): the coarse-2014 Södravägen test now expects "unknown" before
  1968, not before 1984.

## Open items (batch 1b)

**Old bends to trace on the 1968 map:**
- Södravägen at Bolstaholm and Östergård;
- Tobölevägen at Norrgård;
- Hamnsundsvägen at Kroken;
- Finnövägen at Danbo.

**Objects where today's straightened line repeatedly leaves the curving 1968 road:**
- Svartsmaravägen between Sålis and Kräkböle;
- Skarpnåtövägen del 1.

**Others:**
- Bergövägen del 2: red only from 1978.
- Two objects dated from 1968 still leave gaps on today's line: Svartsmaravägen (`rural:hammarland-way-71082200`)
  and Skarpnåtövägen södra.
- About 1.5 km of main road has no object.
