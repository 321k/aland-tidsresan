# Mariehamn buildings b2/b3 and the b1 contact-sheet correction — 2026-11-12

Two new areas next to b1 are dated from house symbols on sheet 101208, and every proposal in all three batches was
checked again, one house at a time. Method, rules and totals are in `docs/mariehamn-building-maps.md`; the b1
review record is `docs/reviews/mariehamn-building-maps-2026-11-12`.

- **b2**, 19.918–19.930° E × 60.109–60.127° N (Klinten, the yard, Notgrundet, Möckelbybäcken): 95 houses.
- **b3**, 19.930–19.958° E × 60.109–60.114° N (the blocks just south of b1): 119 houses.
- **b1 correction:** 83 of the 444 houses published earlier today are withdrawn and keep their previous start; 361
  stay unchanged. 575 houses are map-dated in all (214 from 1968, 269 from 1985, 92 from 1995).

Both areas stay clear of the `printedMapSymbol` objects (north of 60.1078° N) and inside the 1995 registration
(east of 19.917° E). The b2 and b3 boxes do not overlap b1.

## Why b1 was corrected

The tile sheets used for b1 (about 1.7 m per scan pixel, whole blocks per tile) were too coarse. The contact sheets
in `contact/` show each proposal at high zoom with its shifted outline: the previous and the first edition for
later starts (`*-later.jpg`), and 1985 and 1968 for 1968 starts (`*-1968.jpg`). They showed matches on shorelines,
piers, lines and black 1995 place-name lettering; outlines that are empty while the symbol belongs to the
neighbour; partial overlaps; a run of 1968 symbols about one house width from their outlines in Hindersböle; and
hollow, hatched, offset or text-covered drawings in the previous edition that the ink guard cannot see, which could
make a later start too late. 113 proposals were rejected in all (83 in b1, 13 in b2, 17 in b3). Each is listed with
its reason, sheet file and cell in the review's `visualRejections`, from `data/KEY-overrides.json`.

One b3 building is a church whose dates a `historicalReview` decides. It is deferred as `curated-review`, and the
compiler now refuses buildings with `historicalReview`, `museumReview` or `printedMapSymbol`.

## What is committed directly

- `data/mariehamn-building-maps.json` and its copy in `dist/assets/`: now 575 decisions with b1–b3, the deferred
  lists and `visualRejections`, and the contact sheets in `reviewSheets`.
- `scripts/mariehamn_building_maps.py`: the curated-review guard.
- `tests/mariehamn-building-maps.test.cjs`: new totals, the curated-review check, and a test that rejected houses
  are never dated and each rejection names its reason and sheet.
- `tests/test_mariehamn_building_maps.py`: a curated building is refused.
- `docs/mariehamn-building-maps.md`: the batches, the contact-sheet step and the correction.

## What is in `batch.patch`

Only `dist/index.html`: the loader card "Fler hus i Mariehamn – och en noggrannare kontroll" and the renumbering
to 47. It applies on exactly the state the b1 `batch.patch` produces; generated preview bins and cache stamps are
left out. `scripts/build_temporal_objects.py`, `tests/temporal-objects.test.cjs` and
`tests/test_reported_buildings_17_18.py` are unchanged since the b1 patch. See `patch-verification.log`.

## Evidence and scripts

- `sheets/`: the b2 and b3 tile sheets, and `smf-pair.jpg` (the first shoreline match found, at Notgrundet).
- `contact/`: all contact sheets for b1–b3.
- `data/`: per-batch overrides, the contact-cell index files, and the b2/b3 verdicts, fill-ins, ink fractions and
  size mismatches.
- `scripts/`: `contact.py` is new; `match.py` now skips degenerate outlines with fewer than four points;
  `prepare.py` applies the overrides and the curated-review exclusion. Kept for audit; do not rerun blindly.
- `scope-audit.json`: against the pre-review snapshot (the catalogue live before b1), exactly the 575 reviewed
  objects changed, one source was added and no geometry changed. Against the first b1 publication, 297 objects
  changed: the 83 withdrawn houses are byte-identical to the snapshot again, 214 are newly dated, nothing else.

## Tests

- `logs/js-tests-summary.log`: full JavaScript suite, 495/495 passed.
- `logs/python-tests.log`: the building-map, reported-building and catalogue-match tests, passed. The full Python
  suite was not rerun; its 19 older failures are listed in the b1 review record.
- `publication/release-tests.log`: the full JavaScript suite against the release tree, 495/495.

## Publication

Deployed on 2026-11-12 as Cloudflare version `734010f8-97d2-4aef-b18f-480df3d7dec0`, built from the live release
`1354d66c` plus only this batch (5 files uploaded). All 291 live files matched byte for byte; see
`publication/deployment.json`.
