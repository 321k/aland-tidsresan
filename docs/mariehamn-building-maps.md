# Mariehamn buildings dated from sheet 101208 (1968–1995)

Review: `data/mariehamn-building-maps.json` (source `review:mariehamn-building-maps`), applied at build time by
`scripts/mariehamn_building_maps.py` after the reported-building step in `scripts/build_temporal_objects.py`.
Reviewed 2026-11-12.

## Why

Most Mariehamn buildings outside the old town started at their first modern outline source (OSM 2011–2026), even
where the house is clearly drawn on the 1968, 1985 and 1995 base maps. This batch gives those houses their earliest
reviewed map evidence. The map year is first evidence, never the construction year, and the shape shown is still
the earliest measured outline: the map symbols date existence, not form.

## Batches

None of the areas has `printedMapSymbol` objects, so dating an outline cannot duplicate a building that already
exists as a map symbol (those reach 60.1078° N between 19.927° and 19.946° E; Västernäs and Södra need that check in
a later batch). Sheet 101208's 1995 registration starts at about 19.917° E, so nothing further west is reviewed.

- **b1**, 19.930–19.958° E × 60.114–60.127° N: Johannebo, Stenliden, Hindersböle, Norrböle (the areas dated in
  street passes 3–5).
- **b2**, 19.918–19.930° E × 60.109–60.127° N: the western strip from Klinten and the yard (Varv) past Notgrundet
  to Möckelbybäcken.
- **b3**, 19.930–19.958° E × 60.109–60.114° N: the blocks just south of b1.
- **b4**, 19.928–19.962° E × 60.0855–60.0915° N: Övernäs, from Lotsberget and the pilot station on Västerhamn to
  Gröna udden on the east shore, at least 110 m south of the southernmost symbol object.
- **b5**, 19.920–19.9255° E × 60.0925–60.109° N: the Västerhamn shore west of the symbol objects. All 8 proposals
  were shoreline, quay or lettering matches, so it dates nothing.

| | b1 | b2 | b3 | b4 | b5 | total |
|---|---|---|---|---|---|---|
| dated from 1968 | 107 (28 with 1985 *unclear*) | 26 (1) | 81 (19) | 78 (34) | – | 292 |
| dated from 1985 | 179 | 65 | 25 | 20 | – | 289 |
| dated from 1995 | 75 | 4 | 13 | 14 | – | 106 |
| **dated** | **361** | **95** | **119** | **112** | **0** | **687** |
| rejected on the contact sheets (`visual-reject`) | 83 | 13 | 17 | 32 | 8 | 153 |
| no symbol in any edition (`absent`) | 491 | 180 | 118 | 173 | 10 | 972 |
| earlier edition shows hatched or stippled drawing (`earlier-unclear`) | 85 | 16 | 14 | 26 | 2 | 143 |
| symbol missing in a later edition (`inconsistent`) | 47 | 19 | 15 | 31 | 3 | 115 |
| start already earlier than the maps | 4 | – | 1 | 2 | 3 | 10 |
| a curated review decides the dates (`curated-review`: a church, the merged Ringvägen 66) | – | – | 1 | 1 | – | 2 |
| earliest outline differs from the matched one (`outline-changed`) | 1 | – | – | – | – | 1 |

b1 was first published with 444 dated houses after the tile review alone. The contact-sheet review below then
withdrew 83 of them, which keep their previous start: 27 ambiguous partial overlaps, 18 empty outlines matched to a
neighbour, 16 in a run of 1968 symbols offset by about one house width (registration offset or absence cannot be told
apart), 15 where the previous edition already draws something at the outline (hollow, hatched or offset), 3 under
lettering, 3 matched to black place-name lettering on the 1995 map and 1 matched to a line.

## Method

1. Dark filled house symbols were detected on the four scans (`data/map-scan-cache/101208_{1968,1978,1985,1995}.jpg`,
   about 1.68 m/px): grey/brown fill, 3×3 opening to drop lines and hatching, filled components with convex-hull
   solidity of at least 0.6.
2. Each outline of at least 40 m² was matched one-to-one to a symbol within 9 m, after a local registration shift
   (the median outline-to-symbol vector of the neighbours within 150 m). A second pass with 14 m catches symbols
   displaced by lettering. A building more than three times the drawn symbol area is not matched to it.
3. Dating rules:
   - 1978 is a road revision on the 1968 base and is not used as building evidence;
   - a building starts at the first of 1968/1985/1995 with a matched symbol and must be matched in every later one;
   - a house matched in 1968 and 1995 whose 1985 symbol is not found keeps 1968, with 1985 recorded as *unclear*;
   - a later start is deferred if the previous edition shows dark drawing inside the outline (hatched or stippled
     buildings, which the detector does not pick up), so that no house gets a too-late date.
4. Every tile was checked on the review sheets (1968 | 1985 | 1995 side by side, outlines coloured by verdict).
5. Every proposal was then checked on its own on contact sheets (`contact.py`): the building at high zoom with its
   shifted outline, in the previous and the first edition for later starts, and in 1985 and 1968 for 1968 starts.
   The tile sheets are too coarse to see hollow building outlines (which the ink guard does not count), symbols that
   only touch the outline, or matches on shorelines, piers and lettering. Each rejection is recorded with a reason
   and its sheet and cell in the review's `visualRejections`. Detection is only a proposal; the remaining errors
   leave buildings undated rather than dating them wrongly.

The review tooling and sheets are kept in the git-ignored cache `data/map-scan-cache/review/mariehamn-buildings/`
(`match.py`, `verdict.py`, `sheets.py`, `contact.py`, `prepare.py`, the per-batch `KEY-overrides.json`, and
`before.json.gz`).

## Model changes per building

- Evidence `{id}:map-101208-{year}` for each edition from the first year: `observationType: printed-map`, the scan
  pixel, the local shift, the raw distance to the outline, `constructionYear: null`. *Unclear* editions are
  `supports: ['assessment']` and are not cited by the state.
- A new first `standing` state from the map year to the previous start (`certainty: inferred`). Later states are
  unchanged.
- The first geometry period (the earliest measured outline) is extended back to the map year; its previous start is
  kept in `previousFrom` and its previous basis in `previousBasis`; the provisional sentence about the first
  source being used until an earlier date can be estimated is replaced by a note on the map date. `observationYear` stays the outline source year, and `sourceYears` stays the outline
  sources, so the map year is never presented as a measurement of shape.
- `reconstruction.from` moves to the map year, with `mapDated: true` and the previous start and basis in
  `reconstruction.previous`.
- `buildingMapReview` marks the object.

## Compiler checks

The review is rejected as a whole, leaving the catalogue unchanged, if a building's input fingerprint changed, a
building repeats, its start is not the first edition with a symbol, a later edition lacks the symbol (other than the
1985 *unclear* case), a 1978 observation is used, or a recorded symbol pixel, converted through the sheet's
registration, lies more than 30 m from the outline or beyond the match limit after the recorded shift. Buildings with a
`historicalReview`, `museumReview`, `printedMapSymbol` or `neighborhoodReviews` are refused: those reviews decide
their dates.

Tests: `tests/mariehamn-building-maps.test.cjs`, `tests/test_mariehamn_building_maps.py`. The scope audit against
the pre-review snapshot finds exactly the 687 reviewed objects changed, one new source, and no geometry changes.
Against the first b1 publication, the 83 withdrawn houses are byte-identical to the snapshot again, the 361 kept
are unchanged and 214 are newly dated.

## Next batches

- What remains in Mariehamn is the centre, Västernäs and Södra (19.927–19.946° E, 60.092–60.108° N) and the strips
  just around them, which must first be reconciled with the `map-building:nls-symbol-*` printed-symbol objects so a dated outline and a symbol object never show the same house twice.
- Houses south of 60.085° N and east of Slemmern were not reviewed; whether they belong to Mariehamn was not
  checked against the town boundary.
- The `earlier-unclear`, `inconsistent` and `visual-reject` buildings need a closer look (often hatched public
  buildings, replaced houses, houses under map lettering, or a local registration offset).
