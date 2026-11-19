# The road from the Marsund ferry to Marby (Eckerö side)

Build steps, both run after the Frebbenby review and before the atlas review's late pass, in
`scripts/hammarlandsvagen_main_road.py`:
- `apply_hammarlandsvagen_marby`: Marbyvägen and the link at Sundkvist. Data: `data/hammarlandsvagen-marby.json`,
  written by `prepare_marby.py`.
- `apply_hammarlandsvagen_shore`: the shore road. Data: `data/hammarlandsvagen-shore.json`, written by
  `prepare_shore.py`.

The Marsund connection's crossing of the narrow sound is in the Marsund review (`prepare_marsund.py`).

Evidence, in `docs/reviews/hammarlandsvagen-main-road-2026-11-18/renders/`:
- `ferry-eckero-side-1929.jpg`: overview, pier to Marby
- `holmberg-grid-*.jpg`: the ferry ("M. färja") and Holmberg
- `ferry-landing-grid-*.jpg`, `shore-road-grid-1929.jpg`, `sundkvist-grid-1929.jpg`, `sundkvist-marby-grid-1929.jpg`,
  `klemes-grid-*.jpg`: 50 m grids
- `marbyvagen-*.jpg`, `marbyvagen-north-1929-1956.jpg`: Marbyvägen on both editions
- `ferry-route-1968-1978.jpg`: the base maps
- `result-ferry-west-1950-1957-1970.jpg`: what the map draws

Waypoints were read on the grids and converted with `scripts/grid_trace.py`.

## Finding

Before the bridge, the ferry ("M. färja" on the 1929 Eckerö parish map) crossed Marsund from the pier at the end of
Marsundsvägen to a pier on Holmberg. From there the 1929 road went:
1. West across Holmberg to the narrow sound. Not dated in this batch (open item).
2. **Over the narrow sound on today's line**, 3.69–3.88 km from Frebbenby, within about 25 m.
3. **South along the shore of the sound to Nissas**: 1.1 km, 45–80 m east of today's Marbyvägen. On the same map,
   Marbyvägen's line there is a footpath.
4. **Back north-west on Marbyvägen** past Klemes to Sundkvist: 200–2 000 m along Marbyvägen. Within about 10 m;
   past Klemes within about 30 m, with the same shape.
5. **From Sundkvist north-west to Marby**: 540 m, 15–50 m south of today's road, joining it at 5.70 km, where the
   connection's dated Marby stretch starts.

Later maps:

| map | the shore road | Marbyvägen north of Nissas | the link at Sundkvist |
|---|---|---|---|
| 1929 | the road | a path | the road |
| 1956 edition | not drawn | the road | the road |
| 1968 base map | not drawn | the road (red) | not drawn; the road goes via Marbyvägen's branch north to today's road |

The 1968 map also draws today's road straight through Marby, so the 1959 assumption for that part holds.

## Result

- **Marsund connection:** its 1929 period gains 3.69–3.88 km.
- **Marbyvägen** (dated from 1968 by the QGIS review):
  - 1929–1956: 200–2 000 m
  - 1956–1968: from 200 m to its north end at the sound
  - from 1968, its whole line as before
  The step gains `laterStage` for this: a second early period from a later map, with its own ranges.
- **New object "Gamla landsvägen · Sundkvist"**: open 1929–1968, then unknown. Its ends are fixed to the connection
  at 5.70 km and to Marbyvägen at 200 m.
- **New object "Gamla landsvägen · strandvägen vid Holmbergssundet"**: open 1929–1956, then unknown. Its ends are
  fixed to the connection at 3.88 km and to Marbyvägen at 2 000 m. Nothing of it is in OSM.
- **Atlas review:** it names Marbyvägen and both new objects as late links. Between 1929 and 1958 the dated route
  replaces the 1894 atlas line at Marby (atlas vertices 5–7). The schematic ferry crossing (vertices 8–9) stays until
  1959.

In 1929–1955 the road from the narrow sound to Marby is one connected line. In 1956–1958 Marbyvägen's north end is
30 m from the end of the connection's crossing stretch; no road between them is dated yet.

### Two corrections while building

- The shore road first ran on to 1 930 m along Marbyvägen. The build step's survivor check rejected it: its last 70 m
  were within 15 m of Marbyvägen. Measured again, the old road leaves Marbyvägen at about 2 000 m.
- Its northern start first had three waypoints within about 20 m of today's line. The crossing stretch now runs to
  3.88 km instead.

## Open items

- The road across Holmberg from the narrow sound to the ferry pier. Partly today's road to Örliden; it needs the
  Överby treatment (surviving parts owned in OSM).
- 1956–1958: the 30 m between the crossing stretch and Marbyvägen.
- The ferry route itself.
