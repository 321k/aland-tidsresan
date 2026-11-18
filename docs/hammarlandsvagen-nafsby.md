# Hammarlandsvägen: the old road through Näfsby

Build step: `apply_hammarlandsvagen_nafsby` in `scripts/hammarlandsvagen_main_road.py`, run straight after the southern
review. Review data: `data/hammarlandsvagen-nafsby.json` (copied to `dist/assets/`), written by
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/prepare_nafsby.py`. Evidence:
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/`:
- the 1929 line: `data/trace-nafsby-1929.*`
- the village at four dates: `renders/nafsby-village*.jpg`
- the line with today's OSM roads: `renders/nafsby-klaralund-*.jpg`, `renders/nafsby-south-*.jpg`
- the result: `renders/result-nafsby-*.jpg`

The northern review (`docs/hammarlandsvagen-main-road.md`) left a gap at Näfsby: today's road is a 1968 bypass east of
the village, and the old road was not yet in the catalogue. This review fills that gap.

## Finding

The 1929 Hammarby parish map and its 1944 edition draw the main road leaving today's line south of the village. It ran
through Näfsby, past the school (Fsk.) and Klaralund, and rejoined today's road at Korsbroström. Read on the 1929 map
and compared with OpenStreetMap 2026, almost all of it survives as smaller roads, within 0–12 m of the line. The bend
at Klaralund is within 25 m, which is within the sheet's error.

Distances in the table are along the 1929 line from Mattas.

| along the 1929 line | today | from | until |
|---|---|---|---|
| 0–250 m | Hammarlandsvägen (Västmyra object), 10–20 m from the 1929 line | 1929 | (today) |
| 250–320 m | gone | 1929 | 1968, then unknown |
| 320–400 m | Lillåkersgränd, its northern 85 m | 1929 | (today) |
| 400–530 m | Lillåkersgränd (cycleway, way 1419026567) | 1929 | 1968; unknown until 1985 |
| 530–680 m | way 1419026568 | 1929 | (today) |
| 680–810 m | Västmyra · skolvägens östra del | 1929 | (today) |
| 810–1075 m | Västmyra · gamla skolvägen (way 167700519) | 1929 | (today) |
| 1075–1140 m | gone | 1929 | 1968, then unknown |

Notes on the table:
- **First stretch:** the northern review ended the same-road stretch at 14 313 m along the reference. The 1929 line
  stays within 10–20 m of today's road (the review's same-road rule is about 25 m) until 14 420 m. There it turns
  into the village. The north review data now ends Västmyra's first 1929 cut at 14 420 m (`prepare.py`,
  `nafsby-south`).
- **The parallel stretch (400–600 m):** on the 1968 and 1978 base maps it is only a thin line along the west edge of
  the new road, not securely a road. The Hammarland rural review dated it from 1985 for the same reason. The two
  objects on it are therefore treated differently:
  - Way 1419026567 is open 1929–1968, `unknown` 1968–1985 and open again from 1985.
  - Way 1419026568's 1929 period uses its own later (1985) geometry, 154 m long. That includes the southern arm on
    the parallel stretch. In 1968–1985 the object draws, as before, only the 82 m arm the 1968 map shows.
- **Old school road:** the 1929 period covers only its main path. The short branch east to today's road (its second
  path) is the younger junction with the bypass.
- **The two vanished pieces:** they make up one new object, "Gamla Hammarlandsvägen · Näfsby" (two paths, 142 m in
  total). Each piece is the 1929 line between today's roads, with its ends fixed to them. The 1968 map draws no road
  there, and nothing of either piece is in OpenStreetMap.

Each existing object keeps its identity, evidence and later periods. Each gets an earlier open state and geometry
period, cut from its own coordinates. The marker `hammarlandsvagenMainRoad` names this review
(`review: review:hammarlandsvagen-nafsby`).

## Checks in the build step

The shared step (`_apply`) gained optional fields, all checked before any change:
- `laterGeometry`: the early period may cut a later geometry of the same object.
- `pathIndex`: dates one path of a geometry with several paths. Without it, such a geometry can only be dated whole,
  never implicitly.
- `gapUntil`, with `gapBasis`: an `unknown` state between the early period and the object's first year. This needs a
  map in the gap marked `unclear` (none marked `absent`) and a stated reason.
- `oldRoad.paths` and `endObjects`: an old line made of several pieces. Every end must lie on one of the named
  objects (within 1 m).
- `route`: the dated cuts and the old line, in order along the old road. Consecutive pieces must meet within 2 m, so
  the road through Näfsby is one connected line in 1929–1968.

The existing checks still apply: fingerprints, applies once, first year, 50 m minimum cuts, no long run beside a road
open at the same time, and no surviving OSM road along the old line. The northern and southern reviews give the same
result as before. The only change is the moved Näfsby boundary.

## Open items

- Drygsböle (11.8–12.4 km), looked at again after this batch: `renders/drygsbole-village.jpg`,
  `drygsbole-farm-1929-1944.jpg`, `drygsbole-wide-1929-1917.jpg` and `drygsbole-east-1929-1944.jpg`.
  - The 1929 and 1944 maps draw the road from Bolstad to the Drygsböle farm, and from the farm north-east towards
    Boda.
  - South of the farm they draw no road to the lake shore at 11.8 km. The only line there runs east along the field
    edge towards Skamkulla, and it is drawn as a single line, not as a road.
  - The 1917 Senate sheet has no drawing here.
  - So the 1929 through-route cannot be read from these maps. Nothing is dated until another source (an aerial photo
    or a cadastral map) shows it.
