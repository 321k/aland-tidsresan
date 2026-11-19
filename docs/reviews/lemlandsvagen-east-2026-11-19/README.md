# Lemlandsvägen east of the church village · review 2026-11-19

The result and the reasoning are in `docs/lemlandsvagen-east.md`. This folder holds the evidence and the scripts.

## Scripts (run from the repository root with `.venv-geo/bin/python`)

- `scripts/overview.py`: overview windows along the reference line on a tile map or a registered base-map scan
- `scripts/grid_window.py`: a window with a 50 m grid and OSM roads (from the Hammarlandsvägen review's script)
- `scripts/prepare.py CATALOGUE_BEFORE.json.gz`: writes `data/lemlandsvagen-east.json`
- `scripts/drawn_in_year.py`: what the catalogue draws in a year, in magenta, over a map

`data/reference.json` is today's road, `road:qgis:lumparland:lemlandsvagen-100km3`, in EPSG:3874.

The catalogue before the step, read by `prepare.py` and the replay test, is kept in the local review cache:
`data/map-scan-cache/review/lemlandsvagen-east/before-lemlandsvagen-east-step.json.gz`. It is the build of commit
e0261bd, before this step.

## Renders

| file | map |
|---|---|
| `ov-lumparland-1929-*.jpg` | the parish map 1012 11 Lumparland, 1929 |
| `ov-senate-1917-*.jpg` | the Senate atlas, 1917 |
| `ov-101211-1968-*.jpg` | base map 101211, 1968 |
| `simons-grid-1929.jpg`, `simons-east-grid-1929.jpg`, `simons-east-grid-1985.jpg`, `simons-wide-1985.jpg`, `simons-wide-1995.jpg` | Simons and Skolsvängen |
| `delsviken-grid-1929.jpg` | Klubbensvägen and Fiskartorpsvägen |
| `result-1920-on-1929.jpg`, `result-1950-*-on-1929.jpg`, `result-1970-east-on-1968.jpg` | what the map draws |

Tiles for the Flaka sheet (1012 10, `map-39093008`) returned 403 at this location; the Lumparland sheet covers the
whole road east of the church village.

## Test logs

- `node-tests.log`: all JS tests
- `python-tests.log`: all Python tests
