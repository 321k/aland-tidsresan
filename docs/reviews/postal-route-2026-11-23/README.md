# Postal route on real roads: survey, 2026-11-23

## How the route is drawn today

`window.POSTAL_ROUTE` in `dist/archive.js` holds 15 representative stops, joined by straight lines. The file says so:
"Representative places, not surveyed roads". The stops on the main island are Eckerö, Marsund, Boda, Färjsundet,
Kastelholm, Bomarsund and Vargata. The route is drawn for 1638–1911.

## How far dated roads reach

Method: `scripts/route_survey.py`. For each year it builds a graph from the catalogue's open road geometries (vertices
joined within 15 m) and finds the shortest road path between the roads nearest two consecutive stops. The full output
is in `route-survey.txt`.

| leg | 1929 | 1968 | 2026 |
|---|---|---|---|
| Eckerö → Marsund | by road, 9.0 km | by road | by road |
| Marsund → Boda | broken | by road, 8.2 km | by road |
| Boda → Färjsundet | broken | broken | 31.9 km (a detour; straight 13 km) |
| Färjsundet → Kastelholm | broken | by road, 4.4 km | by road |
| Kastelholm → Bomarsund | broken | broken (181 m) | broken (97 m) |
| Bomarsund → Vargata | broken (sound and Vårdö) | broken | broken |

In 1800 and 1900, only scattered c.1800 and 1894 atlas pieces are dated, so the route cannot follow roads there.

## What this means

1. **The stops are not the postal road's stations.** Boda (19.8, 60.19) sends the road path on a 32 km detour even in
   2026. The heritage register places the postal road elsewhere:
   - along Hammarlandsvägen at Kattby (Ha 12.5) and at Postad (Ha 17.8);
   - beside Emkarbyvägen at Ringsböle (Jo 23.6, Jo 23.7);
   - beside Sundsvägen between Haraldsby and Kulla (Sa 10.14, Su 13.16, Su 1.5).

   The route would then run Eckerö, Marsund, Hammarland, Emkarby, Godby, Färjsundet, Haraldsby, Kastelholm, Kulla,
   Bomarsund, Prästö, Vårdö. It needs stops at the actual post stations (gästgiverier) from a source.
2. **Gaps in the 1929 network** along that line, to review leg by leg:
   - Drygsböle on Hammarlandsvägen;
   - Hammarland to Emkarby;
   - Godby to Färjsundet;
   - Färjsundet to Haraldsby;
   - Kastelholm to Bomarsund, which has a 97–181 m break even today;
   - Prästö and the road on Vårdö.
3. **How to draw the route before a road's first dated year.** Most roads are dated from the parish maps of
   1928/1929, but the route runs 1638–1911. One option is to draw the same road objects' earliest surveyed geometry,
   with a note that the line is the 1929 survey. The other is to keep the coarse line until a road is dated.

## Post stations (2026-11-23)

The sources name these post stations (gästgiverier) across the main island:
- Storby (Eckerö), where the post house Ängstorp was built in 1778;
- Frebbenby (Hammarland);
- Emkarby;
- Haraldsby;
- Skarpans;
- then Vårdö.

The road passed Kastelholm. Sources:
- [aland.se, Postvägen över Åland](https://aland.se/besok/sevardheter/postvagen-over-aland/);
- [Wikipedia, Stockholm–Turku mail route](https://en.wikipedia.org/wiki/Stockholm%E2%80%93Turku_mail_route).

A full list of stations needs Jan Andersson, *Postvägen över Åland* (1999).

The stations are positioned at the OSM village points for Storby, Frebbenby, Emkarby, Haraldsby and Vargata. Skarpans
uses the catalogue's Gamla Skarpans. These stations replace the representative stops in `route_survey.py`; the results
are in `route-survey-stations.txt`.

## Base-map roads along the route (step 1)

`scripts/osm_route.py` routes each leg on today's OSM roads and lists every way on the route that no catalogue object
owns. Output: `osm-route.txt`. `scripts/which_sheet.py` lists the registered base-map scans that cover a point.

| leg | 1968 network | what is missing |
|---|---|---|
| Storby → Frebbenby | connected | Eckerövägen and Sandmovägen at Storby are owned by no object (the road connects via the 1929 objects) |
| Frebbenby → Emkarby | connected | — |
| Emkarby → Haraldsby | breaks for 5 km (2.8 km in 1995) | Postgårdsvägen, Nya Godbyvägen and Sundsvägen from Godby to Färjsundet and Haraldsby are unowned. Registered base maps: 101209 and 102107 (1968–1993). |
| Haraldsby → Kastelholm | connected | — |
| Kastelholm → Skarpans | breaks for 181 m (1968) and 97 m (1995–) | Tosarbyvägen and several Sundsvägen ways are unowned. These are the Sundsvägen review's open gaps at Klippan (`docs/sundsvagen.md`). Done 2026-11-23, see below. |
| Skarpans → Vargata | the sound | Prästö and Vårdö: registered base maps 101212, 101403 and 102301 (1968–1995). Prästö is an open item in the Sundsvägen review. |

Notes:
- The shortest OSM route is not necessarily the postal road. Nya Godbyvägen, for example, is a 1978 road.
- Each leg needs a map review, not just the missing ownership.

### Emkarby → Haraldsby on the 1968 map (first look)

- Ringsbölevägen, the main road from Ringsböle past Tingsbacka and Buskböle to Gölby, is in the catalogue from 1968.
- The 1968 network breaks east of Gölby and resumes only at Färjsundet. What is missing is Godbyvägen's northern part
  through Godby, and the road east from Godby to Färjsundet and Haraldsby (sheet 102107, `renders/godby-102107-1968.jpg`).
- The OSM route from Emkarby runs through Gölby. Whether the postal road ran that way, or more directly from Emkarby to
  Godby, needs the parish maps.

## Emkarby → Haraldsby on the base maps: done 2026-11-23

See `docs/postal-route-godby.md`. Added for this step:
- scripts: `holes.py` (the stretches of a leg that no dated road covers in a year, measured by geometry),
  `line_on_map.py`, `prepare_godby.py`;
- renders: `gf-*`, `h1`–`h3`, `ext*`, `bend-*`, `golby-1968.jpg`;
- `scope-audit-godby.json`, `batch-postal-route-godby.patch` with its `patch-verification-godby.log`, and
  `node-tests-godby.log`.

## Vårdö on the base maps (first look, 2026-11-23)

Renders: `vardo-ov-1985.jpg`, `tofto-sheet.jpg` (1970, 1978), `toftos-sheet.jpg` (1970, 1978, 1985) and
`vargata-sheet.jpg` (1971, 1978). Today's Vårdövägen is two objects, both dated only from 1985: the Töftö part
(`road:qgis:tofto:vardovagen-200km1`) and the Vårdö part (`road:qgis:vardo:vardovagen-200km1`).

- **The crossing from Prästö moved.**
  - In 1970 and 1978 the ferry landed at Färjhamn on Töftö's north-west shore. From there the main road ran past
    Södergård to Töftö village.
  - Today's landing on the south shore is a dashed (planned) road in 1978, and the main road from 1985.
- **Töftö to Vårdö.**
  - In 1970 the road from Töftö village runs north-east past Påvals and no further.
  - In 1978 it continues north past Storsved to the shore facing Gersholm and Kumnäs; the map notes a ferry to Vårdö.
  - The bridge via Gersholm is first on the 1985 map.
- **Vargata.** In 1971 and 1978 the road from the Kumnäs landing ran north into Vargata and then in a bend north
  through Västergård and Östergård, past the farm marked "Post". Today's straight road through Vargata is first on the
  1985 map, which is why the earlier review dated the object from 1985.
- **The postal road itself crossed by boat.** The sources give the crossing from Bomarsund to Vårdö (aland.se mentions
  the boat fare in the 1770s), and the route ended at Vargata, where the "Post" farm stands on the base maps. The road
  across Töftö and the bridges belong to the 20th-century road network, not to the postal route.

## Vargata on the base maps: done 2026-11-23

See `docs/postal-route-vardo.md`. Added for this step: `scripts/prepare_vardo.py`, the renders `vbend-*`,
`scope-audit-vardo.json`, `batch-postal-route-vardo.patch` with `patch-verification-vardo.log`, and
`node-tests-vardo.log`.

## Storby end (first look, 2026-11-23)

- **The start is the post and customs house.** The route should start at the post and customs house by Storby harbour
  (`building:osm:way-342899630`, E 20 474 707 N 6 678 693), not at the village point.
- **Connections.** From Labbas to Frebbenby the catalogue's roads already connect in 1968 and 2000. From the post house
  nothing is dated: Eckerövägen's west end (OSM 25208185 and the junction pieces 174570487, 174570484, 172716458,
  174570483, 1182793512) and the access on Sandmovägen belong to no object in any year.
- **Which maps cover the harbour.**
  - The harbour lies on base-map sheet 1012 15, which NLS printed together with 0034 15 (1968, 1978, 1985) and with
    1012 03 (1994).
  - The scans are in the local cache, but only the 1994 one is registered, and its mesh covers just the 1012 03 part.
  - The 1929 Eckerö parish map (map-39091228) and its 1956 edition also stop at about E 20 475 200.
  - No source in `data/historical-map-sources.json` covers the post house.
- **The 1994 scan, extrapolated** (`renders/harbour-1994.jpg`), marks "Post/Posti" at the post house and draws
  Eckerövägen from Labbas round to it, 10–20 m from OSM. `scripts/rural_registration.py` does not allow evidence from
  outside a registered frame, so this is only a screening.
- **To document the stretch:** register sheet 1012 15 from the cached scans (1968, 1978, 1985, 1994) on its printed grid.

## Storby on the base maps: done 2026-11-23

See `docs/postal-route-storby.md`. Sheet 1012 15 is registered from the cached scans with these scripts:
`scripts/grid_crosses.py` and `scripts/make_registration.py`, writing `data/data-reg-*.json` and
`data/registrations-101215.json`. Also added: `scripts/prepare_storby.py`, the renders `harbour-101215-*` and `reg/`,
`scope-audit-storby.json`, `batch-postal-route-storby.patch` with `patch-verification-storby.log`, and
`node-tests-storby.log`.

## Kastelholm → Skarpans on the base maps: done 2026-11-23

See `docs/postal-route-sund.md`. The leg now connects on dated roads from 1968. Three short Sundsvägen pieces were
added: at the Lappböle sheet edge from 1968, and on both sides of Klippan from 1978. The 1968 straight road at Klippan
is left to the Sundsvägen review. The Tosarbyvägen hole came from the Kastelholm stop point, off the route.

Files:
- `scripts/prepare_sund.py`;
- the renders `lappbole-*`, `lappz-*`, `lappj-*`, `klippan-*`, `klippw-*`, `klippe-*` and `klipp-we-sheet.jpg`;
- `scope-audit-sund.json`;
- `batch-postal-route-sund.patch` with `patch-verification-sund.log`;
- `node-tests-sund.log`.

## The route on the roads, and the parish maps 1928–1929: done 2026-11-23

See `docs/postal-route-roads.md` and `docs/postal-route-1929.md`. The route is drawn on dated roads between the post
stations: Frebbenby → Emkarby from 1929, the other land legs from 1968. Still open: the 1929 roads at Färjsundet and
through Haraldsby, the Lappböle sheet edge before 1968, and the Storby harbour before 1968.

Files:
- `scripts/prepare_1929.py`;
- `route_survey.py`, which now takes `VERBOSE=1` to list the objects on each leg;
- the renders `p29-*`, `p44-*`, `b68-farjz.jpg` and `farj-29-68.jpg`;
- `scope-audit-1929.json`;
- `batch-postal-route-roads.patch` with `patch-verification-roads.log`;
- `node-tests-roads.log`.

## Färjsundet and Haraldsby on the parish maps: done 2026-11-23

See `docs/postal-route-haraldsby.md`. Emkarby → Haraldsby now runs on 1929 roads with the Färjsundet ferry, and
Haraldsby → Skarpans runs through the village.

Files:
- `scripts/prepare_haraldsby.py`;
- the renders `farj-2944.jpg`, `h*-cat.jpg`, `h-sheet.jpg`, `hog*`, `lapp29.jpg`, `lapp44.jpg`, `lapp28b.jpg`,
  `lapp-parish.jpg` and `route-haraldsby-68.jpg`;
- `scope-audit-haraldsby.json`;
- `batch-postal-route-haraldsby.patch` with `patch-verification-haraldsby.log`;
- `node-tests-haraldsby.log`.
