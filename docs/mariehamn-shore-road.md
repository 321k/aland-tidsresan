# Nygatan's museum duplicate and the shore road on Västerhamn (2026-11-16)

Both were found by drawing the map's streets over the 1942, 1952, 1962, 1975 and 2021 orthophotos.

## The extra cross-street north of Norragatan

The museum's 1920s picture has two straight cross-streets north of Norragatan. `city-1920-street-38` ("Tvärgata vid
stadens norra kvarter") lies on Nygatan and was already linked to it. `city-1920-street-39` ("Tvärgata norr om
Norragatan") runs 60–90 m further south, from the harbour west to Neptunigatan. On the 1942 photo there is no street
on that line: it crosses house rows and gardens in every block, and the 1942 tracing with the same name was already
identified as Nygatan. The 1920 and 1927 maps nevertheless drew it as a second street.

`data/nygatan-review.json` now lists it under `retiredMuseumTraces` (with its input fingerprint). The Nygatan compiler
(`scripts/nygatan_continuity.py`) validates it, keeps it as identity-only evidence on `road:nygatan` with its
original geometry and source link, and removes its copies from the interpreted 1920 and 1927 stages; the block
outlines of those stages are recomputed. Nygatan's 1942 note no longer begins with the raw trace name.
`data/building-issue-review.json` pins Nygatan as context for the Köpmansgatan school decision; its fingerprint was
re-pinned, the decision itself is unchanged.

## The shore road (today's Sjöpromenaden)

The photos of 1942, 1952 and 1962 show a road along the west shore from the harbour north past the beach and the
boathouses, in the same place as today's Sjöpromenaden, but no object covered it before the 1968 base map. The
museum's "Västra strandens gata" (`city-1920-street-36`) is a coarse drawing of the same road (its north end lies
up to 40 m out in the water); the 1942 frame review had matched the 1942 tracing of that name to Havsgatan and left
the shore road undrawn.

`data/mariehamn-shore-road.json` and `scripts/mariehamn_shore_road.py` (run after the 1942 frame step):

* the three Sjöpromenaden objects get the museum drawing (1920, decade, interpretation) and the 1942 photo as
  evidence, states 1920–1942 and 1942–1968, and an earlier geometry period with their own measured centre lines;
* the long northern part (`way-77077157`) is shown before 1968 only south of latitude 60.1004 (`coverage: partial`,
  `canonicalRange [0.685, 1]`). North of that the modern road runs along a rocky shore where the 1942 and 1952 photos
  show no road; by 1962 a road is visible further north, but that part keeps its 1968 start;
* the museum drawing's stage copies are removed from 1920 and 1927; the drawing stays in the source dataset, linked
  to the northern part and kept as original geometry on all three. Its southern remainder towards Lotsberget, where
  the 1942 photo shows no road, is not drawn.

Each member must lie within 40 m of the drawing; inputs are fingerprinted and every check runs before the catalogue
changes. Tests: `tests/mariehamn-shore-road.test.cjs`, `tests/nygatan.test.cjs`. Scope audit against the catalogue
before the change: exactly `road:nygatan` and the three Sjöpromenaden objects changed, three geometries and one source
were added, and only the 1920, 1927, 1942 and 1952 stages changed.
