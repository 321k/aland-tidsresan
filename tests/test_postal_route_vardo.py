import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from postal_route_vardo import apply_postal_route_vardo, REVIEW

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/postal-vardo/before-postal-vardo-step.json.gz')
VV = 'road:qgis:vardo:vardovagen-200km1'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class PostalRouteVardoTests(unittest.TestCase):
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
        apply_postal_route_vardo(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
        return catalog

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        self.assertEqual(key(catalog)[VV], key(self.built)[VV])
        self.assertEqual([o for o in catalog['objects'] if o['id'] != VV], [o for o in self.pristine['objects'] if o['id'] != VV])
        self.assertEqual([(p['from'], p['to'], p.get('coverage')) for p in key(catalog)[VV]['geometryPeriods']], [(1971, 1985, 'partial'), (1985, None, None)])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        for why, change in (('Changed Hammarlandsvägen input', lambda x: x['early'][0].update(inputHash='changed')),
                            ('First year is not the first map', lambda x: x['early'][0].update(firstYear=1968))):
            x = copy.deepcopy(self.review); change(x)
            catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
            with self.assertRaises(ValueError) as cm:
                self.apply(x, catalog)
            self.assertIn(why, str(cm.exception)); self.assertEqual(before, catalog)


if __name__ == '__main__':
    unittest.main()
