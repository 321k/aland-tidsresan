import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from postal_route_sund import apply_postal_route_sund, REVIEW

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/postal-route-sund/before-postal-route-sund-step.json.gz')
LAP, KW, KE = 'road:sund:sundsvagen:lappbole-bladkant', 'road:sund:sundsvagen:klippan-vast', 'road:sund:sundsvagen:klippan-ost'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class PostalRouteSundTests(unittest.TestCase):
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
        apply_postal_route_sund(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
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
        for i, year in ((LAP, 1968), (KW, 1978), (KE, 1978)):
            self.assertEqual(key(catalog)[i], key(self.built)[i]); self.assertEqual(key(catalog)[i]['states'][0]['from'], year)
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in (LAP, KW, KE)], self.pristine['objects'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('does not abut', lambda x: x['newRoads'][0]['sourceLinks'][0]['sourceVertexRange'].__setitem__(0, 5))
        self.rejected('Changed OSM source', lambda x: x['newRoads'][1]['sourceLinks'][0].update(input='changed'))
        self.rejected('does not join', lambda x: x['newRoads'][2].update(end='road:emkarbyvagen'))
        self.rejected('New road dates do not follow its maps', lambda x: x['newRoads'][1]['maps'].update({'1968-klippan': 'present'}))


if __name__ == '__main__':
    unittest.main()
