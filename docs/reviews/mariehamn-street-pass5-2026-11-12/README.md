# Fifth and final Mariehamn street pass — 2026-11-12

This pass closes the Mariehamn street review. It dates 26 objects against the 1968, 1978, 1985 and 1995 editions of NLS sheet 101208, for 3,034.94 m of newly dated streets:

| First seen on the map | Metres |
| --- | ---: |
| 1968 | 896.21 |
| 1978 | 0 (junction pieces only) |
| 1985 | 970.46 |
| 1995 | 1,168.27 |

No existing object changes.

The pass dates three kinds of street:

- **Gaps in streets that were already dated:**
  - Sjukhusvägen, Mariegatan, the Esplanadgatans, Sjöpromenaden, Skeppargatan, Lotsgatan, Havsgatan, Neptunigatan, Hindersbölevägen and Grindmattesvägen.
  - Each piece starts at its neighbours' edition only when that edition shows it. Havsgatan's middle section and Neptunigatan's curve run through built-up blocks in 1968, so they start in 1985.
- **The Stenliden block:**
  - The Nya Godbyvägen–Bolstavägen junction pieces date from 1978 and count 0 m.
  - Uppgårdsvägen's link dates from 1985.
  - Uppgårdsvägen, Östra Stenliden, the eastern part of Kråkbärsstigen, Blåbärsstigen and Hjortronstigen date from 1995.
- **Lotsby and Ytternäs south:** Fiskhamnsvägen from 1968, Måsvägen and Doppingvägen from 1985.

A survey of the remaining city base found too little datable street length for another 10 km. The rest is absent through 1995, off the sheet, or needs a separate junction or footway review. The full write-up is the "Fifth and final pass" section that `batch.patch` adds to `docs/mariehamn-major-roads.md`.

## What is committed directly

These files belong only to this pass:

- `data/mariehamn-street-pass5.json`, the review data
- `dist/assets/mariehamn-street-pass5.json`, its published copy
- `scripts/mariehamn_street_pass5.py`, the build-time compiler (it uses the shared `apply_reviewed_streets`)
- `tests/mariehamn-street-pass5.test.cjs` and `tests/test_mariehamn_street_pass5.py`

## What is in `batch.patch`

The pass also edits files that are still uncommitted or untracked because they belong to earlier work. Committing them would stage that work, so this pass's edits are kept in `batch.patch` instead:

- `scripts/build_temporal_objects.py` runs the pass after the fourth pass and copies the review JSON to `dist`.
- `tests/temporal-objects.test.cjs` adds the new decisions to the identity count.
- `dist/index.html` gets the new recent-changes card "Sista gatorna i Mariehamn". The other cards are renumbered to 43, and the previous street-pass card is hidden. Generated preview bins and cache stamps are left out.
- `docs/mariehamn-major-roads.md` gets the fifth-pass section and its publication note.

The patch applies on top of the fourth pass's `batch.patch`. `patch-verification.log` records three checks:

- the patch applies cleanly to the pre-edit copies;
- applied, it reproduces the working-tree files, apart from the generated lines;
- it reverse-applies cleanly against the working tree.

## Evidence

- `sheets/ways-p*.jpg` are the per-way contact sheets for the gap and junction pieces, and `sheets/ways-p*.json` hold their boxes.
- `crops/lotsby-*.json` record the Lotsby area crop.
- `overlays/` holds recompressed copies of the Lotsby overlays and comparison pairs.

The original images and the pre-change catalogue snapshot `before.json.gz` stay in the git-ignored `data/map-scan-cache/review/mariehamn-major-roads/pass5/`. The Stenliden block was reviewed in the fourth pass; its sheets (`ways-a*.jpg`, `sten-*`) are in that pass's folder.

## Scripts and tests

- `scripts/prepare.py` writes the review JSON. It is kept for audit; do not rerun it blindly.
- `scripts/audit.py` writes `scope-audit.json`. Objects go from 36,189 to 36,215 and geometries from 46,839 to 47,060, all with the pass-5 prefix. No existing object changes.
- `logs/js-tests.log`: 480/480 passed.
- `logs/python-tests.log`: 82 tests, all passed.
- `publication/release-tests.log`: 143 relevant tests passed against the release tree.

## Publication

Deployed with Wrangler on 2026-11-12 as version `04f931de-8670-4551-b2e2-ab331cb34d07`. The release was built from the live version `e9000b11` plus only this pass. All 288 live files were checked byte for byte; see `publication/deployment.json`.
