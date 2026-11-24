import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from sviby_paths import apply_sviby_paths, REVIEW

# The catalogue built before this step was added, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/sviby-paths/before-sviby-paths-step.json.gz')
EW, NP = 'road:jomala:sviby:vagen-mot-svibyvagen', 'road:jomala:norra-mockelovagen:norra-delen'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class SvibyPathsTests(unittest.TestCase):
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
        apply_sviby_paths(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
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
        for i in (EW, NP):
            self.assertEqual(key(catalog)[i], key(self.built)[i])
            for k in ('states', 'geometryPeriods', 'sourceLinks', 'modernRoadClass'):
                self.assertEqual(key(catalog)[i][k], key(self.pristine)[i][k])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in (EW, NP)], [o for o in self.pristine['objects'] if o['id'] not in (EW, NP)])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed Sviby paths target', lambda x: x['targets'][0].update(inputHash='changed'))
        self.rejected('Invalid road class period', lambda x: x['targets'][1]['roadClassPeriods'][0].update({'from': 1900}))
        self.rejected('Invalid road class period', lambda x: x['targets'][0]['roadClassPeriods'][0].update(evidenceIds=['missing']))
        self.rejected('class range is not the listed ways', lambda x: x['targets'][0]['roadClassPeriods'][0].update(canonicalRange=[0, 0.7]))
        self.rejected('class range is not the listed ways', lambda x: x['targets'][0]['roadClassPeriods'][0]['rangeWays'].append('way/35304978'))


if __name__ == '__main__':
    unittest.main()
