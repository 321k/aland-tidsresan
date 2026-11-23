import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from postal_route_haraldsby import apply_postal_route_haraldsby, REVIEW, SHORE as SHORE_REVIEW

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/postal-route-haraldsby/before-postal-route-haraldsby-step.json.gz')
P = 'road:qgis:saltvik:'
EARLY = [P + 'hamnvagen-batch4', P + 'sundsvagen-varsundet-haraldsby', P + 'haraldsbyvagen-sodra-anslutningen', P + 'haraldsbyvagen',
         P + 'gamla-sundsvagen-vaster', P + 'gamla-sundsvagen-oster']
SHORE = 'road:saltvik:farjvagen:farjsundet'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class PostalRouteHaraldsbyTests(unittest.TestCase):
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
        apply_postal_route_haraldsby(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
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
        for i in EARLY:
            self.assertEqual(key(catalog)[i], key(self.built)[i]); self.assertEqual(key(catalog)[i]['states'][0]['from'], 1929)
        self.assertEqual(key(catalog)[SHORE], key(self.built)[SHORE]); self.assertEqual(key(catalog)[SHORE]['states'][0]['from'], 1929)
        self.assertNotIn(SHORE, key(self.pristine))
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in EARLY + [SHORE]], [o for o in self.pristine['objects'] if o['id'] not in EARLY])
        # the straight road to the bridge is not the 1929 road (a red-only line on the 1929 sheet, absent in 1944)
        self.assertEqual(key(catalog)['road:finstrom:sundsvagen:godby-farjsundet'], key(self.pristine)['road:finstrom:sundsvagen:godby-farjsundet'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed Hammarlandsvägen input', lambda x: x['early'][3].update(inputHash='changed'))
        self.rejected('Invalid same-road ranges', lambda x: x['early'][1].update(ranges=[[196.9, 220.0]]))
        self.rejected('First year is not the first map', lambda x: x['early'][0].update(firstYear=1944))
        self.rejected('The early period must end where the object now begins', lambda x: x['early'][0].update(until=1968))


if __name__ == '__main__':
    unittest.main()
