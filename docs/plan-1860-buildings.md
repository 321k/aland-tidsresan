# The named buildings of the 1860 town plan

G. Th. Chiewitz's 1860 plan of Mariehamn (`dist/assets/mariehamn-plan-1860.png`, source `plan-1860`) draws and
names eighteen building outlines: the hospital (lasarett) with four wings, the town hall, two customs houses, the
warehouse (packhus), the vicarage and its outbuilding, the church, the school, the inn (gästgifveri), two sheds for
the market and fish market, the tavern (wardshus) and the swimming school. Along the block streets it also draws pink
**house rows**, divided into plots by thin lines. The buildings and 35 house rows now appear on the 1860 map as
**planned** buildings. They are pale fills with a dashed outline, and they are gone in 1861.

## House rows

The plan has one row per block side: the north and south sides of the double blocks north and south of the Esplanade,
and all sides of the ring blocks at Hamntorget, the customs house, Strandgatan and Handelstorget. Each row is one
`buildingGroup` object (`building:plan-1860:husrad-<block>-<side>`) with a `location` text. The plot lines inside a
row are not objects of their own, because the plan does not say how many houses a plot would hold. The south row of
the south-western double block is not drawn on the plan, where the Wärdshus hill lies.

The rows were traced by eye from gridded crops at 4–6× (`docs/reviews/plan-1860-buildings-2026-11-17/crops/s-*`,
`nw.jpg`, `sw.png`, `east.jpg`, `se.jpg`, `e3.png`). Each row is a quadrilateral from the line between houses and
yard to the hedge or block frame along the street. The overlay check is in `renders/ovl-w.jpg` and `renders/ovl-e.jpg`.
Reading accuracy is about ±2 view px, about ±1.5 m.

## Data and compiler

- `data/plan-1860-buildings.json`: the review. Each outline is traced by eye from the plan (crops in
  `docs/reviews/plan-1860-buildings-2026-11-17/crops`). Its pixels are in the view space of the plan's street
  traces (`data/mariehamn-city-traces.json`, set `plan-1860`, 1824×1368; the scan is 2048 px wide). The control
  streets pair each plan street with its name(s) on the 1860 stage. *Norra planerade tvärgatan* is left out on
  purpose: its alignment is being reworked separately.
- Control lines: the traces "Norragatan i planen" and "Storagatans planerade stråk" first did not follow a drawn
  street. They ran inside the blocks, along the back edge of the house rows: about 54 px and, in the west, about
  30 px south of the street (`renders/trace-check.jpg`). The step first carried its own street-centre readings for
  them (`planLineCorrections`). Since the traces were corrected (`docs/plan-street-traces.md`) their `pixels` are those
  street centres and the step reads them directly; without them the north rows land on Norragatan, and the hospital
  group about 25 m too far north.
- `scripts/plan_1860_buildings.py`, which `compile_catalog` runs after the 1985 block step: `apply_plan_1860_buildings`.

## Placement

The 1860 map does not draw the plan at its raw three-anchor georeference.
`planned_city_streets.py` puts it on the reconstructed 1861 grid. The buildings follow that grid, so they stay in
the block where the plan puts them:

1. At build time, every crossing of a plan east–west street with a plan north–south street is paired with the
   crossing of the same streets on the 1860 stage, with linked streets resolved through their objects.
   North of Storagatan the stage draws three plan streets as the real Neptunigatan, Ålandsvägen and Strandgatan,
   so those names are paired too. Today 40 of 48 crossings are found.
2. Crossings missing on the stage are filled from a distance-weighted affine fit of the 8 nearest crossings.
3. Each outline is mapped through the bilinear cell of the four crossings around its centre. The cell is chosen by
   street bands in plan space, and an inverse bilinear solve gives each vertex's cell coordinates. Buildings outside
   the grid (the swimming school and the fish-market shed) extrapolate from the nearest cell, at most
   `maxExtrapolationCells` = 3.

A single global affine fit left errors of up to 22 m. A local affine fit gave about 11 m in leave-one-out tests.
The basis text states that placements can be 10–20 m off.

## What each object says

- **State:** one `planned` state, 1860–1861, `certainty: documented`.
- **Geometry period:** `inferred`.
- **Evidence:** `<id>:plan-1860`, with `observationType: plan`, `outcome: planned` and `constructionYear: null`. It
  also stores the traced plan pixels and the placement (cell street names and extrapolation).
- **Not a construction date.** The plan is evidence of intent, not of construction. Buildings that were actually
  built are separate objects with their own evidence. This batch does not link them to the planned outlines.

## Validation (before the catalogue changes)

The step raises `ValueError` and leaves the catalogue untouched when any of these fails:

- the review is not yet applied, and its plan source and the 1860 stage exist;
- object ids are unique;
- every control street exists in both the plan and the stage, and every plan street pair crosses;
- at least 60 % of the crossings are found on the stage;
- every traced polygon is valid;
- every placed outline is valid, between 50 and 20 000 m², and within the extrapolation limit.

## Checks

- `tests/plan-1860-buildings.test.cjs`: all 18 objects are drawn only in 1860; the evidence and pixels match the
  review; the areas are plausible; and the relative positions hold (the hospital is north-west of the church, and
  the swimming school is east of it).
- `tests/test_plan_1860_buildings.py`: applies the step to the pre-batch catalogue snapshot
  (`data/map-scan-cache/review/plan-1860-buildings/before.json.gz`, local review cache), compares the result with
  the build, and confirms that nothing else changes. Changed inputs are rejected without touching the catalogue.
- The JS test also checks that the north and south rows of each regular double block land in the same reconstructed
  block.
- Scope audit (`docs/reviews/plan-1860-buildings-2026-11-17/data/scope-audit.json`): applying the step to the build
  with the step removed adds 53 objects (18 buildings and 35 rows), 53 geometries and 1 source, and changes nothing
  else. The result equals the build by id (only the order differs, because the Lemland step runs after this one).

## Open

- The house rows tilt slightly more than the reconstructed blocks, so their ends can reach about 5 m into the cross
  streets.
- The two misdrawn traces in `data/mariehamn-city-traces.json` should be fixed at the source. The Norra planerade
  tvärgatan step depends on the same reading.
- The planned outlines are not linked to the buildings later built on the same sites.
