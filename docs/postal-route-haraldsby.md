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
- The sound was crossed by ferry: the bridge (`road:historical-dates:farjsund`) opened on 4 July 1937.
- On the 1929 sheet and its black-and-white 1944 edition (`hamn-sheet.jpg`), the road to the ferry runs north on
  today's Hamnvägen, then east along the shore to the landing. Here the two editions agree in position.
- The 1968 and 1978 base maps (`shore-sheet.jpg`) still draw that shore road in red to the old landing. Today it is a
  service track (OSM 960124939), within about 10 m of the 1968 line.
- Today's straight road from Godby to the bridge is not on the 1944 edition. On the coloured 1929 sheet it is drawn
  only in red, without black linework: a later addition for the 1937 bridge.
  - A first reading of this batch took the red line for the 1929 road and dated the straight road from 1929. That was
    wrong, and it is undone: the straight road stays dated from 1968.

**Haraldsby.** From the far landing, which is at the bridge's east end within the sheet's error, the 1929 and 1944 sheets draw the main road:
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
| Hamnvägen | from 1929 (was 1985), whole | Saltvik 1929, 1944; base maps 1968, 1978 |
| Färjvägen · Färjsundet (new) | from 1929, 390 m along the shore to the old ferry landing (OSM 960124939) | Saltvik 1929, 1944; base maps 1968, 1978 |
| Sundsvägen · Vårsundet–Haraldsby | from 1929, 197–758 m of its length (the landing to the Haraldsbyvägen junction) | Saltvik 1929, 1944 |
| Haraldsbyvägen · södra anslutningen | from 1929, whole | Saltvik 1929, 1944 |
| Haraldsbyvägen | from 1929, 0–910 m (to Östergård) | Saltvik 1929, 1944 |
| Gamla Sundsvägen · västra delen | from 1929, its 1968 geometry | Saltvik 1929, 1944 |
| Gamla Sundsvägen · östra delen | from 1929, its 1968 geometry | Saltvik 1929, 1944 |

Each existing object keeps its own coordinates.

**The new road.**
- Färjvägen is added by the connections step (`scripts/sviby_connections.py`), from a second review file,
  `data/postal-route-farjsundet-shore.json`, written by `prepare_farjsundet_shore.py`.
- It starts on Hamnvägen. Its end at the ferry landing is a stated free end.

Scope (`docs/reviews/postal-route-2026-11-23/scope-audit-haraldsby.json`, against the catalogue before this step):
- objects: 6 changed, 1 added;
- geometries: 7 added;
- sources: 3 added (2 reviews and 1 survey);
- the atlas roads file is unchanged.

## The route builder

`scripts/build_postal_route.py` gets two additions, both stated in `data/postal-route-stations.json`:

- **Crossings.** A ferry joins the road points nearest its two landings. The postal route (to 1911) is older than
  the bridges that replaced the ferries, so the ferry is used whatever year dates the roads. The leg lists the ferries
  it uses.
  - **Marsund:** from the pier on Holmberg (`road:eckero:gamla-landsvagen:holmberg`) to the pier at the end of
    Marsundsvägen. This is the 1929 "M. färja"; the bridge came in 1959.
  - **Färjsundet:** from the end of Färjvägen to the bridge's east end. The bridge came in 1937.
- **The roads mapped by a year.** A year's network is every geometry the roads had while open, in any period beginning
  by that year. It includes old roads that closed before it, such as the roads to the Marsund ferry piers, closed in
  1956.
- **Preferring the parish maps' roads.** Among roads open in the leg's year, a segment that is not on its object's
  geometry of any period beginning by 1930 costs five times its length. Joins between road ends cost the same, because
  they are not mapped roads. Without this, Haraldsby → Skarpans (dated 1968 by the Lappböle sheet edge) would take
  today's causeway over Östervik.

| leg | year | change |
|---|---|---|
| Storby → Frebbenby | 1968 | past Bagars, Kyrkoby and Klemes, over Holmberg and the Marsund ferry, not the 1959 bridge |
| Frebbenby → Emkarby | 1929 | unchanged |
| Emkarby → Haraldsby | 1929 (was 1968) | Hamnvägen, the shore road and the Färjsundet ferry, not the 1937 bridge |
| Haraldsby → Skarpans | 1968 | through Haraldsby village, past Östergård and Högbacka, and the old road through Finby |

Renders: `route-ferries.jpg` (the route over the Marsund ferry on the 1929 Eckerö map and over Färjsundet on the 1968
base map) and `route-haraldsby-68.jpg`.

## Tests

- `tests/test_postal_route_haraldsby.py`, the replay;
- `tests/postal-route-haraldsby.test.cjs`:
  - the six objects are open from 1929;
  - Vårsundet–Haraldsby's early geometry stops at Vårsundet;
  - the straight road to the bridge stays from 1968;
  - the route uses both ferries and the village road, not the bridges or the causeway.
- Updated for the earlier dates:
  - `tests/test_postal_route_godby.py`: the replay compares the build from 1968 on, because the later reviews add
    earlier periods to its objects;
  - `tests/qgis-roads.test.cjs` (untracked, in the patch): reads the start from `postalRouteHaraldsbyReview`.

## Open items

- **Lappböle sheet edge:** no map earlier than 1968 covers the 181 m gap, which keeps Haraldsby → Skarpans at 1968.
- **Storby harbour:** the 1929 Eckerö map does not reach it, which keeps Storby → Frebbenby at 1968.
