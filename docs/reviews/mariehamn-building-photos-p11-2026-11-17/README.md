# Mariehamn buildings dated from the orthophotos: p11 (Dalen and Espholm) — 2026-11-17

The eighth photo-dating batch. Buildings with no symbol on the 1968–1995 base maps (`absent` in the building-map
review) on the peninsula south of Lervik, Dalen and Espholm (building-map batch b11), were drawn on Mariehamn's 1991,
1999, 2007 and 2015 orthophotos (1 m/px) and judged by eye. Method, model changes and compiler checks:
`docs/mariehamn-building-photos.md`.

| result | buildings |
|---|---|
| first seen on 1991 | 0 |
| first seen on 1999 | 5 |
| first seen on 2007 | 2 |
| first seen on 2015 | 1 |
| deferred: not on any photo (built after 2015), unclear, or under 40 m² (most are allotment cabins) | 48 |
| deferred: a map may already draw it (map ink guard, all 7 by eye) | 7 |

## Visual map check

All 12 buildings first seen on 1991 or 1999 were drawn enlarged on the 1985 (1995) map and, new in this batch, on the
1978 map (`sheets/p11-guard-zoom.jpg`). The dark-share guard deferred none of them. By eye, seven are deferred
(`data/p11-visual.json`):

- an open symbol lies inside the outline on the 1985 map: `building:osm:way-162997265`, `way-162997267`
  (sheet indices 24, 25) and index 54;
- a symbol touches the outline closely enough that the registration cannot rule it out: indices 26 and 38;
- the 1978 map has a filled symbol inside the outline although the 1985/1995 crop has none: indices 28 and 29.
  An earlier map may draw these buildings, so a photo date could be too late.

`guard.py` is unchanged from p2 (it already applies `KEY-visual.json`). The index-to-id mapping is in
`data/p11-guard.json`. Sheet index 2 (a dark shape on 1991, an empty lawn on 2007, a house on 2015) and index 45 (a
2,104 m² outline over an open field on every photo) were left undated. The photo year is first evidence, not a
construction year.

## What is changed in the working tree (not committed)

- `data/mariehamn-building-photos.json` and its copy in `dist/assets/`: the decisions of all batches, now with p11.
  The 635 earlier decisions are byte-identical to the previous file.
- `tests/mariehamn-building-photos.test.cjs`: new totals and the seven p11 buildings in the visual-deferral test.
- `tests/test_mariehamn_building_maps.py` (643), `tests/test_mariehamn_frame_1942.py` (1240),
  `tests/test_mariehamn_symbols_1968.py`, `tests/test_mariehamn_museum_duplicates.py`,
  `tests/test_mariehamn_museum_offsets.py` (1000): 8 more photo-dated buildings left out of their snapshot comparison.
- `docs/mariehamn-building-photos.md`: batch table and the 1978 crop note.

## What is in `batch.patch`

`dist/index.html`: the loader card "Dalen och Espholm från flygfotona" (1 av 67), the regenerated loader preview and
the catalogue cache stamp. The patch is taken against the pre-p11 file with the block-colour change's new
`city-grid.js` stamp already in place, so that stamp is not part of p11. See `patch-verification.log`.

## Evidence and checks

- `sheets/p11-NN.jpg`: every building on the four photos; `data/`: the building list, decisions by sheet index, the
  map ink guard and the visual deferrals. The tiles stay in the review cache; their sha256 values are in the review.
- `scope-audit.json`: against the catalogue before this batch, exactly the 8 p11 buildings changed; no geometry,
  source or city-stage changes.
- `logs/`: 522 of 522 JS tests; the nine affected Python test files pass.
- `publication/`: deployed as Cloudflare version 806d0727 on top of adebefe4, together with the block-colour change in `dist/city-grid.js`; 297 files matched live byte for byte.
