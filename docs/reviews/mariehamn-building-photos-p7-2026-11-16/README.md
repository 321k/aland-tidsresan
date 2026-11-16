# Mariehamn buildings dated from the orthophotos: p7 (Västernäs and the northern centre) — 2026-11-16

The fifth photo-dating batch. Buildings with no symbol on the 1968–1995 base maps (`absent` in the building-map
review) in Västernäs and the northern centre (building-map batch b7) were drawn on Mariehamn's 1991, 1999, 2007 and
2015 orthophotos (1 m/px) and judged by eye. Method, model changes and compiler checks:
`docs/mariehamn-building-photos.md`. Scripts: `docs/reviews/mariehamn-building-photos-p3-2026-11-16/scripts/prepare.py`
and the rest unchanged from `docs/reviews/mariehamn-building-photos-p10-2026-11-13/scripts/`.

| result | buildings |
|---|---|
| first seen on 1991 | 35 |
| first seen on 1999 | 5 |
| first seen on 2007 | 28 |
| first seen on 2015 | 9 |
| deferred: not on any photo, unclear, overlapping outlines, gone by 2015, or under 40 m² | 77 |
| deferred: the 1985/1995 map is dark at the outline, so it may already draw the building (map ink guard) | 8 |
| deferred: an earlier curated review decides its dates | 1 |

Many of the dated buildings are larger commercial and warehouse buildings. Floating houses in the harbour whose
outlines overlap other outlines were left undated. `building:osm:relation-2315517` and
`building:osm:way-162298851` are two objects for the same 713 m² building (identical outlines; sheet cells 0 and 26);
both are left undated and need a duplicate review. The photo year is first evidence, not a construction year.

## What is committed directly

- `data/mariehamn-building-photos.json` and its copy in `dist/assets/` (p10, p9, p4, p3 and p7 decisions).
- `tests/mariehamn-building-photos.test.cjs` (new totals); `tests/test_mariehamn_building_maps.py`,
  `tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_symbols_1968.py`,
  `tests/test_mariehamn_museum_duplicates.py`, `tests/test_mariehamn_museum_offsets.py`: 77 more photo-dated
  buildings left out of their snapshot comparison.
- `docs/mariehamn-building-photos.md` (batch table and the open duplicate).

## What is in `batch.patch`

`dist/index.html` (loader card "Västernäs och norra centrum från flygfotona"). See `patch-verification.log`.

## Evidence and checks

- `sheets/p7-NN.jpg`: every building on the four photos; `data/`: the building list, decisions by cell and the map
  ink guard.
- `scope-audit.json`: exactly the 77 p7 buildings changed against the p3 publication; no geometry or source changes.
- `logs/`, `publication/`: 517 of 517 JS tests and the affected Python tests; deployed as Cloudflare version
  a7d16adc, 296 files matched live byte for byte.
