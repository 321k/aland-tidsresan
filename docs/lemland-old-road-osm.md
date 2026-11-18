# Gamla Lemlandsvägen in today's road network

Build step: `scripts/lemland_old_road_osm.py`, run straight after `lemlandsvagen_main_road.py` (last in
`build_temporal_objects.py`). Review data: `data/lemland-old-road-osm.json` (copied to `dist/assets/`), written by
`docs/reviews/lemland-old-road-osm-2026-11-18/scripts/prepare.py`. Evidence and renders:
`docs/reviews/lemland-old-road-osm-2026-11-18/`.

## Problem

The early-map review (`docs/lemlandsvagen-main-road.md`) added the old road between the canal and the church village
as four objects traced on the 1929 parish map, open from 1917 until the edition after the last base map that draws
them, then `unknown`. Much of the old road is still in use today. From the 2014 OSM snapshot on, those roads were
drawn as separate, unowned source lines: one physical road with two identities. The 1929 line was also 3–30 m off
where today's line is exact.

## What survives

Every candidate way was checked by eye on the 1929 parish map, the 1985 base map (accurate to a few metres) and OSM.

| old-road object | survives as (OSM 2026) | not surviving |
|---|---|---|
| Övre-Börs–Östergård | Knutsbodavägen from node 2 (its first 35 m is the junction with the 1985 bypass) | the 1929 corner at Fridelund; Knutsboda–Östergård–Dragsvik |
| Johans | Kockobacka from node 4 (nodes 0–4 are a later link north to the bypass) | both ends, where the 1968 bypass runs |
| Mangård–Söderby | Kommunrundan (way/173992646, way/932105680); a service road, Norra Söderbyvägen (way/611965363 nodes 0–8, 611965361, 179382606, 1180076498, 611965359, 611965360, 179382608, 179382607, 179382609) | Frankbo, where the 1968 bypass cuts it; the last stretch into the church village |
| Tomtebo–Solstrand | nothing; only short driveways cross it | the whole object, which is unchanged |

At the Norrbyvägen crossing in Söderby, the old road runs straight across, as OSM's Norra Söderbyvägen does. The
1929 trace wobbled into the junction there. That wobble had produced an apparent 85 m overlap with Norrbyvägen, and
it is gone.

## Övre-Börs: the corner at Fridelund was straightened

The 1929 and 1948 parish maps draw a sharp corner where the road meets the Fridelund road. The 1968 base map is the
first to draw a smooth curve, and 1978, 1985 and OSM (Knutsbodavägen) have the same curve. That settles the question
the early-map review left open for this part: it is a real straightening between 1948 and 1968, not generalisation.
1968 is the first map evidence, not a construction year. The remnants of the corner (a track and the east end of
Bolviksvägen) are not owned by the old road. The straighter drawing of Knutsboda–Dragsvik on the 1968 and 1978 maps is
still not settled; there the 1929 line is kept.

## Model

- **Identity.** One object per road. The three objects keep their ids and evidence; their names add today's names.
  They are open from 1917 with no end. The single `unknown` state is replaced by geometry coverage: from 1995, each
  object's geometry is partial and holds only its surviving parts. The rest is not claimed after the 1985 base map,
  which does not mean it disappeared then.
- **Position.**
  - Where the road survives, every phase uses OSM's centre line, so the 1929 sheet error does not move the road and
    the line does not jump in 1995.
  - Between surviving parts, the 1929 trace is moved linearly from the offset measured at one OSM anchor to the offset
    at the next, or to zero at a trace end. Those ends already rest on today's road.
  - Small smoothing loops (up to 30 m) are cut. The raw trace geometry is kept unchanged and referenced from the
    `osm-review` evidence.
- **Phases.**
  - Övre-Börs: 1917–1968 corner; 1968–1995 curve; 1995– Knutsbodavägen.
  - Johans and Mangård–Söderby: 1917–1995 full; 1995– surviving parts.
- **Source ownership.**
  - 2026: exactly the reviewed way ranges. Later links to the bypass stay unowned.
  - 2014, 2021 and 2025 split the same OSM ways differently. Each feature with the same OSM id owns the runs of it
    (sampled every 2 m, at least 25 m long) that lie within 15 m of a surviving line.
  - Kockobacka is not in the 2014 snapshot. It is still drawn there, as an inferred continuation between 1985 and
    2021: the snapshot not having a road is not evidence that it was gone.
  - 42 source ranges in all. No unowned stretch longer than 30 m runs along a surviving line; what remains are
    side-road junctions and Kommunrundan's turning loop.

## Checks in the build step

- Fingerprints of the four old-road objects, their trace geometries, the 14 OSM 2026 ways and every same-id snapshot
  feature. Any snapshot feature with one of those ids must be in the review. The review applies once.
- Phases run from 1917 without gaps, and the surviving phase begins where the reviewed maps end.
- Every phase before 1995 is one simple line. Each of its ends rests (within 1 m) on a road open at that time that
  its trace end rests on. Today's road and other old-road objects both count.
- Same road: in phases marked `traceCheck`, no point is more than 40 m from the 1929 trace and 90 % are within 25 m.
  This allows for the sheet error and the junction wobbles in the trace. The 1968 curve at Övre-Börs fails this
  check, as it should.
- No phase runs more than 80 m continuously beside another road open at the same time. Junctions and crossings give
  short contacts: up to 40 m at the 1985 bypass.
- The surviving parts lie on the line before them (within 5 cm) and do not overlap. Owned ranges do not overlap
  existing owners.

## Open items

- Knutsboda–Östergård–Dragsvik: the 1968 and 1978 maps draw it straighter than 1929. Settle whether that is a
  straightening; if so, find the 1968–1985 line.
- Check the 1995 base map for the parts that are not in OSM.
- Norrbyvägen is dated from 1985, but the 1929 map draws the north–south road at the Söderby crossing. It is a
  separate dating question for that object.
- Tomtebo–Solstrand: decide whether the shore road disappeared after 1985 (base maps after 1985) or survives
  unmapped.
