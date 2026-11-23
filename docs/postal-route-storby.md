# Postal route: the start at Storby, Eckerö

Part of the work to draw the postal route on real roads (`docs/reviews/postal-route-2026-11-23/README.md`). The postal
road across Åland began at the post and customs house by the harbour in Storby
(`building:osm:way-342899630`, Eckerö Post- och Tullhus). The way next to it is still called Gamla Postrotevägen.

Build step: `apply_postal_route_storby` in `scripts/postal_route_storby.py`, after the Vårdö step.

Review data: `data/postal-route-storby.json` (copied to `dist/assets/`), written by
`docs/reviews/postal-route-2026-11-23/scripts/prepare_storby.py`.

## Registering base-map sheet 1012 15

The harbour lies on base-map sheet 1012 15. NLS printed it together with 0034 15 ("Skeppsvik", 1968, 1978, 1985) and
with 1012 03 (1994). The scans were in the local cache but had not been registered; the 1994 registration covered only
the 1012 03 part. The 1929 Eckerö parish map stops about 500 m east of the post house.

The review registers the four editions on their printed KKJ grid (EPSG:2391), in the format of
`scripts/rural_registration.py` (printed-grid mesh):
- **Finding the crosses.** `docs/reviews/postal-route-2026-11-23/scripts/grid_crosses.py` finds the printed 1 km crosses
  around two seed crosses and fits them with an affine transform:

  | edition | crosses | largest residual | mean residual |
  |---|---|---|---|
  | 1968 | 18 | 3.8 m | 1.6 m |
  | 1978 | 15 | 3.9 m | 2.3 m |
  | 1985 | 17 | 3.5 m | 2.1 m |
  | 1994 | 38 | 4.0 m | 2.1 m |

- **Building the mesh.** `make_registration.py` builds a mesh for E 1 416 000–1 420 000 and N 6 672 000–6 680 000.
  - The nine nodes are placed by that fit, because the 1 420 000 and 6 680 000 lines lie on or just outside the neat
    line, where only margin ticks are printed.
  - One printed cross in each cell is the independent check.
  - `registration_pair` accepts all four meshes, and every printed cross inside the frame lies within 4 m of the mesh.
- **Where the registrations live.** They are in `docs/reviews/postal-route-2026-11-23/data/registrations-101215.json`.
  The four editions enter the catalogue as map sources (`nls:101215:1968` … `nls:101215:1994`) through this step.
  `data/rural-map-review.json` is not changed.

Renders: `renders/harbour-101215-sheet.jpg` (the four editions with OSM) and `renders/storby-sheet.jpg` (1012 03).

## Finding

On all four editions the main road runs from Labbas south-west past Krogarviken to a junction by the harbour. From the
junction one road leads south past the post and customs house (marked "Post Tull" and later "Post Posti"), and the
other runs on north-west to Berghamn harbour. Neither had an object: the Marsund connection, dated from 1929, ended at
Labbas.

## Result

| object | change | maps |
|---|---|---|
| Eckerövägen · Storby hamn–Labbas (new) | from 1968, 729 m | 1012 15: 1968, 1978, 1985, 1994; 1012 03: 1968, 1978, 1985 |
| Sandmovägen · vid post- och tullhuset (new) | from 1968, 127 m | 1012 15: 1968–1994 |

Notes on the table:
- **Eckerövägen's pieces:** the first 17 vertices of OSM 25208185 and four junction pieces up to the Marsund connection.
  Its west end is a stated free end, the junction where the road to Berghamn harbour continues; that road is not
  reviewed here.
- **Sandmovägen's pieces:** 1066815068 and the first vertices of 25208110. It ends at the post house, also a stated free
  end. The connections step (`scripts/sviby_connections.py`) now accepts free ends with a stated basis.
- **Map years** are first evidence, not construction years. The post house itself is dated in the catalogue from 1824.

## Checks

- The registrations: `registration_pair`, which checks the mesh and an independent printed cross in each cell.
- The new roads, through the connections step:
  - OSM pieces unchanged, and nothing owned twice;
  - partial pieces abut owned ranges or have a stated basis;
  - both ends rest on roads, or are stated free ends;
  - no run along another road.

Scope (`docs/reviews/postal-route-2026-11-23/scope-audit-storby.json`):
- objects: 2 added;
- geometries: 2 added;
- sources: 7 added (4 map editions, the review and 2 surveys);
- nothing changed or removed, and the atlas roads file is unchanged.

Tests:
- `tests/test_postal_route_storby.py` (including the registrations);
- `tests/postal-route-storby.test.cjs`.

## Open items

- The road from the junction north-west to Berghamn harbour, on the same maps.
- Earlier maps of the harbour (the 1929 Eckerö sheet does not reach it).
