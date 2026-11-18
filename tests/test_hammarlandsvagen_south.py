import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_south

REVIEW = 'data/hammarlandsvagen-south.json'
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-south.json.gz')


class HammarlandsvagenSouthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        cls.pristine = cls.read(str(SNAPSHOT)) if SNAPSHOT.exists() else None
        cls.review = cls.read(REVIEW)

    def setUp(self):
        # The catalogue just before this review is kept in the local review cache; without it these tests are skipped.
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_hammarlandsvagen_south(lambda p: review if review is not None and p == REVIEW else self.read(p), catalog)
        return catalog

    def rejected(self, change):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            self.apply(review, catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        ids = [e['objectId'] for e in self.review['early']]
        key = lambda c, k: {x['id']: x for x in c[k]}
        self.assertEqual({i: key(catalog, 'objects')[i] for i in ids}, {i: key(self.built, 'objects')[i] for i in ids})
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in ids], [o for o in self.pristine['objects'] if o['id'] not in ids])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), len(ids))
        self.assertEqual(catalog['cityStages'], self.pristine['cityStages'])
        before = {o['id']: o for o in self.pristine['objects']}
        for o in catalog['objects']:
            if o['id'] in ids:
                self.assertEqual(o['states'][1:], before[o['id']]['states']); self.assertEqual(o['geometryPeriods'][1:], before[o['id']]['geometryPeriods'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected(lambda r: r['early'][0].update(inputHash='changed'))
        self.rejected(lambda r: r['early'][1].update(geometryHash='changed'))
        self.rejected(lambda r: r['early'][2].update(until=1978))                                    # must end where the object begins
        self.rejected(lambda r: r['early'][1]['maps'].update({'1928': 'absent'}))                      # first year must be the first map with the road
        self.rejected(lambda r: r['early'][0]['ranges'].__setitem__(0, [4000.0, 4030.0]))              # a partial cut must be at least 50 m
        self.rejected(lambda r: r['early'][3]['maps'].update({'1917': 'present'}))                     # only reviewed maps may be cited
        self.rejected(lambda r: r['maps']['1928'].update(sourceId='nls:unknown'))                      # every map must be a known source


if __name__ == '__main__':
    unittest.main()
