# Mariehamn buildings dated from the orthophotos: p4 (Övernäs) — 2026-11-16

The third photo-dating batch. Buildings with no symbol on the 1968–1995 base maps (`absent` in the building-map
review) in Övernäs (building-map batch b4) were drawn on Mariehamn's 1991, 1999, 2007 and 2015 orthophotos
(1 m/px) and judged by eye, with the same method and scripts as p10 and p9. Method, model changes and compiler
checks: `docs/mariehamn-building-photos.md`.

| result | buildings |
|---|---|
| first seen on 1991 | 17 |
| first seen on 1999 | 3 |
| first seen on 2007 | 10 |
| first seen on 2015 | 49 |
| deferred: not on any photo (built after 2015), unclear, or under 40 m² | 62 |
| deferred: the 1985 map is dark at the outline, so it may already draw the house (map ink guard) | 30 |
| deferred: the photo year is not earlier than the building's current start | 2 |

All 30 map-ink deferrals were seen on the 1991 photo; most are row houses whose 1985 map spot is dark although the
building-map review found no symbol there. They are left for a later map-side review rather than dated from the
photo. Where an earlier photo was ambiguous the building was left undated rather than given a later first year.
With p10 and p9 the review now holds 351 buildings. The photo year is first evidence, not a construction year.

All 79 buildings already had a reconstruction from an OpenStreetMap date; the compiler keeps it as
`reconstruction.previous`.

## What is committed directly

- `data/mariehamn-building-photos.json` and its copy in `dist/assets/` (p10, p9 and p4 decisions, every tile's sha256).
- `tests/mariehamn-building-photos.test.cjs` (new totals); `tests/test_mariehamn_building_maps.py`,
  `tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_symbols_1968.py`,
  `tests/test_mariehamn_museum_duplicates.py`, `tests/test_mariehamn_museum_offsets.py`: 79 more photo-dated
  buildings left out of their snapshot comparison.
- `docs/mariehamn-building-photos.md` (batch table).

## What is in `batch.patch`

`dist/index.html` (loader card "Övernäs från flygfotona") and `tests/temporal-objects.test.cjs` (the
OSM-date-estimate test no longer picks a photo-dated building, as it already skipped map-dated ones). See
`patch-verification.log`.

## Evidence and checks

- `sheets/p4-NN.jpg`: every building on the four photos; `data/`: the building list, decisions by cell and the map
  ink guard. The scripts are unchanged; see `docs/reviews/mariehamn-building-photos-p10-2026-11-13/scripts/`.
- `scope-audit.json`: exactly the 79 p4 buildings changed against the p9 publication; no geometry or source changes.
- `logs/`, `publication/`: JS tests and the affected Python tests; deployed as Cloudflare version a1c55f91,
  296 files matched live byte for byte.
