# Two unlinked museum tracings: Hamngatan and Parkgatan (2026-11-17)

The 1920s museum map's "Gata längs västra kvarteren" (`city-1920-street-37`, trace 11) and "Gata söderut vid östra
stranden" (`city-1920-street-42`, trace 18) are still drawn as raw, unlinked street copies in the 1920 and 1927 city
stages. Each was rendered over the 1942, 1952, 1962, 1975, 1991 and 2021 orthophotos and the 1968 and 1985 base maps
with the catalogue roads near it (`renders/`, made with `scripts/compare.py`).

Colours: cyan/blue = museum tracing; magenta = catalogue road not yet open that year; green = open.

## Gata längs västra kvarteren = Hamngatan

- The 1942, 1952 and 1962 photos show a street along the west edge of the blocks over the whole length of the
  tracing: the house lots face it. It is the street the 1968 map draws and today's Hamngatan.
- Southern two thirds: the tracing lies within about 0–5 m of the catalogue's Hamngatan
  (`road:postwar:way-35011941` and the short pieces `way-392187942`, `way-37210769`, `way-1081060422`). Those
  objects start in 1968 (first base map), so the street is missing from the map from 1942 to 1967, although the
  photos show it. At its south end the tracing runs straight on to the shore, where the street actually curves
  south-east (`way-935611737`).
- Northern third (about 190 m, from Norragatan to the junction where catalogue Hamngatan begins): the street is on
  every photo and on the 1968 map, about 10–15 m east of the tracing. The tracing itself passes through the
  sjöfartsmuseum site. **No persistent object covers this stretch in any year.** The map shows nothing there
  1942–2013 and only the raw modern OSM lines (`city-2014…2026`, "Hamngatan", e.g. `city-2026-street-123`/`-3680`)
  from 2014.

## Gata söderut vid östra stranden = Parkgatan

- North leg: it duplicates Parkgatan `road:postwar:way-39585442`, which is open from 1942 (the 1942 frame photo
  review). The tracing lies 10–14 m east of it, inside the edge of the park: a coarse drawing, not a second road.
  The object's 1942 note already mentions "the southern continuation along the shore".
- South-east leg: it follows Parkgatan `road:mariehamn:major:way-35304989` within about 5–10 m. That object starts
  in 1968 (major-road map review), but the road is plainly visible on the 1942, 1952 and 1962 photos.
- North stub: from Parkgatan's north end to the cross street (about 90 m) there is a road on the 1942 photo and the
  1968 map, a cycleway today, and no object.

## Applied (you chose all three)

As for the shore road (`docs/reviews/mariehamn-nygatan-shore-road-2026-11-16/`), in a fingerprinted review file and a
build step, with regression tests and a scope audit:

1. **Hamngatan:** give the five Hamngatan objects museum-decade evidence (1920, decade precision, interpretation) and
   1942 photo evidence, a state 1920–1942 and 1942–1968, and an earlier geometry period that is their own centre
   line. Link the tracing as a source to the main object only. Remove its two raw stage copies.
2. **Hamngatan's northern stretch:** create one persistent object from the modern OSM geometry, with the same
   evidence, so the street is drawn continuously from the 1920s.
3. **Parkgatan:** link the tracing to `way-39585442` and extend that object to 1920 with museum evidence. Give
   `way-35304989` a 1942 photo state, plus museum evidence for the 1920s. Remove the two raw stage copies. The
   south-east leg's major-road review is unchanged; no later build step pins its fingerprint, so nothing needed re-pinning.
4. Leave the north stub as a follow-up (a cycleway today; it needs its own decision).

The museum and photo years are first evidence, not construction years.

## What was done

Method, model changes and compiler checks: `docs/mariehamn-museum-streets.md`. Data: `data/mariehamn-museum-streets.json`,
written by `scripts/prep_streets.py` from the catalogue just before the step. The build step is `scripts/mariehamn_museum_streets.py`.
Parkgatan's south-east segment extends about 100 m past the end of the drawing, so its 1920s period covers only the drawn
part (`canonicalRange [0, 0.637]`). The photo shows the whole segment from 1942.

- `renders/after-hamngatan-1920-1960.jpg`, `renders/after-parkgatan-1920-1960.jpg`: the map after the change (cyan =
  Hamngatan/Parkgatan, drawn on the 1942 and 1962 photos) for 1920, 1930, 1942 and 1960.
- `scope-audit.json`: 1 new object, 7 changed street objects, 4 new geometries, 1 new source, and the 4 raw stage copies removed.
- Snapshots in the review cache were regenerated (`scripts/resnapshot.py` with the new step). The old ones are kept as
  `*.pre-museum-streets.json.gz`.
- Tests: `tests/mariehamn-museum-streets.test.cjs` (4), `tests/test_mariehamn_museum_streets.py` (4). Updated:
  `tests/mariehamn-major-roads.test.cjs`, `tests/mariehamn-frame-1942.test.cjs`, `tests/temporal-objects.test.cjs`
  (earlier starts and the new object in the object count); `tests/test_mariehamn_frame_1942.py`,
  `test_mariehamn_approaches_1942.py`, `test_mariehamn_building_maps.py` (the new step is chained after the shore road).
- `dist/index.html`: loader card "Hamngatan och Parkgatan från 1920-talet".
- Deployed by the parent session as Cloudflare version 1793b8ac, together with Norrböle (p1) and the Hindersböle places; 298
  files matched live (`publication/`).

## What is committed directly

`scripts/mariehamn_museum_streets.py`, `data/mariehamn-museum-streets.json` and its copy in `dist/assets/`,
`docs/mariehamn-museum-streets.md`, the two new tests, and this review's hunks in `tests/mariehamn-frame-1942.test.cjs`,
`tests/test_mariehamn_frame_1942.py`, `test_mariehamn_approaches_1942.py` and `test_mariehamn_building_maps.py`.

## What is in `batch.patch`

These files also hold other uncommitted work: `scripts/build_temporal_objects.py` (the step and its dist copy),
`tests/mariehamn-major-roads.test.cjs`, `tests/temporal-objects.test.cjs` (earlier starts and the object count; the
Hindersböle test block is in that review's patch) and `dist/index.html` (this card, the renumbering, the loader
preview and cache stamps). The Hindersböle review's index hunk applies on top of this one; see `patch-verification.log`.
