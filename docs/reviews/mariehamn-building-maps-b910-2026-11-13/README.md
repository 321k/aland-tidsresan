# Mariehamn buildings b9–b10 (Ytternäs) — 2026-11-13

Ytternäs, the district south of Övernäs, is dated from the house symbols on sheet 101208 with the same tile and
contact-sheet review as b1–b8. Method, rules and totals are in `docs/mariehamn-building-maps.md` (section
*Ytternäs*); the previous record is `docs/reviews/mariehamn-building-maps-b678-2026-11-13`.

- **b9**, 19.928–19.950° E × 60.0725–60.0855° N: Västra Ytternäs, south of Lotsberget to Korrvik and Lervik.
  69 houses: 11 from 1968 (3 with 1985 *unclear*), 49 from 1985 and 9 from 1995; 72 proposals rejected.
- **b10**, 19.950–19.972° E × 60.0725–60.0855° N: Östra Ytternäs and the terraced rows of central Ytternäs.
  106 houses: 1 from 1968, 79 from 1985 and 26 from 1995; 51 rejected.

927 Mariehamn houses are map-dated in all. `images/ytternas-1985-overview.jpg` shows the area on the 1985 edition. The
review stops at Lervik and Ytternäsfjärden; the land further south (Dalen, Svinö) was left out because the town
boundary was not checked there.

## Rejections

123 of 391 proposals were rejected on the contact sheets: 68 partial overlaps, 23 empty outlines, 21 cases where the
previous edition already draws something at the outline or black lettering covers it, 6 matches on black lettering
(5 of them the large place-name letters on the 1968 sheet) and 5 on lines. Red lettering and plan figures were not
treated as hiding a house: a dark house symbol stays visible under them.

## Modern-only outlines

93 houses that passed the contact sheets are `externalModern` objects: outlines that exist only in the 2026 OSM
extract, outside the reconstructed city building set, with no `reconstruction` to extend. The compiler refused them
("crosses unreviewed phases"), as it should. `prepare.py` now defers them as `external-modern` instead of writing a
decision, and `tests/mariehamn-building-maps.test.cjs` checks that none is dated and that every dated building has a
reconstruction.

## What is committed directly

- `data/mariehamn-building-maps.json` and its copy in `dist/assets/`: 927 decisions with b1–b10. The 752 earlier
  decisions and 202 earlier rejections are identical.
- `tests/mariehamn-building-maps.test.cjs`: new totals and the `external-modern` check;
  `tests/test_mariehamn_frame_1942.py`: leaves out the 240 b6–b10 buildings that postdate its snapshot.
- `docs/mariehamn-building-maps.md`: b9–b10, the Ytternäs section, the updated table and the next batches.

## What is in `batch.patch`

`dist/index.html`: the loader card "Ytternäs hus från kartorna" and the renumbered cards, chained on the b6–b8
review's post-patch state (`patch-verification.log`).

## Evidence and checks

- `sheets/`: tile review sheets; `contact/`: per-proposal contact sheets; `data/`: verdicts, fills, ink, overrides and
  contact indexes; `scripts/`: the review tools, including `prepare.py` with the `external-modern` deferral.
- `scope-audit.json`: against the previous publication exactly the 175 b9–b10 buildings changed; geometries, city
  stages and sources are unchanged.
- `logs/`: 501 of 501 JS tests and the affected Python tests.
- `publication/`: deployed as Cloudflare version 72d9abb3 from the live release plus only this batch; 292 files
  matched live byte for byte.
