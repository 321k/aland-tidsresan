# Mariehamn junction review — 2026-11-12

This review dates the junction pieces that the street passes deferred, against the 1968, 1978, 1985 and 1995 editions of NLS sheet 101208. It adds six objects and 145.37 m of newly dated road, all from 1968. No existing object changes.

| Object | First edition | Counted metres |
| --- | --- | ---: |
| Ålandsplan ring (the southern half of the roundabout, between the dated ring pieces) | 1968 | 94.17 |
| Skarpansvägen's two lanes at the roundabout | 1968 | 27.79 (counted once) |
| Gesällgatan's approach to the roundabout | 1968 | 23.41 (counted once) |
| Godbyvägen–Bolstavägen junction: carriageways, turning lanes and Bolstavägen's eastern leg | 1968 | 0 (junction pieces) |
| Bolstavägen's western approach to that junction | 1978 (thick red overprint) | 0 (junction pieces) |
| Västra Utfarten's second carriageway at the crossing south of Klintvägen | 1995 (first edition with two carriageways) | 0 (parallel) |

Deferred items are listed in the review file:

- Framnäsvägen and Varvsvägen, which would end 6–9 m short of the network until 1995;
- Doktorsvägen's service section, a black path in 1995;
- cycleway-only connections;
- Mästargränd and Ekogränd;
- Michaelsvägen's roundabout.

The full write-up is the "Junction review" section that `batch.patch` adds to `docs/mariehamn-major-roads.md`.

## What is committed directly

- `data/mariehamn-junction-review.json`, the review data
- `dist/assets/mariehamn-junction-review.json`, its published copy
- `scripts/mariehamn_junction_review.py`, the build-time compiler (the shared `apply_reviewed_streets`, marker `mariehamnJunctionReview`)
- `tests/mariehamn-junction-review.test.cjs` and `tests/test_mariehamn_junction_review.py`

## What is in `batch.patch`

The review also edits files that are still uncommitted or untracked from earlier work. Committing them would stage that work, so this review's edits are kept in `batch.patch`, which applies on top of the fifth street pass's patch:

- `scripts/build_temporal_objects.py`: runs the review after the fifth pass and copies the review JSON to `dist`.
- `tests/temporal-objects.test.cjs`: the identity count includes the new decisions.
- `dist/index.html`: the loader card "Korsningar i Mariehamn". Generated preview bins and cache stamps are left out.
- `docs/mariehamn-major-roads.md`: the "Junction review" section.

`patch-verification.log` records two checks: the patch applies to the post-pass-5 copies, and it reproduces the state right after this review. The working tree also carries the later 1942 approach review; `docs/reviews/mariehamn-approaches-1942-2026-11-12/batch.patch` takes the same files from that state to the working tree.

## Evidence and scripts

- `overlays/j?-seq.jpg` are the four-edition strips for:
  - A: Godbyvägen–Bolstavägen;
  - B: Ålandsplan;
  - C: Västra Utfarten at Klintvägen;
  - D: Doktorsvägen's service section, deferred.

  `overlays/*-overlay.jpg` are the per-edition crops with the undated pieces highlighted. All are recompressed JPEG copies.
- `crops/*.json` record each crop's bbox, pixel box, scale and scan SHA-256. `scripts/crop.py` recreates them from the git-ignored scan cache.
- `scripts/prepare.py` writes the review JSON from the pre-change snapshot. It is kept for audit; do not rerun it blindly.
- `scripts/audit.py` writes `scope-audit.json`. Objects go from 36,215 to 36,221 and geometries from 47,060 to 47,200; all 140 new geometries carry the review's prefix. Nothing existing changed and the city stages are unchanged.

## Tests

- `logs/js-tests.log`: full JavaScript suite, 485/485 passed.
- `logs/python-tests.log`: 89 tests in the affected Python modules, all passed.
- `publication/release-tests.log`: the relevant JavaScript tests run against the release tree.

## Publication

Deployed together with the 1942 approach review on 2026-11-12 as Cloudflare version `7c730ce9-4a66-4379-b989-eeb38575c641`, because the 1942 step runs after this review in the same build. The release was built from the live version `04f931de` plus only these two reviews. All 290 live files were checked byte for byte; see `publication/deployment.json`.
