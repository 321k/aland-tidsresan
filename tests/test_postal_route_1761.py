import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from postal_route_1761 import apply_postal_route_1761, REVIEW

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/postal-route-1761/before-postal-route-1761-step.json.gz')
OLD = 'road:finstrom:gamla-farjvagen:farjsundet'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class PostalRoute1761Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.review = read(REVIEW)

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_postal_route_1761(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, why, change):
        x = copy.deepcopy(self.review); change(x)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(x, catalog)
        self.assertIn(why, str(cm.exception)); self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        self.assertEqual(key(catalog)[OLD], key(self.built)[OLD])
        self.assertEqual([(s['from'], s['to'], s['state']) for s in key(catalog)[OLD]['states']], [(1638, 1761, 'open'), (1761, None, 'unknown')])
        self.assertEqual([o for o in catalog['objects'] if o['id'] != OLD], self.pristine['objects'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Old road dates do not follow its maps', lambda x: x['oldRoad'].update(until=1800))
        self.rejected("Old line does not end on today's road", lambda x: x['oldRoad'].update(endObjects=['road:emkarbyvagen']))
        self.rejected('Invalid free end', lambda x: x['oldRoad'].pop('freeEndBasis'))


if __name__ == '__main__':
    unittest.main()
