# Hammarlandsvägen on the 1929 parish map — 2026-11-18

Method and decisions: `docs/hammarlandsvagen-main-road.md`. In short:
- Between Söderby and the church in Hammarland, today's road is drawn from 1929 where it follows the road on the 1929
  Hammarby parish map.
- The bypasses at Drygsböle, Smedens and Näfsby keep 1968.
- The old line at Smedens is a new object.
- Långskata del 2's early period, from the Lemlandsvägen review, now draws only its first 300 m.

## Evidence

- `data/reference.json`: today's Hammarlandsvägen as one line (Mariehamn's edge to Kattby), from the catalogue.
- `renders/along-*.jpg` (every 500 m) and `renders/detail-*.jpg` (every 250 m, Söderby–church): today's road (red)
  over the 1917 Senate atlas, the 1928/1929 parish map, the 1944 edition, the 1968/1978 and 1985 base maps, and OSM.
- `renders/overview-*.jpg`, `osm-overview-south.jpg`, `ulling-odanbole.jpg`: the southern half. The older main road
  ran via Ullingsvägen–Ödanbölevägen; the pink Ödanböle–Söderby line on the 1929 sheet is a hand addition.
- `renders/raw-*.jpg`, `base-drygsbole-smedens.jpg`, `osm-*-1944.jpg`, `grid-*-1929.jpg`: the closer looks at
  Drygsböle, Smedens and Näfsby.
- `data/waypoints.json`, `data/trace-smedens-1929.*`, `data/trace-nafsby-1929.*`: the old lines read on the 1929 map.
  They are polylines through grid-read waypoints. Least-cost tracing followed slope hatching here, and the first
  Smedens attempt is described in the waypoints note. Only the Smedens line is used in this batch.
- `renders/result-1950-on-1929.jpg`: what the map draws in 1950 (magenta) over the 1929 sheet.
- `scripts/`:
  - `maps.py`: tile and scan windows.
  - `reference.py`, `along.py`, `overview.py`, `osm_overview.py`, `way_windows.py`, `osm_on_map.py`: the renders.
  - `trace_old.py`, `overlay_to_metric.py`: the old lines.
  - `prepare.py`: writes the review data with fingerprints, from
    `data/map-scan-cache/review/hammarlandsvagen-main-road/before.json.gz`.
  - Map tiles stay in the review cache (`data/map-scan-cache/review/church-road/tiles.json` has their sha256).
- `scope-audit.json`: compared with the catalogue before this review:
  - added: 1 object, 7 geometries and 3 sources
  - changed: 6 objects (the five Hammarlandsvägen objects and Långskata del 2)
  - nothing else changed; no city stage changed.

  The full build also contains another session's Erikssonska and Societetshuset work (2 added and 4 changed objects).
  That work is listed separately, and nothing of it belongs to this batch.

## Tests

- New: `tests/hammarlandsvagen-main-road.test.cjs` and `tests/test_hammarlandsvagen_main_road.py` (snapshot replay).
  Each rejection was checked to fail for its stated reason.
- Updated:
  - `tests/lemlandsvagen-main-road.test.cjs`: Långskata draws about 300 m before 1985.
  - `tests/test_lemlandsvagen_main_road.py`: one more geometry.

Runs (`logs/`): all 581 JS tests pass with the batch applied. The Python tests for this step, the Lemlandsvägen
main-road and old-road reviews and the QGIS road reconciliation pass (40 tests).

## What is in `batch.patch`

- `scripts/build_temporal_objects.py`: the hook and the asset copy.
- `dist/index.html`: the loader card "Hammarlandsvägen från 1929", and the loader preview regenerated from the
  current catalogue.
- `tests/rural-map-review.test.cjs`: the farm-road check accepts the review's earlier start through
  `previousFirstYear`, as it already does for `historicalDating`. The Boda/Drygsböle check expects the partial 1929
  period on way 345142933.
- `tests/temporal-objects.test.cjs`: counts the Smedens old line.

These files also hold other uncommitted work; see `patch-verification.log`. `scripts/lemlandsvagen_main_road.py`
(Långskata's own early geometry) has no other uncommitted work and is committed directly.

Committed as 0d1b396 and deployed (Cloudflare 0af559f2) on 2026-11-18.

## Southern half (second batch, same day)

Method and decisions: `docs/hammarlandsvagen-south.md`.
- **Dated from 1929:** the old road east from Söderby to Mattas (Östanträskvägen, Furubacksvägen, Brobackavägen
  and Södersundavägen; 9 existing objects).
- **Dated from 1928:** Utängsvägen, and Natbacken–Sagalund on today's road.
- **Unchanged:** the Gottby straight and Ödanböle–Söderby, which are later. The pink Ödanböle line on the 1929 sheet
  is a hand addition.
- **Review data:** `data/hammarlandsvagen-south.json`, written by `scripts/prepare_south.py` from
  `data/map-scan-cache/review/hammarlandsvagen-main-road/before-south.json.gz`.
- **Scope:** `scope-audit-south.json` lists 11 objects changed and 11 geometries and 4 sources added. Nothing else
  changed.
- **Tests:** new `tests/hammarlandsvagen-south.test.cjs` and `tests/test_hammarlandsvagen_south.py`.
- **`batch-south.patch`:** `scripts/build_temporal_objects.py` (the hook and the asset copy), `dist/index.html`
  (the card "De äldre vägarna mot Hammarland" and the regenerated preview) and `tests/qgis-roads.test.cjs` (reads the
  review's earlier start from the object). See `patch-verification-south.log`.
- **Runs:** all 586 JS tests pass (`logs/js-tests-south.log`). The south, north and QGIS reconciliation Python tests
  pass (36 tests).
