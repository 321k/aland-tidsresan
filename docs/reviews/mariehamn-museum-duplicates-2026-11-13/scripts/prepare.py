"""Writes data/mariehamn-museum-duplicates.json: museum-map houses that overlap a later house, judged on the 1942 orthophoto
and the 1968 sheet 101208 (sheets.py, museum-NN.jpg; pair numbers below refer to pairs.json).

The 1920 museum map's houses were kept as provisional objects with assumed continued existence. Where one overlaps a
later house, the same building was drawn twice, or the museum house was replaced:
- merge: the 1942 photo shows one house where the later outline is, with the museum outline offset by 5–16 m; the later
  object keeps its identity and outline, takes over the museum record (evidence, links, aliases) and is shown from 1920;
- replacement: a different, usually much larger later building stands on the plot; the museum house ends at the
  successor's first reviewed evidence, the latest replacement boundary (demolition may be earlier);
- deferred: a shed or garage that is not the counterpart, an unclear shape or orientation, or a later house whose
  building-map review records it absent in 1968/1985.
Retained for audit; it fingerprints the catalogue as it was before this step (museum-before.json.gz in this folder).
Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/museum-duplicates/prepare.py
"""
import gzip, json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from mariehamn_museum_duplicates import fingerprint
P = Path('data/map-scan-cache/review/museum-duplicates')
cat = json.loads(gzip.decompress((P / 'museum-before.json.gz').read_bytes())); O = {o['id']: o for o in cat['objects']}
pairs = json.load(open(P / 'pairs.json'))
SYM = 'map-building:nls-symbol-'; OSM = 'building:osm:way-'; MUS = 'building:museum:'
MERGE_BASIS = ('Museikartans hus och den senare inmätta byggnaden tolkas som samma hus. Flygfotot 1942 visar ett hus där den senare '
               'konturen ligger; museikartans schematiska kontur ligger {d} meter därifrån, inom den äldre inpassningens osäkerhet, och inget '
               'annat hus på tomten passar bättre. Den senare uppmätta konturen används från museikartans 1920-tal; detta är ett '
               'kontinuitetsantagande, inte ett fastställt byggår.')
REPL_BASIS = ('Museikartans hus och den senare byggnaden på tomten tolkas som olika byggnader: den senare är {why}. Det äldre husets antagna '
              'fortsättning avslutas senast {year}, då efterföljaren först är belagd. Rivningen kan ha skett tidigare; {year} är den senaste '
              'belagda ersättningsgränsen, inte ett rivningsår.')
merges = [  # (pair, keep, donor)
    (12, SYM + '409', 83), (15, SYM + '429', 99), (17, SYM + '436', 66), (18, SYM + '445', 51), (22, SYM + '470', 63), (23, SYM + '477', 75),
    (24, SYM + '485', 60), (26, SYM + '486', 62), (27, SYM + '488', 151), (29, SYM + '520', 144), (33, OSM + '176377064', 94),
    (39, OSM + '274182776', 72), (40, OSM + '274188734', 111), (41, OSM + '415215787', 79), (49, OSM + '523420568', 7)]
replacements = [  # (pairs, museum, successors, why)
    ([1], 0, [SYM + '288'], 'det stora kvartershuset som flygfotot 1942 redan visar'),
    ([2], 1, [SYM + '288'], 'det stora kvartershuset som flygfotot 1942 redan visar'),
    ([4], 17, [SYM + '326'], 'en mycket större och längre byggnad'),
    ([5], 14, [SYM + '365'], 'en mycket större byggnad som täcker flera äldre hus'),
    ([6], 15, [SYM + '365'], 'en mycket större byggnad som täcker flera äldre hus'),
    ([7, 8], 3, [SYM + '373', SYM + '378'], 'två hus med annan orientering'),
    ([9], 44, [SYM + '390'], 'ett större hus med annan orientering som täcker två äldre hus'),
    ([10], 45, [SYM + '390'], 'ett större hus med annan orientering som täcker två äldre hus'),
    ([13], 101, [SYM + '410'], 'ett längre hus med annan orientering'),
    ([14], 81, [SYM + '419'], 'en mycket större byggnad'),
    ([16], 71, [SYM + '433'], 'ett större hus med annan orientering'),
    ([20], 49, [SYM + '448'], 'en mycket större byggnad som täcker flera äldre hus'),
    ([21], 53, [SYM + '448'], 'en mycket större byggnad som täcker flera äldre hus'),
    ([31, 35], 24, [OSM + '165529209', OSM + '1280029886'], 'en mycket större byggnad som redan ersatt grannhuset 1975, och senare den stora byggnaden från 2021'),
    ([42], 80, [OSM + '415215793'], 'en mycket större U-formad byggnad'),
    ([43], 88, [OSM + '415215793'], 'en mycket större U-formad byggnad')]
deferred = {
    'shed-not-counterpart': [(0, 55), (44, 205), (46, 56), (47, 58), (48, 55), (52, 61), (36, 68)],
    'unclear-shape-or-orientation': [(11, 42), (19, 103), (28, 116), (30, 119), (32, 48), (34, 104), (38, 11), (45, 206)],
    'map-review-records-absence': [(37, 8), (50, 105)],
    'courtyard-not-overlapping': [(3, 2)]}
start = lambda o: o['states'][0]['from']
inputs = {}
def pin(i): inputs[i] = fingerprint(O[i])
out_m, out_r = [], []
for n, keep, d in merges:
    donor = MUS + str(d); p = pairs[n]; assert {p['museum'], p['later']} == {donor, keep}, n
    pin(keep); pin(donor); dist = round((p['dx'] ** 2 + p['dy'] ** 2) ** 0.5)
    out_m.append(dict(id=f'museum-{d}', keep=keep, donor=donor, pair=n, fromYear=start(O[donor]), keepFrom=start(O[keep]),
                      offsetMeters=[p['dx'], p['dy']], basis=MERGE_BASIS.format(d=dist)))
    if d == 62:  # museum 62 also touches symbol 485, which merges with museum 60 (pair 24); merging 62 into 486 resolves both
        out_m[-1]['alsoResolvesPairs'] = [25]
for ns, m, succ, why in replacements:
    museum = MUS + str(m); pin(museum); [pin(s) for s in succ]
    for n in ns: assert pairs[n]['museum'] == museum and pairs[n]['later'] in succ, n
    year = min(start(O[s]) for s in succ)
    out_r.append(dict(id=f'museum-{m}', museum=museum, successors=succ, pairs=ns, endYear=year, basis=REPL_BASIS.format(why=why, year=year)))
    if m == 80:  # the small shed way/570786570 (pair 51) is not a successor; it no longer overlaps once the museum house ends
        out_r[-1]['alsoResolvesPairs'] = [51]
review = dict(schemaVersion=1, reviewedAt='2026-11-13',
              source=dict(id='review:mariehamn-museum-duplicates', title='Mariehamns museikartehus · dubbletter och ersättningar granskade mot flygfotot 1942',
                          url='assets/mariehamn-museum-duplicates.json'),
              aerialSourceId='mariehamn-aerial-1942', method=__doc__.split('Retained for')[0].strip(),
              merges=out_m, replacements=out_r,
              deferred={k: [dict(pair=n, museum=MUS + str(m), later=pairs[n]['later']) for n, m in v] for k, v in deferred.items()},
              inputs=dict(sorted(inputs.items())))
assert sorted([m['pair'] for m in out_m] + [n for m in out_m for n in m.get('alsoResolvesPairs', [])] + [n for r in out_r for n in r['pairs'] + r.get('alsoResolvesPairs', [])]
              + [n for v in deferred.values() for n, _ in v]) == list(range(len(pairs)))
Path('data/mariehamn-museum-duplicates.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(len(out_m), 'merges,', len(out_r), 'replacements,', sum(len(v) for v in deferred.values()), 'deferred pairs')
