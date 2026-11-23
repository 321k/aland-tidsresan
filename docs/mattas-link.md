# Mattas: the old road to Södersundavägen

Build step: `apply_mattas_link` in `scripts/mattas_link.py`. It runs after the Möckelö steps and before the atlas
review's late pass.

Review data: `data/mattas-link.json` (copied to `dist/assets/`), written by
`docs/reviews/mattas-2026-11-23/scripts/prepare.py`. Evidence: `docs/reviews/mattas-2026-11-23/renders/m-sheet.jpg`,
which shows these maps:
- the parish map 1012 06 Hammarby (1929) and its 1944 print;
- the base maps 1012 06 of 1968, 1978, 1985 and 1995.

## Finding

The road from Hammarland to Jomala left Mattas north round the old bend (ways 495221553 and 160987689), then ran
straight on north-east to Södersundavägen.
- **The bend:** both ways lie on the maps' road in every edition, so the registration is good here.
- **The link:** on the 1968 map, the line beyond the bend passes E 20 493 297 N 6 671 573 and 3 354/1 626, and meets
  Södersundavägen at about 3 515/1 732.
- **Earlier maps:** the 1929 map and its 1944 print draw the same line, and no road on Södersundavägen's line west of the
  junction.
- **Later maps:** the 1978 and 1985 maps draw the link too. The 1995 map draws today's road through Mattas, the bypass,
  as the main road. Nothing of the link is in OSM.

Two corrections follow:
- The two bend ways were dated only from 1968.
- Södersundavägen's 1929–1995 periods, from the rural review and the Södersundavägen review (`docs/sodersundavagen.md`),
  began 170 m further west than the junction. That stretch is the line of the 1995 bypass, 40–60 m north-west of the
  old road.

## Result

| object | change | maps |
|---|---|---|
| ways 495221553 and 160987689 (the bend) | from 1929 (were 1968), whole | 1929, 1944 |
| Gamla Södersundavägen · Mattas (new, old road) | 1929 until the 1995 map, 352 m | 1929, 1944, 1968, 1978, 1985; 1995 unclear |
| Södersundavägen (way 86548779) | the 1929–1995 periods end at the junction: 211.9–3316.6 m (was 211.9–3495.4 m) | 1929, 1968, 1978, 1985 |

Notes on the table:
- The old road is traced on the 1968 map, which agrees with the 1929 map. Its ends are the end of way 160987689 and a
  point on Södersundavägen.
- From 1995 the old road's state is unknown: the 1995 map draws the bypass as the main road, and it cannot be told
  whether the old line is still drawn as a lesser road.
- Map years are first evidence, not construction years.

## Checks

The step runs on one copy of the catalogue and replaces it only if both parts pass:
- **The main-road helper (`_apply`):**
  - fingerprints, geometry digests and lengths, and the review applies once;
  - first years follow the maps;
  - the old road ends within 1 m on the bend and on Södersundavägen;
  - no road runs along it, and nothing of it survives in OSM.
- **The coverage step (`_coverage`):** Södersundavägen's fingerprint, its whole-geometry digest, each period's
  geometry, and a map marked present in each period.

Scope (`docs/reviews/mattas-2026-11-23/scope-audit.json`):
- objects: 1 added, 3 changed;
- geometries: 4 added;
- sources: 1 added;
- nothing else, and the atlas roads file is unchanged.

Tests:
- `tests/test_mattas_link.py`;
- `tests/mattas-link.test.cjs`;
- `tests/rural-map-review.test.cjs`: Södersundavägen's 1985 end now lies 150–200 m east of the rural review's boundary.
