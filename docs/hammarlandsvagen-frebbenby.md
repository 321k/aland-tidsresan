# The road to the Marsund ferry: Frebbenby and Marsundsvägen from 1929

Build step: `apply_hammarlandsvagen_frebbenby` in `scripts/hammarlandsvagen_main_road.py`. It runs after the Överby
review and before the atlas review's late pass.

Review data: `data/hammarlandsvagen-frebbenby.json` (copied to `dist/assets/`), written by
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/prepare_frebbenby.py`. The Marsund connection's own
Frebbenby stretch is in the Marsund review (`prepare_marsund.py`).

Evidence, in `docs/reviews/hammarlandsvagen-main-road-2026-11-18/renders/`:
- `marsundsvagen-*.jpg`: along Marsundsvägen every 400 m, on the 1929 and 1956 sheets and with OSM
- `frebbenby-grid-1929-osm.jpg`, `frebbenby-grid-1956.jpg`: the junction at Frebbenby on a 50 m grid
- `marsundsvagen-base-maps.jpg`: the 1956 edition and the base maps 1968, 1978 and 1985 (sheet 101203)
- `result-frebbenby-1950.jpg`: what the map draws in 1950

## Finding

Before the Marsund bridge (1959), the road from Hammarland to Eckerö crossed the sound by ferry. The 1929 Eckerö parish
map and its 1956 edition draw the road and the ferry route:
- **Through Frebbenby, along today's Marsund connection:** 0–0.47 km from Frebbenby, within about 13 m. At 0.47 km
  the connection turns north-west (the 1959 line). The old road went straight on west.
- **Along today's Marsundsvägen to the ferry pier:** 0–1.04 km along it, within about 15 m; in the bend at Marsund
  within about 25 m. The pier is at 1.04 km, where both editions draw the ferry route across the sound.
- **South of the pier:** neither edition draws a road along Marsundsvägen's line; 1956 has a dotted track along the
  shore.

The base maps 1968, 1978 and 1985 draw Marsundsvägen to the pier as a road; 1968 still in the red of a main road.
Marsundsvägen was dated from 1994 by the QGIS review, as one segment; its note already says that the northern part
has 1968 evidence.

## Result

- **Marsund connection:** its 1929 period gains 0–0.47 km. That is its paths 18, 17 and 16 whole. Path 17 is 36 m
  long; a cut under 50 m is now allowed when it is a whole path inside a longer stretch.
- **Marsundsvägen:** an earlier open state and geometry period from 1929 until 1994, its first 1 040 m, cut from its
  own coordinates. Everything from 1994 is unchanged.
- **Route check:** Kattby west, then the Marsund connection, then Marsundsvägen. There is one stated gap of 26.7 m:
  Marsundsvägen starts beside the connection, and an unreviewed OSM link (way 125420159) joins them.

In 1929–1958 the road runs on the map from Hammarland church through Frebbenby to the ferry pier.

The 1894 atlas line is 734 m away here and needs no link.

## Open items

- Marsundsvägen south of the pier: the 1968 map draws it as a road, but the QGIS review dated it as one segment from
  1994. This review leaves that as it is.
- The ferry route itself. The road on the Eckerö side from the narrow sound to Marby: done, see
  `docs/hammarlandsvagen-ferry-west.md` and `docs/hammarlandsvagen-holmberg.md`.
