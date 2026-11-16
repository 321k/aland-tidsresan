# Nygatan's museum duplicate and the shore road on Västerhamn — 2026-11-16

A critical look at "Tvärgata norr om Norragatan" and "Västra strandens gata", requested after the photo-dating batches.
Method and model changes: `docs/mariehamn-shore-road.md`. `renders/` shows the map's streets over the dated orthophotos
before (`nygatan-before.jpg`, `shore-before.jpg`, `sjopromenaden-*.jpg`) and after (`after.jpg`); `scripts/streetview.py`
draws them.

* **Nygatan drawn twice 1920–1941.** The museum's straight `city-1920-street-39` ran 60–90 m south of Nygatan through
  house lots where the 1942 photo shows no street. It is now recorded in `data/nygatan-review.json` under
  `retiredMuseumTraces`, kept as identity-only evidence on `road:nygatan`, and no longer drawn. Nygatan's 1942 note no
  longer starts with the raw trace name.
* **The shore road missing 1942–1967.** The 1942, 1952 and 1962 photos show the road along Västerhamn where today's
  Sjöpromenaden runs. `data/mariehamn-shore-road.json` / `scripts/mariehamn_shore_road.py` show the three Sjöpromenaden
  objects from the museum decade (the museum's `city-1920-street-36` is their coarse drawing) and from the 1942 photo,
  the long northern part only south of latitude 60.1004.

## What is committed directly

`scripts/mariehamn_shore_road.py`, `data/mariehamn-shore-road.json` and its `dist/assets/` copy,
`tests/mariehamn-shore-road.test.cjs`, `docs/mariehamn-shore-road.md`; the shore step added to
`tests/test_mariehamn_frame_1942.py`, `tests/test_mariehamn_approaches_1942.py`, `tests/test_mariehamn_building_maps.py`;
the shore road's earlier start allowed in `tests/test_mariehamn_street_pass5.py` and `tests/mariehamn-street-pass5.test.cjs`.

## What is in `batch.patch`

Files that also hold other uncommitted work: `scripts/build_temporal_objects.py` (runs the shore step and copies its
review), `scripts/nygatan_continuity.py` (retired museum traces), `data/nygatan-review.json`,
`data/building-issue-review.json` and its `dist/assets/` copy (Nygatan's context fingerprint re-pinned; the Köpmansgatan
school decision is unchanged), `tests/nygatan.test.cjs`, `tests/mariehamn-major-roads.test.cjs`, and the loader card in
`dist/index.html`. See `patch-verification.log`.

## Checks

`scope-audit.json`; `logs/`: the new and updated JS tests and the eight affected Python tests pass. Twelve other Python
test files fail identically in a clone with this change reverted, so they predate it (listed in
`logs/python-tests.log`). Deployed as Cloudflare version 499222f1 together with the p6 Södra photo batch.
