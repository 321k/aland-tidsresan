# The 1942 city traces reviewed against the orthophoto

Review: `data/mariehamn-frame-1942.json` (source `review:mariehamn-frame-1942`), applied at build time by
`scripts/mariehamn_frame_1942.py` as the last step of `scripts/build_temporal_objects.py`. Reviewed 2026-11-12.

## Why

The 1942 city stage contained four hand traces drawn on the 25 July 1942 orthophoto in a 4 m/pixel view, with two to
six points per street. Their corners meet: together they form a coarse rectangle around the town. They were not
attached to persistent objects and were shown 1942–1967 as streets; parts outside earlier reviewed cores were still
drawn 1968–1985. Compared with the original photo at 2 m/pixel, with every persistent road object labelled
(`frame.py`), none of them lies on a street:

| trace | points | finding | result |
|---|---|---|---|
| Södra stadsgatan · 1942 | 2 over 870 m | 60–70 m south of Skillnadsgatan, which the photo shows and which is already shown from 1871; forest and garden plots under the trace | rejected; its two 1942 leftovers and the 1968–1985 piece are gone |
| Västra strandens gata · 1942 | 6 over 1.1 km | crosses the western blocks diagonally through house lots (76 % more than 15 m from any road, median 28 m, max 164 m); its south end runs through forest to the Lotsberget cliff | replaced by Havsgatan (5 pieces) from the blocks' north edge to Mariegatan |
| Norra kvarterens tvärgata · 1942 | 2 over 845 m | the east half lies 20–30 m south of Köpmansgatan, which the photo shows with houses on both sides; the west half crosses forest and open ground | replaced by Köpmansgatan (4 pieces) |
| Strandgatan · 1942 | 5 | its core was already replaced by Strandgatan's reviewed object; the leftovers follow Strandgatan's northern piece (about 7 m) and Parkgatan (about 23 m); between them the trace cut diagonally through houses | replaced by `way-35011592` and Parkgatan, plus a retraced connector |

## The remaining 1942 traces

After the frame, every other 1942 city trace still drawn without an object was reviewed the same way, with the 1968
base map as a second witness (`map1968.py`). Afterwards no raw 1942 city trace is drawn in any stage.

| trace | points | finding | result |
|---|---|---|---|
| Förbindelse mellan infartsvägarna, 1942 | 7 over 1.1 km | the north-east part follows a straight clearing that the 1968 map shows as a power line; the west part crosses fields and forest about 25 m north of the main road; neither is a road on the photo | rejected, including its 1968–1985 pieces |
| Väg till västra stadskanten, 1942 | 5 | crosses the industrial plot and forest on Badhusberget; no road on the photo or the 1968 map | rejected, including its 1968–1985 piece |
| Västra stadsgatan · 1942 | 8 | Neptunigatan; the leftovers beside the reviewed core lie 3–17 m from Neptunigatan's objects | replaced by 8 Neptunigatan pieces north and south of the core |
| Gata öster om esplanaden · 1942 | 7 | Ålandsvägen; leftovers 6–19 m from its objects | replaced by 6 Ålandsvägen pieces |
| Torggatan · 1942 | 15 | seven short leftovers at junctions, 0–5 m from Torggatan's objects | replaced by 9 short Torggatan pieces |
| Tvärgata i norra staden · 1942 | 2 over 566 m | the east part lies 13–18 m south of Styrmansgatan, which the photo shows with houses; the west part runs into forest | replaced by 5 Styrmansgatan pieces |
| Norragatan · 1942 | 7 | four short leftovers at junctions, 0–1 m from Norragatan's objects | replaced by 4 short Norragatan pieces |
| Storagatan · 1942 | 3 | only a 34 m leftover beside Storagatan's reviewed core, drawn 1968–1985 | rejected |
| Södra kvarterens tvärgata · 1942 | 2 over 593 m | runs through the middle of the blocks, across house lots between two streets that are already shown; no street on the photo | rejected |
| Förbindelse till södra vägen · 1942 | 2 | crosses garden plots about 35 m west of the road the photo shows, which is already shown | rejected, including its 1968–1985 piece |

## What changes

- Every raw city-stage copy of the 14 traces is removed (features of street objects that carry a trace id as
  their source are kept). Their original pixels stay in
  `data/mariehamn-city-traces.json`.
- The 43 road objects that the photo shows in the traces' place get the photo as 1942 evidence
  (`{id}:frame-photo-1942`, `observationType: aerial`, `constructionYear: null`), an open state from 1942 to their
  previous start and a geometry period with their own earliest centre line. Every earlier state, period, evidence
  item and source link is kept after the new entries. They are drawn in the 1942 and 1952 city stages
  (Köpmansgatan was already drawn from 1952).
- Between the south end of the Strandgatan core and Parkgatan, the photo shows the street turning east along the
  cross street and then running straight south; no object covers it. That 146 m stretch is drawn 1942–1967 from a
  least-cost retrace over the pale road surface (`retrace-strand.jpg`), simplified to 2 m.

Earlier interpretations that change:

- The 1942 approach review left Strandgatan `way-35011592` to the city map's own Strandgatan trace; it is now shown
  from 1942 itself.
- The school-street review (`data/building-issue-review.json`) assumed the 1942 trace was a through street that
  Övernäs school cut in 1952, and started Köpmansgatan in 1952. The photo shows Köpmansgatan in 1942 and no street
  through the forest west of it, so Köpmansgatan now starts in 1942; its 1952 state and note are unchanged.
- South of Mariegatan the 1942 road followed an older line than today's Havsgatan (the 1985 section lies up to
  28 m east), so that section is not re-dated.

## Compiler checks

The review is rejected as a whole, leaving the catalogue unchanged, if an original trace or one of its stage copies
changed, a stage copy is not listed, an object's fingerprint or start changed, an object repeats or is not a single
line, a rejected trace carries objects, an object lies farther from the trace it replaces than the per-trace limit
(40 m for Västra strandens gata, 35 m for Norra kvarterens tvärgata, 30 m for Strandgatan, 25 m for Neptunigatan,
Ålandsvägen and Styrmansgatan, 10 m for the Torggatan and Norragatan junction pieces), or the retraced gap does
not join its two objects within 1 m.

Tests: `tests/mariehamn-frame-1942.test.cjs`, `tests/test_mariehamn_frame_1942.py`. Tests that pinned the earlier
interpretations now allow this reviewed evidence (marker `frame1942`).

Tests that pinned the earlier reviewed cores (Neptunigatan, Ålandsvägen, Strandgatan, Skillnadsgatan) expected the
coarse trace ends to stay drawn; they now accept their removal by this review.
