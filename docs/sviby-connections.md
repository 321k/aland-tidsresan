# The connections at Sviby

Build step: `apply_sviby_connections` in `scripts/sviby_connections.py`. It runs after the Sviby step
(`docs/svibyvagen.md`) and before the atlas review's late pass.

Review data, written by `docs/reviews/sviby-connections-2026-11-23/scripts/prepare.py` and copied to `dist/assets/`:
- `data/sviby-connections-early.json`
- `data/sviby-connections.json`

Evidence: `docs/reviews/sviby-2026-11-23/renders/junction/` (and the Sviby review's other renders), read on these maps:
- the parish maps 1012 05 (1928; Kungsö 1944, 1953) and 1012 08 (1929; Mariehamn 1948);
- the 1942 aerial photo, as reviewed in `data/mariehamn-approaches-1942.json`;
- the base maps 1012 05 (1978, 1985) and 1012 08 (1968–1995).

## Why

After the Sviby step, Norra Svibyvägen was a loose end on the map. Kasbergsvägen began 90 m east of it. The road on
south along Svibyviken (Norra Möckelövägen) began only in 1968. A thick 1942 piece east of the junction (the 1942
approach review's "western stub at the bend") ended in empty ground at the photo's western edge.

## Finding

- **Kasberget junction:** the 1928 sheet and its 1944 and 1953 Kungsö editions draw the road from Norra Svibyvägen
  south-east to the sheet edge. There the 1929/1948 Mariehamn sheet continues it as Kasbergsvägen. The base maps 1978
  and 1985 draw it as the main road.
  - Today it is Bäckvägen's west way (940586838) and the first vertices of way 1066273698, up to where the Kasbergsvägen
    object's ownership begins (vertex 4.502).
  - No object owned these pieces.
- **The road along the shore:** the 1929 sheet labels it "Svibyväg", and its 1948 edition draws it too. It runs on from
  the junction south along the west shore of Svibyviken: today the cycleway 35072855 and Norra Möckelövägen.
  - The 1929 sheet lies 50–80 m east at its west edge; the 1948 edition within 20–40 m.
  - Norra Möckelövägen was dated only from the 1968 base map. The cycleway had no object.
- **The road east to Svibyvägen:** the 1929 sheet and its 1948 edition (an unrevised print of the 1929 survey) do not
  draw it.
  - The aerial photo of 25 July 1942 shows it from the photo's western edge to Svibyvägen.
  - The base map 1968 draws it whole, as the road to the airport.
  - Today it is four cycleways and way 35304978. OpenStreetMap 2014 and 2021 had it as one way.

## Result

| object | change | maps |
|---|---|---|
| Kasbergsvägen · vid Norra Svibyvägen (new) | from 1928, 119 m | 1928, 1944, 1953, 1978, 1985 |
| Norra Möckelövägen · norra delen (new, today a cycleway) | from 1929, 123 m | 1929, 1948, 1968–1995 |
| Norra Möckelövägen | from 1929 (was 1968), whole | 1929, 1948 |
| Vägen mot Svibyvägen · Sviby (new) | from 1942, 422 m | absent 1929; photo 1942 (the eastern 54 %); 1968–1995 |

Notes on the table:
- The western 190 m of the road east to Svibyvägen lie outside the 1942 photo. They are included because the road runs
  on there and has no other connection; the basis says so.
- In the 1942 and 1952 city stages, the stub is replaced by a feature tied to the new object.
- The new objects own exactly the OSM pieces listed, in every extract that has them. A partial piece ends where
  Kasbergsvägen's ownership of the same way begins.
- Map and photo years are first evidence, not construction years.

## Checks

The step runs on one copy of the catalogue and replaces it only if every check passes. It is rejected if:
- it was already applied;
- an input changed (Norra Möckelövägen's fingerprint, or any OSM piece's digest);
- a piece is owned already, or a partial piece does not abut the owned rest of its way;
- a geometry is not its OSM pieces in order;
- a road does not rest within 1 m on the roads it joins, in every period from its first year;
- a road runs along another road, or two new roads run together;
- a first year is not the first map marked present, or a map after it is marked absent;
- a replaced stage feature changed, or lies more than 35 m from its road.

Scope (`docs/reviews/sviby-connections-2026-11-23/scope-audit.json`):
- objects: 3 added, 1 changed;
- geometries: 4 added;
- sources: 5 added;
- city stages: 2 changed (the stub replaced);
- the atlas roads file is unchanged.

Tests:
- `tests/test_sviby_connections.py`;
- `tests/sviby-connections.test.cjs`;
- `tests/svibyvagen.test.cjs` (the junction now joins Norra Svibyvägen);
- `tests/mariehamn-approaches-1942.test.cjs` (6 gap pieces instead of 7, and the main-road review's earlier state);
- `tests/mariehamn-major-road-followups.test.cjs`.

## Open items

- South of Norra Möckelövägen, the 1929 road ran on along the shore towards Möckelö. That has not been reviewed.
- The 1942 trace remainder at the other gaps is unchanged.
