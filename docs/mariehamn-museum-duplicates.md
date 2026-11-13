# Museum-map houses that duplicated or were replaced by later houses

Review: `data/mariehamn-museum-duplicates.json` (source `review:mariehamn-museum-duplicates`), applied at build time by
`scripts/mariehamn_museum_duplicates.py` as the last step of `scripts/build_temporal_objects.py`, after the 1968
symbol review. Reviewed 2026-11-13.

## Why

The 1920 museum map's houses (`building:museum:*`) were kept as provisional objects with assumed continued existence
when no unambiguous later counterpart was found (`sourceMigration.decision: retain`). Where such a house lies next to
the same building's later outline, the map drew it twice: on Storagatan, for example, several museum houses sat about
half a house north of a 1985 symbol house or an OSM house from 1983 or 2021 onward. A town-wide check found 53 pairs
of a museum house overlapping a later house (from a year-by-year resolve of every building between 19.92–19.965° E and
60.085–60.13° N; at least 4 m² and 15 % of the smaller outline).

## Review

Every pair was drawn on the 1942 orthophoto (plain and with outlines) and the 1968 sheet 101208, with all other
outlines nearby (`data/map-scan-cache/review/museum-duplicates/sheets.py`, `museum-NN.jpg`). The offsets between the
museum map and the measured outlines vary from 0 to 37 m in every direction, so no systematic shift was applied.

| decision | pairs | museum houses |
|---|---|---|
| **merge**: the 1942 photo shows one house where the later outline is; the museum outline is 5–16 m off | 16 | 15 |
| **replacement**: a different, usually much larger later building stands on the plot | 19 | 16 |
| deferred: a shed or garage that is not the counterpart | 7 | 6 |
| deferred: shape or orientation does not decide it | 8 | 8 |
| deferred: the later house's building-map review records it absent in 1968/1985 | 2 | 2 |
| not an overlap: a museum house in the courtyard hole of the large block building | 1 | 1 |

## Model changes

- **Merge.** The later object keeps its identity, outline, states and periods. It takes over the museum record's
  evidence and source links, and the museum id and its aliases become its aliases (references, for example from the
  aerial-review page, resolve through them). A new first state from 1920 to the previous start is added and the
  first geometry period is extended back with `previousFrom`; the outline shown from 1920 is the later measured one,
  a continuity assumption, not the museum map's drawing. `reconstruction.firstObserved` becomes 1920 and the previous
  values are kept in `reconstruction.previous`. Two later houses already started in 1920; they only gain the museum
  evidence. `museumDuplicateReview` keeps the merged museum object.
- **Replacement.** The museum house ends at its successor's first reviewed start (1942, 1975, 1983 or 2021) with a
  `demolished` state, `replaced-by` / `replaces` relationships and a `replacementReview`. That year is the latest
  replacement boundary, not a demolition year.

## Compiler checks

The review is rejected as a whole, leaving the catalogue unchanged, if any input fingerprint changed, a museum house is
not an open provisional object, a museum house is both merged and ended or two museum houses merge into one object, a
merge's starts changed or its partners no longer overlap (at least 4 m², centroids within 25 m), or a replacement's
end year is not its successors' first start or a successor no longer overlaps.

Tests: `tests/mariehamn-museum-duplicates.test.cjs`, `tests/test_mariehamn_museum_duplicates.py` (which uses the
pre-step snapshot `museum-before.json.gz` in the review cache). After the step the town-wide check finds 18 museum
pairs (the deferred ones and the courtyard case) instead of 53, and no new pair. The scope audit finds exactly the 15
merged museum objects removed and 44 objects changed: the 15 merged houses, the 16 ended museum houses and their 13
successors; no geometry or city-stage changes.

## Not done

- The 18 deferred pairs.
- Museum house 74 touches the merged Storagatan house `way/274182776` with about 30 m² (8 % of the smaller outline),
  below the 15 % threshold that found the pairs. The edge overlap existed from 2021 before this review and now also
  shows from 1920; it is not treated as a duplicate.
- 41 OSM-vs-OSM overlaps (mostly new outlines in the 2026 extract) and 10 OSM-vs-symbol overlaps.
