# Saltviksvägen: Tjudö to Kvarnbo

Build step: `apply_saltviksvagen_east` in `scripts/saltviksvagen.py`, which uses the Hammarlandsvägen helper `_apply`
on a copy. It runs right after the Getavägen steps and before the atlas review's late pass.

Review data: `data/saltviksvagen-east.json` (copied to `dist/assets/`), written by
`docs/reviews/saltviksvagen-2026-11-21/scripts/prepare.py` from the catalogue before the step.

Evidence, in `docs/reviews/saltviksvagen-2026-11-21/renders/`:
- `sheet-*.jpg`, `g-*.jpg`: windows along today's road, with a 50 m grid and OSM in green
- `andelsby-*.jpg` (1927, 1941, 1968, 1978, 1984, 1993), `andelsby-1927-zoom.jpg` (the trace)
- `odkarby-*.jpg`, `prastgarden-*.jpg`, `kavelbro-*.jpg`
- `del1-*.jpg`, `del1n-*.jpg`, `vastergard-*.jpg`, `vg-*.jpg`, `vgz-*.jpg`: Västergård and the sheet seam
- `result-andelsby-1950.jpg`, `result-andelsby-1975.jpg`, `result-andelsby-1990.jpg`, `result-kavelbro-1950.jpg`,
  `result-1950-overview.jpg`: what the map draws

Distances are along today's road from Saltviksvägen del 1 at Laby to Kvarnbo (8.67 km): the Tjudö object, del 2,
Antböle–Nygård, Kavelbro (the bypass) and Kvarnbo–Kavelbro joined end to end (`data/reference.json` in the review).

## Finding

Today's Saltviksvägen east of Laby was dated from 1968. The parish maps 1021 08 Tjudö–Dåglösa (1927) and 1021 07
Saltvik (1929), and their black-and-white editions (1941, 1944), draw:

| along today's road | 1927/1929 and 1941/1944 | today |
|---|---|---|
| 0–1.39 km, Laby–Andelsby | the road on today's line | |
| 1.39–1.83 km, Andelsby–Nygård | no road: the road went north along today's Dåglösavägen for 200 m and east in a curve up to 150 m north of today's line | today's diagonal is first on the 1968 map; the 1968 and 1978 maps still draw the curve as a lesser road, the 1984 map does not |
| 1.83–7.20 km, Nygård, Ödkarby, Prästgården, Antböle | the road on today's line; at Ödkarby and Prästgården 20–40 m east with the same shape, as on the 1968 map, so a sheet error | |
| 7.20–7.45 km, Kavelbro | the road through the curve east of today's line, today's Kavelbrovägen | the bypass is first on the 1978 map |
| 7.45–8.67 km, Kavelbro–Kvarnbo | the road on today's line | |

The 1927 sheet ends just north of Saltviksvägen del 2 (3.65 km); south of it the road is on the 1929 Saltvik sheet.

**Västergård.** West of Laby, Saltviksvägen del 1 runs south-west through Västergård to Sålis. The 1929 map draws the
road on today's line from Sålis north to Västergård (del 1, 0.50 km from its east end). There it leaves today's
diagonal, turns east past Bygge and runs north to the sheet edge. The 1968 map draws the same route as the main road.
The diagonal is first on the 1978 map. Between that sheet edge and the start of the Tjudö object, every map has a sheet
edge: 1927/1929, 1941/1944 and the 1968 base maps. So how the road ran for the last few hundred metres is not drawn.

## Result

Seven existing objects gain an early period, each its own geometry or a cut of it:
- Saltviksvägen (Tjudö): 1927–1968, without the diagonal at Andelsby (1.83–2.26 km of the object, which runs east to
  west);
- Dåglösavägen: the 200 m from Andelsby to the bend, 1927–1968. The rest of Dåglösavägen is not reviewed;
- Saltviksvägen · del 2: whole, 1927–1993 (it is dated from 1993 after that);
- Antböle–Nygård, norr om Kavelbro, Kavelbrovägen and Kvarnbo–Kavelbro: whole, 1929–1968. The Kavelbro bypass keeps
  1978.

New object "Gamla Saltviksvägen · Andelsby" (472 m), traced on the 1927 map. It runs from the bend on Dåglösavägen to
today's road at Nygård and is open from 1927 until 1984, then `unknown`. Almost nothing of it is in OpenStreetMap.

The Saltvik review (`docs/getavagen.md`) now dates Saltviksvägen del 1 from Västergård (0.50 km) instead of from
Kroklundsvägen (1.78 km), in `docs/reviews/getavagen-2026-11-20/scripts/prepare_saltvik.py`.

The route check joins the pieces within 1 m: Saltviksvägen (Tjudö) → Dåglösavägen → the Andelsby curve → Saltviksvägen
(Tjudö) → del 2 → Antböle–Nygård → norr om Kavelbro → Kavelbrovägen → Kvarnbo–Kavelbro. One gap is stated: 488 m
between del 1 at Västergård and the start of the Tjudö object, across the sheet seam.

## Checks

The step is rejected as a whole, leaving the catalogue unchanged, if:
- an input object or geometry changed (fingerprint, digest, length);
- a first year is not the first map marked present, or an early period does not end where the object now begins;
- the curve's dates do not follow its maps;
- the curve does not end on Dåglösavägen and today's road, runs along another road open in 1927–1983, or survives in
  OSM. The review states `todayRoadName: Saltviksvägen`, so today's road, which its ends merge into, is not taken as a
  survivor;
- the route breaks, or the stated gap is not 488 m (±2 m).

Tests:
- `tests/test_saltviksvagen_east.py`. Its pre-step snapshot is kept in
  `data/map-scan-cache/review/saltviksvagen/before-saltviksvagen-east-step.json.gz`;
- `tests/saltviksvagen.test.cjs`.

## Open items

- The link at Västergård across the sheet seam. A map without a seam there (the 1917 Senate map does not cover it) or a
  later edition could settle it.
- The rest of Dåglösavägen, which the 1927 map also draws.
- At Kvarnbo the road ends at the junction (Kvarnbo vägskäl, dated from 1968). Kvarnbo kyrkväg is open from the atlas
  of 1894, so there is a gap of about 25 m at the junction.
