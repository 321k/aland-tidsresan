# 1942 approach traces reviewed against the orthophoto — 2026-11-12

The 1942 city stage (shown 1942–1967) contained five hand traces of approach roads. They were drawn on the official orthophoto of 25 July 1942 in a 4 m/pixel view, with only 12–13 points per road over 2–3 km. They were not attached to persistent objects, and from 1968 their parts outside the reviewed city area were still drawn, until 2013. This review checks three of the traces against the original photo, the 1968 NLS sheet 101208 and today's roads. The photo was fetched as georeferenced 2 m/pixel tiles: EPSG:3874, with tile x = E // 512 and y = N // 512.

- **Södra vägen på halvön, 1942: rejected.** There is no road under it on the 1942 photo. South of the town edge it crosses continuous forest and rocky ground, and its northern end crosses what are built-up blocks by 1968. The 1968 map shows no road there either. The real peninsula road in 1942 is the main road (Västra Ytternäsvägen), 100–330 m to the west. The trace is no longer drawn in the city stages or in the older-roads layer; its original pixels stay in the trace files.
- **Östra infarten norrifrån: 17 objects shown from 1942.** The road is clearly visible on the photo. Godbyvägen (6 objects), Johannebovägen, Grindmattesvägen and nine Strandgatan pieces get the photo as 1942 evidence and are drawn with their own centre lines.
- **Västra infarten norrifrån: 13 objects shown from 1942.** Also clearly visible. The objects are Svibyvägen, Klintvägen's straight northern part (still partial until its 1978 bend), Klintgränd, Västra Utfarten's diagonal and nine Ålandsvägen pieces.

The coarse traces were up to 20–60 m off these roads. Where no persistent object matches the 1942 road, the 1942 and 1952 stages draw a short connecting piece, seven in all. Two of them were retraced from the photo:

- Grindmattesvägen to Strandgatan;
- Svibyvägen to Klintvägen.

Each retrace is a least-cost path over the pale road surface between the two object ends, simplified to 2 m and checked visually (`images/retrace-ostra.jpg`, `images/retrace-vastra.jpg`). The coarse trace was 30–40 m off on these two stretches. The other five keep the reviewed trace remainder, with its ends moved onto the adjoining objects. The traces' last stretches into the town are not drawn: Östra's runs along Strandgatan, which is already shown from 1861, and Västra's is 30–50 m off.

From 1968 only the dated objects are drawn, so the three raw traces' carried-over parts are removed from the 1968–2013 stages. The review file lists the objects that are not backdated, each with a reason:

- Godbyvägen's northernmost object, which runs past the photo edge;
- the Godbyvägen–Bolstavägen junction pieces;
- Skiljevägen;
- Nya Godbyvägen;
- Stenhuggarvägen, whose north end hooks west where the photo shows no road;
- Svibyvägen's slip piece at the later Västra rondellen;
- the Västra Utfarten stub and the split pieces at Ålandsplan;
- Strandgatan `way-35011592`, which the 1942 city map's own Strandgatan trace already draws.

The photo dates presence, not construction.

## What is committed directly

- `data/mariehamn-approaches-1942.json`: the review. It holds input hashes of the original traces, their city-stage copies and every object, the per-approach distance guards, the retraced gaps and the reasons.
- `dist/assets/mariehamn-approaches-1942.json`: its published copy.
- `scripts/mariehamn_approaches_1942.py`: the build-time compiler. It runs after the junction review and validates everything before changing the catalogue.
- `tests/mariehamn-approaches-1942.test.cjs` and `tests/test_mariehamn_approaches_1942.py`.
- Five tracked tests whose only change is to allow this reviewed 1942 evidence (marker `approach1942`): `tests/mariehamn-major-road-followups.test.cjs` and `tests/mariehamn-street-pass3.test.cjs` / `-pass4.test.cjs` (the "absent before the first edition" check), and `tests/test_mariehamn_street_pass3.py` / `_pass4.py` (the 1942 additions are undone before comparing with the pass's own output).

## What is in `batch.patch`

These files are still uncommitted or untracked, or carry other people's uncommitted changes, so this review's edits are kept in `batch.patch`:

- `scripts/build_temporal_objects.py`: runs the review after the junction review and copies its JSON to `dist`.
- `scripts/build_historical_roads.py`: drops rejected traces from the older-roads layer.
- `tests/temporal-objects.test.cjs`, `tests/mariehamn-major-roads.test.cjs` and `tests/qgis-roads.test.cjs`: allow the 1942 evidence for reviewed objects.
- `tests/mariehamn-core.test.cjs`: two Strandgatan pieces of the northern extension now start in 1942 from the photo, and the guard still checks that `way-35011592` is not backdated.
- `tests/historical-roads.test.cjs`: the 1942 set has four traces.
- `tests/rural-map-review.test.cjs`: the fixture drops city-stage references to the objects it removes.
- `dist/index.html`: the loader card "Infartsvägarna 1942 rättade". Generated preview bins and cache stamps are left out.
- `docs/mariehamn-major-roads.md`: the "1942 approach traces" section and the joint publication note.

The four files shared with the junction review start from the state that `docs/reviews/mariehamn-junction-review-2026-11-12/batch.patch` produces. `patch-verification.log` records three checks: the patch applies to the pre-edit copies, it reproduces the working tree, and it reverse-applies cleanly.

## Evidence, data and scripts

- **Rejected Södra trace:** `images/sodra-1942-pair.jpg`, `sodra-zoom*.jpg`, `sodra-1968.jpg`.
- **Objects labelled on the photo:** `images/ostra-label-*.jpg` and `vastra-label-*.jpg`, with legends in `data/ostra-label.json` and `data/vastra-label.json`.
- **Close checks:** `images/chk-*.jpg` (Stenhuggarvägen's hook and the Klintgränd junction).
- **The map as built:** `images/result-1945.jpg` and `result-1970.jpg`. Green is the objects shown from 1942, red the connecting pieces, white the old traces, which are no longer drawn.
- **Retraced centre lines:** `data/retrace-*.json`. `images/retrace-ostra-ridge.jpg` is an earlier brightest-pixel attempt that wandered into clearings; it was not used.
- **Tile list:** `data/tile-manifest.json`, with SHA-256 for each tile. The tiles and the pre-change snapshot `before.json.gz` stay in the git-ignored `data/map-scan-cache/review/trace-1942/`.
- **`scripts/prepare.py`:** writes the review from the snapshot. It is kept for audit; do not rerun it blindly.
- **`scripts/retrace.py`:** the least-cost retrace. `label.py` and `ridge.py` are review helpers.
- **`scripts/audit.py`:** writes `scope-audit.json`. It confirms that the baseline equals the snapshot and that exactly the 30 reviewed objects changed, each with its earlier states, periods, evidence and source links kept after the new 1942 entries. No geometry was added or changed, and in each city stage only the three trace features were removed.

## Tests

- `logs/js-tests.log`: full JavaScript suite, 490/490 passed.
- `logs/python-tests.log`: 91 tests in the affected Python modules, all passed.
- `publication/release-tests.log`: 226 relevant JavaScript tests run against the release tree.

## Publication

Deployed together with the junction review on 2026-11-12 as Cloudflare version `7c730ce9-4a66-4379-b989-eeb38575c641`, built from the live version `04f931de` plus only these two reviews. All 290 live files were checked byte for byte; see `publication/deployment.json`.
