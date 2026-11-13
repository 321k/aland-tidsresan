# Centre symbol houses from the 1968 map — 2026-11-13

125 of the centre's printed-map symbol objects (`map-building:nls-symbol-*`), which started at the 1985 edition's
survey year 1983 (two at 1982), are now shown from 1968: the same house symbol stands on the 1968 edition of sheet
101208. Method, selection and compiler checks are in `docs/mariehamn-symbols-1968.md`.

| step | objects |
|---|---|
| 1968 symbol matched one-to-one in the b6–b8 matching, start after 1968 | 412 |
| outside the 1968 built-up area objects (`printedMapArea`) | 244 |
| hatched surroundings on the 1968 scan (dark share > 0.40 or stripe density > 0.22) | 86 left out |
| checked on the contact sheets | 158 |
| rejected (28 partial overlaps, 3 hatched blocks, 1 empty outline, 1 lettering) | 33 |
| **dated from 1968** | **125** (87 in b7, 38 in b6) |

The 1968 edition draws the centre's blocks hatched as built-up area; houses inside it are left at their 1985 start,
because single houses cannot be told from the hatching.

## What is committed directly

- `scripts/mariehamn_symbols_1968.py`: the new last build step; validates everything before changing the catalogue.
- `data/mariehamn-symbols-1968.json` and its copy in `dist/assets/`: 125 decisions, the 86 hatched objects and the
  33 rejections with reasons and contact-sheet cells.
- `tests/mariehamn-symbols-1968.test.cjs`, `tests/test_mariehamn_symbols_1968.py`: new regression checks (the
  Python tests use the pre-step snapshot `symbols-before.json.gz` in the review cache and skip without it).
- `tests/test_mariehamn_building_maps.py`, `tests/test_mariehamn_frame_1942.py`: apply the new step after theirs
  before comparing with the build.
- `docs/mariehamn-symbols-1968.md`; `docs/mariehamn-building-maps.md` points to it.

## What is in `batch.patch`

Files that are untracked or carry other uncommitted work (`patch-verification.log`):

- `scripts/build_temporal_objects.py`: calls `apply_symbols_1968` after the 1942 street review and copies the review
  to `dist/assets`.
- `dist/index.html`: the loader card "Centrums hus redan 1968" and the renumbered cards.
- `tests/test_reported_buildings_17_18.py`: also leaves out the new review source before comparing. Without it the
  first test run hung for 40 minutes: the comparison failed and unittest tried to print a diff of the whole catalogue.

## Evidence and checks

- `contact/`: the contact sheets; `data/`: candidates (with the hatched objects and their measures) and overrides;
  `scripts/`: `sym_prepare.py` (selection, hatching measure, contact sheets) and `sym_review.py` (writes the review).
- `scope-audit.json`: against the previous publication exactly the 125 objects changed, one source was added, and
  geometries and city stages are unchanged.
- `logs/`: 504 of 504 JS tests and the affected Python tests.
- `publication/`: deployed as Cloudflare version 9f58c3ba from the live release plus only this batch; 293 files
  matched live byte for byte.
