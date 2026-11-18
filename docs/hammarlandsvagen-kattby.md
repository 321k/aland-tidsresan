# Hammarlandsvägen west of Kattby

Build step: `apply_hammarlandsvagen_kattby` in `scripts/hammarlandsvagen_main_road.py`, run straight after the Näfsby
review. Review data: `data/hammarlandsvagen-kattby.json` (copied to `dist/assets/`), written by
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/scripts/prepare_kattby.py`. Evidence:
`docs/reviews/hammarlandsvagen-main-road-2026-11-18/renders/kattby-west*.jpg` and `result-kattby-1950.jpg`, made with
`scripts/kattby_windows.py`.

The object "Hammarlandsvägen · Kattby västerut" (17.3–18.6 km from Mariehamn, way 69739598) was shown from 1959.
That year was an assumption: the opening of the Marsund bridge, used as the year for the whole road corridor to
Eckerö. No map dated it. The 1968 base map sheet 101206 covers only its eastern quarter. The northern review left it
as an open item, because the 1929 Hammarby sheet stops about 340 m west of the church.

## Sources

| map | use |
|---|---|
| Sockenkarta 1012 06 Hammarby, 1929, and its 1944 edition | the eastern 340 m, up to the sheet edge |
| Sockenkarta 1012 03 Eckerö, 1929 (colour, funet `map-39091228`) | the rest, west past Kockars and beyond the object's end |
| Sockenkarta 1012 03 Eckerö, 1956 (black and white, funet `map-37971493`) | the same, as a later edition |

The two Eckerö sheets were not in `data/historical-map-sources.json`. They are read through the vanhatkartat tiles of
the funet scans (tiles cached with sha256 in the church-road tile index). They are added to the catalogue as this
review's sources, `nls:map-39091228` and `nls:map-37971493`.

## Finding

Both 1929 sheets draw the road where today's road runs, with the same shape. The editions of 1944 and 1956 draw it the
same way:
- At Kockars and westwards, the map line is 9–15 m south of today's road.
- Near the edge between the two sheets (17.3–17.8 km), it is 17–29 m south. That is within the 25–30 m same-road rule
  of the earlier reviews.
- No other road runs at that distance today.

So this is the same road, not a realignment.

## Result

The object gets an earlier open state and geometry period from 1929 until 1959. The period uses its own copy of the
object's line, with the same coordinates. The 1959 assumption and everything after it stay as they were. The
object's marker `hammarlandsvagenMainRoad` names this review.

The step also checks that the object's 1929 line starts where the church corridor's 1929 line ends (within 2 m).
In 1929–1958 the main road from Söderby therefore runs without a gap to the west end of the object, except at
Drygsböle (see `docs/hammarlandsvagen-nafsby.md`).

## Open items

- West of the object (from 18.6 km) the Marsund connection to Eckerö is also shown from 1959 only. The Eckerö 1929
  sheet draws the road continuing west. Before the bridge there was a ferry, so whether the road reached the sound
  needs its own look.
