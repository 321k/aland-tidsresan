# Postal route: Emkarby through Gölby and Godby to Färjsundet on the base maps

Part of the work to draw the postal route on real roads; the survey and plan are in
`docs/reviews/postal-route-2026-11-23/README.md`. The first step documents the roads that the base maps (1968–1995)
draw along the route, so the route can follow dated roads before earlier maps are used.

Build step: `apply_postal_route_godby` in `scripts/postal_route_godby.py`. It runs after the Mattas step and before the
atlas review's late pass.

Review data: `data/postal-route-godby.json` (copied to `dist/assets/`), written by
`docs/reviews/postal-route-2026-11-23/scripts/prepare_godby.py`.

Evidence: `docs/reviews/postal-route-2026-11-23/renders/`, read on the base maps 1012 09 Jomala and 1021 07 Godby
(1968, 1978, 1985, 1993/1995).

## Finding

Routing the leg Emkarby → Haraldsby on the catalogue's 1968 roads, the network broke in four places along the road the
base maps draw:

- **Emkarbyvägen east of Tingsbacka.** Emkarbyvägen's own review stopped at the edge of its sheet. Its geometry before
  2021 ends at Tingsbacka.
  - The 1968 map draws the main road on from Tingsbacka:
    - east at N 6 676 760;
    - round today's Tingsgränd to Buskböle;
    - on today's line to Bergens;
    - and from there east along today's Postgårdsvägen to Godbyvägen at Gölby.
  - The 1978 map draws today's straight road at Tingsbacka, and today's curve from Bergens to Godbyvägen.
- **Postgårdsvägen**, the 1968 main road from Bergens to Godbyvägen, had no object.
- **Godbyvägen**, the object dated from c.1800, had holes where OSM junction pieces belong to no object: 22 m at Gölby,
  116 m at Björkäng, and the crossroads in Godby (today a roundabout).
- **From Godby to the Färjsundet bridge**, the 1968 main road continues from von Knorringsvägen's east end on today's
  Sundsvägen ways. These had no object.

## Result

| object | change | maps |
|---|---|---|
| Emkarbyvägen | 1968–1977: an added path from Tingsbacka round the old bend to Bergens. 1978–2020: an added path on today's line to Gölby. The old paths are unchanged. | 1968; 1978, 1985, 1995 |
| Postgårdsvägen (new) | from 1968, 702 m | 1968–1995 |
| Godbyvägen · vid Gölby (new) | from 1968, 22 m | 1968, 1978 |
| Godbyvägen · vid Björkäng (new) | from 1968, 116 m | 1968, 1978 |
| Godbyvägen · korsningen i Godby (new) | from 1968, 113 m, including an arc of today's roundabout | 1968–1993 |
| Sundsvägen · Godby–Färjsundet (new) | from 1968, 432 m | 1968–1993 |

Notes on the table:
- Emkarbyvägen's added paths are cuts of its own 2021 geometry, with the same coordinates.
- The 1968 bend is read on the 1968 map as far as Tingsgränd, and follows Tingsgränd's OSM vertices from there.
- The new objects own their OSM pieces in every extract where those pieces are the same line and are not already owned.
- The 1894 atlas line "Storby–Hammarland–Godby" gets two more replacement intervals, so it is hidden in 1968–2020
  where Emkarbyvägen now draws the same road. `build_historical_roads.py` computes this.
- Map years are first evidence, not construction years.

After the step the leg Emkarby → Haraldsby is one connected line on dated roads in 1968, 1980 and 2000 (10.6–10.7 km).
The only gap left is the 76 m lane from the road to the Haraldsby village point.

## Checks

- **Extension:**
  - the object's fingerprint, and the digests of its whole geometry and each period's geometry;
  - a map marked present in each period;
  - the added path continues an old path's end, within 1 m;
  - it does not run along the old geometry;
  - a traced bend leaves and rejoins the line within 1 m.
- **New roads** (the connections step, `scripts/sviby_connections.py`):
  - OSM pieces unchanged;
  - nothing owned twice;
  - partial pieces abut the owned rest of their way, unless a basis is stated (here the roundabout arc);
  - both ends rest on the roads they join;
  - no run along another road.

Scope (`docs/reviews/postal-route-2026-11-23/scope-audit-godby.json`):
- objects: 5 added, 1 changed;
- geometries: 7 added;
- sources: 6 added;
- nothing else in the catalogue.

Tests:
- `tests/test_postal_route_godby.py`;
- `tests/postal-route-godby.test.cjs`;
- `tests/emkarby-road-continuity.test.cjs`: Emkarbyvägen now has a second path in 1968–2020; its original path is unchanged and nothing is added before 1968.

## Open items

- **A visual kink** where the Sundsvägen piece meets von Knorringsvägen's east end. There are two OSM junction ways,
  and the line follows one of them.
- **The Godby junction** follows today's roundabout arc; in 1968 the place was a crossroads.
- **Earlier maps** (the parish maps 1928/1929 and older) are the next step, along with the rest of the route.
