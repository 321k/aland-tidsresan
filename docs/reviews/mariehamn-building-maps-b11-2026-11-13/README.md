# Mariehamn buildings b11 (Dalen and Espholm) — 2026-11-13

The last unreviewed part of Mariehamn's built-up area: the peninsula south of Lervik and Ytternäsfjärden,
19.948–19.966° E × 60.060–60.0725° N, with Dalen and Espholm (`images/dalen-espholm-1985.jpg`). Espholm is listed as
a Mariehamn district on the town's map (mariehamn.ax); Svinö to the west and Nåtö and Järsö to the south belong to
Lemland (a planned transfer of Järsö and Nåtö to Mariehamn has not taken effect) and are not reviewed.

Same matching, tile sheets and contact sheets as b1–b10. The peninsula is sparsely built: 96 buildings, 19 proposals,
16 rejected on the contact sheets (partial overlaps and empty outlines beside the house), 3 dated (2 from 1985, 1 from
1995). All three are modern-only outlines and get a created reconstruction like the Ytternäs ones. The 9
`earlier-unclear` and 5 `inconsistent` buildings here are deferred. 1284 Mariehamn houses are map-dated in all.

## What is committed directly

- `data/mariehamn-building-maps.json` and its copy in `dist/assets/`: 1284 decisions with b11.
- `tests/mariehamn-building-maps.test.cjs`: new totals, b11 in the sheet checks, and the modern-only test widened to
  b11; `tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_symbols_1968.py`,
  `tests/test_mariehamn_museum_duplicates.py`, `tests/test_mariehamn_museum_offsets.py`: also leave b11 out of their
  snapshot comparison.
- `docs/mariehamn-building-maps.md`: b11 and the boundary note.

## What is in `batch.patch`

`dist/index.html`: the loader card "Dalen och Espholm", chained on the previous patch.

## Evidence and checks

- `sheets/`, `contact/`, `data/` (verdicts, fills, ink, overrides, contact indexes).
- `scope-audit.json`: exactly the 3 b11 buildings changed against the previous publication.
- `logs/`, `publication/`: 514 of 514 JS tests and the affected Python tests; deployed as Cloudflare version
  14800de6, 295 files matched live byte for byte.
