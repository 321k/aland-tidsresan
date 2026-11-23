import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from postal_route_storby import apply_postal_route_storby, REVIEW
from rural_registration import registration_pair

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/postal-storby/before-postal-storby-step.json.gz')
EK, SM = 'road:eckero:eckerovagen:storby-hamn', 'road:eckero:sandmovagen:posthuset'
REG = 'docs/reviews/postal-route-2026-11-23/data/registrations-101215.json'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class PostalRouteStorbyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.review = read(REVIEW)

    def test_registrations_pass_the_printed_grid_checks(self):
        for s in read(REG)['sources']:
            registration_pair(s)                                    # raises if the mesh or an independent check fails

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_postal_route_storby(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, why, change):
        x = copy.deepcopy(self.review); change(x)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(x, catalog)
        self.assertIn(why, str(cm.exception)); self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        for i in (EK, SM):
            self.assertEqual(key(catalog)[i], key(self.built)[i]); self.assertEqual(key(catalog)[i]['states'][0]['from'], 1968)
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in (EK, SM)], self.pristine['objects'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')
        self.rejected('A free end needs a stated basis', lambda x: x['newRoads'][1].pop('freeEndBasis'))
        self.rejected('does not abut', lambda x: x['newRoads'][0]['sourceLinks'][0].pop('partialBasis'))
        self.rejected('Changed OSM source', lambda x: x['newRoads'][0]['sourceLinks'][1].update(input='changed'))
        self.rejected('does not join', lambda x: x['newRoads'][0].update(end='road:emkarbyvagen'))


if __name__ == '__main__':
    unittest.main()
