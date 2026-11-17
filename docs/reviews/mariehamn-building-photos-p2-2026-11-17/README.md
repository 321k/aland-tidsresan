# Mariehamn buildings dated from the orthophotos: p2 (the western strip) — 2026-11-17

The seventh photo-dating batch. Buildings with no symbol on the 1968–1995 base maps (`absent` in the building-map
review) in the western strip from Klinten and the yard (Varv) past Notgrundet (building-map batch b2) were drawn on
Mariehamn's 1991, 1999, 2007 and 2015 orthophotos (1 m/px) and judged by eye. Method, model changes and compiler
checks: `docs/mariehamn-building-photos.md`.

| result | buildings |
|---|---|
| first seen on 1991 | 6 |
| first seen on 1999 | 6 |
| first seen on 2007 | 51 |
| first seen on 2015 | 37 |
| deferred: not on any photo (built after 2015), unclear, overlapping another outline, or under 40 m² | 69 |
| deferred: the 1985 (1995) map may already draw it (map ink guard; 2 by dark share, 8 by eye) | 10 |
| deferred: its start (2012) is not after the first photo year (2015) | 1 |

## New: visual map check

Every building first seen on 1991 or 1999 was also drawn on the 1985 (1995) map crop and inspected
(`sheets/p2-guard-maps.jpg`, enlarged with the 1978 map in `sheets/p2-guard-zoom.jpg`). The dark-share guard
measures only filled ink, so it passed three yard buildings whose outlines contain an open or hatched symbol on the
1985 map: the halls `building:osm:way-165914218` (1,143 m²) and `way-165914225` (2,516 m²) and the shed
`way-165914206`, plus `way-584481413`. Four more touch a symbol closely enough that the registration cannot rule it
out. These eight are listed in `data/p2-visual.json`, and `guard.py` now defers such listed buildings
(`scripts/guard.py.diff`; no visual list exists for the earlier batches, whose results are unchanged). The halls are
`absent` in the building-map review although the map draws them; that matching should be revisited for hatched
symbols (noted as open in the method document).

Buildings whose outline overlaps another building object (sheet indices 62–66, 71, 72) were left undated, as in p6
and p7. The photo year is first evidence, not a construction year.

## What is committed directly

- `data/mariehamn-building-photos.json` and its copy in `dist/assets/`: the decisions of all batches, now with p2.
  The 535 earlier decisions are byte-identical to the previous file.
- `tests/mariehamn-building-photos.test.cjs`: new totals and a test that the eight visually deferred buildings stay
  undated.
- `tests/test_mariehamn_building_maps.py`, `tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_symbols_1968.py`,
  `tests/test_mariehamn_museum_duplicates.py`, `tests/test_mariehamn_museum_offsets.py`: 100 more photo-dated
  buildings left out of their snapshot comparison.
- `docs/mariehamn-building-photos.md`: batch table, the visual check and the open building-map item.

## What is in `batch.patch`

`dist/index.html` (loader card "Västra stranden från flygfotona", the regenerated loader preview and cache stamps),
which also holds other uncommitted work. See `patch-verification.log`. The generated catalogue and the cache stamps in
the untracked `dist/object.html` and `dist/temporal-objects.js` are rebuilt from the committed review, as before.
The guard change lives in the ignored review cache; `scripts/guard.py` here is the new version and
`scripts/guard.py.diff` the change.

## Evidence and checks

- `sheets/p2-NN.jpg`: every building on the four photos; `data/`: the building list, decisions by sheet index, the
  map ink guard and the visual deferrals. The tiles stay in the review cache; their sha256 values are in the review.
- `scope-audit.json`: against the catalogue before this batch, exactly the 100 p2 buildings changed; no geometry,
  source or city-stage changes.
- `logs/`: 522 of 522 JS tests; the affected Python tests pass.
- `publication/`: deployed as Cloudflare version adebefe4 on top of 499222f1; 297 files matched live byte for byte.
