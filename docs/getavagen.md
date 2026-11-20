# Getavägen in Saltvik and Finström: Godby to the Tjudö sheet edge

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
- Saltviksvägen · del 1: from Kroklundsvägen to today's road, 1929–1993. The rest of that road is not reviewed.

There is no new object: each old road is a road that exists today and keeps its identity. The route check joins them
within 1 m: Kyrkvägen → Getavägen → Bartsgårdavägen → Kroklundsvägen → Saltviksvägen → Getavägen → Gamla Getavägen. In
1929–1967 the road from Godby village to the Tjudö sheet edge is one connected line.

## Open items

- North of the sheet edge (Tjudö and Geta, 10.4–21 km), the objects are dated only from 1984. The 1927 parish maps draw
  nearly all of the road there, apart from a corner at Fenell–Dala and two 30–40 m offsets near Klevberg and Höckböle.
  That is the next batch.
- Pålsbölevägen, the road from Grönlunda, is also a 1929 road; it is not part of the main road and is not dated here.
- The eastern part of Saltviksvägen is not reviewed.
