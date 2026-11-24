# Main roads on the base maps, batch 5: roads that grow over time

Part of the main-road survey (`docs/reviews/main-roads-2026-11-23/README.md`).

Build step: `apply_main_roads_growing` in `scripts/main_roads_growing.py`, after the Sviby paths step.

Review data: `data/main-roads-growing.json` (copied to `dist/assets/`), written by
`docs/reviews/main-roads-2026-11-23/scripts/prepare_growing.py`.

## Why these roads were left out

The Hammarland rural review gave its road objects (`road:rural:hammarland-*`) several geometry periods. The early
periods hold only what that review read on its own sheet, 1012 06. The rest of today's line appears only when the
OSM extract has it whole (2014–2025).

The review's evidence says so: only the part inside the sheet it read is used. The rest of these roads, on the
neighbouring sheets, was never reviewed. Batch 1's helper only handles objects with one period, so batches 1–3 left
these out.

## Method

- **Matching** (`scripts/match_growing.py`, output `batch5-growing.json`):
  - Along each object's latest geometry (today's line), the red main-road symbol is read within 12 m on every
    edition of every registered sheet except those the earlier review read.
  - The ranges follow batch 1's rules: gaps up to 100 m are bridged and pieces under 150 m are dropped.
  - Pieces within 5 m of the object's own early geometry are left out, and so are pieces along another road open
    that year.
- **Checking by eye:** `renders/b5-*.jpg`.
- **The step:**
  - Each early period keeps its own paths. The stretches of today's line in force from its start are added after
    them, as pieces of the latest geometry with their own coordinates.
  - A later stage starts a new period at its year.
  - States, source links and the latest geometry are not changed.
  - Map years are first evidence, not construction years.

## Result

| road | sheets | added from | m |
|---|---|---|---|
| Svartsmaravägen | 1021 04 | 1968 | 4,060 |
| Skarpnåtövägen · södra delen | 1021 04 | 1968; 1984 | 2,130; 3,850 from 1984 |
| Ringsbölevägen | 1012 09 | 1968 | 2,170 |
| Bovikvägen · östra delen | 1012 03, 1021 01 | 1968 | 1,220 |
| Tellholmsvägen | 1012 03 | 1968 | 1,160 |

Main road not covered at the first edition, all sheets: 154.9 → 143.9 km.

**Changed tests:**
- `tests/rural-map-review.test.cjs` (untracked, in the patch): the Erssons test. The review's own three paths,
  with the old bend, stay first and unchanged. Any further paths must come from this review.
- `tests/startup-loader.test.cjs`: the loader preview was regenerated.

## Open items

- **Old curves to trace on the 1968 map:**
  - Svartsmaravägen at Svedals, Hammarbacka, Fågelholm and Breidablick–Strömsvik;
  - Skarpnåtövägen at Norrgård;
  - Bovikvägen at Furulund.
- **Later stages not taken:**
  - Ringsbölevägen 1985 (470 m);
  - Bovikvägen 1978 (230 m);
  - Svartsmaravägen 1993.
- **Jomala Torpvägen:** its match crosses a blank sheet margin, and it sits about 20 m off at Boskas.
- **Other growing objects with older periods** (Torpvägen at Kattby, Södersundavägen, Norra Torpvägen, Norrbygatan,
  Hammarlandsvägen) have detailed old-road reviews and are left to them.
