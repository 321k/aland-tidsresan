# Mariehamn buildings b6–b8 (the centre, Södra and along Slemmern) — 2026-11-13

Three more areas are dated from the house symbols on sheet 101208, with the same tile and contact-sheet review as
b1–b5. Method, rules and totals are in `docs/mariehamn-building-maps.md` (section *The centre*); earlier records are
`docs/reviews/mariehamn-building-maps-2026-11-12` (b1), `…-b2b3-2026-11-12` and `…-b4b5-2026-11-12`.

- **b6**, 19.9255–19.946° E × 60.0915–60.100° N: Södra and the southern centre. 43 houses: 26 from 1968 (9 with
  1985 *unclear*) and 17 from 1995; 32 proposals rejected.
- **b7**, 19.9255–19.946° E × 60.100–60.109° N: the northern centre. 18 houses: 10 from 1968, 3 from 1985 and 5 from
  1995; 13 rejected.
- **b8**, 19.946–19.962° E × 60.0915–60.109° N: the strip east of the centre along Slemmern. 4 houses from 1968;
  4 rejected.

752 Mariehamn houses are map-dated in all.

## Printed-symbol objects

The centre already holds 615 `map-building:nls-symbol-*` objects (`printedMapSymbol`) that show houses from the 1985
edition of the same sheet. They take part in the matching, so each uses up the symbol it stands on, and the curated
rule keeps them from being map-dated. None of the 65 dated outlines comes within 3 m of any period of a symbol object.
The compiler now also refuses the whole review if a dated outline overlaps a symbol object by more than 5 m² or
contains its centre (`rules.symbolObjectOverlapSquareMeters`); `tests/test_mariehamn_building_maps.py` adds an
overlapping symbol object and checks that the catalogue stays unchanged.

## Hatched 1968 blocks

The 1968 edition draws the centre's blocks hatched as built-up area. A symbol detected inside the hatching cannot be
told from it, so 8 such 1968 proposals were rejected with the new reason `hatched-block`. They keep their previous
start rather than 1985, because the hatched drawing could already include them. The other 41 rejections are partial
overlaps, empty outlines, elevation figures or lettering over the previous edition, circle-symbol lines and a pier.
`scripts/zoom.py` renders the 1968 | 1985 | 1995 close-ups used for the hatched cells.

## What is committed directly

- `data/mariehamn-building-maps.json` and its copy in `dist/assets/`: 752 decisions with b1–b8. The 687 earlier
  decisions and 153 earlier rejections are identical.
- `scripts/mariehamn_building_maps.py`: the symbol-object overlap check.
- `tests/mariehamn-building-maps.test.cjs`: new totals, the `hatched-block` reason and a no-overlap check against
  every symbol-object period; `tests/test_mariehamn_building_maps.py`: the overlap rejection;
  `tests/test_mariehamn_frame_1942.py`: its pre-frame snapshot predates b6–b8, so it leaves those 65 buildings out
  and compares everything else exactly.
- `docs/mariehamn-building-maps.md`: b6–b8, the centre section, the updated table and the next batches.

## What is in `batch.patch`

`dist/index.html`: the loader card "Hus i Mariehamns centrum" and the renumbered cards, chained on the 1942 frame
review's post-patch state (`patch-verification.log`).

## Evidence and checks

- `sheets/`: tile review sheets; `contact/`: per-proposal contact sheets (`-1968` for 1968 starts, `-later` for
  1985/1995); `data/`: verdicts, fills, ink, overrides and contact indexes; `scripts/`: the review tools.
- `scope-audit.json`: against the previous publication exactly the 65 b6–b8 buildings changed; geometries, city
  stages and sources are unchanged.
- `logs/`: 500 of 500 JS tests and the affected Python tests.
- `publication/`: deployed as Cloudflare version 7feadf31 from the live release plus only this batch; 292 files
  matched live byte for byte.
