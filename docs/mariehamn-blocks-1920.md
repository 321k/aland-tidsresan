# Blocks carried through the 1920s stages

Review: `data/mariehamn-blocks-1920.json`, applied at build time by `scripts/mariehamn_blocks_1920.py`, straight after
the 1985 block step (`docs/mariehamn-blocks-1985.md`) in `scripts/build_temporal_objects.py`. Reviewed 2026-11-19.

## Why

The 1871 reconstruction stage (`city-reconstruction-1871`, shown 1871–1919) draws the town plan's blocks. The 1920 and
1927 stages, from the 1920s museum map, take their blocks only from street lines that close a loop. Where they do not
close, the land showed through, so about ten blocks turned from beige to green in 1920. The 1942 stage draws them as
blocks again. Nothing on the maps says those blocks went away. One example is the block between Ålandsvägen and
Mariegatan (`city-reconstruction-1871:block:13:alandsvagen:0:mariegatan:0`), north of Norra Esplanadgatan.

## What the step does

The step changes every city stage that starts in 1920–1941. Today these are `city-reconstruction-1920` and
`city-reconstruction-1927`. Into each it carries plain `block` fill (`carriedBlock`: the 1871 stage id):
- what it carries: the part of the 1871 blocks that the 1942 stage also covers with blocks. Only blocks drawn on both
  sides of the gap are carried;
- what it leaves out: the stage's own blocks, parks and squares (+1 m, so nothing is drawn twice), and 4 m around the
  stage's streets, as the derived blocks are;
- what it drops: pieces under 150 m².

No objects are created or changed. The fill is an interpretation of block extent, not evidence of individual houses.
The method is the same as the 1985 step's.

In the current build it adds 14 pieces, 71,194 m², to each of the two stages.

## Checks

The step is rejected as a whole, leaving the catalogue unchanged, if:
- the 1871 or 1942 blocks changed (digest);
- the list of stages differs;
- a stage already has carried blocks;
- the carried area is more than 10 % off the recorded figure.

Tests:
- `tests/mariehamn-blocks-1920.test.cjs`;
- `tests/test_mariehamn_blocks_1920.py`. Its pre-step snapshot is kept in `data/map-scan-cache/review/blocks-1920/`.

The 1985 step's replay snapshot (`data/map-scan-cache/review/blocks-1985/before.json.gz`) was rebuilt with this step
in place.

## Not carried

These parts of the 1871 blocks have no block fill in any stage from 1920 to 1952, so they stay green from 1920:
- about half of block 13 (its east part);
- block 16;
- block 18 at Skillnadsgatan.

All three lie on the east side towards Österhamn. The 1968 base map draws built-up areas over block 16 and most of
block 18. Whether the 1871 reconstruction drew blocks there that were only planned, or the 1920s and 1940s maps leave
out blocks that existed, is not settled.
