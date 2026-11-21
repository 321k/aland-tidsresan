# Getavägen: Godby to Geta

Build step: `apply_getavagen_saltvik` in `scripts/getavagen.py`, which uses the Hammarlandsvägen helper `_apply` on a
copy. It runs after the road-remnant step and before the atlas review's late pass.

Review data: `data/getavagen-saltvik.json` (copied to `dist/assets/`), written by
`docs/reviews/getavagen-2026-11-20/scripts/prepare_saltvik.py` from the catalogue before the step.

Evidence, in `docs/reviews/getavagen-2026-11-20/renders/`:
- `ref-*-1929.jpg`: windows every kilometre with today's road in magenta
- `candidates-*-1929.jpg`: the candidate old roads in colour over the map
- `bartsgarda-1929.jpg`, `bartsgarda-1944.jpg`, `bartsgarda-1968.jpg`, `godby-1944.jpg`
- `result-1950-on-1929.jpg`, `result-1970-on-1968.jpg`: what the map draws

Distances are along "Getavägen · Godby–norra bladgränsen" (10.39 km) from Godby.

## Finding

The parish map 1021 07 Saltvik (1929) and its black-and-white edition (1944) draw:

| along today's road | 1929 and 1944 | today |
|---|---|---|
| 0–0.57 km | no road: the old road turned east along today's Kyrkvägen into Godby village | today's diagonal is first on the 1968 map |
| 0.57–4.85 km | the road on today's line, within the sheet error | |
| 4.85–5.66 km | no road: the main road went straight north along today's Bartsgårdavägen to Mellangård | today's straight across the fields is first on the 1968 map |
| 5.66–8.81 km | a lesser road through Bartsgårda, Tallnäs and Ödkarby | the main road went north-east from Mellangård along today's Kroklundsvägen through Ödkarby to Sålis, then west along today's Saltviksvägen |
| 8.81–10.39 km | the road at Avanåker, with the shore road past Sjöstrand (today's Gamla Getavägen) | |

The 1968 base map draws today's line as the main road.

## Result

Six existing objects gain an early period from 1929. Each is the object's own geometry, or a cut of it at the
junctions:
- Getavägen: 0.57–4.85 km and 5.66 km to the end, 1929–1968;
- Kyrkvägen, Bartsgårdavägen, Kroklundsvägen and Gamla Getavägen: whole, 1929–1968;
- Saltviksvägen · del 1: from Västergård over Sålis to today's road, 1929–1993. Until 2026-11-21 this period started
  at Kroklundsvägen; the Saltviksvägen review (`docs/saltviksvagen.md`) extended it east and north to Västergård,
  where the 1929 road leaves today's diagonal.

There is no new object: each old road is a road that exists today and keeps its identity. The route check joins them
within 1 m: Kyrkvägen → Getavägen → Bartsgårdavägen → Kroklundsvägen → Saltviksvägen → Getavägen → Gamla Getavägen. In
1929–1967 the road from Godby village to the Tjudö sheet edge is one connected line.

## Tjudö and Geta (10.39–21.04 km)

Build step: `apply_getavagen_tjudo_geta` in `scripts/getavagen.py`, which also runs `_apply` on a copy. It runs right
after the Saltvik step.

Review data: `data/getavagen-tjudo-geta.json`, written by `prepare_tjudo_geta.py`.

Evidence, in the same renders folder:
- `ref-*-1927.jpg`
- `fenell-*.jpg`, `skraddars-*.jpg`, `st-*.jpg`, `base-*-1978.jpg`
- `result-fenell.jpg`, `result-tjudo-geta.jpg`

The parish maps 1021 08 Tjudö–Dåglösa and 1021 05 Geta (1927), and their black-and-white editions (1941), draw the road
on today's line, with two exceptions:
- **Fenell–Dala.** The road ran in a loop up to 200 m east past Lignell, from the sheet edge (10.39 km, where the
  Saltvik object ends) to 11.16 km. The 1968 and 1978 base maps still draw it as a lesser road beside today's diagonal,
  and the 1984 map does not. Almost nothing of it is in OpenStreetMap.
- **Östergeta.** The 1927 map and the 1968 base map draw the main road along today's Skräddarsvägen, a curve up to
  100 m east of today's straight. The straight is first on the 1984 map, the earlier review's date.

Near Klevberg and Höckböle the 1927 road lies 30–40 m east of today's line, with the same shape; it is kept as one road.
Västanträsk and Örang, where the earlier review noted a straightening, are the same road on the 1927 map.

Result:
- **Getavägen (Tjudö):**
  - 1927–1968: from 11.16 km to the end;
  - 1968–1984: whole, since the diagonal at Fenell is first drawn in 1968.
- **New object "Gamla Getavägen · Fenell"** (906 m), traced on the 1927 map. It is open from 1927 until 1984, then
  `unknown`.
  - The loop joins today's road at both ends. Its south end crosses the sheet seam between the Tjudö and Saltvik sheets,
    about 50 m apart.
  - The review states `todayRoadName: Getavägen`, a new opt-in in `_apply`, so OSM's Getavägen, which the loop's ends
    merge into, is not taken as a survivor.
- **Getavägen · del 1 (Geta):** 1927–1984, without the Skräddarsvägen span (1.22–1.70 km).
- **Skräddarsvägen:** 1927–1984, whole.

Within each period the route joins within 1 m: Getavägen (Saltvik) → Fenell loop → Getavägen (Tjudö) → Getavägen
(Geta) → Skräddarsvägen → Getavägen (Geta). From 1929 the road from Godby to Geta is one connected line. The Saltvik
sheet is from 1929, so in 1927–1928 only the Tjudö and Geta part is drawn.

## Open items

- Getavägen · del 2 (100 m, a residential stretch in Geta) is not reviewed.
- Pålsbölevägen, the road from Grönlunda, is also a 1929 road; it is not part of the main road and is not dated here.
- The eastern part of Saltviksvägen: done 2026-11-21, see `docs/saltviksvagen.md`.
