# Hammarlandsvägen, southern half: the older roads towards Hammarland

Build step: `apply_hammarlandsvagen_south` in `scripts/hammarlandsvagen_main_road.py`, run straight after the northern
review. Review data: `data/hammarlandsvagen-south.json` (copied to `dist/assets/`), written by
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/prepare_south.py`. Evidence:
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/` (`renders/south-*`, `route-*`, `utang-odanbole.jpg`,
`odanbole-north.jpg`, `natbacken-*.jpg`, `vastansunda-*.jpg`, `result-south-1940-*.jpg`). The northern half is in
`docs/hammarlandsvagen-main-road.md`.

## Finding

From Mariehamn to Söderby, today's Hammarlandsvägen is almost entirely new:

- The Gottby straight is first on the 1978 base map; the Gottby sheet has no 1968 edition in the catalogue.
- Ödanböle–Söderby is first on the 1968 base map.
- Only Natbacken–Sagalund, 4.1–5.5 km from Mariehamn, follows an older road: the village road on the 1928
  Hammarudda–Kungsö parish map.

On the 1929 Hammarby sheet, Ödanböle–Söderby and the northern part of Ödanbölevägen are hand-drawn pink lines with
no printed road under them. The 1944 print of the same survey shows nothing there. They were added after 1929
(probably a new road being planned or built) and are not evidence of a road in 1929.

Before that, the road to Hammarland ran east from Söderby. The 1917 Senate atlas draws a main road
Söderby–Västansunda–Södersunda. Its position is too rough to tie to one modern road; it lies between Furubacksvägen
and Krossvägen. The 1929 parish map draws the road where today's Östanträskvägen, Furubacksvägen, Brobackavägen and
Södersundavägen (through Mattas) run, within the sheet's error of 10–30 m. These are existing objects of the
Hammarland rural review, which dated them from the 1968 base map.

Utängsvägen, from Sviby towards Ödanböle, is printed in full on the 1928 map. The 1944 and 1953 editions label it
"Andelsl." (a cooperative road).

## Result

| object | from | basis |
|---|---|---|
| Östanträskvägen ×4, Furubacksvägen ×3, Brobackavägen, Södersundavägen (way 1422779920) | 1929 (until 1968) | Hammarby parish map 1929; 1944 edition |
| Utängsvägen | 1928 (until 1978) | Hammarudda–Kungsö 1928; Kungsö 1944 and 1953 |
| Hammarlandsvägen del 1, 4.1–5.5 km (Natbacken–Sagalund) | 1928 (until 1978), partial | the same maps |

As in the northern review, each object keeps its identity, evidence and later periods. It gets an earlier open state
and geometry period, with its own cut where only part of it is the old road. The objects' marker
(`hammarlandsvagenMainRoad`) names this review (`review: review:hammarlandsvagen-south`).

Between Brobackavägen and Mattas there is a 137 m gap at Burs. The Mattas object's own first geometry (1968) covers
only part of its way, and the early period does too, as the 1968–1994 periods already did.

## Checks

- The same build checks as the northern review: fingerprints, applies once, ends where the object begins, first year
  is the first map marked present, ranges lie on the object, and partial cuts are at least 50 m. A whole object may
  be shorter: way 1422997221 is 20 m.
- Maps are labelled, because two 1944 editions (Kungsö and Näfsby–Emkarby) are cited. Every label must be a known or
  added source.

## Open items

- Södersundavägen north-east of Mattas towards Jomala: done 2026-11-21, see `docs/sodersundavagen.md`. The link
  from the old bend at Mattas to Södersundavägen: done 2026-11-23, see `docs/mattas-link.md`.
- Ödanbölevägen: only its southernmost few hundred metres are on the 1928 sheet; the rest is a post-1929 addition.
  It stays 1968.
- The 1917 route: Furubacksvägen versus Krossvägen, which the Senate atlas cannot separate.
- The route from Mariehamn to Sviby: done 2026-11-23, see `docs/svibyvagen.md`. In 1929 it ran from Utängsvägen through
  Sviby to Norra Svibyvägen, and on to the town by Kasbergsvägen and Svibyvägen.
- The 1968 Gottby sheet (101205): is the Gottby straight older than 1978?
