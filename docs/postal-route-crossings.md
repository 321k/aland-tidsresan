# Postal route: the crossings at Färjsundet and to Vårdö

Part of the work to draw the postal route on real roads (`docs/postal-route-roads.md`). This batch:
- draws the Färjsundet ferry in two periods;
- replaces the straight line from Skarpans to Vargata with the boat crossings to Vårdö: from Delvik before 1670, and
  from the Bomarsund pier from 1670.

## Färjsundet before 1761

Ålands kulturarvsregister, **Fi 8.17** ("Väglämning – Godby"), describes:
- **The descent:** a serpentine road in a steep ravine, about 100 m long, down to the old ferry place on the west
  shore, about 120 m south of today's bridge.
- **The road west:** remains of the postal road run west from the top of the descent to today's main road.
- **The dates:** in use until 1761, when a new ferry place was built north of today's bridge. That is the landing of
  Färjvägen (`docs/postal-route-haraldsby.md`). When it came into use is not known.

The registry outline is in `docs/reviews/postal-route-2026-11-23/data/registry-fi-8-17.json`, fetched 2026-11-23. The
road-remnants review had left this entry unmatched (`data/road-remnants.json`).

**New object "Gamla färjvägen · Färjsundet"** (`road:finstrom:gamla-farjvagen:farjsundet`):
- **Build step:** `apply_postal_route_1761` in `scripts/postal_route_1761.py`, after the Haraldsby step. It uses the
  old-road check of `_apply` in `scripts/hammarlandsvagen_main_road.py`.
- **Review data:** `data/postal-route-1761.json` (copied to `dist/assets/`), written by
  `docs/reviews/postal-route-2026-11-23/scripts/prepare_1761.py`.
- **Trace (481 m):**
  - from the east end of von Knorringsvägen along today's main road, using its own coordinates, for 149 m (the
    registry says the remains continue west under it);
  - then along the middle of the registry outline to the shore.
  - 326 m of it lies within the outline, taking 5 m around it. The midline does not reproduce the serpentine bends.
- **Dates:** open 1638–1760, then unknown.
  - 1638 is the postal route's opening. The road's own start is not known.
  - 1761 is the registry's date for the move.
  - The two dated sources are recorded as `historical-source` and `heritage-register`, not as map reviews.
- **End:** at the ferry place, a stated free end.

The leg Emkarby → Haraldsby now has two periods:
- **1638–1760:** von Knorringsvägen, the old ferry road and the ferry `farjsundet-1761`.
- **1761–1911:** Hamnvägen, Färjvägen and the ferry `farjsundet`.

Where the old ferry landed on the east shore is not known. The crossing ends where the road from Vårsundet reaches the
shore.

## The boat to Vårdö

The crossing was rowed by the Finby post farmers in the early period ("Finbyroten"), and later from Skarpans
(Persnäs, "Skarpgården"). Sources:
- Johan Granlund, [Stora landsvägen över Åland – postvägen ned till kaj i Delvik](http://granlundslada.blogspot.com/2017/06/stora-landsvagen-over-aland-ned-till.html) (2017)
  and [Vy över Finby samt karta över Bomarsundsområdet år 1650](http://granlundslada.blogspot.com/2013/01/vy-over-finby.html) (2013).
  These cite:
  - Hans Hansson's maps of 1650, which end the road at a post pier in Delvik ("Deele Wijken") and show no road or pier
    at Bomarsund;
  - Bjurman 1743: "Bomarsunds fjärd, till Wargata på Wårdö 1 mil";
  - a 1745 map of the post pier's loading place in a small bay at Bomarsund.
- Wikipedia, [Stockholm–Turku mail route](https://en.wikipedia.org/wiki/Stockholm%E2%80%93Turku_mail_route), and
  Ålands landskapsregering, [Postvägen över Åland](https://aland.se/besok/sevardheter/postvagen-over-aland/).

**When the pier moved.** The sources disagree:
- Jan Andersson's *Postvägen över Åland* (as quoted by Granlund) has the 1650s, and Bomarsund as the end from the
  start.
- Granlund dates the Bomarsund pier to the 1670s or 1670–80s.

The route switches at 1670, which is uncertain by a decade or more.

**Stations and legs** (`data/postal-route-stations.json`):
- **New station Delvik:** at the end of today's Delviksvägen on the shore of Delvik, on the route until 1669.
- **Skarpans:** on the route from 1670.
- **Before 1670:**
  - Haraldsby → Delvik by road;
  - Delvik → Vargata by boat to Båthusviken, then by road (Båthusviksvägen) to Vargata.
- **From 1670:**
  - Haraldsby → Skarpans by road;
  - Skarpans → Vargata: by road to the pier at Bomarsund, by boat to Båthusviken, and by road to Vargata.
- **Båthusviken:** the landing in Vargata, from one source, at the west end of Båthusviksvägen.
- **The Bomarsund pier:** the pier the 1928 parish map draws where the old road past the ruins ends
  (`road:sund:gamla-landsvagen:bomarsund`), in the bay where Bryggvägen ends. It is taken to be the small bay of the
  later steamboat pier where Granlund places the post pier.

**The boat lines.**
- `docs/reviews/postal-route-2026-11-23/scripts/boat_path.py` computes them: the shortest path through water on a
  20 m grid of today's OSM coastline, keeping 60 m from land where possible, then simplified.
  - From Bomarsund the line runs north up the sound between Sund and Prästö and east over Vargata fjärden, north of
    Prästö and Töftö (6.5 km).
  - From Delvik it runs down the bay and east over the fjärd (7.8 km).
- They show the way over water nearest the landings, not a recorded fairway. The sea stood higher then, so channels
  were if anything wider.
- They touch land only within the last few metres at the landings.
- Renders: `crossing-boat.png`, `route-east.png`.

**The road legs:**

| leg | years | roads dated from |
|---|---|---|
| Haraldsby → Delvik | 1638–1669 | 1985 (Mångstektavägen; no earlier map covers Delvik) |
| Skarpans → the Bomarsund pier | 1670–1911 | 1928 |
| Båthusviken → Vargata | 1638–1911 | 1971 |

## Builder and drawing

`scripts/build_postal_route.py`:
- **Legs:** each leg holds for its `years` and may use only its listed `crossings`.
- **Boat legs:** each is made of `parts`:
  - a road part to the departure pier, unless the station is the pier;
  - the boat line;
  - a road part from the landing.

`dist/archive.js`: Delvik is a stop until 1669 and Skarpans from 1670, as Grisslehamn moves in 1756.

`dist/explorer.js`:
- **Which leg:** the one for the year.
- **How:** road parts solid, boat lines dashed.
- **Fallback:** a straight dashed line when no leg is found.
- **Texts:** they describe the crossings.

## Checks

Scope (`docs/reviews/postal-route-2026-11-23/scope-audit-crossings.json`):
- 1 object added;
- 1 geometry added;
- 3 sources added (the review, the registry entry and the route's opening);
- nothing changed, and the atlas roads file is unchanged.

Tests:
- `tests/test_postal_route_1761.py`, the replay;
- `tests/postal-route-crossings.test.cjs`:
  - the old ferry road's dates;
  - the two Färjsundet periods;
  - the two boat crossings;
  - `drawPostal` for 1650, 1700 and 1800, with a recording canvas.
- Updated for the new periods and stops:
  - `tests/postal-route-roads.test.cjs`;
  - `tests/postal-route-haraldsby.test.cjs`;
  - `tests/transport-routes.test.cjs` (untracked, in the patch).
- The object count in `tests/temporal-objects.test.cjs` gets +1.

## Open items

- **A recorded fairway:** a historical map of the boat route, such as the 1745 or 1756 maps Granlund cites.
- **Pier sites:** the exact sites of the post piers at Delvik and Bomarsund.
- **East landing at Färjsundet:** where the pre-1761 ferry landed on the east shore.
- **Delvik on the maps:** the roads to Delvik on a map earlier than 1985.
