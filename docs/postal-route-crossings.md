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

## Vårdö to Kumlinge (added 2026-11-23)

**Sources:**
- Swedish Wikipedia, [Vårdö](https://sv.wikipedia.org/wiki/V%C3%A5rd%C3%B6):
  - the postal road went from Vargata brygga (Båthusviken) through Vargata to Hullvik in Vårdö by;
  - its last original stretch runs from Holmsklint to Hullvik;
  - a memorial stone to postmen was raised at Hullvik in 1983.
- [Postvägen Stockholm–Åbo](https://sv.wikipedia.org/wiki/Postv%C3%A4gen_Stockholm%E2%80%93%C3%85bo): at Vårdö the
  rowing "took over at Delet towards Kumlinge".

**Where Hullvik is.** No source gives a position. It is placed from Ålands kulturarvsregister: Vå 14.3 and Vå 14.4,
sea marks "on the south side of the inlet to Hullvik", about 200 m south of the bay.

**The leg Vargata → Kumlinge** (1638–1911):

| part | how | dated from |
|---|---|---|
| Vargata → Hullvik | Vårdövägen, Vårdöbyvägen and Postrotevägen (OSM's name for the Holmsklint–Hullvik stretch) to the head of the bay | 1971 |
| Hullvik → Kumlinge | boat over Delet, 20.4 km (`boat_path.py`) | — |
| landing → Kumlinge by | Södra postvägen and Kumlingevägen | 1971 |

- **The road to Hullvik** ends 78 m from the water.
- **The landing on Kumlinge** is the south-west end of Södra postvägen, 21 m from the shore. No source names it. The
  street names "Södra postvägen" and "Norra postvägen" on Kumlinge are the evidence for the line across the island.
- **Render:** `crossing-delet.png`.

**The Kumlinge station** is in Kumlinge by; see the next section.

## Stations on buildings, and the clickable route

**Stations tied to a building or site** (`objectId` or `registryId` in `data/postal-route-stations.json`):

| station | tied to | basis |
|---|---|---|
| Storby | `building:osm:way-342899630`, Eckerö Post- och Tullhus (1828) | the post and customs house at the start of the route |
| Skarpans | `bom-gamla-skarpans`, Gamla Skarpans (site) | where the road ended at Skarpgården (Granlund). The post office moved to Nya Skarpans in 1842; this is not drawn |

**Correction.** The previous batch put the Kumlinge station at the gästgiveri remains at Krokarna (Ku 4.5). The 1971 map
(`renders/kumlinge-n71.jpg`) shows that the postal road runs from Kumlinge by north and then east along Norra
postvägen to the shore at Ramsholm. Krokarna lies on a side road to the north-west, so the station is in Kumlinge by
instead, on Kumlingevägen where the 1971 map draws the village (`renders/kumlinge-by71.jpg`). The milestone's place is
not known.

The other stations stay at village points, each with a stated note:
- **Frebbenby, Emkarby, Haraldsby:** no source identifies the gästgiveri building.
- **Vargata:** two candidates, neither certain.
  - the farm "Post" on the 1971–1978 base maps;
  - "gästgivargården å Västergårds" (1854, per Granlund).
- **Delvik:** the post pier, not a building.

**The clickable route** (in `dist/explorer.js`):
- **Hit-testing:** `drawPostal` records every line it draws and every station marker, and `postalHit` hit-tests them
  after the map's point hits, within 9 px of a station and 8 px of a line.
- **Leg stories:** clicking a leg opens its story. It shows:
  - the leg's period;
  - for each road part, the year and length, and the roads as buttons that open each object;
  - the ferries with their basis;
  - the boat note and the sources.
  The selected leg is drawn thicker.
- **Sea lines without a reviewed leg** (Grisslehamn–Signilskär, Kumlinge–Brändö and so on) open a short story saying
  they are schematic.
- **Station stories:** clicking a station opens its story, with a button for its building or site. The "Visa all
  objektdata" link goes to that object's page (`dist/object-link.js`). Legs get no such link.
- **Data:** the builder also writes `window.POSTAL_ROUTE_INFO` (the sources and the ferry crossings) for the stories.

**Checked in the app:**
- clicking the Delet line opens the Vargata–Kumlinge story;
- clicking Storby opens the station;
- its button opens the post and customs house.

**Tests:** `tests/postal-route-click.test.cjs`:
- the Kumlinge leg;
- clicking a leg, a sea line and a station;
- the stations' objects and positions.


## Kumlinge to Brändö (added 2026-11-23)

**Sources:**
- Swedish Wikipedia, [Gravstensgrundet](https://sv.wikipedia.org/wiki/Gravstensgrundet), and Ålands kulturarvsregister
  Br 8.4: in November 1773 an open sailing boat with ten people was wrecked at Gravstensgrundet, "under a sailing along
  the postal road between Kumlinge and Brändö". Lieutenant Taube and 7 others drowned.
- The Finnish [Suuri Postitie](https://fi.wikipedia.org/wiki/Suuri_Postitie) names the waters crossed: Lappvesi and
  Teili.
- No source names the piers or a post station on Brändö.

**The leg Kumlinge → Brändö** (1638–1911):

| part | how | dated from |
|---|---|---|
| Kumlinge by → the shore at Ramsholm | Kumlingevägen and Norra postvägen, to its east end, 13 m from the water | 1971 |
| the boat | 21.3 km past Gravstensgrundet (the line passes within 150 m of the registry point) | — |
| the landing → Brändö by | Brändövägen | 1991 |

- **The landing** is on Brändö's west shore, the shore point nearest Brändö by that lies within reach of a dated road.
- **The Brändö station** is on Brändövägen nearest Wikipedia's coordinates for Brändö by. Kyrkväg, beside the old
  stop, is a separate piece of road 283 m away and does not connect.
- **Render:** `crossing-brando.png`.

The crossing from Brändö over Skiftet to Vartsala stays schematic.

## The route at every zoom

`drawPostal` returned early in the Bomarsund fortress detail view, which turns on from 1832 at zoom 12 and above
whenever the fortress is on screen. So the route vanished around Skarpans and Bomarsund. It is now drawn at every zoom.

Tests (`tests/postal-route-click.test.cjs`):
- the Brändö leg;
- drawing with `fortressDetail` set.
