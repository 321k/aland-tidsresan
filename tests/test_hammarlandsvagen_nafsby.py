import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_nafsby, metric

REVIEW = 'data/hammarlandsvagen-nafsby.json'
# The catalogue as it is just before this step (built with the step disabled), kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-nafsby-step.json.gz')


class HammarlandsvagenNafsbyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        cls.pristine = cls.read(str(SNAPSHOT)) if SNAPSHOT.exists() else None
        cls.review = cls.read(REVIEW)

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_hammarlandsvagen_nafsby(lambda p: review if review is not None and p == REVIEW else self.read(p), catalog)
        return catalog

    def rejected(self, change):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(review, catalog)
        if '-v' in sys.argv: print('   rejected:', cm.exception)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        ids = [e['objectId'] for e in self.review['early']] + [self.review['oldRoad']['id']]
        key = lambda c, k: {x['id']: x for x in c[k]}
        self.assertEqual({i: key(catalog, 'objects')[i] for i in ids}, {i: key(self.built, 'objects')[i] for i in ids})
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in ids], [o for o in self.pristine['objects'] if o['id'] not in ids])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), len(ids))
        self.assertEqual(catalog['cityStages'], self.pristine['cityStages'])
        before = {o['id']: o for o in self.pristine['objects']}
        for e in self.review['early']:
            o = key(catalog, 'objects')[e['objectId']]; n = 2 if e.get('gapUntil') else 1     # the gap adds an 'unknown' state
            self.assertEqual(o['states'][n:], before[o['id']]['states']); self.assertEqual(o['geometryPeriods'][1:], before[o['id']]['geometryPeriods'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        e = {x['objectId'].rsplit('-', 1)[-1]: i for i, x in enumerate(self.review['early'])}
        self.rejected(lambda r: r['early'][0].update(inputHash='changed'))
        self.rejected(lambda r: r['early'][1].update(geometryHash='changed'))
        self.rejected(lambda r: r['early'][e['1419026568']].pop('laterGeometry'))                     # only the first geometry unless stated
        self.rejected(lambda r: r['early'][e['approach']].pop('pathIndex'))                           # two paths: whole or one path, never implicit
        self.rejected(lambda r: r['early'][e['1419026567']].pop('gapUntil'))                          # must end where the object begins (1985)
        self.rejected(lambda r: r['early'][e['1419026567']]['maps'].update({'1968': 'absent'}))       # a gap is unclear, not absent
        self.rejected(lambda r: r['early'][e['1419026567']]['maps'].pop('1968') and r['early'][e['1419026567']]['maps'].pop('1978'))
        self.rejected(lambda r: r['gapBasis'].clear())                                                 # the gap must be explained
        self.rejected(lambda r: r['early'][0]['ranges'].__setitem__(0, [0.0, 30.0]))                   # a partial cut must be at least 50 m

    def test_old_line_and_route_checks(self):
        self.rejected(lambda r: r['oldRoad'].update(id=r['early'][0]['objectId']))                     # never a second identity for a road
        def off_road(r):            # ends lie on today's roads (start moved 10 m along the line, length adjusted)
            p = r['oldRoad']['paths'][0]; t = 10 / metric(p[:2]).length
            p[0] = [p[0][i] + (p[1][i] - p[0][i]) * t for i in (0, 1)]
            r['oldRoad']['lengthMeters'] = round(sum(metric(q).length for q in r['oldRoad']['paths']), 1)
        self.rejected(off_road)
        self.rejected(lambda r: r['oldRoad'].update(endObjects=r['oldRoad']['endObjects'][:1]))
        self.rejected(lambda r: r['oldRoad']['maps'].update({'1968': 'present'}))                      # open until the first map without it
        def drop_korsbro(r):        # the Korsbroström piece closes the route (length and snaps adjusted, so only the route fails)
            r['oldRoad']['paths'].pop(); r['oldRoad']['endSnapMeters'] = r['oldRoad']['endSnapMeters'][:2]
            r['oldRoad']['lengthMeters'] = round(metric(r['oldRoad']['paths'][0]).length, 1)
        self.rejected(drop_korsbro)
        self.rejected(lambda r: r['route']['order'].remove('road:rural:hammarland-way-1419026567'))    # every dated piece is on the route
        self.rejected(lambda r: r['route']['order'].insert(2, r['route']['order'].pop(4)))             # in order along the road
        self.rejected(lambda r: r['early'][0]['ranges'].__setitem__(0, [0.0, 60.0]))                   # Lillåkersgränd cut must reach the link


if __name__ == '__main__':
    unittest.main()
