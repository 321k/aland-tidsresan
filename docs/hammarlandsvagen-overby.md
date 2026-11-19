# The old road through Överby, and the later bypass

Build step: `apply_hammarlandsvagen_overby` in `scripts/hammarlandsvagen_main_road.py`. It runs straight after the
Marsund review and before the atlas review's late pass.

Review data: `data/hammarlandsvagen-overby.json` (copied to `dist/assets/`), written by
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/prepare_overby.py` from the catalogue built without this
step.

Evidence, in `docs/reviews/hammarlandsvagen-main-road-2026-11-18/`:
- `renders/overby-grid-1929.jpg`, `overby-grid-1956.jpg`, `overby-grid-1929-osm.jpg`: the village on a 50 m grid, and
  with OSM 2026 (`scripts/grid_window.py`)
- `data/trace-overby-1929.json`: the old road read on that grid (`scripts/overby_trace.py`)
- `renders/overby-base-maps.jpg`, `overby-east-1956-1985.jpg`, `overby-west-1956-1985.jpg`: the 1956 edition and the
  base maps 1968, 1978 and 1985 of sheet 101203 (`scripts/overby_base_maps.py`, `scripts/overby_loops.py`)
- `renders/overby-bypass-symbol-1978.jpg`: the bypass on the 1978 map, close up
- `renders/result-overby-1950-1975-1990.jpg`: what the map draws in 1950, 1975 and 1990

Distances are along the Marsund connection from Frebbenby (`docs/hammarlandsvagen-marsund.md`).

## Finding

On the 1929 Eckerö parish map, the road through Överby leaves today's line at 6.04 km. It makes two loops north before
rejoining at 7.08 km:
- **Henrikas loop (6.04–6.30 km):** up to 85 m north. Its middle is today's Brinkbacken (OSM way 1140848345, within
  13 m).
- **6.30–6.43 km:** on today's line, within 2–15 m. This stretch is the Marsund connection's own 1929 cut, added to
  the Marsund review.
- **Överby loop (6.43–7.08 km):** up to 88 m north, through the village. From Norra Överbyvägen westwards it is today's
  Gamla Landsvägen (way 641674806, within 17 m). The 110 m east of Norra Överbyvägen and the last curve down to today's
  road are not roads today.

The later maps:

| map | the old road | the straight bypass |
|---|---|---|
| parish map 1956 | the road | not drawn |
| base map 1968 | the main road (red, cased) | not drawn |
| base map 1978 | the main road (red, cased) | a red band without the dark edge lines every road on the sheet has: an overprint, probably planned or being built |
| base map 1985 | minor roads | the main road |

So the bypass is first drawn as a road in 1985. It was shown from 1959, when the Marsund bridge opened, because the
whole connection was given that year as an assumption.

## Result

**The Marsund connection:**
- 1929–1959: five cuts, now including 6.30–6.43 km.
- 1959–1985: the connection without its two bypass pieces (6.04–6.30 and 6.43–7.08 km). They are cut from its own
  path 3, with the same coordinates.
- From 1985: the whole line, as before. The opening state and everything else are unchanged.
- The bypass's map evidence: 1968 absent, 1978 unclear, 1985 present.

**New object "Gamla landsvägen · Överby"** (`road:eckero:gamla-landsvagen:overby`), open from 1929:
- 1929–1985, the main road: both loops, 1.08 km. Where Brinkbacken and Gamla Landsvägen survive, the line uses their
  OSM coordinates; elsewhere, the trace. Its four ends lie on the Marsund connection's ends in both 1929–1959 and
  1959–1985.
- From 1985: only Brinkbacken (vertices 1–8) and Gamla Landsvägen (vertices 7–31), with the same coordinates. The
  object owns those parts of the two OSM ways, so they are not drawn twice.
- Today these surviving parts are local roads. The 1985 map draws more of the old road as minor roads; those parts
  are not in OSM and are not drawn after 1985.

In 1929–1985 the road from Marby to Kyrkoby is now one connected line on the map.

## Checks in the build step

Every check runs before any change:
- **Bypass split:**
  - the connection's fingerprint and geometry are unchanged;
  - the period being split starts in 1959 and is open-ended;
  - the first map marked present is the end of the split, and a map in between is marked absent;
  - each removed piece is at least 50 m.
- **Old road:**
  - its first year is its first map;
  - it is the main road until the bypass, and no map marks it absent;
  - every end lies on the connection, within 1 m, in both periods;
  - each later path is exactly the coordinates of its OSM way's vertex range, and appears unchanged in the
    1929–1985 line;
  - each later path stays within 20 m of the 1929 trace;
  - it does not run alongside another road open at the same time for more than 80 m (12 m buffer).

The 1894 atlas line is hidden beside the old road. The atlas review names it as a late link
(`afterStep: apply_hammarlandsvagen_overby`), and `scripts/build_historical_roads.py` was rerun.
