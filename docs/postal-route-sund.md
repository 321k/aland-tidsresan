# Postal route: Sundsvägen east of Kastelholm

Part of the work to draw the postal route on real roads (`docs/reviews/postal-route-2026-11-23/README.md`). From
Kastelholm the postal road ran east along today's Sundsvägen towards Skarpans and the crossing to Vårdö. On dated roads
the leg Kastelholm → Gamla Skarpans was broken in every year: the road pieces of earlier reviews left three short
stretches of today's road in no object.

Build step: `apply_postal_route_sund` in `scripts/postal_route_sund.py`, after the Storby step.

Review data: `data/postal-route-sund.json` (copied to `dist/assets/`), written by
`docs/reviews/postal-route-2026-11-23/scripts/prepare_sund.py`.

## The gaps

Sundsvägen is made of several objects:
- the Saltvik piece, "Sundsvägen · Lappböle till bladgränsen", which stops at a sheet edge;
- del 2, del 3 and del 1 from the Sundsvägen review (`docs/sundsvagen.md`).

Between them, three stretches of today's road were in no object:
- **at Lappböle:** 181 m at the sheet edge, between the Saltvik piece and del 2 (OSM way 71081797, between the two
  owned vertex ranges);
- **at Klippan, west:** 265 m between del 2 and del 3;
- **at Klippan, east:** 98 m from the Klippanvägen junction to del 1.

The Sundsvägen review lists the Lappböle and Klippan gaps as open items. Its batch is still uncommitted in the working
tree. This step runs after it and changes none of its objects.

The survey first also found a 185 m hole on Tosarbyvägen at Lappböle. That came from the Kastelholm stop point, which
lies on Slottsvägen; the postal road itself runs along Sundsvägen. That hole is not part of the route and is left alone.

## Reading the base maps

Renders are in `docs/reviews/postal-route-2026-11-23/renders/`.

- **Lappböle** (`lappbole-sheet.jpg`, sheet 1021 10, 1968, 1978 and 1985; `lappbole-n-sheet.jpg`, sheets 1012 09 and
  1021 07): Sundsvägen runs south-east across the sheet edge on today's line in every edition. Sheet 1012 12
  (`lappbole-101212-sheet.jpg`) has only its margin here.
- **Klippan** (`klippan-sheet.jpg`, sheet 1012 12, 1968, 1978, 1985 and 1994; `klipp-we-sheet.jpg`, 1968 and 1978
  enlarged):
  - From 1978 the road runs straight along N 6 679 000 from del 2 to del 3, and on past the Klippanvägen junction to
    del 1.
  - The 1968 sheet already draws the straight road east of the Svensböle junction, as the wide main-road symbol. The
    road from Svensböle bends into it. The Klippanvägen loop is drawn as a smaller road.
  - Sheet 1021 10 has only its margin at Klippan.

## Result

| object | change | maps |
|---|---|---|
| Sundsvägen · Lappböle vid bladkanten (new) | from 1968, 181 m | 1021 10: 1968, 1978, 1985, 1993 |
| Sundsvägen · Klippan (new) | from 1978, 265 m | 1012 12: 1978, 1985, 1994 |
| Sundsvägen · öster om Klippan (new) | from 1978, 98 m | 1012 12: 1978, 1985, 1994 |

Notes on the table:
- **Geometry:** each piece is OSM 2026 geometry, joined within 1 m to the objects on both sides. The pieces are on the
  Sundsvägen route, like their neighbours.
- **Parallel ways:** at each Klippan junction OSM has two parallel ways. The step uses the eastbound one (615021067 and
  613971997); 615021063 and 613972000 stay unowned.
- **Klippan dates:** the Klippan pieces are dated with del 2 and del 3, from 1978. The Sundsvägen review keeps the old
  road along Klippanvägen ("Gamla landsvägen · Hallbacka–Klippan") as the main road until 1978. The 1968 sheet already
  draws the straight east of the Svensböle junction, so 1968 is left as an open item for that review and is not used as
  evidence here.
- **Before 1968 at Lappböle:** no map in the project covers the sheet edge. The 181 m gap stays unknown before 1968.
- **Map years** are first evidence, not construction years.

On dated catalogue roads (`scripts/route_survey.py`), Kastelholm → Gamla Skarpans is now connected in 1968, 1978, 1995
and 2026. Before this step it was broken in every year. In 1929 it is still broken at the Lappböle sheet edge.

## Checks

The new roads go through the connections step (`scripts/sviby_connections.py`), which checks:
- the OSM pieces are unchanged, and nothing is owned twice;
- the partial piece of way 71081797 abuts both owned ranges;
- both ends of each piece rest on the neighbouring objects in every period from its first year;
- no piece runs along another road;
- the first year is the earliest map marked present.

Scope (`docs/reviews/postal-route-2026-11-23/scope-audit-sund.json`):
- objects: 3 added;
- geometries: 3 added;
- sources: 4 added (the review and 3 surveys);
- nothing changed or removed, and the atlas roads file is unchanged.

Tests:
- `tests/test_postal_route_sund.py`;
- `tests/postal-route-sund.test.cjs`;
- `tests/qgis-roads.test.cjs` (untracked, in the patch): the Kulla test expected OSM way 71081797 to keep an unowned
  remainder at the Lappböle sheet edge. That remainder is the gap this step closes, so the test now expects the way
  to be owned in full by the Saltvik piece, the new piece and del 2.

The changes to files that hold other work (the build script, the loader card, the count test and the Kulla test) are
in `docs/reviews/postal-route-2026-11-23/batch-postal-route-sund.patch`, checked forwards on before-copies and in
reverse (`patch-verification-sund.log`).

## Open items

- **For the Sundsvägen review:** the 1968 sheet 1012 12 draws the straight road at Klippan east of the Svensböle
  junction. That suggests del 3 and the Klippan piece date from 1968, with the old road along Klippanvägen a smaller
  road by then.
  - Done in the main-road review (`docs/main-roads-mainland.md`): del 3 and both Klippan pieces are open from 1968.
- **Lappböle before 1968:** an earlier map that covers the sheet edge.
- **Earlier maps:** the whole leg on the parish maps.
