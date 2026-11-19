# Långnäsvägen: from the sound at Bergören past Skag and Södergård to Sjögård

Build step: `apply_langnasvagen` in `scripts/langnasvagen.py`. It runs after the Lemlandsvägen east step and before the
atlas review's late pass. It applies two reviews on a copy first:
- `data/langnasvagen.json`, through `_apply`;
- `data/langnasvagen-skag.json`, through `_old_roads`.

Both are written by `docs/reviews/langnasvagen-2026-11-19/scripts/prepare.py` from the catalogue before the step, and
copied to `dist/assets/`.

Evidence, in `docs/reviews/langnasvagen-2026-11-19/renders/`:
- `ov-lumparland-1929-*.jpg`, `grid-*-1929.jpg`, `skag-close-1929.jpg`, `sodergard-close-1929.jpg`: the parish map
  1012 11 Lumparland (1929)
- `ov-senate-1917-*.jpg`: the Senate atlas (1917), for presence only
- `grid-*-1968.jpg`, `skag-close-1968.jpg`, `sodergard-close-{1968,1978,1985,1995}.jpg`: the base maps (sheet 101211)
- `result-*.jpg`: what the map draws in 1920, 1950 and 1970

Distances are along today's road (`road:qgis:lumparland:langnasvagen-100km3`, 5.17 km) from the sound at Bergören.

## Finding

Today's road was dated only from 1968. The 1929 parish map draws:

| along today's road | 1929 | today |
|---|---|---|
| 0–0.60 km | the road from the crossing at Bergören over Furuholm | |
| 0.60–1.09 km | straight north to a sharp corner in Skag village, then east | today's curve is younger; part of the old line is a track (OSM 349946241) |
| 1.09–1.98 km | the road east to Södergård, and on towards Åkerlund | today's road leaves it at 1.98 km |
| 1.77–2.37 km | the road north-east through Södergård, up to 150 m from today's line | today's line across the fields is younger |
| 2.37–3.22 km | the road north along Krokstadviken to Sjögård | |
| from 3.22 km | the road turns north to Nyabonds | today's road on to Långnäs is younger |

- **The 1929 sheet** lies north of today's road here: about 30 m at Södergård and 18 m east of Skag. The traces are
  moved south linearly between the offsets measured at their ends.
- **The 1917 Senate atlas** draws the road from Skag east and north along Krokstadviken, but no crossing to Bergören. It
  is too coarse for the shape at Södergård.
- **The 1968 base map** is the first to draw today's line. At Skag it draws the curve and no corner. At Södergård it
  draws today's road as the main road and part of the old line as a lesser road along the field edges. No map between
  1929 and 1968 covers this sheet.

## Result

- **Today's road** (Långnäsvägen, from 1968) gains early periods, cut from its own geometry:
  - 1917–1929: 1.09–1.98 km and 2.37–3.22 km;
  - 1929–1968: the same, plus 0–0.60 km.
- **New object "Gamla landsvägen · Södergård"** (538 m), traced on the 1929 map. It is open from 1917 until 1968, then
  `unknown`. The 1968 map is marked unclear, not absent, because it still draws part of the line as a lesser road.
  Later maps were not reviewed for it, and nothing of it is in OSM. This uses the new opt-in `untilBasis` in `_apply`:
  the old road may end at a map marked unclear, with a stated reason.
- **New object "Gamla landsvägen · Skag"** (566 m), traced on the 1929 map, with the track's OSM coordinates where it
  survives. It is the main road from 1929 until 1968; after that only the track is drawn, which the object owns in OSM.
  It uses the new opt-in `connectionEarlyPeriods` in `_old_roads`: its south end lies on the 1929 stage of today's
  road, which is the connection's second period.
- The review property on today's road is `mainRoadReview`. `tests/qgis-roads.test.cjs` now reads it as well.

In 1929–1967 the road from Lemlandsvägen over the sound to Sjögård is one connected line.

## Open items

- **1917–1928:** the road starts at 1.09 km, 150 m east of Skag village. The village end of the Skag road is in the old
  Skag object, which starts in 1929.
- **The stub at 1.98 km:** in 1917–1967 today's road is drawn to there. It is the start of the 1929 road towards
  Åkerlund and the bridge to Norrgård, which is not in the catalogue for those years.
- **North of Sjögård:** the 1929 road through Nyabonds, Mattas and Klemetsby to the church, and the road from
  Klemetsby to the shore (Stickvägen), are separate roads with their own dating.
- **Today's road from Sjögård to Långnäs** (3.22 km to its end, and OSM's further 1.2 km to the harbour) is first on
  the 1968 map. The last 1.2 km is in no catalogue object.
- **The road to Svinö:** the 1968 map draws it as a main road, but the catalogue does not draw it in 1970.
