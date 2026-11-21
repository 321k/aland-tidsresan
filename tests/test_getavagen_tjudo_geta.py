import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from getavagen import apply_getavagen_tjudo_geta

REVIEW = 'data/getavagen-tjudo-geta.json'
SNAPSHOT = Path('data/map-scan-cache/review/getavagen/before-getavagen-tjudo-geta-step.json.gz')
TJ, FEN = 'road:qgis:tjudo:getavagen-100km1', 'road:tjudo:gamla-getavagen:fenell'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class GetavagenTjudoGetaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.review = read(REVIEW); cls.ids = [e['objectId'] for e in cls.review['early']] + [FEN]

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_getavagen_tjudo_geta(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, change, why):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(review, catalog)
        self.assertIn(why, str(cm.exception))
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        for i in self.ids:
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in self.ids], [o for o in self.pristine['objects'] if o['id'] not in self.ids])
        self.assertEqual([(p['from'], p['to']) for p in key(catalog)[TJ]['geometryPeriods']], [(1927, 1968), (1968, 1984), (1984, None)])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        e = lambda r: r['early'][0]; od = lambda r: r['oldRoad']
        self.rejected(lambda r: e(r).update(inputHash='changed'), 'Changed Hammarlandsvägen input')
        self.rejected(lambda r: e(r)['laterStage'].update(firstYear=1990), 'Invalid later stage')
        self.rejected(lambda r: od(r)['maps'].update({'1984': 'present'}), 'Old road dates')
        self.rejected(lambda r: od(r).update(todayRoadName='Hammarlandsvägen'), 'survives as')          # today's Getavägen is where the loop's ends merge
        self.rejected(lambda r: e(r)['ranges'][0].__setitem__(0, e(r)['ranges'][0][0] + 60), 'route breaks')


if __name__ == '__main__':
    unittest.main()
