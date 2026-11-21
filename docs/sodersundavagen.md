# Södersundavägen: Hammarland to Jomala church

Build step: `apply_sodersundavagen` in `scripts/sodersundavagen.py`, run right after the Saltviksvägen step and before
the atlas review's late pass. It runs three steps on one copy of the catalogue, which replaces it only if all pass.

Review data, both copied to `dist/assets/`, written by
`docs/reviews/hammarland-jomala-2026-11-21/scripts/prepare.py` from the catalogue before the step:
- `data/sodersundavagen.json`: the early period and the coverage step;
- `data/sodersundavagen-jomala.json`: the old road.

Evidence, in `docs/reviews/hammarland-jomala-2026-11-21/renders/`:
- `sheet-sod.jpg` and `sod-*.jpg`: Södersundavägen on the Hammarby (1929), Näfsby–Emkarby (1944) and Jomala (1928)
  sheets
- `al-*.jpg`: the loop on the 1928 and 1955 maps; `al-base-1968-1985.jpg` and `al-base-1995.jpg`: the base maps
- `mattas.jpg`, `mattas-bend.jpg`: Mattas and the old bend on the 1929, 1944, 1968 and 1995 maps
- `result-loop.jpg` (1950, 1975, 2000) and `sheet-result.jpg`: what the map draws

## Finding

The southern Hammarlandsvägen review (`docs/hammarlandsvagen-south.md`) dated the 1929 road from Söderby east to
Mattas. It left the road on towards Jomala as an open item. That is today's Södersundavägen (way 86548779) through
Ulvsby, then three OSM ways that no object owned. The maps draw:

- **Södersundavägen from Södersunda to Ulvsby:** the 1929/1928 road, within 20–40 m and with the same shape, the
  S-curve through Ulvsby included. The road lies on three sheets: Hammarby 1929, its 1944 print (Näfsby–Emkarby) and
  Jomala 1928. Its westernmost 84 m are part of the 1995 bypass at Mattas, as the rural review found.
- **The bend east of Ulvsby** (from 212 m before Södersundavägen's east end): the 1928 road turns north-east. It runs
  round a loop past Al, along today's Drittel-Mattes Gränd, then east past Häggblom along today's S:t Olofs vägen to
  Godbyvägen at the church. The 1955 edition and the base maps 1968, 1978 and 1985 draw the main road on this loop. The
  1995 map draws today's straight and Nya Godbyvägen, and the loop as a local road.
- **Mattas.** The 1929 map, its 1944 print and the 1968 map draw the road from Mattas along the old bend that the
  rural review kept (ways 495221553 and 160987689), then north-east to Södersundavägen. The Mattas way's north-eastern
  part is the 1995 bypass, as the rural review found.

## Result

- **Södersundavägen** (86548779): an early period 1929–1968, cut from its whole geometry. It runs from the rural
  review's west end (east of the 1995 bypass) to the bend. Its 1968–1995 periods drew only the 2.0 km on the Hammarby
  base-map sheet. They now draw the same stretch as the early period, from the Jomala base maps 1968–1985. Its
  1995–2021 period draws the whole road (Jomala 1995); until now the Ulvsby part appeared only from 2021.
- **New object "Gamla Södersundavägen · Jomala kyrkby"** (905 m):
  - from 1928 until 1995 it draws the whole loop: the bend, Drittel-Mattes Gränd, the link past Häggblom and S:t
    Olofs vägen;
  - from 1995 it draws only the surviving parts, owned in OpenStreetMap 2026: Drittel-Mattes Gränd without its later
    link to today's road, and S:t Olofs vägen;
  - its east end lies on Godbyvägen at the church, which is dated from about 1800.

From 1929 to 1994 Södersundavägen and the loop make one connected line from Södersunda to Jomala church.

## Changes to shared code

`_old_roads` in `scripts/hammarlandsvagen_main_road.py` has a new opt-in, `endsOn`: an end that joins another road
partway along it. That end must lie within 1 m of that road in every period from the old road's first year on. Other
reviews do not use it and are unchanged.

## Checks

The step is rejected as a whole, leaving the catalogue unchanged, if:
- an input object or geometry changed (fingerprints, digests, lengths), or the early period does not follow its maps;
- a coverage period no longer has its recorded geometry, the whole geometry changed, or no map marked present falls in
  the period;
- the old road's dates do not follow its maps;
- a surviving part is not its OSM way, has moved, or lies more than 35 m from the 1928 drawing;
- the old road does not join Södersundavägen's early stretch and its later line, or does not end on Godbyvägen;
- the old road runs along another road open in 1928–1994.

Tests:
- `tests/test_sodersundavagen.py`. Its pre-step snapshot is kept in
  `data/map-scan-cache/review/sodersundavagen/before-sodersundavagen-step.json.gz`;
- `tests/sodersundavagen.test.cjs`.

## Open items

- Mattas to Södersundavägen: the 1929 and 1968 maps draw the road on from the old bend (way 160987689) north-east to
  Södersundavägen. The last 190 m are in no object, and the maps join Södersundavägen 40–60 m south-east of where its
  1968–1995 geometry begins. This gap was already there in 1968–1995. Nothing of it is in OSM.

- Today's straight from Södersundavägen's east end to Nya Godbyvägen (OSM ways 1422779921 and 963752543, 390 m) is in
  no object. From 1995 the road there is not drawn.
- S:t Olofs vägen in the older extracts (2014–2025, way 70759517) is not owned.
- The 1917 Senate atlas (Jomala) shows nothing here.
