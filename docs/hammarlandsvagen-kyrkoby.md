# Kyrkoby to Storby: the old road north of Kyrkoby and through Bagars

Build step: `apply_hammarlandsvagen_kyrkoby` in `scripts/hammarlandsvagen_main_road.py` (helper `_old_roads`). It runs
after the Holmberg step and before the atlas review's late pass.

Review data: `data/hammarlandsvagen-kyrkoby.json` (copied to `dist/assets/`), written by `prepare_kyrkoby.py`. The
connection's two new 1929 stretches are in the Marsund review (`prepare_marsund.py`).

Evidence, in `docs/reviews/hammarlandsvagen-main-road-2026-11-18/renders/`:
- `storby-*.jpg`: the parish maps 1021 01 Mörby (1929) and its Bovik edition (1946), the 1968 base map and OSM
- `kyrkoby-north-grid-*.jpg`, `bagars-grid-1929-osm.jpg`: 50 m grids
- `bagars-base-maps*.jpg`, `storby-base-maps*.jpg`: base maps 101203 and 102101, 1968–1993
- `result-kyrkoby-1950-1965.jpg`: what the map draws

Distances are along the Marsund connection from Frebbenby.

## Finding

North of Kyrkoby the 1929 maps (Eckerö and Mörby) and the editions of 1946 (Bovik) and 1956 (Eckerö) draw:

| along the connection | 1929 | today |
|---|---|---|
| 8.22–9.20 km | the old road ("från Storby"): a bump about 50 m east around a hill at Furuboda, then north-west, 50–80 m west of today's straight road, to Kristiansund | today's straight road is younger. Part of the old line is today's Södra Bölevägen (two OSM ways, 503 m, within 17 m). |
| 9.20–9.40 km | the road on today's line | |
| 9.40–9.85 km | the old road straight through Bagars, up to about 80 m south of today's arc | part of it is an OSM way (139 m, within 18 m) |
| 9.85–10.23 km | the road on today's line, within about 15 m | |
| from 10.23 km | the road turns south-west into Storby village | next batch |

The 1968 base map (sheets 101203 and 102101) already draws today's straight road at Kyrkoby and the arc at Bagars as
the main road. There is no map here between the 1946/1956 editions and 1968. So the old lines are the main road until
1959, the connection's bridge assumption, which this review keeps.

## Result

- **Marsund connection:**
  - its 1929 period gains 9.20–9.40 km and 9.85–10.23 km;
  - the Mörby (1929) and Bovik (1946) sheets are added as sources.
- **New objects "Gamla landsvägen · Kyrkoby–Böle" (1 094 m) and "Gamla landsvägen · Bagars" (454 m)**, both open
  from 1929:
  - until 1959, the whole old line. It uses the trace where nothing survives and the OSM coordinates where something
    does. Its ends are fixed to the connection's 1929 stretches.
  - from 1959, only the surviving parts, with the same coordinates. Each object owns those vertex ranges of the OSM
    ways. That period's evidence is the OSM survey; no base-map reading is claimed for the surviving parts.
- **Atlas review:** both objects are late links.

In 1929–1958 the road from Kyrkoby to the edge of Storby is now one connected line.

## Build step

`_old_roads` checks, before any change:
- the connection's fingerprint;
- each old road's dates against its maps (no map marks it absent), and that the switch year is stated;
- its length, and that its ends lie on the connection's 1929 stretches and on its later line;
- that each surviving part is exactly an OSM vertex range, appears unchanged in the 1929 line, stays within 20 m of
  the trace, and is not owned by another object;
- that it does not run along another road open at the same time.

## Open items

- Storby (from 10.23 km): done, see `docs/hammarlandsvagen-storby.md`.
- The small hooks of about 15 m where the traces join today's line.
