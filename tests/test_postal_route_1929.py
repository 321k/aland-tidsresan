import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from postal_route_1929 import apply_postal_route_1929, REVIEW

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/postal-route-1929/before-postal-route-1929-step.json.gz')
EARLY = {'road:jomala:postgardsvagen': 1928, 'road:jomala:godbyvagen:golby-junction': 1928, 'road:jomala:godbyvagen:bjorkang': 1928,
         'road:finstrom:godby-korsningen': 1929, 'road:qgis:saltvik:von-knorringsvagen-1-batch4': 1929, 'road:rural:hammarland-way-459195076': 1929}


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class PostalRoute1929Tests(unittest.TestCase):
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
        apply_postal_route_1929(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
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
        for i, year in EARLY.items():
            self.assertEqual(key(catalog)[i], key(self.built)[i]); self.assertEqual(key(catalog)[i]['states'][0]['from'], year)
        self.assertEqual(key(catalog)['road:emkarbyvagen'], key(self.built)['road:emkarbyvagen'])
        changed = set(EARLY) | {'road:emkarbyvagen'}
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in changed], [o for o in self.pristine['objects'] if o['id'] not in changed])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed Hammarlandsvägen input', lambda x: x['early'][0].update(inputHash='changed'))
        self.rejected('First year is not the first map', lambda x: x['early'][0].update(firstYear=1917))
        self.rejected('The early period must end where the object now begins', lambda x: x['early'][1].update(until=1978))
        self.rejected('No map draws the extension', lambda x: x['extend'][0]['periods'][0].update(maps={'1928-jomala': 'absent'}))
        self.rejected('No map draws the extension', lambda x: x['extend'][0]['periods'][0].update(**{'from': 1800, 'to': 1894}))   # the 1800 period stays as it is
        self.rejected('Changed period to split', lambda x: x['split'][0].update(at=1968))


if __name__ == '__main__':
    unittest.main()
