# Main roads on the base maps, batch 2: the archipelago

Part of the main-road survey (`docs/reviews/main-roads-2026-11-23/README.md`). Batch 2 covers the survey's batches 2, 3
and 5: Föglö, Brändö and Fiskö, Kumlinge (Enklinge, Seglinge), Vårdö (Sandö) and Ängö–Bussö.

Build step: `apply_main_roads_archipelago` in `scripts/main_roads_archipelago.py`, after batch 1.

Review data: `data/main-roads-archipelago.json` (copied to `dist/assets/`), written by
`docs/reviews/main-roads-2026-11-23/scripts/prepare_archipelago.py`.

## Method

As in batch 1 (`docs/main-roads-saltvik.md`), with the same 12 m tolerance:
1. `objects_for_gaps.py` lists the candidate objects (`batch2-objects.json`).
2. `match_editions.py` finds where each edition draws the red main-road symbol (`batch2-match.json`).
3. `propose.py` turns the matches into ranges (`batch2-proposal.json`):
   - it bridges gaps of at most 100 m and drops stubs under 150 m;
   - it adds a later stage where the next edition adds at least 200 m.

**Checking by eye.** Every proposal was checked along its whole line:
- on the first edition: `renders/b2-*.jpg` and `b2-group1..5.jpg`;
- for the later stages: `b2L-*.jpg` and `b2L-group.jpg`.

**Lines over two sheets.** `along.py` now reads each tile from the first listed sheet whose frame contains it. Without
this, the renders of Brändövägen and Enklingevägen were black off the first sheet's frame. The redone renders are
`b2-group2b.jpg` and `b2-enklingevagen-200km2.jpg`.

**Which sheet dates a range.** A range is credited only to the sheets whose registered frame holds at least 50 m of
it. The proposal listed two sheets for some objects, and this changes two first years:
- Fiskövägen's matched stretch lies on 1023 12 (1971) only, so it is dated 1971, not 1968 from the Brändö sheet.
- Brändövägen del 1 lies on 1041 03 (1968), not on 1041 02 (1969).

## Maps

| sheet | area | editions used |
|---|---|---|
| 1014 01 | Degerby | 1970, 1978 |
| 1014 03 | Ängö, Bussö | 1970 |
| 1014 04 | Sonnboda, Näversholm | 1970, 1978 |
| 1014 05 | Överö, Nötö, Ulversö | 1970 |
| 1014 09 | Seglinge | 1970 |
| 1023 01 | Sandö | 1971 |
| 1023 08 | Enklinge | 1971 |
| 1023 12 | Fiskö | 1971 |
| 1041 03 | Åva, Brändö | 1968, 1984 |

## Result

Each object gets an earlier open period on its own geometry, cut to the reviewed ranges, with a second stage where a
later edition draws more of it.

| object | from | until (its first year before) | on the first edition |
|---|---|---|---|
| Föglövägen (Sonnboda) | 1970; more from 1978 | 1985 | all but the bend at Henriks; the end towards Geta is not on the 1970 map |
| Föglövägen (Degerby) | 1970 | 1978 | all but the bend at Alkär |
| Hummersövägen | 1970; more from 1978 | 1995 | all but a short bend and the last stretch |
| Fiskövägen · del 1 | 1971 | 1985 | the middle 4.1 km; the ends are not on the map |
| Överövägen · del 1 | 1970 | 1985 | from 1 050 m to the end |
| Överövägen · del 2 | 1970 | 1985 | all but two short stretches |
| Sandövägen | 1971 | 1978 | to Tällholm, and a short piece beyond; not the end towards Alören |
| Brändövägen · del 1 | 1968; more from 1984 | 1991 | at Åva, and from Djurholm to Finnkors. The 1984 edition also draws it over Andersör and Nötö |
| Brändövägen · del 2 | 1968 | 1991 | all but a short stretch |
| Enklingevägen | 1971 | 1985 | from the village south to Bovik and the ferry pier; not the northern part |
| Ängö-Bussövägen | 1970 | 1985 | from Ängö to Bussö village; not the last stretch east |
| Nötövägen | 1970 | 1985 | all but a short stretch |
| Näversholmavägen | 1970; more from 1978 | 1995 | to Näversholm; from 1978 on towards Bondbacka; not the stretch to Andholm |
| Ulversövägen | 1970 | 1995 | all but the middle |
| Bofjärdsvägen · del 1 | 1970; more from 1978 | 1995 | from Sonnboda; further out from 1978 |
| Seglingevägen | 1970 | 1985 | all but two short stretches at Månsas |

**In total:** 52.5 km dated from the first edition, and 7.3 km more from the later stages.

**Left out:**
- Vårdövägen (Töftö): the 1970 match is fragmented.
- Björkövägen del 1: no match.

Scope (`docs/reviews/main-roads-2026-11-23/scope-audit-archipelago.json`, against the catalogue before this step):
- objects: 16 changed;
- geometries: 21 added;
- sources: 1 added;
- the atlas roads file is unchanged.

**Effect on the survey** (`survey-after-archipelago.json`):
- On these sheets, the main roads not covered at the first edition fall from 96.5 km to 43.9 km.
- Over all sheets, after batches 1 and 2, the figure falls from 268.7 km to 182.8 km.

**The postal route.** Its road from the Brändö landing to the station now dates from the 1984 edition, not 1991.

**A fix in the helper** (`scripts/hammarlandsvagen_main_road.py`):
- The two Föglövägen objects share the last part of their ids, which the helper used to name their new geometries.
  The second geometry took the first one's id.
- An entry may now give `geometryName`.
- The helper refuses a geometry id that is already in the catalogue.

## Tests

- `tests/test_main_roads_archipelago.py`: the replay, plus the rejections, including a duplicate geometry id.
- `tests/main-roads-archipelago.test.cjs`:
  - each object is open from its first year and not the year before;
  - each first geometry and each later stage matches its reviewed length;
  - each object has evidence from a 1014, 1023 or 1041 sheet;
  - Fiskövägen is not open in 1970;
  - Brändövägen del 1 is longer from 1984;
  - the postal route's Brändö landing road dates from 1984.
- `tests/qgis-roads.test.cjs` (untracked, in the patch): the archipelago crossing test reads Brändövägen del 1's
  earlier start from `mainRoadReview`, as it already does from `historicalDating`.

## Open items

**Old bends to trace on the first edition:**
- Föglövägen at Henriks and Alkär;
- Brändövägen del 1 at Söderholm.

**Still to do:**
- Vårdövägen and Björkövägen.
- Brändövägen on 1041 02: 8.3 km there are still not covered at its 1969 edition; not yet reviewed.
