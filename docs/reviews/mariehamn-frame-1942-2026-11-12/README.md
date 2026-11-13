# Mariehamn 1942 city traces against the orthophoto — 2026-11-12

All 14 hand traces of the 1942 city stage that were still drawn without a persistent object were compared with the
original 25 July 1942 orthophoto at 2 m/pixel, with every persistent road object labelled, and with the 1968 base map
(sheet 101208) as a second witness. Method, both decision tables and the compiler checks are in
`docs/mariehamn-frame-1942.md`. The earlier approach-road review is `docs/reviews/mariehamn-approaches-1942-2026-11-12`.

- **Rejected (6):** Södra stadsgatan, Förbindelse mellan infartsvägarna (a power-line clearing on the 1968 map),
  Väg till västra stadskanten, Södra kvarterens tvärgata, Förbindelse till södra vägen and a 34 m Storagatan leftover.
  The photo shows no street along them. Their 1968–1985 pieces are removed too.
- **Replaced (8):** the persistent road objects the photo shows in the trace's place get the photo as 1942 evidence
  and are drawn on their own centre lines: Havsgatan (5), Köpmansgatan (4, keeping its 1952 school-street phase),
  Strandgatan and Parkgatan (2, plus one connector retraced on the photo, 1942–1967 only), Neptunigatan (8),
  Ålandsvägen (6), Torggatan (9), Styrmansgatan (5) and Norragatan (4): 43 objects.

The photo year is evidence, not a construction year. Every member keeps its later states and geometry; the 1942 phase
is inserted before them. Original trace pixels stay in `data/mariehamn-city-traces.json`. Afterwards no raw 1942 city
trace is drawn in any stage, which `tests/mariehamn-frame-1942.test.cjs` pins.

## What is committed directly

- `data/mariehamn-frame-1942.json` and its copy in `dist/assets/`: the 14 decisions with input hashes.
- `scripts/mariehamn_frame_1942.py`: validates everything (trace and stage-feature hashes, member fingerprints,
  distance to the trace, gap end points) before changing the catalogue, then applies the review.
- `tests/mariehamn-frame-1942.test.cjs`, `tests/test_mariehamn_frame_1942.py`: new regression checks.
- `tests/mariehamn-approaches-1942.test.cjs`, `tests/test_mariehamn_approaches_1942.py`,
  `tests/test_mariehamn_building_maps.py`: tracked tests that now allow, or apply, the frame step.
- `docs/mariehamn-frame-1942.md`.

## What is in `batch.patch`

Files that are untracked or carry other uncommitted work are kept as an apply-checked patch
(`patch-verification.log`):

- `scripts/build_temporal_objects.py`: calls `apply_frame_1942` after the building maps and copies the review to
  `dist/assets`.
- `dist/index.html`: the loader card "Stadens gator 1942 rättade" and the renumbered cards.
- `tests/mariehamn-core.test.cjs`, `tests/mariehamn-second-pass.test.cjs`, `tests/mariehamn-south-streets.test.cjs`,
  `tests/site-building-stories.test.cjs`, `tests/temporal-objects.test.cjs`,
  `tests/test_reported_buildings_17_18.py`: pinned expectations that now allow the removed traces and the reviewed
  1942 phase (marker `frame1942`).

## Evidence and scripts

- `images/frame-*-pair.jpg`: photo and labelled overlay for each area; `map1968-r2.jpg`, `map1968-r3.jpg`: the 1968
  witness for the power line and Badhusberget; `frame-w2-havsgatan.jpg`, `frame-e-connector.jpg`,
  `frame-r2-west.jpg`, `south-*.jpg`, `north-*.jpg`: close-ups; `retrace-strand.jpg`: the retraced connector.
- `data/retrace-strand.json`, `data/frame-*-legend.json`: retraced line and overlay legends.
- `scripts/`: `frame.py`, `map1968.py`, `south.py`, `north.py`, `retrace.py` (review images), `frame_prepare.py`
  (writes the review file from the pre-step catalogue snapshot, which stays in the local review cache) and `audit.py`.

## Checks

- `scope-audit.json`: against both the pre-step snapshot and the previous publication, exactly the 43 members
  changed, no geometry changed, one source added, and the city stages only lost reviewed trace copies and gained
  frame features.
- `logs/js-tests-summary.log`: 499 of 499 JS tests; `logs/python-tests.log`: the affected Python tests.
- `publication/`: deployed as Cloudflare version 684870cc from the live release plus only this batch; 292 files
  matched live byte for byte.
