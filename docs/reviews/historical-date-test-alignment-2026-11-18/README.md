# Older review tests and the historical-date review — 2026-11-18

The historical-date review (`scripts/historical_date_review.py`, not yet committed) gives 21 objects a sourced earlier
start than the map or photo review that first dated them: the Klinten roads from 1937, Västra utfarten from 1967,
Järsövägen from 1975, Bjärströms bro from 1538, the Ceders buildings, Norragatan 31 and Norra Esplanadgatan 9 A, and
others. Each keeps its earlier review's year as `historicalDating.previousFirstYear`. Fifteen older tests still
required the earlier review's year as the first year and failed.

The tests now accept a sourced earlier start when an object has `historicalDating`, and check instead that
`previousFirstYear` is the year the review set. Nothing else in them is loosened.

- `mariehamn-approaches-1942`, `mariehamn-street-pass3`, `mariehamn-street-pass4`, `mariehamn-major-road-followups`,
  `qgis-roads`: first-year checks read the sourced start; the 1942 approach state index allows the extra state.
- `mariehamn-building-maps`, `mariehamn-building-photos`, `mariehamn-museum-duplicates`: dated buildings with a
  sourced earlier start skip the state-structure checks of the earlier review and are drawn from their sourced year.
- `rural-map-review`: Bjärströms bro is owned from 1538; the test that rebuilds the model without QGIS roads also drops
  relationships pointing at them (the historical-date review links the old Färjsund crossing to Sundsvägen).
- `qgis-roads` also reads Långskata del 2's 1917 start from the Lemlandsvägen early-map review
  (`docs/reviews/lemlandsvagen-main-road-2026-11-17`), which the Svibyvägen failure had hidden.

Committed directly: the building-maps, building-photos, museum-duplicates and street-pass4 tests, which had no other
uncommitted work. The other five files also hold other uncommitted work, so their changes are in `batch.patch`
(see `patch-verification.log`). `js-tests.log`: 567 of 567 JS tests pass.
