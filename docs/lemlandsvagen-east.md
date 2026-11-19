# Lemlandsvägen east of the church village: Norrböle, Rörstorp, Granboda and Bergören

Build step: `apply_lemlandsvagen_east` in `scripts/lemlandsvagen_east.py`. It runs after the Storby step and before the
atlas review's late pass. It uses the Hammarlandsvägen helpers:
- `_apply`, for the early periods;
- `_new_road_check` and `_new_road_add`, factored out of the Holmberg step, for the new object.

Everything runs on a copy first.

Review data: `data/lemlandsvagen-east.json` (copied to `dist/assets/`), written by
`docs/reviews/lemlandsvagen-east-2026-11-19/scripts/prepare.py` from the catalogue before the step.

Evidence, in `docs/reviews/lemlandsvagen-east-2026-11-19/renders/`:
- `ov-lumparland-1929-*.jpg`, `simons-*-grid-1929.jpg`, `delsviken-grid-1929.jpg`: the parish map 1012 11 Lumparland
  (1929), with a 50 m grid and OSM
- `ov-senate-1917-*.jpg`: the Senate atlas (1917), for presence only
- `ov-101211-1968-*.jpg`, `simons-east-grid-1985.jpg`, `simons-wide-1995.jpg`: the base maps
- `result-*.jpg`: what the map draws in 1920, 1950 and 1970

Distances are along today's road (`road:qgis:lumparland:lemlandsvagen-100km3`, 7.29 km) from the church village.

## Finding

Today's road was dated only from 1968. The 1929 parish map draws:

| along today's road | 1929 | today |
|---|---|---|
| 0–2.28 km | the road on today's line, within the sheet error (up to 25 m) | |
| 2.28–2.62 km | a bend about 100 m north past Fsk. and Simons | Skolsvängen (OSM way 611723906) follows it |
| 2.62–5.94 km | the road on today's line, through Rörstorp and Granboda | |
| 5.94–6.75 km | the road east along today's Klubbensvägen, then north along Fiskartorpsvägen to Bergören | today's diagonal is younger |
| 6.75–7.29 km | the road across Bergören and over the sound towards Skag | |

- **The 1917 Senate atlas** draws the road from the church village through Rörstorp and Granboda, and east to the shore
  at Delsviken. It draws no road north to Bergören and none over the sound.
- **The 1968 base map** (sheet 101211) is the first to draw today's straight road at Simons and the diagonal as the
  main road. Skolsvängen, Klubbensvägen and Fiskartorpsvägen are still drawn, as minor roads.
- No map between 1929 and 1968 covers this sheet; the only other parish-map edition is a black-and-white copy of 1929.

## Result

- **Today's road** (Lemlandsvägen, from 1968) gains two early periods, cut from its own geometry:
  - 1917–1929: 0–2.28 km and 2.62–5.94 km;
  - 1929–1968: the same, plus 6.75 km to the sound.
- **Skolsvängen** is open from 1917. Until 1968 it is drawn as its loop up to vertex 26; vertex 27 is a later spur to
  the house at Simons.
- **Klubbensvägen** is open from 1917, whole.
- **Fiskartorpsvägen** is a new object, open from 1929 with its OSM line. It owns its way in the 2021, 2025 and 2026
  extracts. The 2014 extract does not have it, which is not evidence that it was missing.

There is no new object for the old road: each piece of it is a road that exists today, so it keeps that road's
identity (one object per physical road). Each old road keeps its own class and name. Before 1968 they are the route of
the main road, but they are drawn as the smaller roads they are today.

In 1929–1967 the road from Lemland's church village to the sound is one connected line, except for the 15 m gap
described under Open items. Its west end meets the old road from Söderby, which is open from 1917.

## Build step

Checks, all before any change:
- fingerprints and geometry digests of the three existing objects, and their lengths;
- each early period's first year is its first map marked present. The later stage starts at a map marked present,
  inside the early period;
- the route main road → Skolsvängen → main road → Klubbensvägen joins within 1 m;
- the stated gap: Skolsvängen's end lies 15.9 m (±1 m) from the road open at the time;
- the new road: its dates follow its maps, and it is owned whole in every extract that has it, with a stated reason
  for each extract that lacks it, which is checked to lack it. Its OSM sources are unowned and unchanged. Both of its
  ends rest (within 1 m) on roads open in 1929.

## Open items

- **Skolsvängen:** the loop ends 15 m from today's road, where a cycle path now runs between them, and the old link
  is not drawn. The 1929 map draws it merging into today's line within the sheet error.
- **The road beyond the sound** (Långnäsvägen, dated from 1968): the 1929 map continues the road over the sound to
  Skag. Done 2026-11-19, see `docs/langnasvagen.md`.
- **The 1894 atlas:** it has not been compared here. The atlas replacement intervals are unchanged by this step.
