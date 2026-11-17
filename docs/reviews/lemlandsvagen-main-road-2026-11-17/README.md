# Lemlandsvägen on the early maps — 2026-11-17

Method and decisions: `docs/lemlandsvagen-main-road.md`. In short: Lemlandsvägen del 1 is now eight sections dated
by the first map that draws each (1917 where the old road is today's road, 1968 or 1985 where a bypass was built), and
the old road between the canal and the church village is four new objects traced on the 1929 parish map.

## Evidence

- `renders/grid-*-1929.jpg`: the 1929 map with a 50 m grid, used to place the waypoints in `data/waypoints.json`.
- `data/trace-*-1929.json`: the traced old road (EPSG:3874) with its distance profile to today's road.
- `renders/check-*-1929.jpg`: the traces (magenta) over the 1929 map; `renders/base-*.jpg`: the same over the 1968,
  1978 and 1985 base maps, showing the old road kept as a minor road beside the new one.
- `renders/along-*`: traces of sections B and D, where old and new coincide (bin medians: the 1929 sheet's error).
- `scripts/`: `trace.py` (least-cost tracing on the road-centre band), `trace_route.py`, `trace_along.py`,
  `grid_render.py`, `check_render.py`, `check_base.py`, `sheet_shift.py` (shows the 1968 sheet's 30–60 m offset)
  and `prepare.py`, which writes `data/lemlandsvagen-main-road.json` with fingerprints. Map tiles stay in the review
  cache (`data/map-scan-cache/review/church-road/tiles.json` has their sha256).
- `scope-audit.json`: against the catalogue before this review, exactly 11 objects added (7 sections, 4 old-road
  objects) and 2 changed (the original del 1, Långskata del 2); 12 geometries and 2 sources added; no city stage.

## Tests

`tests/lemlandsvagen-main-road.test.cjs` and `tests/test_lemlandsvagen_main_road.py` are new. `qgis-roads` counts
the new sections as owners of the moved source ranges, and `temporal-objects` counts the 11 new objects (both in
`batch.patch`). The other failing JS tests fail the same way without this step (checked against a build without it).

## What is in `batch.patch`

`scripts/build_temporal_objects.py` (the hook and the asset copy), `tests/qgis-roads.test.cjs`, `tests/test_qgis_road_reconciliation.py` (its replay leaves out the new sections, as it does the Strandnäs split),
`tests/temporal-objects.test.cjs` and `dist/index.html` (loader card "Gamla Lemlandsvägen"; the loader preview was
regenerated and came out unchanged). These files also hold other uncommitted work. See `patch-verification.log`.

Not deployed or committed yet.
