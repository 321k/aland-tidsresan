# Mariehamn buildings dated from sheet 101208 (1968–1995)

Review: `data/mariehamn-building-maps.json` (source `review:mariehamn-building-maps`), applied at build time by
`scripts/mariehamn_building_maps.py` after the reported-building step in `scripts/build_temporal_objects.py`.
Reviewed 2026-11-12.

## Why

Most Mariehamn buildings outside the old town started at their first modern outline source (OSM 2011–2026), even
where the house is clearly drawn on the 1968, 1985 and 1995 base maps. This batch gives those houses their earliest
reviewed map evidence. The map year is first evidence, never the construction year, and the shape shown is still
the earliest measured outline: the map symbols date existence, not form.

## Batch b1: Johannebo, Stenliden, Hindersböle, Norrböle

The areas whose streets were dated in street passes 3–5. There are no `printedMapSymbol` objects here, so dating an
outline cannot duplicate a building that already exists as a map symbol (Västernäs and Södra need that check in a
later batch).

| | buildings |
|---|---|
| dated from 1968 | 152 (45 of them with 1985 recorded as *unclear*) |
| dated from 1985 | 199 |
| dated from 1995 | 93 |
| **dated** | **444** |
| deferred: no symbol in any edition | 491 |
| deferred: earlier edition shows hatched/stippled drawing (`earlier-unclear`) | 85 |
| deferred: symbol missing in a later edition (`inconsistent`) | 47 |
| deferred: start already earlier than the maps | 4 |
| deferred: earliest outline differs from the matched one (`outline-changed`) | 1 |

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
   Detection is only a proposal; the remaining errors leave buildings undated rather than dating them wrongly.

The review tooling and sheets are kept in the git-ignored cache `data/map-scan-cache/review/mariehamn-buildings/`
(`match.py`, `verdict.py`, `sheets.py`, `prepare.py`, `before.json.gz`).

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
registration, lies more than 30 m from the outline or beyond the match limit after the recorded shift.

Tests: `tests/mariehamn-building-maps.test.cjs`, `tests/test_mariehamn_building_maps.py`. The scope audit against
the pre-review snapshot found exactly the 444 reviewed objects changed, one new source, and no geometry changes.

## Next batches

- Västernäs and Södra: must first reconcile with the `map-building:nls-symbol-*` printed-symbol objects so a dated
  outline and a symbol object never show the same house twice.
- The 85 `earlier-unclear` and 47 `inconsistent` buildings in b1 need a closer look (often hatched public buildings,
  replaced houses or houses under map lettering).
