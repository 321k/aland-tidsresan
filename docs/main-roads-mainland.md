# Main roads on the base maps, batch 3: Lemland, Lumparland, Jomala, Eckerö and Sund

Part of the main-road survey (`docs/reviews/main-roads-2026-11-23/README.md`). Batch 3 covers the survey's batches 4, 6,
7 and 8.

Build step: `apply_main_roads_mainland` in `scripts/main_roads_mainland.py`, after batch 2.

Review data: `data/main-roads-mainland.json` (copied to `dist/assets/`), written by
`docs/reviews/main-roads-2026-11-23/scripts/prepare_mainland.py`.

## Method

As in batches 1 and 2 (`docs/main-roads-saltvik.md`, `docs/main-roads-archipelago.md`).

**Candidates** (`batch3-objects.json`, 71 rows on sheets 1012 03, 05, 08, 09, 11, 12 and 1021 10). This batch takes
the 30 objects that:
- are dated later than the first edition;
- have a single period;
- have at least 50 m of red candidate pieces.

The other rows are not in this batch:
- Objects already open at the first edition but on another line (for example Ringsbölevägen and Norrbygatan) need the
  old line traced. That is left to batch 1b.
- Pieces that no object owns are also left out.

**Proposals.** The matcher and `propose.py` gave proposals for 18 objects (`batch3-match.json`, `batch3-proposal.json`).

**Checking by eye:**
- `renders/b3-*.jpg`, `b3L-*.jpg` and `b3-group1..5.jpg`;
- closer views for doubtful lines: `b3z-*.jpg`, and the plain scan at Södra Överbyvägen in `b3z-sodra-overby-raw.jpg`;
- lines over two sheets, rendered across both: `b3m-*.jpg`.

**Reading the renders.** `along.py` draws other catalogue roads open in the year as thin red lines. Only the wide red
band is the map's main-road symbol.

**A fix in the helper** (`scripts/hammarlandsvagen_main_road.py`): the Klippan pieces already had a `mainRoadReview`
record from the Sund postal step that created them. The helper replaced it. It now keeps an earlier record of the
same kind under `earlier`.

**A fix in the scan loader.** The 1978 edition of 1012 07 is cached under its download name, `101207_1968_1978.jpg`.
`maps.scan_window` (`docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/maps.py`) now opens a scan by the name
in its `originalUrl` when that file is cached.

## Result

All objects are dated from the 1968 edition. A second stage from 1978 is added where that edition draws more.

| object | sheet | from | until (its first year before) | on the 1968 map |
|---|---|---|---|---|
| Ängösundsvägen | 1012 11 | 1968; more from 1978 | 1985 | all but a bend at Åkerkulla and a few short stretches |
| Mångstektavägen | 1021 10 | 1968; nearly whole from 1978 | 1985 | all but bends at Delvik and a few short stretches |
| Svinövägen | 1012 11 | 1968 | 1995 | all but the last stretch to the shore |
| Torpvägen · del 1 | 1012 03 | 1968 | 1978 | at Backans, and from Torp south; not the middle through the forest |
| Södra Överbyvägen | 1012 03 | 1968 | 1978 | from Ekör to Överby; not the western part |
| Norra Svibyvägen | 1012 09 | 1968 | 1995 | all but the bend at Svibyån |
| Skeppsviksvägen | 1012 03 | 1968; more from 1978 | 1994 | from Lund towards Skeppsvik, but not one bend (on today's line from 1978); not the first part at Torp |
| Lumpovägen | 1012 12 | 1968 | 1985 | from Lumpo by on |
| Persbyvägen | 1021 10 | 1968 | 1985 | whole |
| Narmovägen | 1012 09 | 1968 | 1985 | all but the first part |
| Norrbyvägen | 1012 08 | 1968 | 1985 | through Norrby; not the first part |
| Stickvägen | 1012 11 | 1968 | 1978 | all but the first part at Klockars |
| Sundsvägen · del 3 | 1012 12 | 1968 | 1978 | whole, through Finby |
| Sundsvägen · Klippan | 1012 12 | 1968 | 1978 | all but the first 80 m, where the road from Svensböle bends in |
| Sundsvägen · öster om Klippan | 1012 12 | 1968 | 1978 | whole (98 m) |

**In total:** 18.4 km dated from 1968, and 1.4 km more from 1978.

**Lumpovägen at the sheet edge.** The road crosses the collar of sheet 1012 12, where the map draws nothing, for about
250 m. It is drawn in red on both sides of the collar, and the stretch across the collar is dated with it.

**Klippan.**
- This settles the open item in `docs/postal-route-sund.md`: the 1968 sheet draws the straight road at Klippan.
- Sundsvägen öster om Klippan was below the matcher's candidate limit and was added by hand
  (`renders/b3z-klippan-ost.jpg`).
- The old road along Klippanvägen ("Gamla landsvägen · Hallbacka–Klippan") stays open until 1978, as the Sundsvägen
  review dates it. The 1968 sheet draws it as a smaller road.

**Left out:**
- Järsövägen. Its 1968 match is short and partly over water, and its 1978 matches are fragments.
- Lemlandsvägen · del 2 and Lemlandsvägen · Knutsboda–Dragsvik. The matcher proposed both, but earlier, more detailed
  reviews date them, and their findings stand:
  - `docs/lemlandsvagen-main-road.md`: the 1968 and 1978 maps still run the main road through Övre-Börs, and sheet
    1012 08 sits 30–60 m off in Lemland, so a 12 m match there can be the old road beside today's;
  - `docs/mariehamn-major-roads.md`: the Strandnäs split records the Solstrand stretch as absent in 1968 and 1978.
  - Running the full test suite caught this: the tests of both reviews failed on the first build of this batch.
- Norrbyvägen, also on 1012 08 in Lemland, is kept: its 1968 line lies on the red band along 815 m through Norrby
  (`renders/b3-group3.jpg`). The offset is not seen there.

Scope (`docs/reviews/main-roads-2026-11-23/scope-audit-mainland.json`, against the catalogue before this step):
- objects: 15 changed;
- geometries: 18 added;
- sources: 1 added;
- the atlas roads file is unchanged.

**Effect on the survey** (`survey-after-mainland.json`):
- On these sheets, the main roads not covered at the first edition fall from 81.7 km to 63.3 km.
- Over all sheets, after batches 1–3, the figure falls from 268.7 km to 164.4 km.

**The postal route.** Haraldsby → Delvik now dates from 1978 (was 1985): Mångstektavägen is drawn nearly whole on that
edition.

## Tests

- `tests/test_main_roads_mainland.py`: the replay and the rejections; the Klippan pieces keep the Sund postal step's
  record under `earlier`.
- `tests/main-roads-mainland.test.cjs`:
  - each object is open from 1968, not 1967;
  - each 1968 geometry and each later stage matches its reviewed length;
  - each has evidence from a 1012 or 1021 sheet;
  - Järsövägen and the two Lemlandsvägen objects are left out;
  - the Haraldsby → Delvik leg dates from 1978.
- `tests/postal-route-sund.test.cjs`: the Klippan pieces are open from 1968, with evidence from this review. They join
  their neighbours from 1978, when del 2 begins.
- `tests/test_postal_route_sund.py`: the Sund replay compares the Klippan pieces with the build from 1978 on, and
  checks that its record is kept under `earlier`.
- `tests/qgis-roads.test.cjs` (untracked, in the patch): the Sund coastal test reads Mångstektavägen's earlier start
  from `mainRoadReview`.

## Open items

**Old bends to trace on the 1968 map:**
- Ängösundsvägen at Åkerkulla;
- Mångstektavägen at Delvik;
- Norra Svibyvägen at Svibyån;
- Skeppsviksvägen's bend.

**Other:**
- Objects open at the first edition but on another line: Ringsbölevägen, Norrbygatan, Jomala Torpvägen, Tellholmsvägen
  and others in `batch3-objects.json`.
- Pieces with no object today.
- Järsövägen.
