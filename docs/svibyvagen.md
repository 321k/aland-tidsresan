# Sviby: the road from Hammarland towards Mariehamn

Build step: `apply_svibyvagen` in `scripts/svibyvagen.py`. It runs after the Södersundavägen step and before the
atlas review's late pass.

Review data, written by `docs/reviews/sviby-2026-11-23/scripts/prepare.py` and copied to `dist/assets/`:
- `data/svibyvagen.json`
- `data/svibyvagen-kasberg.json`
- `data/svibyvagen-old.json`

Evidence: `docs/reviews/sviby-2026-11-23/renders/`, read on these maps:
- the parish map 1012 05 Hammarudda–Kungsö (1928), with its Kungsö editions of 1944 and 1953;
- the parish map 1012 08 Maarianhamina (1929), with its Mariehamn edition of 1948;
- the base maps 1012 05 (1978) and 1012 08 (1968–1995).

## Finding

- **Through Sviby:** on the 1928 sheet, the road from Hammarland continues from Utängsvägen's east end straight
  east-south-east through Sviby. It ends in a T-junction with the north–south road at the sheet edge. The 1944 and 1953
  editions draw the same line, and the two sheets agree within 20 m.
  - On the 1978 base map, the airport covers the line's western half and Flygfältsvägen runs beside it.
  - Only its first 200 m east of Utängsvägen are drawn in 1978, up to the airport fence. That piece survives today as
    the service road along the fence (way 162795209, vertices 15–20), 8–15 m from the drawing.
- **Norra Svibyvägen:** the north–south road is today's Norra Svibyvägen, over its whole length. The 1929 sheet labels
  it "Svibyväg". Sheet 1012 05 has no 1968 base map, so the object was dated only from 1978.
- **Towards the town:** the 1929 and 1948 maps draw no direct road from the junction east to Svibyvägen; that road (the
  airport road) is first on the 1942 aerial photo (`docs/sviby-connections.md`). In 1929 the road to the town ran north
  along Norra Svibyvägen, then south-east along Kasbergsvägen, Kasbergsgatan and Svibyvägen. Kasbergsvägen follows the
  1929 road except at Talläsen:
  - On the 1929, 1948, 1968 and 1978 maps, the road there turns east and then south along the slope. This is a corner up
    to 63 m from today's diagonal.
  - The 1985 map draws the diagonal, so the object was dated from 1985.
- **Sheet registration:** the 1929 sheet lies 50–80 m off along its west edge. Its 1948 edition and the Kungsö sheets
  lie within 10–30 m, so positions were read on those.

## Result

| object | change | maps |
|---|---|---|
| Norra Svibyvägen | from 1928 (was 1978), whole | 1928, 1929, 1944, 1953 |
| Svibyvägen · del 1 | from 1929 (was 1937), whole | 1929 |
| Kasbergsvägen | from 1929 (was 1985); until 1985 without the diagonal at Talläsen (475–625 m) | 1929, 1948, 1968, 1978 |
| Gamla Kasbergsvägen · Talläsen (new, old road) | the corner, 1929–1985, then not drawn | 1929, 1948, 1968, 1978; absent 1985 |
| Kasbergsgatan (new, from OSM way 490727406) | from 1929 | 1929, 1968–1995 |
| Gamla vägen genom Sviby (new, old road) | main road 1928–1978; afterwards only the piece along the fence | 1928, 1944, 1953; 1978 the piece |

Notes on the table:
- The corner is read on the 1968 map. It is moved 18 m east, which is the scan's offset from OSM where the two run
  together.
- Kasbergsgatan owns its way in the OSM extracts from 2021, 2025 and 2026. In 2014 the stretch was part of Kasbergsvägen.
- Map years are first evidence, not construction years.

## Checks

The step runs all three files on one copy of the catalogue and replaces it only if every check passes. It uses the
Hammarlandsvägen helpers:
- **`_apply`:** the inputs' fingerprints, the first year is the first map marked present, and the cuts lie on each
  object. The corner's ends are on Kasbergsvägen, and no OSM road follows it.
- **The new-road check:** the way is owned whole in every extract that has it, and both ends rest on roads open in 1929.
- **`_old_roads`:** the Sviby road ends on Utängsvägen and on Norra Svibyvägen. Its surviving part is the OSM way's own
  vertices, within 20 m of the drawing, and it runs along no other road open in 1928–1978.

Scope (`docs/reviews/sviby-2026-11-23/scope-audit.json`):
- objects: 3 added, 3 changed;
- geometries: 7 added;
- sources: 5 added;
- nothing removed, and the atlas roads file is unchanged.

Tests:
- `tests/test_svibyvagen.py` (replay against the pre-step snapshot, and rejection cases);
- `tests/svibyvagen.test.cjs`.

## Open items

- **The junction at Kasberget:** done, see `docs/sviby-connections.md`.
- **The road east to Svibyvägen:** done, see `docs/sviby-connections.md`. It is on the 1942 aerial photo.
- **Into the town:** the town end of Svibyvägen. The 1929 streets of Mariehamn are dated by the town reviews.
