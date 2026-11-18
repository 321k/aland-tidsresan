# Gamla Lemlandsvägen in today's road network — 2026-11-18

Method and decisions: `docs/lemland-old-road-osm.md`. In short: three of the four old-road objects from the
Lemlandsvägen early-map review now own the OpenStreetMap roads they survive as (Knutsbodavägen, Kockobacka,
Kommunrundan, Norra Söderbyvägen). Each one is a single road from 1917 to today, on today's line where it survives.
The corner at Fridelund was straightened between 1948 and 1968. Tomtebo–Solstrand has nothing left and is unchanged.

## Evidence

- `renders/ovre-bors*.jpg`, `johans.jpg`, `mangard-*.jpg`, `soderby-*.jpg`: the raw 1929 trace (magenta) and the
  candidate OSM ways over the 1929 parish map, the 1985 base map and OSM 2026, used to choose the ways and cut points.
- `renders/result-*.jpg`: the rebuilt lines. Black is the first phase, dark green Övre-Börs 1968–1995, thick yellow
  the surviving part from 1995. Magenta is the raw trace.
- The 1948 parish map and the 1968–1995 base maps at Fridelund were also checked (crops not kept). 1948 still draws
  the corner; 1968 is the first to draw the curve.
- `scripts/`:
  - `render.py`: the comparison sheets.
  - `prepare.py`: writes `data/lemland-old-road-osm.json` with fingerprints, from
    `data/map-scan-cache/review/lemlandsvagen-main-road/before-old-road-osm.json.gz`.
  - `leftovers.py`: unowned OSM roads still beside a surviving line.
  - `audit.py`: the scope audit.
  - Map tiles stay in the review cache (`data/map-scan-cache/review/church-road/tiles.json` has their sha256).
- `scope-audit.json`: compared with the catalogue before this review, exactly 3 objects changed and 7 geometries and
  1 source added. Nothing was removed, and no other object, geometry or city stage changed. A full rebuild is
  byte-identical to applying the step to the snapshot.

## Tests

- New: `tests/lemland-old-road-osm.test.cjs` (6) and `tests/test_lemland_old_road_osm.py` (3, snapshot replay;
  each rejection was checked to fail for its stated reason).
- Updated: `tests/lemlandsvagen-main-road.test.cjs` and `tests/test_lemlandsvagen_main_road.py`. The old-road
  objects no longer turn `unknown` after 1985/1995, and the replay runs both steps before comparing with the build.

Runs (`logs/`): the full JS suite passed 572 of 573. The one failure was the loader-preview test, which ran before
the preview was regenerated; rerun afterwards, it passes (`js-startup-loader-rerun.log`). The Python tests
(old-road OSM, Lemlandsvägen main road, QGIS road reconciliation, Lemlandsvägen split) pass: 44 tests.

## What is in `batch.patch`

`scripts/build_temporal_objects.py` (the hook and the asset copy) and `dist/index.html` (the loader card "Gamla
Lemlandsvägen i dagens vägnät", now 79 cards; the loader preview was regenerated and changed only by this batch's
+15 observations and +1 source). Both files also hold other uncommitted work. See `patch-verification.log`.

Not deployed or committed yet.
