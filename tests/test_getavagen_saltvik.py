import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from getavagen import apply_getavagen_saltvik

REVIEW = 'data/getavagen-saltvik.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/getavagen/before-getavagen-saltvik-step.json.gz')
GE = 'road:qgis:saltvik:getavagen-godby-norra-bladgransen'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class GetavagenSaltvikTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.review = read(REVIEW); cls.ids = [e['objectId'] for e in cls.review['early']]

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_getavagen_saltvik(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
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
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), 6)
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        e = lambda r, i: next(x for x in r['early'] if x['objectId'] == i)
        self.rejected(lambda r: e(r, GE).update(inputHash='changed'), 'Changed Hammarlandsvägen input')
        self.rejected(lambda r: e(r, GE)['maps'].update({'1929': 'unclear'}), 'First year is not the first map')
        self.rejected(lambda r: e(r, GE)['ranges'][0].__setitem__(1, e(r, GE)['ranges'][0][1] - 80), 'route breaks')     # Bartsgårdavägen no longer joins
        self.rejected(lambda r: e(r, 'road:qgis:saltvik:saltviksvagen-1-batch4')['ranges'][0].__setitem__(0, 1900.0), 'route breaks')


if __name__ == '__main__':
    unittest.main()
