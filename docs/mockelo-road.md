# The road to Möckelö

Build step: `apply_mockelo_road` in `scripts/mockelo_road.py`. It uses the connections step from
`scripts/sviby_connections.py` (`apply_connections`) and runs straight after the Sviby connections step.

Review data, written by `docs/reviews/mockelo-2026-11-23/scripts/prepare.py` and copied to `dist/assets/`:
- `data/mockelo-road-early.json`
- `data/mockelo-road.json`

Evidence: `docs/reviews/mockelo-2026-11-23/renders/`, read on these maps:
- the parish map 1012 05 Hammarudda–Kungsö (1928), with its Kungsö editions of 1944 and 1953;
- the parish map 1012 08 Maarianhamina (1929), with its Mariehamn edition of 1948;
- the base maps 1012 08 (1968) and 1012 05 (1978).

## Finding

- **Möckelövägen:** the 1928 sheet and its 1953 edition draw the road from the sheet edge at Svibyviken south-west to
  the corner at Gustavsberg. From there it runs on past Pellas, Södergård, Lunden, Strömbäck and Sunnvik to Möckelö
  (`m-k1928.jpg`, `m-k1953.jpg`).
  - Today's Möckelövägen follows it within 10–20 m over its whole 3.1 km.
  - Sheet 1012 05 has no 1968 base map, so the object was dated only from 1978.
- **Past Lönnelund:** from Norra Möckelövägen's south end the road runs south along the shore and then south-west to
  Möckelövägen (`z-sheet.jpg`, `e-sheet.jpg`).
  - West of the sheet seam it is on the 1928 and 1953 sheets; the shore part is on the 1929 sheet and its 1948 edition.
  - The base map 1968 labels it "t. Möckelö", and the 1978 base map draws it as part of Möckelövägen.
  - Today it is the cycleways across Hammarlandsvägen, Lönnelundsgatan and the first way of Möckelövägen. No object
    owned any of them.

## Result

| object | change | maps |
|---|---|---|
| Möckelövägen | from 1928 (was 1978), whole | 1928, 1944, 1953 |
| Möckelövägen · vid Lönnelund (new) | from 1928, 883 m | 1928, 1929, 1944, 1948, 1953, 1968, 1978 |

Notes on the table:
- The new object owns exactly the OSM pieces listed, in every extract that has them. In 2014, 2021 and 2025, way
  166080081 runs on into Möckelövägen. There the new object owns only the part before Möckelövägen's ownership begins.
- Hammarlandsvägen crosses the road; it is from the 1960s.
- Norra Möckelövägen is dated from 1929 (`docs/sviby-connections.md`), so in 1928 the new road's north end is drawn
  without it.
- Map years are first evidence, not construction years.

## Checks

The same checks as the Sviby connections step (`docs/sviby-connections.md`):
- inputs and OSM pieces unchanged;
- no piece owned twice, and partial pieces abut the owned rest of their way;
- the geometry is its pieces in order;
- both ends rest within 1 m on Norra Möckelövägen and Möckelövägen in every period;
- no run along another road;
- dates follow the maps.

Scope (`docs/reviews/mockelo-2026-11-23/scope-audit.json`):
- objects: 1 added, 1 changed;
- geometries: 2 added;
- sources: 3 added;
- nothing else, and the atlas roads file is unchanged.

Tests: `tests/test_mockelo_road.py` and `tests/mockelo-road.test.cjs`.

## Open items

- Mjölkdalsvägen, from the Gustavsberg corner south-east along the shore, may be on the 1928 sheet in part. It stays at
  1978.
- The road west from the Gustavsberg corner towards Hammarland (Småholmavägen) is not reviewed.
