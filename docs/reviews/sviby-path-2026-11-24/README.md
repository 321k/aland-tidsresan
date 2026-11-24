# Roads at Sviby that became paths

Two roads from the Sviby connections (`docs/sviby-connections.md`) are cycle and foot paths today. Before this
review, the map drew each of them in one style for every year:
- **The road from Norra Svibyvägen east to Svibyvägen** was drawn as a full road to this day, although its west part
  is a cycle path today.
- **The north piece of Norra Möckelövägen** was drawn as a path back to 1929, although it was a road then.

Build step: `apply_sviby_paths` in `scripts/sviby_paths.py`, after the main-road batches.

Review data: `data/sviby-paths.json` (copied to `dist/assets/`), written by
`docs/reviews/sviby-path-2026-11-24/scripts/prepare.py`.

## Dated road classes

A road object may now carry `roadClassPeriods`. Each period has these fields:
- `from` and `to`;
- `class`, an OSM road class;
- `basis` and `evidenceIds`;
- optionally `canonicalRange`, a fraction of the line's length.

At most one period applies in a year. Outside the periods the object's `modernRoadClass` applies.
- The map (`dist/city-grid.js`) draws the class in force each year. Paths (footway, cycleway, path, track) are drawn
  in the path style.
- With a `canonicalRange`, only that part of the line changes style.
- `dist/temporal-objects.js` validates the periods.

The objects keep their identity, geometry and open state. The physical way is the same; only its use changed.

## Evidence

**The road east to Svibyvägen:**
- **OSM 2014 and 2021:** the whole road is one residential way (35304978).
- **OSM 2025 and 2026:** the west 252 m from Norra Svibyvägen are four cycleway ways; the east 170 m are residential.
- **The aerial photos 2007, 2015 and 2021** (`renders/photos-all.jpg`, `photos-plain-zoom*.jpg`): an even gravel road
  of the same width along the whole length. When the west part was closed to cars cannot be seen on them.
- **Result:** the west 252 m are a cycleway from 2025, the first evidence. The east part stays a residential road.

**The north piece of Norra Möckelövägen** (`renders/norra-delen-photos.jpg`):
- **Maps:** a road on the maps 1929–1995.
- **Aerial photos 1952–1999:** a full-width gravel road.
- **Aerial photo 2007:** Norra Svibyvägen has a new curve to the south-west, and the old piece is a narrow path.
- **OSM:** a footway in 2014 and a cycleway in 2025.
- **Result:** a residential road 1929–2006, then its modern class, cycleway, from 2007.

The aerial tiles are Mariehamn's city photos at 1 m per pixel. They were fetched with
`docs/reviews/mariehamn-building-photos-p2-2026-11-17/scripts/fetch.py`.
