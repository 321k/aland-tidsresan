# Postal route on the dated roads

The postal route across Åland (1638–1911) used to be drawn as straight lines between 15 representative places
(`window.POSTAL_ROUTE` in `dist/archive.js`). On the main island it now follows the catalogue's roads between the post
stations. This completes the plan in `docs/reviews/postal-route-2026-11-23/README.md`.

## Stations

`data/postal-route-stations.json` lists the post stations (gästgiverier) the sources name, in order:
- Storby: the post and customs house by the harbour;
- Frebbenby;
- Emkarby;
- Haraldsby;
- Skarpans;
- Vargata, where the route ended on Vårdö.

The file also lists the legs between them: four by road and the boat crossing from Skarpans to Vargata.

**Positions:**
- Storby: the post and customs house (OSM building 342899630);
- Frebbenby, Emkarby, Haraldsby and Vargata: the OSM village points;
- Skarpans: the catalogue's Gamla Skarpans.

A village point is not the station building, whose site is not known here.

In `dist/archive.js` these six stations replace the representative stops Eckerö, Marsund, Boda, Färjsundet,
Kastelholm, Bomarsund, Vargata and Vårdö. The stops in Sweden, in the archipelago and in Finland are unchanged.

## Building the road legs

`scripts/build_postal_route.py`, run after `build_temporal_objects.py`, writes `dist/postal-route-roads.js`. That file
holds `window.POSTAL_ROUTE_STATIONS` and `window.POSTAL_ROUTE_ROADS`.

For each road leg the script works as follows:

1. **The network for a year.** The graph is every geometry the roads had while open in a period beginning by that year,
   within 4 km of the leg. This includes old roads that closed before it.
   - Vertices within 15 m are joined.
   - A road end within 40 m of a vertex of another road is joined by a straight connector. This covers a junction the
     maps draw where one object follows today's road and the other the older line beside it.
2. **Which year.** The candidate years are the years in which some road period begins, from 1800 on. The leg takes the
   first year in which:
   - both stations lie within 150 m of a road;
   - the network connects them.
3. **The line.** The shortest path in that year's network, made of the road segments' own coordinates. The leg records:
   - the year;
   - the length;
   - the objects it runs on;
   - any connectors used.

| leg | year | length | connectors |
|---|---|---|---|
| Storby → Frebbenby | 1968 | 12.4 km | one, 27 m (the Marsundsvägen junction at Frebbenby); the Marsund ferry |
| Frebbenby → Emkarby | 1929 | 11.8 km | one, 34 m (the Smedens junction at Drygsböle) |
| Emkarby → Haraldsby | 1929 | 11.7 km | none; the Färjsundet ferry |
| Haraldsby → Skarpans | 1968 | 13.1 km | none; through Haraldsby village |
| Haraldsby → Delvik (1638–1669) | 1985 | 14.7 km | none |
| Skarpans → Vargata, Delvik → Vargata, Vargata → Kumlinge | by boat, with road parts | see `docs/postal-route-crossings.md` | none |

**What the line means.** It shows where the road ran when the maps first draw it connected, not a reconstruction of
the 18th-century road. The texts in `dist/explorer.js` and the info panel in `dist/index.html` say so.

**Why some legs are not earlier:**
- **Storby → Frebbenby:** the 1929 Eckerö map does not reach the harbour, so the road to the post house is dated from
  1968.
- **Haraldsby → Skarpans:** no map earlier than 1968 covers the Lappböle sheet edge (`docs/postal-route-sund.md`).

The ferry crossings (Marsund and Färjsundet; the route never uses the later bridges) and the preference for the parish maps' roads are described in `docs/postal-route-haraldsby.md`. The legs' periods (Färjsundet before and from 1761; Delvik before 1670, Bomarsund from 1670) and the boat crossings to Vårdö are in `docs/postal-route-crossings.md`.

## Drawing

`drawPostal` in `dist/explorer.js` draws:
- **land legs between two stations:** solid, along the road path;
- **everything else:** straight and dashed, as before (the sea crossings, and any leg without a road path).

`dist/index.html` loads `postal-route-roads.js` before `archive.js`.

## Tests

- `tests/postal-route-roads.test.cjs`:
  - every road leg starts and ends at its stations, within 150 m of the road;
  - every inner point lies on an object open in the leg's year;
  - the Åland stops are the stations, in order.
- `tests/transport-routes.test.cjs` (in the patch): the stop list now names the stations.

The route is clickable, and three stations are tied to a building, site or registry entry: see `docs/postal-route-crossings.md`.
