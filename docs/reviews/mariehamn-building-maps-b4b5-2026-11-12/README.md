# Mariehamn buildings b4/b5 (Övernäs and the Västerhamn shore) — 2026-11-12

Two more areas are dated from house symbols on sheet 101208, with the same tile and contact-sheet review as b2/b3.
Method, rules and totals are in `docs/mariehamn-building-maps.md`; earlier records are
`docs/reviews/mariehamn-building-maps-2026-11-12` (b1) and `…-b2b3-2026-11-12`.

- **b4**, 19.928–19.962° E × 60.0855–60.0915° N: Övernäs, from Lotsberget and the pilot station on Västerhamn to
  Gröna udden, at least 110 m south of the southernmost `printedMapSymbol` object. 112 houses: 78 from 1968 (34 with
  1985 *unclear*: the dense 1985 rows merged in detection, but the 1985 panel of every such cell shows the house),
  20 from 1985 and 14 from 1995. 32 proposals were rejected on the contact sheets.
- **b5**, 19.920–19.9255° E × 60.0925–60.109° N: the Västerhamn shore west of the symbol objects, inside the 1995
  registration (which starts at about 19.918° E here). All 8 proposals were shoreline, quay or lettering matches and
  were rejected, so b5 dates nothing; it is kept so the review is complete.

687 Mariehamn houses are map-dated in all.

Ringvägen 66 (`building:osm:way-498109513`) had 1985 and 1995 symbols, but it is a merged building whose identity,
shape and 2015 start a neighbourhood review decided from aerial photos; the 1985 symbol could be a predecessor.
`neighborhoodReviews` is now a curated review like `historicalReview`, `museumReview` and `printedMapSymbol`: such
buildings are deferred as `curated-review`, and the compiler refuses them. The regression test in
`tests/city-buildings.test.cjs` that pins its 2014 state caught this.

## What is committed directly

- `data/mariehamn-building-maps.json` and its copy in `dist/assets/`: 687 decisions with b1–b5.
- `scripts/mariehamn_building_maps.py`: `neighborhoodReviews` added to the curated reviews.
- `tests/mariehamn-building-maps.test.cjs`: new totals, the b5 rejections and the curated-review list.
- `docs/mariehamn-building-maps.md`: b4, b5 and the updated table.

## What is in `batch.patch`

Only `dist/index.html`: the loader card "Övernäs hus från 1968" and the renumbering to 48. It applies on exactly the
state the b2/b3 `batch.patch` produces; generated preview bins and cache stamps are left out. See
`patch-verification.log`.

## Evidence and scripts

- `sheets/`: the b4 (4 tiles) and b5 (3 tiles) review sheets. `contact/`: all b4 and b5 contact sheets.
- `data/`: overrides with reasons, contact-cell indexes, verdicts, fill-ins, ink fractions and size mismatches.
- `scripts/`: as in b2/b3; `prepare.py` now also defers `neighborhoodReviews` buildings. Kept for audit; do not
  rerun blindly.
- `scope-audit.json`: against the pre-review snapshot exactly the 687 reviewed objects changed, one source was
  added and no geometry changed; against the previous publication only the 112 b4 houses changed.

## Tests

- `logs/js-tests-summary.log` and `publication/release-tests.log`: full JavaScript suite against the release tree,
  495/495.
- `logs/python-tests.log`: the building-map, reported-building and catalogue-match tests, passed. The full Python
  suite was not rerun.

## Publication

Deployed on 2026-11-12 as Cloudflare version `a9d4aa22-23d3-4461-809d-33efc7af9273`, built from the live release
`734010f8` plus only this batch (5 files uploaded). All 291 live files matched byte for byte.
