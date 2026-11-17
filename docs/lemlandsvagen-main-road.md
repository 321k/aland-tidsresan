# Lemlandsvägen on the early maps

Build step: `scripts/lemlandsvagen_main_road.py` (last step of `build_temporal_objects.py`), review data
`data/lemlandsvagen-main-road.json` (copied to `dist/assets/`), written by
`docs/reviews/lemlandsvagen-main-road-2026-11-17/scripts/prepare.py`.

This is the pilot for using the earliest good maps of the main roads: once the 1917–1948 line of a main road is known,
it can be used to place the same road on the older, rougher maps (the 1894 atlas, the circa-1800 map).

## Sources

| map | use |
|---|---|
| Senatens kartverk, Maarianhamina 1917 (1:21 000, tiles at about 4.8 m/px) | presence only; too coarse for position |
| Sockenkarta 101208, 1929 and 1948 (1:20 000, tiles at 2.4 m/px) | position: the old road was traced on the 1929 map |
| Grundkarta 101208, 1968, 1978, 1985 | presence and which road is the main road; 1985 also position |

Placement of each map along the road, measured on the stretches where the old and the new road are the same:

- 1929 (and 1948): 3–10 m from today's centre line at Askelund–Björkelund, 5–22 m (east) at Solstrand–Knutsboda,
  15–30 m (east) just north of the canal. These are sheet errors, not road moves.
- 1968 and 1978: 30–60 m off in Lemland (the whole drawing, shores included, sits west of the 1985 sheet). They are
  used only for which roads exist and how they lie relative to each other, never for position.
- 1985: within a few metres of today's road.

Rule used: a stretch is the same road when the 1929 road keeps today's shape within about 25 m; a different shape
30–340 m away is a different road. Where a deviation sits between those (the canal approach, 15–30 m), the road is kept
as one object and the deviation is written down.

## Result

Today's road (formerly "Lemlandsvägen · del 1", 10.6 km) is eight sections. The years are the first map that draws
each section, not construction years.

| section | from | why |
|---|---|---|
| A Kalmarnäs–Askelund | 1968 | not on the 1929/1948 maps; the old road came from the north along Önningebyvägen |
| B Askelund–Lemströms kanal | 1917 | same road on every map |
| C Tomtebo–Solstrand | 1968 | new line west of the old shore road |
| D Solstrand–Knutsboda | 1917 | same road on every map |
| E Knutsboda–Dragsvik (the original object) | 1985 | bypass east of Övre-Börs; 1968 and 1978 still run the main road through the village |
| F1 Dragsvik–Johans | 1968 | bypass north of Johans |
| F2 at Lindebo | 1917 | 160 m where the bypass reuses the old road |
| F3 Lindebo–kyrkbyn | 1968 | bypass south of Lindebo, Mangård and Söderby |

The old road ("Gamla Lemlandsvägen", route `road:Gamla Lemlandsvägen`) is four objects traced on the 1929 map:
Tomtebo–Solstrand, Övre-Börs–Östergård, Johans and Mangård–Söderby. Each is open from 1917 until the edition after the
last base map that draws it (1985 or 1995), then `unknown`: not reviewed later, which does not mean it disappeared.
Much of it survives as local roads in OpenStreetMap (Knutsbodavägen, Kockobacka, Kommunrundan, Norra Söderbyvägen)
that are not yet reconciled with these objects. Between the Johans piece and the Mangård piece, the first 300 m of
Långskata del 2 are the old road; that object gets a partial 1917–1985 period, as other partially dated streets do.

The 1968 and 1978 maps draw the old road between Fridelund and Dragsvik straighter than 1929. Whether that is a
straightening or generalisation is not settled; the 1929 line is kept.

## Checks in the build step

- The original object, its geometry and Långskata del 2 must match their fingerprints; the review applies once.
- The sections cover the road exactly once, and each section's first year is its first map marked present.
- Source ownership is cut at the section boundaries: the pieces rebuild every original range exactly, and each piece
  lies within 25 m of its section.
- Each old-road object ends on today's road (or on Långskata) and runs along no other road open at the same time for
  more than 80 m.

## Open items

- Reconcile the surviving old-road stretches with their OpenStreetMap roads (ownership and 1995–2026 states).
- Use the 1929 line to place Lemlandsvägen on the 1894 atlas and the circa-1800 map; both left del 1 deferred
  because of the reroutings found here. Önningebyvägen is already dated from circa 1800, and section B continues it.
- Repeat for the other main roads (Godbyvägen, Eckerövägen, Getavägen, Saltviksvägen).
