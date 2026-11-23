# Main roads on the base maps: survey, 2026-11-23

**Goal:** every main road the base maps (grundkartor) draw is in the catalogue from the first edition that draws it.

## Method

- **Survey** (`scripts/survey.py`, output `survey.json`):
  - Today's main roads are the OSM classes primary, secondary and tertiary, split into 20 m pieces.
  - The registered sheets in `data/rural-map-review.json` give each piece the earliest edition whose metric frame
    contains it.
  - A piece is covered if a catalogue road open that year lies within 25 m.
- **Screen** (`scripts/screen_red.py`, output `screen-red.json`):
  - Each uncovered piece is sampled on that first-edition scan, in a 40 m square.
  - At least 6% strong red pixels counts as the red main-road symbol there.
  - This is a screening only: every candidate is checked by eye before it is dated.
- **Spot checks** (`renders/check-sheet.jpg`): Södravägen (1012 05, 1968) and Överövägen (1014 05, 1970) are drawn in
  red on today's line, and the catalogue has no road open there.

## Result

| | km |
|---|---|
| main roads on registered sheets | 681.8 |
| not covered by a dated road at the first edition | 268.7 |
| …of which drawn in red on that edition (candidates) | 141.1 |
| …of which not red (likely built later, or a minor road then) | 127.5 |
| not covered even today | 31.2 |

## Batches, by area (red candidates)

| # | area | sheets | main candidates | km |
|---|---|---|---|---|
| 1 | Saltvik north and west, Geta | 1021 04, 05, 07, 08, 11 | Södravägen, Tjudövägen, Skarpnåtövägen, Hamnsundsvägen, Svartsmaravägen, Tobölevägen, Finnövägen | ≈42 |
| 2 | Föglö | 1014 01, 04, 05 | Överövägen, Föglövägen, Hummersövägen, Nötövägen, Näversholmavägen, Ulversövägen, Bofjärdsvägen | ≈31 |
| 3 | Brändö, Fiskö, Kumlinge | 1041 03, 1023 07, 08, 12, 1014 09 | Brändövägen, Fiskövägen, Enklingevägen, Kungshamnsvägen, Seglingevägen | ≈17 |
| 4 | Lemland, Lumparland | 1012 08, 11, 12 | Ängösundsvägen, Svinövägen, Bistorpvägen, Lemlandsvägen, Lumpovägen, Södra Söderbyvägen | ≈9 |
| 5 | Vårdö, Sandö, Ängö | 1023 01, 1014 03 | Sandövägen, Ängö-Bussövägen, Vårdövägen | ≈8 |
| 6 | Jomala, Mariehamn's edge | 1012 05, 09 | Ringsbölevägen, Norrbygatan, Norra Svibyvägen, Klockargränd, Narmovägen, Södersundavägen | ≈8 |
| 7 | Eckerö, Hammarland | 1012 03 | Torpvägen, Södra Överbyvägen, Skeppsviksvägen, Tellholmsvägen | ≈6 |
| 8 | Sund | 1021 10 | Mångstektavägen, Sonrödavägen, Persbyvägen | ≈5 |
| — | the rest | | short pieces under about 800 m | ≈15 |

**How each batch works.**
- Most candidates are existing objects dated from a later edition. They get an earlier period on their own geometry
  where the first edition draws them on the same line (the `early` step of `_apply`).
- Where the first edition draws another line, the old line is traced as an old road.
- Pieces no object owns (31 km today) become new objects of OSM pieces.

## Progress

| batch | survey batches | docs | not covered at the first edition, all sheets |
|---|---|---|---|
| 1 | 1 | `docs/main-roads-saltvik.md` | 268.7 → 235.4 km |
| 2 | 2, 3 and 5 (the archipelago) | `docs/main-roads-archipelago.md` | 235.4 → 182.8 km |
