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

## Näfsby (third batch, same day)

Method and decisions: `docs/hammarlandsvagen-nafsby.md`.
- **Dated from 1929:** the old road through Näfsby, on five existing objects:
  - Lillåkersgränd (its northern 85 m)
  - way 1419026567 (then unknown 1968–1985)
  - way 1419026568
  - the old school road and its east part
- **New object:** "Gamla Hammarlandsvägen · Näfsby", for the two vanished pieces.
- **Västmyra:** its first 1929 cut now runs to 14 420 m (`prepare.py`: `nafsby-south` moved from 14 313).
- **Evidence:**
  - `renders/nafsby-village.jpg` and `nafsby-village-south.jpg`: 1929, 1944, 1968 and 1985
  - `renders/nafsby-village-1968-1985.jpg`: the parallel stretch on the base maps
  - `renders/nafsby-klaralund-*.jpg` and `nafsby-south-*.jpg`: the 1929 line with OSM 2026
  - `renders/result-nafsby-1950-on-1929.jpg` and `result-nafsby-1975-on-1968.jpg`: what the map draws
- **Scripts:** `village_window.py`, `trace_osm_window.py`, `drawn_in_year.py`, `prepare_nafsby.py`.
- **Review data:** `data/hammarlandsvagen-nafsby.json`, written from
  `data/map-scan-cache/review/hammarlandsvagen-main-road/before-nafsby.json.gz`.
- **Snapshots:** the Python test replays the step on `before-nafsby-step.json.gz`, the catalogue built with the step
  disabled.
- **Scope:** `scope-audit-nafsby.json`, compared with the catalogue before this batch:
  - added: 1 object, 6 geometries and 1 source
  - changed: 6 objects (the five above and Västmyra) and Västmyra's 1929 cut geometry
  - nothing else changed; no city stage changed.
- **Tests:**
  - new: `tests/hammarlandsvagen-nafsby.test.cjs` and `tests/test_hammarlandsvagen_nafsby.py`. Each rejection was
    checked to fail for its stated reason.
  - updated: `tests/temporal-objects.test.cjs` counts the new object.
- **`batch-nafsby.patch`:**
  - `scripts/build_temporal_objects.py`: the hook and the asset copy
  - `dist/index.html`: the card "Den gamla vägen genom Näfsby" and the regenerated preview
  - `tests/temporal-objects.test.cjs`

  See `patch-verification-nafsby.log`.
- **Runs:**
  - All 596 JS tests pass (`logs/js-tests-nafsby.log`).
  - The Näfsby, south, north, QGIS reconciliation and rural road phase/replacement Python tests pass, 60 tests
    (`logs/python-tests-nafsby.log`).

## Kattby westwards (fourth batch, same day)

Method and decisions: `docs/hammarlandsvagen-kattby.md`.
- **Dated from 1929:** "Hammarlandsvägen · Kattby västerut", the whole object. It was shown from 1959 only by the
  Marsund bridge assumption.
- **Sources:** the parish maps of sheet 1012 03 Eckerö, 1929 and 1956, are added as the review's sources.
- **Evidence:**
  - `renders/kattby-west.jpg`: the Hammarby sheets end west of the church
  - `renders/kattby-west-eckero.jpg`, `kattby-west-close-*.jpg`: the Eckerö sheets
  - `renders/result-kattby-1950.jpg`: what the map draws in 1950
- **Scripts:** `kattby_windows.py`, `prepare_kattby.py`.
- **Snapshots:**
  - `before-kattby.json.gz`: the catalogue before this batch; the review data is written from it.
  - `before-kattby-step.json.gz`: the catalogue built with the step disabled; the Python test replays the step on it.
- **Scope:** `scope-audit-kattby.json`:
  - changed: 1 object
  - added: 1 geometry and 3 sources (the review and the two Eckerö maps)
  - nothing else changed.
- **Tests:**
  - new: `tests/hammarlandsvagen-kattby.test.cjs` and `tests/test_hammarlandsvagen_kattby.py`. Each rejection was
    checked to fail for its stated reason.
  - updated: `tests/marsund-road-continuity.test.cjs` (Kattby west now has its 1929 period before 1959) and
    `tests/rural-map-review.test.cjs` (for an assumed date, this review's first period is now the second).
- **`batch-kattby.patch`:** `scripts/build_temporal_objects.py`, `dist/index.html` (the card "Hammarlandsvägen väster
  om Kattby från 1929" and the preview), `tests/marsund-road-continuity.test.cjs` and `tests/rural-map-review.test.cjs`. See
  `patch-verification-kattby.log`.
- **Runs:**
  - All 599 JS tests pass (`logs/js-tests-kattby.log`).
  - The Kattby, Näfsby, south, north, Marsund continuity, road date assumption and QGIS reconciliation Python tests
    pass, 49 tests (`logs/python-tests-kattby.log`).

## The 1894 atlas line (fifth change, same day)

Method and decisions: `docs/hammarlandsvagen-main-road.md`, "Also fixed: the 1894 atlas line beside the 1929 road".
- **Problem:** between Kattby and Smedens, the schematic 1894 atlas line was drawn in 1929–1967 beside the old road
  dated by the four batches above (`renders/atlas-1894-in-1950.jpg`).
- **Fix:**
  - `data/regional-road-review.json` names the old Smedens and Näfsby lines and the five Näfsby objects.
  - `scripts/regional_road_review.py` takes `links='early'|'late'|'all'`.
  - `scripts/build_temporal_objects.py` runs the review early, and again late after the Kattby step.
  - `dist/assets/historical-roads.json` is rebuilt with `scripts/build_historical_roads.py`.
- **Snapshots:** in `data/map-scan-cache/review/hammarlandsvagen-main-road/`: `before-atlas.json.gz` (the
  catalogue as deployed after the Kattby batch) and `atlas-before/` (the files before this change).
- **Scope:** `scope-audit-atlas.json`:
  - 23 replacement intervals added on `atlas-1894-1`, none removed
  - 7 objects gain one `regional-context` evidence each
  - nothing else changed.
- **Tests:**
  - new: `tests/hammarlandsvagen-atlas.test.cjs` (the drawn atlas line by year; it fails on the old roads file for
    both stated reasons) and `tests/test_hammarlandsvagen_atlas.py` (the early/late split, replayed on the snapshot).
  - updated: the replay comparisons in `tests/test_hammarlandsvagen_main_road.py` and
    `tests/test_hammarlandsvagen_nafsby.py` leave out the atlas review's evidence, which another step adds.
- **`batch-atlas.patch`:** `scripts/build_temporal_objects.py`, `scripts/regional_road_review.py`,
  `data/regional-road-review.json`, `dist/assets/historical-roads.json` and `dist/index.html` (the card "Atlasens
  väg 1894 ersatt längs Hammarlandsvägen" and the preview). See `patch-verification-atlas.log`.
- **Runs:**
  - All 601 JS tests pass (`logs/js-tests-atlas.log`).
  - The atlas, Hammarlandsvägen (all four), regional review, atlas continuity and dating, Marsund continuity and
    road date assumption Python tests pass, 32 tests (`logs/python-tests-atlas.log`).
  - `tests/test_emkarby_road_continuity.py` has one failure, the same before this change ("Changed applied
    Emkarby review" is raised where "shared road" is expected). It is not part of this batch.
