# Road remnants from the heritage register

Build step: `apply_road_remnants` in `scripts/road_remnants.py`. It runs after the Postad step and before the atlas
review's late pass.

Review data: `data/road-remnants.json` (copied to `dist/assets/`), written by
`docs/reviews/road-remnants-2026-11-20/scripts/prepare_remnants.py`.

Renders: `docs/reviews/road-remnants-2026-11-20/renders/`. They were made with `scripts/remnant_window.py`, which draws
the register outline over the parish map together with the catalogue's roads for a chosen year.

## What the register adds

The heritage register (Ålands landskapsregering) records 16 road remnants ("Väglämning"), each with a surveyed outline.
These are the dashed brown outlines on the map. They are evidence of where the old roads ran, independent of the old
maps. Their dating is broad ("Sentid", from 1500), so they do not set first years.

| remnant | road | distance | reading |
|---|---|---|---|
| Lu 6.1 Skag | Gamla landsvägen · Skag | inside (109 m) | the sharp corner in Skag village on the 1929 road; confirms the trace |
| Lu 2.1 Krogstad | Långnäsvägen | 10 m | the 1929 road at 1.45 km; same road within the sheet error |
| Le 16.16 Rörstorp | Lemlandsvägen (east) | 30 m | the 1700s road bed slightly south of today's line at 3.4 km; same corridor |
| Le 18.7 Söderby | Gamla Lemlandsvägen · Mangård–Söderby | inside (55 m) | on the old road the 1929 map draws |
| Ha 12.5 Kattby | Hammarlandsvägen · Kattby västerut | 20 m | the postal road beside today's road; same corridor |
| Jo 23.6, Jo 23.7 Ringsböle | Emkarbyvägen | 17 m, 8 m | the postal road beside it |
| Sa 10.14, Su 13.16, Su 1.5 | Sundsvägen · Haraldsby–Kulla | 10–17 m | the postal road beside it |
| Ha 17.8 Postad | Äldre väg vid Korsberg | inside | an old curve the first Hammarlandsvägen review missed: `docs/hammarlandsvagen-postad.md` |

The step adds each register entry as `heritage-register` evidence to its road. The evidence supports geometry and
identity where the road runs inside the outline, and identity only where the remnant lies beside the road. It also
records `registerRemnants` (code and distance) on the object. No states or geometries change.

Not matched, and listed in the review with the reason:
- Fi 8.17: the old ferry road at Godby, in use until 1761. The catalogue has no road for it.
- Jo 18.11: the road to the Kungsö battery, built in 1916.
- Ma 33, Ma 37, Ma 47: roads in Mariehamn, which have not been reviewed here.

## Checks

The step is rejected as a whole, leaving the catalogue unchanged, if:
- it was already applied;
- an entry is not a single register road remnant;
- a road's fingerprint or an outline's digest changed;
- an outline is no longer within its stated distance of the road's geometry in the stated year;
- the overlap no longer matches what is claimed.

Tests: `tests/test_road_remnants.py` and `tests/road-remnants.test.cjs`.

## Open items

- Rörstorp (Le 16.16) and Kattby (Ha 12.5) lie 20–30 m off today's line. If more of these road beds are found, those
  stretches could get old-road objects of their own.
- The register's Skag remnant belongs to the road between Jomala and Föglö. That suggests the Skag corner is older than
  1929, but the 1917 atlas draws no road there, so 1929 is kept.
