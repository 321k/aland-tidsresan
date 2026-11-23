# Postal route: the end at Vargata on Vårdö

Part of the work to draw the postal route on real roads (`docs/reviews/postal-route-2026-11-23/README.md`). The postal
road crossed from Bomarsund to Vårdö by boat and ended at Vargata, where the base maps mark the farm "Post" at
Västergård–Östergård. The road across Töftö, with its ferries and the bridge via Gersholm, belongs to the
20th-century road network and is left for later.

Build step: `apply_postal_route_vardo` in `scripts/postal_route_vardo.py`, after the Godby step.

Review data: `data/postal-route-vardo.json` (copied to `dist/assets/`), written by
`docs/reviews/postal-route-2026-11-23/scripts/prepare_vardo.py`.

Evidence: `docs/reviews/postal-route-2026-11-23/renders/vargata-sheet.jpg` and `vbend-sheet.jpg`, on the base map
1023 01 (1971, 1978, 1985).

## Finding

- Vårdövägen's Vårdö object was dated only from 1985.
- The 1971 and 1978 maps draw the road from the Kumnäs ferry landing north into Vargata. From there it ran in a bend
  north past the Post farm, along today's Drottning Kristinas gata, and back east to today's line.
- Drottning Kristinas gata is already in the catalogue from 1971.
- Today's straight road through Vargata (OSM 296585218) is first on the 1985 map. The earlier review recorded this but
  dated the whole object from 1985.

## Result

| object | change | maps |
|---|---|---|
| Vårdövägen (`road:qgis:vardo:vardovagen-200km1`) | 1971–1984 without the straight (0–2 096.3 m and 2 401.5–3 587.6 m of its own geometry); unchanged from 1985 | 1971, 1978 |

From 1971 the road from the Kumnäs landing through Vargata is one line: Vårdövägen, Drottning Kristinas gata,
Vårdövägen. Map years are first evidence, not construction years.

## Checks

The main-road helper (`_apply`) on a copy of the catalogue:
- input fingerprint, geometry digest and length;
- the review applies once;
- the first year is the first map marked present;
- the cuts lie on the object.

Scope (`docs/reviews/postal-route-2026-11-23/scope-audit-vardo.json`):
- objects: 1 changed;
- geometries: 1 added;
- sources: 1 added;
- the atlas roads file is unchanged.

Tests:
- `tests/test_postal_route_vardo.py`;
- `tests/postal-route-vardo.test.cjs`.

## Open items

- **Where the postal boat landed on Vårdö.** The base maps show no single landing for it.
- **The Töftö route:** Prästö–Töftö–Kumnäs (the Töftö part of Vårdövägen, the Färjhamn road, and the road north of
  Påvals first on the 1978 map).
