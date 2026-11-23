# Postal route: Emkarby through Gölby and Godby on the parish maps 1928 and 1929

Part of the work to draw the postal route on real roads (`docs/postal-route-roads.md`). The base-map batches connected
the route from 1968. This step reads the earlier parish maps along the same roads.

Build step: `apply_postal_route_1929` in `scripts/postal_route_1929.py`, after the Sund step.

Review data: `data/postal-route-1929.json` (copied to `dist/assets/`), written by
`docs/reviews/postal-route-2026-11-23/scripts/prepare_1929.py`.

## Maps

| sheet | year | catalogue source |
|---|---|---|
| Jomala (1012 09) | 1928 | `nls:9c76c492-3fb4-43dd-8cc7-eb03d2a00ecd` |
| Saltvik (1021 07) | 1929 | `nls:map-38157483` |
| Saltvik (1021 07) | 1944 | `nls:map-38147682` |
| Hammarby (1012 06) | 1929 | `nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08` |

The catalogue's geometry was drawn over each map with a 100 m grid. Renders are in
`docs/reviews/postal-route-2026-11-23/renders/`: `p29-*`, `p44-*`, `b68-farjz.jpg` and `farj-29-68.jpg`.

## Result

| object | change | maps |
|---|---|---|
| Postgårdsvägen | from 1928 (was 1968) | Jomala 1928, within 10–20 m |
| Godbyvägen · vid Gölby | from 1928 (was 1968) | Jomala 1928 |
| Godbyvägen · vid Björkäng | from 1928 (was 1968) | Jomala 1928, 20–40 m east of the drawn straight road |
| Godbyvägen · korsningen i Godby | from 1929 (was 1968) | Saltvik 1929 and 1944 |
| von Knorringsvägen · del 1 | from 1929 (was 1968) | Saltvik 1929 and 1944, within 20–40 m |
| Emkarbyvägen, a piece in Hammarland (way 459195076) | from 1929 (was 1968) | Hammarby 1929 |
| Emkarbyvägen | the period 1894–1968 split at 1928; from 1928 an added path from Tingsbacka round the bend to Bergens | Jomala 1928, within 10–30 m |

Notes on the table:
- **Geometry:** each object keeps its own geometry, with the same coordinates.
- **The Saltvik sheet's offset:** at Godby it lies 30–40 m west of today's roads, parallel along all of von
  Knorringsvägen.
- **Emkarbyvägen's added path:** it is the path of its 1968 period, with the same traced bend at Tingsbacka.
  - The period that begins with the 1894 atlas is split at 1928 (`split` in the review), and only the part from 1928
    gets the path.
  - The atlas does not show where the road ran, so before 1928 Emkarbyvägen still ends at Tingsbacka.
  - The 1800–1894 period is unchanged.

Scope (`docs/reviews/postal-route-2026-11-23/scope-audit-1929.json`):
- objects: 7 changed, none added or removed;
- geometries: 7 added;
- sources: 1 added (the review).

In the atlas roads file, the 1894 line Storby–Hammarland–Godby gets new replacement intervals where these pieces are
now dated.

Tests:
- `tests/test_postal_route_1929.py`, the replay;
- `tests/postal-route-1929.test.cjs`;
- tests that encoded "from 1968" for these objects, now reading the 1928/1929 dates:
  - `tests/postal-route-godby.test.cjs`;
  - `tests/emkarby-road-continuity.test.cjs` (untracked, in the patch): Emkarbyvägen has two paths from 1928 and ends
    at Tingsbacka before;
  - `tests/qgis-roads.test.cjs` (untracked, in the patch): von Knorringsvägen's start is read from the review property
    `postalRoute1929Review`;
  - `tests/hammarlandsvagen-atlas.test.cjs` (untracked, in the patch): from 1928 the Gölby pieces retire part of the
    1894 atlas line, so its drawn length equals 1900's only until 1927.

## Frebbenby → Emkarby from 1929

Routing on the 1929 roads, the leg broke only at Drygsböle, a 34 m gap.
- **The two objects:** the old Hammarlandsvägen at Smedens is traced 25 m west of today's road, and Emkarbyvägen begins
  on today's road.
- **The map:** the 1929 Hammarby sheet draws the junction between them.

The route builder joins a road end to another road within 40 m, so the leg now runs on the 1929 roads.

## Open items

- **Färjsundet** (`farj-29-68.jpg`):
  - In 1929 the main road ran from the end of von Knorringsvägen north-east to an older bridge, 50–80 m north-west of
    today's straight road. The 1968 map draws today's straight road and bridge.
  - The old line may partly survive as OSM tracks (960124936–8).
  - The Saltvik sheet's offset here is 30–80 m, so the line needs a careful trace.
- **Vårsundet to Högbacka** (`p29-hw-sheet.jpg`):
  - On the 1929 and 1944 Saltvik sheets the main road ran from Vårsundet north-east through Västerdal into Haraldsby
    village, east past Östergård, and round by Högbacka to today's road.
  - The catalogue has none of it before 1968. Parts survive as today's minor roads (OSM 532577639–42 and others).
  - This needs an old-road review with the surviving pieces, as for the old roads in the Sundsvägen review.
- **Lappböle sheet edge:** no map earlier than 1968 covers the 181 m gap (`docs/postal-route-sund.md`).
- **Storby harbour:** the 1929 Eckerö map does not reach it.

Until these are done, Emkarby → Haraldsby and Haraldsby → Skarpans are drawn from the 1968 base maps.
