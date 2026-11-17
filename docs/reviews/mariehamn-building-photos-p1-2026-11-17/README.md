# Mariehamn buildings dated from the orthophotos: p1 (Norrböle) — 2026-11-17

The last photo-dating batch. Buildings with no symbol on the 1968–1995 base maps (`absent` in the building-map
review) in Johannebo, Stenliden, Hindersböle and Norrböle with their industrial blocks (building-map batch b1) were
drawn on Mariehamn's 1991, 1999, 2007 and 2015 orthophotos (1 m/px) and judged by eye. Method: `docs/mariehamn-building-photos.md`.

| result | buildings |
|---|---|
| first seen on 1991 | 35 |
| first seen on 1999 | 34 |
| first seen on 2007 | 94 |
| first seen on 2015 | 51 |
| deferred: not on any photo (built after 2015), unclear, overlapping another outline, rebuilt on the spot, or under 40 m² | 197 |
| deferred: the 1985 (1995) map may already draw it (28 by dark share; 48 by eye: 14 open or hatched symbols inside, 32 touching a symbol, 2 with a filled symbol on the 1978 map) | 76 |
| deferred: earliest outline under 40 m² | 1 |
| deferred: start not after the first photo year | 3 |

Buildings that a photo shows and a later photo shows replaced or missing (for example sheets 81, 93, 152, 216, 312)
were left undated: a later first-photo date would wrongly record the earlier photo as `absent`. The industrial blocks
repeat the p2 finding: many halls are `absent` in the building-map review although the 1985 map draws them with open
or hatched symbols (`sheets/p1-mapcheck-NN.jpg`, the decisions in `data/p1-visual.json`). The photo year is first
evidence, not a construction year.

## What is committed directly

- `data/mariehamn-building-photos.json` and its copy in `dist/assets/` (all batches, now with p1; the 643 earlier
  decisions are unchanged).
- `tests/mariehamn-building-photos.test.cjs` (totals, six visually deferred p1 halls) and the snapshot counts in
  `tests/test_mariehamn_building_maps.py`, `test_mariehamn_frame_1942.py`, `test_mariehamn_symbols_1968.py`,
  `test_mariehamn_museum_duplicates.py`, `test_mariehamn_museum_offsets.py`.
- `docs/mariehamn-building-photos.md` (batch table, scope audit, the open building-map item).

## What is in `batch.patch`

`dist/index.html` (loader card "Norrböle från flygfotona", loader preview, cache stamps). See `patch-verification.log`.

## Evidence and checks

- `sheets/p1-NN.jpg` (photos), `sheets/p1-mapcheck-NN.jpg` (1985/1995 and 1978 map crops of the buildings the dark
  share passed); `data/`: building list, decisions, guard and visual deferrals.
- `scope-audit.json`: against the catalogue before this batch, exactly the 214 p1 buildings changed; nothing else.
- `logs/`: 523 of 523 JS tests; the affected Python tests pass.
- `publication/`: deployed as Cloudflare version 1793b8ac (with the Hamngatan/Parkgatan street review and the Hindersböle places); 298 files matched live byte for byte.
