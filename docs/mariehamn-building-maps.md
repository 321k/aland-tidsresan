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

b1–b5 contain no `printedMapSymbol` objects. b6–b8 cover the centre, Västernäs and Södra, where 615 such objects
(between 19.927° and 19.946° E, up to 60.1078° N) already show houses from the same sheet; see *The centre* below.
Sheet 101208's 1995 registration starts at about 19.917° E, so nothing further west is reviewed.

- **b1**, 19.930–19.958° E × 60.114–60.127° N: Johannebo, Stenliden, Hindersböle, Norrböle (the areas dated in
  street passes 3–5).
- **b2**, 19.918–19.930° E × 60.109–60.127° N: the western strip from Klinten and the yard (Varv) past Notgrundet
  to Möckelbybäcken.
- **b3**, 19.930–19.958° E × 60.109–60.114° N: the blocks just south of b1.
- **b4**, 19.928–19.962° E × 60.0855–60.0915° N: Övernäs, from Lotsberget and the pilot station on Västerhamn to
  Gröna udden on the east shore, at least 110 m south of the southernmost symbol object.
- **b5**, 19.920–19.9255° E × 60.0925–60.109° N: the Västerhamn shore west of the symbol objects. All 8 proposals
  were shoreline, quay or lettering matches, so it dates nothing.
- **b6**, 19.9255–19.946° E × 60.0915–60.100° N: Södra and the southern centre.
- **b7**, 19.9255–19.946° E × 60.100–60.109° N: Västernäs and the northern centre.
- **b8**, 19.946–19.962° E × 60.0915–60.109° N: the strip east of the centre along Slemmern.
- **b9**, 19.928–19.950° E × 60.0725–60.0855° N: Västra Ytternäs, south of Lotsberget to Korrvik and Lervik.
- **b10**, 19.950–19.972° E × 60.0725–60.0855° N: Östra Ytternäs and the terraced rows of central Ytternäs.

| | b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8 | b9 | b10 | total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dated from 1968 | 107 (28 with 1985 *unclear*) | 26 (1) | 81 (19) | 78 (34) | – | 26 (9) | 10 (2) | 4 | 11 (3) | 1 | 344 |
| dated from 1985 | 179 | 65 | 25 | 20 | – | – | 3 | – | 49 | 79 | 420 |
| dated from 1995 | 75 | 4 | 13 | 14 | – | 17 | 5 | – | 9 | 26 | 163 |
| **dated** | **361** | **95** | **119** | **112** | **0** | **43** | **18** | **4** | **69** | **106** | **927** |
| rejected on the contact sheets (`visual-reject`) | 83 | 13 | 17 | 32 | 8 | 32 | 13 | 4 | 72 | 51 | 325 |
| accepted on the contact sheets but modern-only (`external-modern`, no reconstruction) | – | – | – | – | – | – | – | – | 55 | 38 | 93 |
| no symbol in any edition (`absent`) | 491 | 180 | 118 | 173 | 10 | 175 | 163 | 23 | 305 | 244 | 1882 |
| earlier edition shows hatched or stippled drawing (`earlier-unclear`) | 85 | 16 | 14 | 26 | 2 | 12 | 9 | 2 | 35 | 58 | 259 |
| symbol missing in a later edition (`inconsistent`) | 47 | 19 | 15 | 31 | 3 | 19 | 17 | 4 | 23 | 11 | 189 |
| start already earlier than the maps | 4 | – | 1 | 2 | 3 | 121 | 20 | 1 | 12 | 11 | 175 |
| printed-map symbol objects (matched only so that their symbols are used up) | – | – | – | – | – | 384 | 211 | 1 | – | – | 596 |
| a curated review decides the dates (`curated-review`: a church, the merged Ringvägen 66) | – | – | 1 | 1 | – | – | – | – | – | – | 2 |
| earliest outline differs from the matched one (`outline-changed`) | 1 | – | – | – | – | – | – | – | – | – | 1 |

b1 was first published with 444 dated houses after the tile review alone. The contact-sheet review below then
withdrew 83 of them, which keep their previous start: 27 ambiguous partial overlaps, 18 empty outlines matched to a
neighbour, 16 in a run of 1968 symbols offset by about one house width (registration offset or absence cannot be told
apart), 15 where the previous edition already draws something at the outline (hollow, hatched or offset), 3 under
lettering, 3 matched to black place-name lettering on the 1995 map and 1 matched to a line.

## The centre (b6–b8)

In the centre, 615 `map-building:nls-symbol-*` objects already show houses from the 1985 edition of the same sheet,
most of them linked to their OSM outline. They take part in the matching, so each uses up the symbol it stands on and
no other outline can be dated from it. As a second guard, the compiler refuses the whole review if a dated outline
overlaps any period of a symbol object by more than 5 m² or contains its centre (`symbolObjectOverlapSquareMeters`);
none of the 65 dated houses comes within 3 m of one.

The 1968 edition draws the centre's blocks hatched as built-up area. A symbol detected inside a hatched block cannot be
told from the hatching, so 8 such 1968 proposals were rejected (`hatched-block`); the houses keep their previous
start rather than being moved to 1985, because the hatched 1968 drawing could already include them. 41 more were
rejected on the contact sheets for the usual reasons (partial overlaps, empty outlines, elevation figures or lettering
over the previous edition, circle symbols, a pier).

## Ytternäs (b9–b10)

Ytternäs, south of Övernäs, is on all four scans. The review stops at Lervik and Ytternäsfjärden; the land further
south (Dalen, Svinö) was left out because the town boundary was not checked there. Much of Ytternäs was built
between 1968 and 1985, so most dated houses start in 1985 (128 of 175). Of the 391 proposals, 123 were rejected on
the contact sheets: 68 partial overlaps, 23 empty outlines, 21 cases where the previous edition already draws
something at the outline or black lettering covers it, 6 matches on black lettering (5 of them the large place-name
letters on the 1968 sheet) and 5 on lines. Red lettering and plan figures were not treated as hiding a house: a dark house symbol
stays visible under them.

93 accepted houses were not dated: they are `externalModern` objects, outlines that exist only in the 2026 OSM extract
outside the reconstructed city building set and have no reconstruction to extend. The compiler requires one, so
they are deferred as `external-modern` until that model exists.

## Recheck r1: earlier drawings (2026-11-13)

The 226 `earlier-unclear` buildings of b1–b10 that still exist, are not modern-only and have no curated review were
drawn in all three editions (`recheck.py`, `recheck-earlier-unclear-NN.jpg`) and judged by eye
(`recheck-earlier-unclear-decisions.json`):

| decision | buildings |
|---|---|
| **E1968**: the 1968 edition already draws the building (hatched, stippled, hollow or a symbol the size rule set aside) | 16 |
| **E1985**: the 1985 edition draws it (mostly an ordinary symbol the detector missed, or a hatched or hollow building) | 67 |
| **P**: the earlier ink is lettering, lines, an area fill or block hatching; the proposed edition stands | 97 |
| deferred: unclear, lettering over the outline, quays and piers | 44 |
| deferred: the building overlaps a printed-map symbol object (`recheck-symbol-overlaps.json`) | 2 |

A visually confirmed edition records the scan pixel of the shifted outline's centre and `visualReview: true` on the
observation and the evidence; where a symbol was detected but set aside by the size rule, that symbol is recorded.
An earlier 1968 edition whose surroundings are block-hatched (stripe density above 0.22, as in the symbol review) is
recorded as `unclear` with `reason: hatched-block`, not `absent`: the house may be inside the hatching. The compiler
accepts `unclear` before the start only for that case. 180 buildings are dated in batch `r1`; 1107 in all.

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
registration, lies more than 30 m from the outline or beyond the match limit after the recorded shift. It is also rejected if a dated outline
overlaps a printed-map symbol object (more than 5 m², or containing its centre) in any of its periods. Buildings with a
`historicalReview`, `museumReview`, `printedMapSymbol` or `neighborhoodReviews` are refused: those reviews decide
their dates.

Tests: `tests/mariehamn-building-maps.test.cjs`, `tests/test_mariehamn_building_maps.py`. The scope audit against
the pre-review snapshot finds exactly the 1107 reviewed objects changed, one new source, and no geometry changes.
Against the first b1 publication, the 83 withdrawn houses are byte-identical to the snapshot again, the 361 kept
are unchanged and 214 are newly dated.

## Next batches

- The centre's hatched 1968 blocks: houses there could be dated from 1985 only with a closer look at whether the
  hatching already includes them.
- The 615 printed-symbol objects start at their 1985 symbol (mostly 1983). 125 of them outside the hatched blocks are
  now dated from the 1968 edition by a separate review (`docs/mariehamn-symbols-1968.md`).
- The 93 `external-modern` Ytternäs houses that the maps show from 1968–1995: they need a reconstruction first.
- Ytternäs south of Lervik (Dalen), the area north of b1 and east of Slemmern were not reviewed; whether they belong
  to Mariehamn was not checked against the town boundary.
- The 79 remaining `earlier-unclear` and the 189 `inconsistent` buildings, and the `visual-reject` ones, need a closer look (often hatched public
  buildings, replaced houses, houses under map lettering, or a local registration offset).
