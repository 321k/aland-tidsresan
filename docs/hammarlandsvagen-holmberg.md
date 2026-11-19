# Holmberg: the road to the Marsund ferry pier, and Öravägen

Build step: `apply_hammarlandsvagen_holmberg` in `scripts/hammarlandsvagen_main_road.py`. It runs after the shore-road
step and before the atlas review's late pass.

Review data: `data/hammarlandsvagen-holmberg.json` (copied to `dist/assets/`), written by
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/prepare_holmberg.py`.

Evidence, in `docs/reviews/hammarlandsvagen-main-road-2026-11-18/renders/`:
- `holmberg-road-grid-1929*.jpg`, `holmberg-road-grid-1956*.jpg`: 50 m grids, with and without OSM
- `holmberg-road-1968-1985.jpg`: the base maps, with Öravägen
- `result-holmberg-1950-1957-1970.jpg`: what the map draws

## Finding

- **1929 parish map:** the Marsund ferry ("M. färja") landed at a pier on Holmberg's east shore. From there the road
  ran straight west across Holmberg to the narrow sound (454 m). There it joins the connection's 1929 crossing
  stretch (`docs/hammarlandsvagen-ferry-west.md`). Nothing of this line is in OSM; today's Öravägen only crosses it.
- **1956 edition:** the road leaves the line halfway across and turns south-east to a new pier at Örliden, on today's
  Öravägen. It no longer reaches the old pier.
- **Base maps 1968 and 1978:** Öravägen is the main road (red) to the Örliden pier. In 1985 it is a minor road.

## Result

- **New object "Gamla landsvägen · Holmberg"**: open 1929–1956, then unknown. Its west end is fixed to the
  connection's 1929 crossing stretch (3.69 km). Its east end is the ferry pier.
- **New object "Öravägen"**, open from 1956:
  - its geometry is its OSM 2026 line, used as a stable position from 1956;
  - it owns the way whole in the OSM extracts of 2014, 2021, 2025 and 2026, so the city layer does not draw it again.
- No existing object changed.

From 1929 to 1955 the map now draws the whole road from Hammarland church, over the ferry, to Marby.

## Changes to the build step

- **`freeEnds` on an old road** (with `freeEndBasis`): the ends listed there need not lie on a road. Here that is the
  ferry pier. Every other end is still checked.
- **Öravägen is checked before any change:**
  - it is owned in every OSM extract;
  - each extract's way is unchanged (digest) and linked whole;
  - no other object owns it;
  - its geometry is exactly the 2026 way;
  - its first year is its first map, and no map marks it absent.

## Open items

- **1956–1958:** Öravägen's west end is at today's road (3.6 km), about 90 m from the dated crossing stretch. That
  junction is younger, and the 1956 road's west end is not dated separately.
- **The ferry routes** (to the old pier and to Örliden) are not drawn.
- **The 1894 atlas line:** these two objects are not linked to it. The atlas segment here is its schematic crossing
  of the sound, which stays until the bridge (`tests/marsund-road-continuity.test.cjs`).
