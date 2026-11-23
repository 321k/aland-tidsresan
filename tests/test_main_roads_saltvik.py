import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from main_roads_saltvik import apply_main_roads_saltvik, REVIEW

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/main-roads-saltvik/before-main-roads-saltvik-step.json.gz')


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class MainRoadsSaltvikTests(unittest.TestCase):
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
        apply_main_roads_saltvik(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, why, change):
        x = copy.deepcopy(self.review); change(x)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(x, catalog)
        self.assertIn(why, str(cm.exception)); self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        ids = [e['objectId'] for e in self.review['early']]
        key = lambda c: {x['id']: x for x in c['objects']}
        for i in ids:
            self.assertEqual(key(catalog)[i], key(self.built)[i]); self.assertEqual(key(catalog)[i]['states'][0]['from'], 1968)
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in ids], [o for o in self.pristine['objects'] if o['id'] not in ids])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed Hammarlandsvägen input', lambda x: x['early'][0].update(inputHash='changed'))
        self.rejected('The early period must end where the object now begins', lambda x: x['early'][0].update(until=1978))
        self.rejected('First year is not the first map', lambda x: x['early'][0].update(firstYear=1960))
        self.rejected('Invalid same-road ranges', lambda x: x['early'][5].update(ranges=[[0.0, 2210.0], [2190.0, 5950.0]]))
        self.rejected('Invalid later stage', lambda x: x['early'][3]['laterStage'].update(firstYear=1990))


if __name__ == '__main__':
    unittest.main()
