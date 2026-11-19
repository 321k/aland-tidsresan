# Storby: the old road through the village, and the later bypass

Build step: `apply_hammarlandsvagen_storby` in `scripts/hammarlandsvagen_main_road.py`. It runs after the Kyrkoby step
and before the atlas review's late pass. It uses two helpers:
- `_bypass`, for the bypass split;
- `_old_roads`, for the old road.

Both run on a copy first. The catalogue changes only if both pass.

Review data: `data/hammarlandsvagen-storby.json`, written by `prepare_storby.py`. The connection's last 1929 stretch is
in the Marsund review.

Evidence, in `docs/reviews/hammarlandsvagen-main-road-2026-11-18/renders/`:
- `storby-mosaic-1929*.jpg`: the Eckerö and Mörby sheets combined (`scripts/mosaic_window.py`)
- `storby-village-grid-*.jpg`
- `storby-base-maps*.jpg`: the base maps 101203 and 102101, 1968–1993
- `storby-survivors-check.jpg`
- `result-storby-1950-1970-1990.jpg`: what the map draws

## Finding

On the 1929 parish maps (1012 03 Eckerö and 1021 01 Mörby, here combined), the road leaves today's line at 10.23 km
from Frebbenby. It runs south-west to Kars, curves west through the village past Hinders and Storby, and rejoins today's
line at 11.10 km. The last 140 m to the end of the connection is on today's line.

- **The Bovik edition (1946)** draws the same.
- **The base maps of 1968** (101203 and 102101) still draw the main road through the village.
- **The 1978 base map** is the first to draw today's line north of the village as the main road.

Today the old line survives as village roads, within 20 m:
- the way 433455766 to Kars;
- Gammeleksvägen and Stångbackan through Hinders;
- a short service way near the west end.

## Result

- **Marsund connection:**
  - its 1929 period gains 11.10 km to its end;
  - its 1959–1985 period (already without the Överby bypass) is split at 1978. Until then it also leaves out
    10.23–11.10 km: the tail of path 2, path 1 and the head of path 0. Its extents are given along the whole connection.
- **New object "Gamla landsvägen · Storby"** (1 158 m), open from 1929:
  - the main road until 1978;
  - then only its surviving parts, with the same coordinates, owned in OSM. That period's evidence is the OSM survey.
- **Atlas review:** the new object is a late link.

From Hammarland church to Storby the road is now drawn from 1929, over the ferry, with the bypasses at Överby (1985) and
Storby (1978) at their first map years.

## Build step

- **`_bypass`** splits the period that starts at a given year at the first map that draws the bypass. That period may
  be open-ended or end later. It checks:
  - the object's fingerprint and geometry;
  - one map without the bypass, and the first map with it;
  - each removed piece is a whole path or at least 50 m;
  - given extents are in order.
- **`old_road_lib.py`**, for the prepare scripts: when two surviving runs overlap along the trace, it trims the later
  one's leading vertices instead of dropping it. Here that keeps Gammeleksvägen, which starts a few metres behind the
  end of the way to Kars.

## Open items

- The small hooks of about 15 m where the trace joins today's line at 10.23 and 11.10 km.
- West of the connection's end (Storby to Berghamn): about 1.5 km of OSM's primary road (Eckerövägen) is in no
  catalogue object.
