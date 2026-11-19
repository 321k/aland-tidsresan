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

## The Marsund connection at Marby and Kyrkoby (sixth batch, 2026-11-19)

Method and decisions: `docs/hammarlandsvagen-marsund.md`.
- **Dated from 1929:** two stretches of "Eckerö–Hammarland · Marsundsförbindelsen", where today's road is the old road
  on the 1929 Eckerö parish map and its 1956 edition:
  - Marby, 5.70–6.04 km from Frebbenby
  - Överby–Kyrkoby, 7.08–8.22 km
- **Unchanged:** the rest stays 1959, the bridge assumption. Through Överby village the old road ran north of today's
  bypass and is not yet in the catalogue.
- **Build step:** `_apply` gains `pathRanges` and `pathOrder`, for cuts on an object of several paths.
- **Evidence:** `renders/marsund-*.jpg`, `marsund-close-*.jpg` and `result-marsund-1950.jpg`.
  `data/marsund-reference.json` is the object as one line; `scripts/kattby_windows.py` takes it as `REF`.
- **Scripts:** `prepare_marsund.py`.
- **Snapshot:** `before-marsund.json.gz`, the catalogue as deployed after the atlas fix. The review data is written from
  it, and the Python test replays the step on it (the build with the step disabled is the same).
- **Scope:** `scope-audit-marsund.json`:
  - changed: 1 object
  - added: 1 geometry and 1 source (the review)
  - 4 replacement intervals added on `atlas-1894-1` (`dist/assets/historical-roads.json` rebuilt)
  - nothing else changed.
- **Tests:**
  - new: `tests/hammarlandsvagen-marsund.test.cjs` and `tests/test_hammarlandsvagen_marsund.py`. Each rejection is
    checked for its stated reason.
  - updated: `tests/marsund-road-continuity.test.cjs`. Before 1959 the connection now draws the two stretches, not
    nothing.
- **`batch-marsund.patch`:**
  - `scripts/build_temporal_objects.py`: the hook and the asset copy
  - `dist/index.html`: the card "Landsvägen genom Eckerö från 1929" and the preview
  - `dist/assets/historical-roads.json`
  - `tests/marsund-road-continuity.test.cjs`

  See `patch-verification-marsund.log`.
- **Runs:**
  - All 603 JS tests pass (`logs/js-tests-marsund.log`).
  - The Marsund, atlas, Hammarlandsvägen (all four), regional review, atlas continuity and dating, Marsund continuity
    and road date assumption Python tests pass, 34 tests (`logs/python-tests-marsund.log`).

## The old road through Överby (seventh batch, 2026-11-19)

Method and decisions: `docs/hammarlandsvagen-overby.md`.
- **New object:** "Gamla landsvägen · Överby", open from 1929.
  - 1929–1985, the main road: its two loops north of today's road.
  - From 1985: the parts that survive as Brinkbacken and Gamla Landsvägen, which it owns in OSM.
- **Marsund connection:**
  - its 1929 period gains 6.30–6.43 km (`prepare_marsund.py`)
  - its 1959 period is split: until 1985 it leaves out the Överby bypass, which is first drawn as a road on the 1985
    base map (1978: an uncased overprint)
- **Evidence:** `renders/overby-*.jpg` and `result-overby-1950-1975-1990.jpg`; `data/trace-overby-1929.json`.
- **Scripts:** `grid_window.py`, `overby_trace.py`, `overby_base_maps.py`, `overby_loops.py`, `prepare_overby.py`.
- **Snapshots:**
  - `before-overby.json.gz`: the catalogue as deployed after the Marsund batch
  - `before-overby-step.json.gz`: the catalogue built with this step disabled; the review data is written from it,
    and the Python test replays the step on it
  - `overby-before/`: the patched files before this batch
- **Scope:** `scope-audit-overby.json`:
  - added: 1 object, 3 geometries and 2 sources (the review and the OSM survey)
  - changed: the Marsund object and its 1929 cut geometry
  - 19 replacement intervals added on `atlas-1894-1`, none removed
  - nothing else changed.
- **Tests:**
  - new: `tests/hammarlandsvagen-overby.test.cjs` and `tests/test_hammarlandsvagen_overby.py`. Each rejection is
    checked for its stated reason. One of them found a missing check, now fixed: a map marked absent before 1985 was
    not rejected.
  - updated:
    - `tests/hammarlandsvagen-marsund.test.cjs`, `tests/test_hammarlandsvagen_marsund.py`: three stretches, and the
      whole line from 1985
    - `tests/marsund-road-continuity.test.cjs`: the bypass-free geometry in 1959–1984
    - `tests/temporal-objects.test.cjs`: counts the new object
    - `tests/test_hammarlandsvagen_atlas.py`: its snapshot predates the Överby link, so that link is left out of its
      replay
- **`batch-overby.patch`:**
  - `scripts/build_temporal_objects.py`: the hook and the asset copy
  - `data/regional-road-review.json`: the atlas link
  - `dist/assets/historical-roads.json`
  - `dist/index.html`: the card "Gamla landsvägen genom Överby" and the preview
  - `tests/marsund-road-continuity.test.cjs` and `tests/temporal-objects.test.cjs`

  See `patch-verification-overby.log`.
- **Runs:**
  - All 606 JS tests pass (`logs/js-tests-overby.log`).
  - The Överby, Marsund, atlas, Hammarlandsvägen (all four), regional review, atlas continuity and dating, Marsund
    continuity and road date assumption Python tests pass, 37 tests (`logs/python-tests-overby.log`).

## The road to the Marsund ferry (eighth batch, 2026-11-19)

Method and decisions: `docs/hammarlandsvagen-frebbenby.md`.
- **Dated from 1929:**
  - the Marsund connection through Frebbenby, 0–0.47 km (`prepare_marsund.py`)
  - Marsundsvägen from Frebbenby to the old ferry pier, its first 1 040 m (it was dated from 1994)
- **Build step:** `_path_cuts` allows a whole path under 50 m inside a longer stretch.
- **Evidence:** `renders/marsundsvagen-*.jpg`, `frebbenby-grid-*.jpg` and `result-frebbenby-1950.jpg`.
  `data/marsundsvagen-reference.json` is Marsundsvägen as one line.
- **Scripts:** `prepare_frebbenby.py` and `marsundsvagen_base_maps.py`. `prepare_overby.py` now finds its join points
  by distance along the connection, because the Marsund cuts gained three paths at the front.
- **Snapshots:**
  - `before-frebbenby.json.gz`: the catalogue as deployed after the Överby batch
  - `before-frebbenby-step.json.gz`: the catalogue built with this step disabled; the Python test replays the step on
    it
  - `before-overby-step.json.gz`: rebuilt with the changed Marsund review. Only the Överby data's input fingerprint
    changed.
- **Scope:** `scope-audit-frebbenby.json`:
  - changed: Marsundsvägen, and the Marsund object and its 1929 cut geometry
  - added: 1 geometry and 1 source (the review)
  - 3 replacement intervals added on `atlas-1894-1`, none removed
  - nothing else changed.
- **Tests:**
  - new: `tests/hammarlandsvagen-frebbenby.test.cjs` and `tests/test_hammarlandsvagen_frebbenby.py`. Each rejection is
    checked for its stated reason.
  - updated: `tests/hammarlandsvagen-marsund.test.cjs`, `tests/test_hammarlandsvagen_marsund.py` and
    `tests/marsund-road-continuity.test.cjs` (four stretches, eight cuts).
- **`batch-frebbenby.patch`:**
  - `scripts/build_temporal_objects.py`: the hook and the asset copy
  - `dist/assets/historical-roads.json`
  - `dist/index.html`: the card "Vägen till Marsundsfärjan" and the preview
  - `tests/marsund-road-continuity.test.cjs`

  See `patch-verification-frebbenby.log`.
- **Runs:**
  - All 608 JS tests pass (`logs/js-tests-frebbenby.log`).
  - The Frebbenby, Överby, Marsund, atlas, Hammarlandsvägen (all four), regional review, atlas continuity and dating,
    Marsund continuity, road date assumption and QGIS road reconciliation Python tests pass, 70 tests
    (`logs/python-tests-frebbenby.log`).

## The road from the ferry to Marby (ninth batch, 2026-11-19)

Method and decisions: `docs/hammarlandsvagen-ferry-west.md`.
- **Dated from 1929:**
  - the Marsund connection over the narrow sound, 3.69–3.88 km (`prepare_marsund.py`)
  - Marbyvägen, 200–2 000 m (from 1929), and from 200 m to its north end (from 1956)
  - new objects: "Gamla landsvägen · Sundkvist" (1929–1968) and "Gamla landsvägen · strandvägen vid
    Holmbergssundet" (1929–1956)
- **Build step:** `laterStage`, a second early period from a later map.
- **Atlas review:** Marbyvägen and the two new objects are late links.
- **Snapshots:**
  - `before-ferry-west.json.gz`: the catalogue as deployed after the Frebbenby batch
  - `before-marby-step.json.gz` and `before-shore-step.json.gz`: the catalogue built with each step disabled
  - `before-overby-step.json.gz`: rebuilt for the changed Marsund review. Only the Överby data's input fingerprint
    changed.
- **Scope:** `scope-audit-ferry-west.json`:
  - added: 2 objects, 4 geometries and 2 sources
  - changed: the Marsund object and its 1929 cut geometry, and Marbyvägen
  - 5 replacement intervals added on `atlas-1894-1`, none removed
  - nothing else changed.
- **Tests:**
  - new: `tests/hammarlandsvagen-ferry-west.test.cjs` and `tests/test_hammarlandsvagen_ferry_west.py`. Each rejection
    is checked for its stated reason; two meaningless mutations (a reversed route, which the check rightly accepts)
    were replaced.
  - updated:
    - the Marsund tests: five stretches
    - `tests/marsund-road-continuity.test.cjs`: the schematic crossing kept until 1959 is now checked at atlas
      vertex 8, the sound. Vertex 6, at Marby, is replaced from 1929 by the dated road.
    - `tests/temporal-objects.test.cjs`: counts the two new objects
    - `tests/test_hammarlandsvagen_atlas.py`: replays only its own two late links
- **`batch-ferry-west.patch`:**
  - `scripts/build_temporal_objects.py`: the two hooks and asset copies
  - `data/regional-road-review.json`: the three late links
  - `dist/assets/historical-roads.json`
  - `dist/index.html`: the card "Landsvägen från färjan till Marby" and the preview
  - `tests/marsund-road-continuity.test.cjs` and `tests/temporal-objects.test.cjs`

  See `patch-verification-ferry-west.log`.
- **Runs:**
  - All 610 JS tests pass (`logs/js-tests-ferry-west.log`).
  - The ferry-west, Frebbenby, Överby, Marsund, atlas, Hammarlandsvägen (all four), regional review, atlas continuity
    and dating, Marsund continuity, road date assumption and QGIS road reconciliation Python tests pass, 74 tests
    (`logs/python-tests-ferry-west.log`).

## Holmberg and Öravägen (tenth batch, 2026-11-19)

Method and decisions: `docs/hammarlandsvagen-holmberg.md`.
- **New objects:**
  - "Gamla landsvägen · Holmberg", 1929–1956: the road from the narrow sound to the ferry pier
  - "Öravägen", from 1956, from its OSM way, owned in the 2014–2026 extracts
- **Build step:** `freeEnds` for an old road's pier end. `apply_hammarlandsvagen_holmberg` checks the new OSM-based
  object first, then runs `_apply` for the old road.
- **Evidence:** `renders/holmberg-road-*.jpg` and `result-holmberg-1950-1957-1970.jpg`.
- **Snapshots:** `before-holmberg.json.gz` and `before-holmberg-step.json.gz` are the same here, the catalogue as
  deployed after the ferry-west batch.
- **Scope:** `scope-audit-holmberg.json`:
  - added: 2 objects, 2 geometries and 2 sources (the review and the OSM survey)
  - nothing else changed; the roads file is unchanged.
- **Tests:**
  - new: `tests/hammarlandsvagen-holmberg.test.cjs` and `tests/test_hammarlandsvagen_holmberg.py`. Each rejection is
    checked for its stated reason.
  - updated: `tests/temporal-objects.test.cjs` counts the two new objects.
- **`batch-holmberg.patch`:**
  - `scripts/build_temporal_objects.py`: the hook and the asset copy
  - `dist/index.html`: the card "Vägen över Holmberg till färjan" and the preview
  - `tests/temporal-objects.test.cjs`

  See `patch-verification-holmberg.log`.
- **Runs:**
  - All 612 JS tests pass (`logs/js-tests-holmberg.log`).
  - The Holmberg, ferry-west, Frebbenby, Överby, Marsund, atlas, Hammarlandsvägen (all four), regional review,
    atlas continuity and dating, Marsund continuity, road date assumption and QGIS road reconciliation Python tests
    pass, 77 tests (`logs/python-tests-holmberg.log`).
