# One fill for Mariehamn's city blocks in every year — 2026-11-17

## Problem

The city layer (`dist/city-grid.js`) filled blocks with `#e8e1cb` in most years, but two kinds of area gave other
browns:

- the built-up areas of the 1968, 1978 and 1982 base maps (`builtUp`) were filled with translucent `#c4ac8e88` on top
  of the blocks, so the screen showed `#d5c5ab` over the grass and `#c6be9d` where they covered blocks;
- the blocks of the 1860 plan were filled with translucent `#ecdebd55`, giving an olive `#b4ac87` over the grass.

Measured by sampling the drawn map canvas at 1860, 1861, 1942, 1968, 1978, 1985 and 2026 (Mariehamn centre).

## Change

- One constant, `CityGrid.BLOCK_FILL = '#e8e1cb'`, fills every block-like area: planned, reconstructed, mapped and
  built-up. Plans and built-up areas keep their dashed outlines, which are now their only difference.
- Built-up areas are drawn before (under) the blocks, so the block outlines stay visible where they overlap.
- Buildings, parks, yards and squares keep their own colours.

After the change the same sampling finds `#e8e1cb` as the block colour in every year and none of the other shades.

## Test

`tests/temporal-objects.test.cjs`, "city blocks have one fill in every year": draws every city stage from 1860 to
2026 with the real catalogue, records the fill of each block and built-up area, and requires exactly `#e8e1cb` and
built-up areas under the blocks in 1968. It fails on the previous code. 523 of 523 JS tests pass.

## What is committed

Only this folder. `dist/city-grid.js` in the last commit predates the built-up areas and catalogue-driven stages, so
the change cannot be committed on its own; `batch.patch` holds it (with the new test and the `city-grid.js` cache
stamp in `dist/index.html`). See `patch-verification.log`.

Deployed with the p11 photo batch as Cloudflare version 806d0727; 297 files matched live byte for byte.
