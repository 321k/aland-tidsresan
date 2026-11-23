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
| Kastelholm → Skarpans | breaks for 181 m (1968) and 97 m (1995–) | Tosarbyvägen and several Sundsvägen ways are unowned. These are the Sundsvägen review's open gaps at Klippan (`docs/sundsvagen.md`). |
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
