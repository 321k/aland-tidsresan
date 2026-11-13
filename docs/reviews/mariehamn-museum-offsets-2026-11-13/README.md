# Museum-map offset duplicates and vanished houses — 2026-11-13

Second pass after the overlap review (`docs/reviews/mariehamn-museum-duplicates-2026-11-13`), started from reports of
remaining duplicates near Storagatan: museum houses 136, 138, 152 and 153. The museum map is often shifted about a
house depth, so a museum house can stand in a street, front garden or yard next to its house without overlapping it,
which the overlap check missed. Every museum house still open (74) was judged on the 1942 photo and the 1968 and
1985 maps with every building within 40 m numbered. Method and table: `docs/mariehamn-museum-duplicates.md`,
section *Second pass*.

| decision | museum houses |
|---|---|
| merge into the directly neighbouring house (gap at most 6.8 m) | 24, into 22 houses (41 + 42 and 149 + 150 each join one longer building) |
| ending by 1983: footprint empty on the 1985 map, no clear counterpart | 33 (including 153 and 156 by the 1978 block) |
| deferred | 17 |

The reported houses: 136 → symbol 498, 138 → way/165436732, 139 → symbol 492, 152 → symbol 487; 153 ends by 1983.
`way/201325604` and `way/165436785` are a house and an annex present in every OSM extract, not a duplicate.

## What is committed directly

- `scripts/mariehamn_museum_duplicates.py`: `apply_museum_offsets` (adjacency merges, at most two museum houses per
  building, map-absence endings), applied after the overlap review.
- `data/mariehamn-museum-offsets.json` and its copy in `dist/assets/`.
- `tests/mariehamn-museum-offsets.test.cjs`, `tests/test_mariehamn_museum_offsets.py` (pre-pass snapshot
  `offsets-before.json.gz` in the review cache); `tests/mariehamn-symbols-1968.test.cjs`: a rejected symbol house may
  be merged by this pass.
- `docs/mariehamn-museum-duplicates.md`: the second-pass section.

## What is in `batch.patch`

`scripts/build_temporal_objects.py` (copies the review to `dist/assets`), `dist/index.html` (loader card "Museikartans
hus på rätt plats"), `tests/city-buildings.test.cjs` and `tests/temporal-objects.test.cjs` (museum counts and ends
include this pass; the street-alignment check reads a museum house merged by either pass),
`tests/test_reported_buildings_17_18.py` (leaves out the new source). See `patch-verification.log`.

## Evidence and checks

- `sheets/open-NN.jpg`: every open museum house on the 1942 photo, 1968 and 1985; `museum-136-138-zoom.jpg`.
- `data/`: the neighbour index, the footprint dark shares and the overlap list after the pass; `scripts/`: the tools.
- `scope-audit.json`: exactly the 24 merged museum objects removed and 55 objects changed; no geometry or city-stage
  changes. 17 museum houses remain open; 11 town-wide museum overlap pairs remain, all among them.
- `logs/` and `publication/`: 512 of 512 JS tests and the affected Python tests; deployed as Cloudflare version
  cac264af, 295 files matched live byte for byte.
