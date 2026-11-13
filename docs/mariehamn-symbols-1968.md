# Centre symbol houses dated from the 1968 map

Review: `data/mariehamn-symbols-1968.json` (source `review:mariehamn-symbols-1968`), applied at build time by
`scripts/mariehamn_symbols_1968.py` as the last step of `scripts/build_temporal_objects.py`, after the building-map
review and the 1942 street review. Reviewed 2026-11-13.

## Why

The centre's 615 `map-building:nls-symbol-*` objects come from the house symbols on the 1985 edition of sheet
101208 and start at its survey year, 1983 (two at 1982). The b6–b8 building-map matching (see
`docs/mariehamn-building-maps.md`) matched 464 of them one-to-one to a symbol on the 1968 edition as well, but
symbol objects are curated and that review never dates them. This review does, where the 1968 drawing is clear.

## Selection

1. A 1968 symbol matched within 9 m of the object's outline after the local registration shift, and a first state
   that starts after 1968: 412 objects.
2. Outside the 1968 built-up area objects (`printedMapArea`, the hatched blocks shown 1968–1985): 244.
3. The hatching reaches beyond those area objects. The surroundings 5–14 m outside the shifted outline were measured
   on the 1968 scan; a candidate is left out as hatched if the dark share there is above 0.40 or the dark stripe
   density is above 0.22 (on the first contact sheet, hatched surroundings measured 0.32 or more and open ones 0.21
   or less): 86 left out, 158 reviewed.
4. Every remaining candidate was checked on the contact sheets (`sym-contact-*.jpg`: 1968 | 1985 | 1995, the
   outline shifted by the local 1968 registration, the matched 1968 symbol circled). 33 were rejected: 28 where the
   1968 symbol covers only part of the outline (an extension, a longer building or a neighbour), 3 still in a hatched
   block, 1 empty outline and 1 match on the lettering "berg". 125 are dated.

The 1985 panel is unshifted and often offset by the 1985 registration; the objects already rest on that edition,
so only the 1968 drawing was judged.

## Model changes per object

- Evidence `{id}:map-101208-1968`: `observationType: printed-map`, the scan pixel, the local shift, the raw distance
  to the outline, `constructionYear: null`.
- A new first state (the object's own state type, `occupied` or `standing`) from 1968 to the previous start
  (`certainty: inferred`). Later states are unchanged.
- The first geometry period is extended back to 1968 with `previousFrom`; the shape is still the first outline, not
  the map drawing. `sourceYears` is unchanged.
- `reconstruction.from` moves to 1968 with `mapDated: true` and the previous start in `reconstruction.previous`.
- `symbolMap1968` marks the object.

## Compiler checks

The review is rejected as a whole, leaving the catalogue unchanged, if an object's input fingerprint changed, it
repeats, it is not a printed-map symbol building, its first state or period does not start at the recorded start
(after 1968, at most 1985), the recorded 1968 pixel lies inside a 1968 built-up area object, or the pixel converted
through the 1968 registration lies more than 30 m from the outline or more than 9.5 m after the recorded shift.

Tests: `tests/mariehamn-symbols-1968.test.cjs`, `tests/test_mariehamn_symbols_1968.py` (which uses the pre-step
snapshot `symbols-before.json.gz` in the review cache). The scope audit against the previous publication finds
exactly the 125 objects changed, one new source and no geometry or city-stage changes.

## Not done

- The 203 symbol houses in the 1968 built-up areas and the 86 in hatched surroundings: the hatching may already
  include them, but single houses cannot be told apart.
- The 33 rejected candidates, and the 52 symbol objects without a 1968 match.
