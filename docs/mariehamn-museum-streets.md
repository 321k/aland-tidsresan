# Hamngatan and Parkgatan before 1968 (the museum map's last unlinked streets)

Review: `data/mariehamn-museum-streets.json` (source `review:mariehamn-museum-streets`), applied at build time by
`scripts/mariehamn_museum_streets.py`, right after the shore road step in `scripts/build_temporal_objects.py`.
Reviewed 2026-11-17. Evidence and renders: `docs/reviews/mariehamn-hamngatan-parkgatan-2026-11-17/`.

## Why

Two streets of the museum's 1920s picture were still drawn as raw, unlinked copies in the 1920 and 1927 city stages:

| museum name | street | what the review found |
|---|---|---|
| Gata längs västra kvarteren (`city-1920-street-37`) | Hamngatan | The 1942, 1952 and 1962 photos show the street along the west edge of the blocks over its whole length, where the 1968 map and today's Hamngatan run. The catalogue's five Hamngatan segments started at the 1968 map. The northern stretch (Norragatan to the junction, about 155 m) had no persistent object at all and was drawn only by the raw 2014–2026 OSM lines. The drawing is coarse: in the north it lies 10–15 m west of the street, through the sjöfartsmuseum site, and in the south it runs straight on to the shore where the street curves south-east. |
| Gata söderut vid östra stranden (`city-1920-street-42`) | Parkgatan | The north leg duplicates Parkgatan (`road:postwar:way-39585442`, already dated from the 1942 photo), 10–14 m east of it in the park edge. The south-east leg follows Parkgatan `road:mariehamn:major:way-35304989`, which started at the 1968 map, although the 1942–1962 photos show it. The drawing ends at about 64 % of that segment. |

## Model changes

- Every member keeps its own measured centre line and gets the museum drawing as evidence (`museum-1920`: map, decade
  precision, interpretation, original geometry = the drawing) and a state from 1920. Members that started in 1968 also
  get the 1942 photo (`street-photo-1942`, aerial, 1942-07-25) and a state 1942–1968. The first geometry period starts
  in 1920.
- Parkgatan's south-east segment shows only the part the drawing covers in the 1920s (`coverage: partial`,
  `canonicalRange [0, 0.637]`, cut at latitude 60.0925), and the whole segment from 1942.
- Hamngatan's northern stretch becomes `road:mariehamn:museum-streets:hamngatan-norra`: one independent road from
  today's four OSM pieces (identical in the 2014, 2021, 2025 and 2026 street sets, which become its source links),
  joined to `road:postwar:way-1081060422`. It has museum, 1942 photo and 1968/1985 base-map evidence.
- Each drawing is a source of one object only (`way-35011941` and `way-39585442`) and is kept as an original geometry.
  Its raw copies leave the 1920 and 1927 stages. `museumStreetReview` marks the objects.

The museum, photo and map years are evidence, not construction years.

## Compiler checks

The review is rejected as a whole, leaving the catalogue unchanged, if a drawing, a stage copy, a member fingerprint,
a member start, the cut latitude or a modern piece changed; if a member lies farther than 35 m from the drawing (only
the covered part counts); if a modern piece already belongs to an object or the pieces do not form one line joined to
Hamngatan; or if the review was already applied.

Tests: `tests/mariehamn-museum-streets.test.cjs`, `tests/test_mariehamn_museum_streets.py` (pre-step snapshot
`museum-streets/before.json.gz` in the review cache). The scope audit against the catalogue before the step finds the
new Hamngatan object, the seven member objects, four new geometries, one new source and only the four raw stage copies
removed from the 1920 and 1927 stages.

Open: north of Parkgatan, a roughly 90 m stub to the cross street is on the 1942 photo and the 1968 map and is a
cycleway today; it has no object and needs its own decision.
