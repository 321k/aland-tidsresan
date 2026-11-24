# Main roads on the base maps, batch 4: main roads no object had

Part of the main-road survey (`docs/reviews/main-roads-2026-11-23/README.md`).

Build step: `apply_main_roads_new` in `scripts/main_roads_new.py`, after batch 3.

Review data: `data/main-roads-new.json` (copied to `dist/assets/`), written by
`docs/reviews/main-roads-2026-11-23/scripts/prepare_new.py`.

## Method

**Candidates** (`scripts/unowned.py`, output `batch4-unowned.json`):
- today's main-road ways in OSM 2026 (primary, secondary, tertiary) that no catalogue object owns;
- under half of the way within 25 m of a catalogue road open in 2026;
- on a registered base-map sheet.

Ways with the same name that touch are grouped. That gives 46 groups, 26.6 km.

**Matching** (`match_editions.py`, output `batch4-match.json`). Each group is read on every registered edition. The
tools read a catalogue copy with the candidates added as objects (env `CAT`); `unowned.py` writes that copy.

**Checking by eye** (`renders/b4-*.jpg`). The 17 groups with the red symbol under at least half their length on the
first edition were rendered. This batch takes the 10 that the first edition draws on today's line.

**The step.** Each road is a new object made of its OSM ways in order. The form is the `newRoads` form of the Sviby
connections, checked and added by `scripts/sviby_connections.py`:
- the ways must be unchanged and owned by no other object;
- the geometry is the ways joined;
- each end rests within 1 m of the road it joins in every period from the road's first year, or is a stated free end;
- no new road runs along an existing road.

The same ways in the 2014, 2021 and 2025 extracts are owned too where their coordinates are identical. Every edition
that draws the road in red is evidence. The first is the first year. Map years are first evidence, not construction years.

## Result

| road | sheet | from | m |
|---|---|---|---|
| Kungshamnsvägen · Kumlinge | 1023 07 | 1971 | 2,341 |
| Ödkarbyvägen · Ödkarby–Haga | 1021 07 | 1968 | 1,785 |
| Bistorpvägen | 1012 11 | 1968 | 1,409 |
| Sonrödavägen | 1021 10 | 1968 | 1,321 |
| Klockargränd | 1012 09 | 1968 | 954 |
| Vägen till färjfästet · Långäng (Brändö) | 1041 02 | 1969 | 596 |
| Bovikvägen | 1021 04 | 1968 | 484 |
| Vägen vid Påvals · Kökar | 1013 12 | 1971 | 419 |
| Björbyvägen · Strömsborg–Trygghem | 1021 10 | 1968 | 361 |
| Eliasvägen | 1021 10 | 1968 | 317 |

Ten roads, 10.0 km.

**Free ends.** Six ends stop short of the road they meet. Each continues over a short unowned stub (under 50 m) to a
junction, or, at Långäng, ends at the ferry landing the 1969 map draws. Each is stated in the road's record.

## Open items

- **Kungshamnsvägen at Skålberg:** all three editions draw the road about 30 m north of today's line, for about
  200 m (about 150 m in 1991).
- **Sonrödavägen at Karlsro:** for about 100 m the 1968 road runs through the junction south of today's curve.
- **Not in this batch:**
  - **Different line at the first edition:**
    - the road west of Lillbolstad (`way/54052704`): its west 270 m is a later line;
    - Södra Söderbyvägen: its north end joins the main road about 100 m further west in 1968;
    - Valborgsvägen.
  - **Short junction pieces:** Tosarbyvägen, Hagavägen and Södersundavägen.
  - **Red only from a later edition:** Emkarbyvägen (1978), Östra Ytterbyvägen (1978–1985), Bölevägen (1978), the
    Brändö road `way/1355323682` (1984) and Skinnarskärsbron (1984).
  - **Not red on any edition:** Industrivägen, Solbergsvägen, Kyrkvägen and others. These were probably not main
    roads when the maps were drawn.
