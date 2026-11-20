# Postad: the old curve of Hammarlandsvägen

Build step: `apply_hammarlandsvagen_postad` in `scripts/hammarlandsvagen_main_road.py`. It runs after the Sundsvägen
step and before the road-remnant step and the atlas review's late pass.

Review data: `data/hammarlandsvagen-postad.json` (copied to `dist/assets/`), written by
`docs/reviews/road-remnants-2026-11-20/scripts/prepare_postad.py`.

Evidence, in `docs/reviews/road-remnants-2026-11-20/renders/`:
- `ha-17-8-1929.jpg`, `ha-17-8-1944.jpg`: the register outline on the parish map 1012 06 Hammarby (1929) and its 1944
  edition
- `result-postad-1950-1970.jpg`: what the map draws

## Finding

The heritage register records a road remnant at Postad, Ha 17.8: "Väglämning – Postad". It is about 450 m long, runs
NW–SE, belongs to the early-modern postal road through Åland, and is abandoned for good in the north-west.

- **On the 1929 map and the 1944 edition**, the main road follows the register outline. It runs in a curve up to 70 m
  east of today's straight line, between 119 m and 575 m along "Hammarlandsvägen · Postad–Korsängen".
- **The first Hammarlandsvägen review** (`docs/hammarlandsvagen-main-road.md`) had dated the whole of Postad–Korsängen
  from 1929. It missed this curve.
- **The straight line** is first on the 1968 base map. From then on only the curve's north-west end remains, as the
  existing object "Äldre väg vid Korsberg", dated from 1968. The register's "abandoned" north-west end and this
  surviving part are at opposite ends of the curve. The register describes the remnant, not today's roads.

## Result

- **The main-road review** (`data/hammarlandsvagen-main-road.json`, from its `prepare.py`): Postad–Korsängen's 1929–1967
  period now leaves out 119.3–575.0 m. Its same-road interval is split at the reference points `postad-curve` (15 520.3 m)
  and `postad-rejoin` (15 976.0 m). All its input fingerprints are unchanged.
- **"Äldre väg vid Korsberg"** is the same physical road, so it keeps its identity and gains an early period, open from
  1929 until 1968. That period draws the whole curve, 497 m:
  - its own 12 vertices where it survives;
  - then the centre line of the register outline, which was surveyed;
  - then today's road, where the 1929 stretch resumes.

  474 m of the curve lie within 10 m of the outline. From 1968 the object is as before.
- **The atlas review** (`data/regional-road-review.json`) gets a late link for the Korsberg road (atlas vertices
  10–21). The 1894 atlas line is therefore not drawn beside the curve in 1929–1967.

## Checks

- **Inputs:** the Korsberg road's and Postad–Korsängen's fingerprints, and the Korsberg geometry digest.
- **Dates:** the maps, with 1929 as the first marked present.
- **The curve:** it keeps the Korsberg vertices unchanged, both its ends rest within 1 m of today's road as dated for
  1929, and it runs inside the register outline for at least 450 m.
- **Overlap:** it does not run along any other road open in 1929–1967.

Tests:
- `tests/test_hammarlandsvagen_postad.py`;
- `tests/road-remnants.test.cjs`;
- `tests/hammarlandsvagen-main-road.test.cjs`, which now expects Postad–Korsängen in two pieces in 1950, joined by the
  curve.
