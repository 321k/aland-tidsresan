# The Marsund connection: Marby and Överby–Kyrkoby from 1929

Build step: `apply_hammarlandsvagen_marsund` in `scripts/hammarlandsvagen_main_road.py`, run straight after the Kattby
review. Review data: `data/hammarlandsvagen-marsund.json` (copied to `dist/assets/`), written by
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/prepare_marsund.py`. Evidence:
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/renders/`:
- `marsund-*.jpg`: the whole connection, every 1.1 km
- `marsund-close-*.jpg`: Marby–Kyrkoby, every 400 m
- `result-marsund-1950.jpg`: what the map draws in 1950

They are made with `scripts/kattby_windows.py` and `REF=data/marsund-reference.json` (the connection as one line, from
Frebbenby to Storby).

"Eckerö–Hammarland · Marsundsförbindelsen" (Frebbenby–Öra–Marsund–Storby, 11.2 km, one object of 19 paths) is shown
from 1959, the opening of the Marsund bridge. That year is a stated model assumption for the whole corridor, not a map
date for each part.

## Sources

The parish map of sheet 1012 03 Eckerö, 1929 (colour), and its 1956 black-and-white edition. Both were added by the
Kattby review (`nls:map-39091228`, `nls:map-37971493`). Distances below are along the object from Frebbenby.

## Finding

| from Frebbenby | 1929 and 1956 maps | result |
|---|---|---|
| 0–0.4 km | the old road; it then ran west along today's Marsundsvägen to the ferry | not dated here (open item) |
| 0.4–3.0 km | no road on today's line (part is off the sheet) | 1959 |
| 3.0–4.4 km, Öra and the sound | 1929: no road. 1956: the new road is drawn, three years before the bridge opened, so the edition was updated | 1959 |
| 4.4–5.7 km, Marby | no road on today's line; the old road ran further south, past Sundkvist | 1959 |
| **5.70–6.04 km** | **the old road, within about 10 m (15 m at 5.7 km)** | **1929** |
| 6.04–7.08 km, Överby | the old road went north through the village, 40–80 m from today's road. Part of it is today's Gamla Landsvägen (OSM way 641674806), which is not in the catalogue | 1959 |
| **7.08–8.22 km**, Överby–Kyrkoby | **the old road, within 8–12 m** | **1929** |
| 8.22–8.4 km | the old road bends about 50 m east around a hill | 1959 |
| 8.4–9.0 km | the old road ("från Storby") goes off to the north-west | 1959 |
| 9.0–10.8 km | off the sheet | 1959 |
| 10.8–11.2 km, Storby | the old road runs through the village, south of today's road | 1959 |

The 1956 edition draws the two dated stretches the same way. In Överby it still draws the road through the village,
so the bypass is later than 1956.

## Result

The object gets an earlier open state and geometry period from 1929 until 1959. The period draws only the two
stretches: four cuts of the object's own paths (4, 3, 3, 2), with the same coordinates. The 1959 assumption and
everything after it are unchanged.

## Change to the build step

The step (`_apply`) could cut only one path of an object. It gains `pathRanges` and `pathOrder` (`_path_cuts`):
- `pathOrder` lists the paths in order along the road. Each must start where the one before it ends (within 1 m).
- `pathRanges` are cuts `[path, from, to]` in metres along a path, in order along the road. Each is at least 50 m.
- Cuts that run on across a path boundary form one stretch. The stretches must be the reviewed `ranges` (metres along
  the whole object, within 0.5 m).
- The period's `canonicalRanges` are those stretches as fractions of the object's length, in path order.

The atlas line `atlas-1894-1` is hidden where the stretches replace it in 1929–1958. That needs no change of its own:
the atlas review already names the object, and `scripts/build_historical_roads.py` was rerun (4 intervals added).

## Open items

- Överby village (6.04–7.08 km): the old road through the village, partly today's Gamla Landsvägen, needs its own
  object. Then the road from Marby to Kyrkoby is connected in 1929–1958.
- Frebbenby–Marsund: the old road to the ferry along today's Marsundsvägen, and the ferry itself.
- Marby east of 5.7 km (past Sundkvist), north of Kyrkoby (8.2–9.0 km) and Storby (10.8 km on): the old road is a
  separate line beside today's road.
- 9.0–10.8 km: needs the neighbouring parish sheet.
