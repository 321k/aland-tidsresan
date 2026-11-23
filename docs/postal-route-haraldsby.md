# Postal route: over Färjsundet and through Haraldsby on the parish maps 1929 and 1944

Part of the work to draw the postal route on real roads (`docs/postal-route-roads.md`). This step follows the open
items in `docs/postal-route-1929.md`.

Build step: `apply_postal_route_haraldsby` in `scripts/postal_route_haraldsby.py`, after the 1929 step.

Review data: `data/postal-route-haraldsby.json` (copied to `dist/assets/`), written by
`docs/reviews/postal-route-2026-11-23/scripts/prepare_haraldsby.py`.

## Maps and their error

| map | year | catalogue source |
|---|---|---|
| Saltvik (1021 07) | 1929 | `nls:map-38157483` |
| Saltvik (1021 07) | 1944 | `nls:map-38147682` |

Base maps 1021 07 from 1968 to 1993 are used for comparison.

**How far off the parish maps are:**
- The parish maps are tile maps placed by the map service, not registered by the project. Here they lie 30–90 m from
  today's roads.
- Along von Knorringsvägen the 1929 sheet lies 50–70 m north-west of the catalogue road.
- At Färjsundet the 1929 and 1944 tiles are placed about 90 m apart.
- The base maps are registered on their printed grid. At Högbacka a hand trace on the 1968 map lands within 4–6 m of
  today's OSM vertices.

**What counts as evidence:** the course of a road on the parish maps — its turns, junctions and the farms it passes —
matched against the base maps. The parish maps' exact position is not used. Renders are in
`docs/reviews/postal-route-2026-11-23/renders/`:
- `farj-2944.jpg`, `farj-29-68.jpg`, `h-sheet.jpg`;
- `hog-sheet.jpg`, `hog-later.jpg`;
- `route-haraldsby-68.jpg`, the drawn route over the 1968 map.

## Finding

**Färjsundet.**
- The 1929 sheet draws the main road from Godby north-east to a ferry landing. The sound was crossed by ferry: the
  bridge (`road:historical-dates:farjsund`) opened on 4 July 1937.
- The road lies 60–80 m north-west of today's straight road. That is the sheet's offset along von Knorringsvägen too,
  so it is the same line.
- The 1968 base map draws today's straight road and the bridge. It also draws the old shore road ending at the former
  landing, 50–60 m from the bridge's west end.

**Haraldsby.** From the far landing the 1929 and 1944 sheets draw the main road:
- north-east to Vårsundet;
- north through Västerdal and Enelund into Haraldsby village;
- east past Östergård;
- in a curve past Högbacka to Sundsvägen.

The 1968–1993 base maps draw the same course. It is already in the catalogue, but only from 1968:
- Vårsundet–Haraldsby, as far as the Haraldsbyvägen junction (the rest of that object, over Östervik, is later);
- Haraldsbyvägen and its southern connection, as far as Östergård;
- Gamla Sundsvägen västra and östra. Their 1968–2013 geometry already holds the Högbacka curve, which today's
  Kvarnbovägen replaced.

## Result

| object | change | maps |
|---|---|---|
| Sundsvägen · Godby–Färjsundet | from 1929 (was 1968), whole | Saltvik 1929 |
| Sundsvägen · Vårsundet–Haraldsby | from 1929, 197–758 m of its length (the landing to the Haraldsbyvägen junction) | Saltvik 1929, 1944 |
| Haraldsbyvägen · södra anslutningen | from 1929, whole | Saltvik 1929, 1944 |
| Haraldsbyvägen | from 1929, 0–910 m (to Östergård) | Saltvik 1929, 1944 |
| Gamla Sundsvägen · västra delen | from 1929, its 1968 geometry | Saltvik 1929, 1944 |
| Gamla Sundsvägen · östra delen | from 1929, its 1968 geometry | Saltvik 1929, 1944 |

Each object keeps its own coordinates. Scope (`docs/reviews/postal-route-2026-11-23/scope-audit-haraldsby.json`):
- objects: 6 changed, none added;
- geometries: 6 added;
- sources: 1 added;
- the atlas roads file is unchanged.

## The route builder

`scripts/build_postal_route.py` gets two additions, both stated in `data/postal-route-stations.json`:

- **Crossings.** The Färjsundet ferry joins the road points nearest its two landings in years before 1937. The landings
  are the bridge's ends. The leg lists the ferries it uses.
- **Preferring the parish maps' roads.** Among roads open in the leg's year, a segment that is not on its object's
  geometry of any period beginning by 1930 costs five times its length. Joins between road ends cost the same, because
  they are not mapped roads. Without this, Haraldsby → Skarpans (dated 1968 by the Lappböle sheet edge) would take
  today's causeway over Östervik.

| leg | year | change |
|---|---|---|
| Emkarby → Haraldsby | 1929 (was 1968) | over Färjsundet by ferry |
| Haraldsby → Skarpans | 1968 | now through Haraldsby village, past Östergård and Högbacka |
| Storby → Frebbenby, Frebbenby → Emkarby | unchanged | — |

## Tests

- `tests/test_postal_route_haraldsby.py`, the replay;
- `tests/postal-route-haraldsby.test.cjs`:
  - the six objects are open from 1929;
  - Vårsundet–Haraldsby's early geometry stops at Vårsundet;
  - the route uses the ferry and the village road, not the causeway.
- Updated for the earlier dates:
  - `tests/postal-route-godby.test.cjs`: Sundsvägen Godby–Färjsundet is open from 1929;
  - `tests/test_postal_route_godby.py`: the replay compares the build from 1968 on, because the later reviews add
    earlier periods to its objects;
  - `tests/qgis-roads.test.cjs` (untracked, in the patch): reads the start from `postalRouteHaraldsbyReview`.

## Open items

- **Lappböle sheet edge:** no map earlier than 1968 covers the 181 m gap, which keeps Haraldsby → Skarpans at 1968.
- **Storby harbour:** the 1929 Eckerö map does not reach it, which keeps Storby → Frebbenby at 1968.
