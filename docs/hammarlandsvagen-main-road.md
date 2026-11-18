# Hammarlandsvägen on the 1929 parish map

Build step: `scripts/hammarlandsvagen_main_road.py`, run after `lemland_old_road_osm.py` in `build_temporal_objects.py`.
Review data: `data/hammarlandsvagen-main-road.json` (copied to `dist/assets/`), written by
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/prepare.py`. Evidence and renders:
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/`.

This is the second main road reviewed with the method of `docs/lemlandsvagen-main-road.md`. It covers the northern
half, from Söderby to the church in Hammarland. The southern half, from Mariehamn to Söderby, is a separate follow-up
(see Open items).

## Sources

| map | use |
|---|---|
| Sockenkarta 101206 Hammarby, 1929 (tiles at 2.4 m/px) | presence and position; the old line at Smedens is read on it |
| Sockenkarta 101206 Näfsby–Emkarby, 1944 (black-and-white edition) | presence; the same survey as 1929, so not independent for position |
| Grundkarta 101206, 1968–1995 (registered scans) | presence; 1968 is the first map with the bypasses |
| Senatens kartverk, Jomala 1917 | not used here: north of Söderby the sheet has no drawing, and south of it its line is unclear |
| Sockenkartor 1928 Hammarudda–Kungsö, 1944 and 1953 Kungsö | used only for the southern half (Open items) |

On the 1929 Hammarby sheet some roads are hand-coloured pink. A pink line with printed black road lines under it is a
coloured road. A pink line with nothing printed under it (Ödanböle–Söderby) is a later hand addition. It is not
evidence that the road existed in 1929, and the 1944 print of the same survey shows nothing there.

## Result

Distances are along today's road from the western edge of Mariehamn (the start of Hammarlandsvägen del 1).
Boundaries are OSM junction nodes where the old road meets today's road. The one exception is 12.6 km, which is
measured, and so is 14.4 km (`nafsby-south`, moved from 14.3 km by the Näfsby review).

| stretch | today's road | from |
|---|---|---|
| Söderby (Torpvägen junction) – Långträsk – Drygsböle, 9.0–11.8 km | the 1929 road along the east shore of Långträsk | 1929 |
| Drygsböle, 11.8–12.4 km | bypass; in 1929 no road runs on this line | 1968 |
| Bolstad, 12.4–12.6 km | the 1929 road | 1929 |
| Smedens–Björkgård, 12.6–14.1 km | new line 25–70 m east of the 1929 road (about 35 m east of the Smedens farm, which the 1929 road passed) | 1968 |
| Björkgård–Mattas–Näfsby, 14.1–14.4 km | the 1929 road | 1929 |
| Näfsby, 14.4–15.3 km | bypass east of the village; the old road went through Näfsby and past Klaralund, up to 115 m west | 1968 |
| Korsbroström – Korsängen – Postad – church, 15.3–17.3 km | the 1929 road | 1929 |

The objects keep their identity, evidence and later periods. Each gets an earlier open state and geometry period from
1929 until its current first year (1968). Where only part of the object is the old road, that period is partial and
has its own cut of the object's geometry. The objects are 345142933, 345143750, Västmyra, Postad–Korsängen and the
church corridor. The small objects between Smedens and Björkgård (174570457, 345143751, 69739600, 345143754) lie
wholly on the Smedens line and keep 1968.

The old line at Smedens is a new object, "Gamla Hammarlandsvägen · Smedens". It is read by hand on the 1929 map and is
open 1929 until 1968, then `unknown`: the 1968 map does not draw it, and nothing of it is in OpenStreetMap.

Before 1968 the main road had two gaps, at Drygsböle and at Näfsby, where the old route was not yet an object. The
Näfsby gap is filled by `docs/hammarlandsvagen-nafsby.md`; Drygsböle is still open.

## Checks in the build step

- Fingerprints of each object and of its geometry; the review applies once. The early period must end where the
  object now begins, and its first year must be the first map marked present.
- Ranges lie on the object and are at least 50 m long. Together the cuts cover each reviewed same-road interval of the
  reference line exactly once, without gaps (within 2 m), and stretches that run on across an object boundary meet.
- The Smedens line ends on today's road (within 1 m). It runs no more than 80 m continuously beside a road open at
  the same time, or beside a same-road cut. No OSM road other than Hammarlandsvägen runs more than 60 m within 15 m
  of it; if one did, it would have to be reconciled instead.

## Also fixed: Långskata del 2's early period

The Lemlandsvägen review gave Långskata del 2 a partial 1917–1985 period for its first 300 m, but the period referred
to the whole Långskata geometry, and `canonicalRange` is metadata only, so all 2.4 km were drawn from 1917. The period
now has its own cut geometry (`geometry:lemland:langskata-2-old-road`), like every other partial period in the
catalogue.

## Open items

- Southern half, Mariehamn–Söderby: today's road is new there, with the Gottby straight first on the 1978 map and
  Ödanböle–Söderby on the 1968 map. The older main road ran from Sviby along Ullingsvägen and Ödanbölevägen. The 1928
  map prints it, and the 1944 and 1953 Kungsö maps print it as "Andelsl.". It is not in the catalogue as the historical
  main road. The 1917 route through Västansunda and Söderunda is still to be checked.
- Näfsby: done, see `docs/hammarlandsvagen-nafsby.md`.
- Drygsböle: the 1929 through-route between the lake shore and Bolstad is not clear on the map. It probably ran by the
  farm (today's Drygsbölevägen); this needs a closer look.
- Kattby westwards: done, on the 1929 Eckerö sheet; see `docs/hammarlandsvagen-kattby.md`.
