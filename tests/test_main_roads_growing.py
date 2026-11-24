import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from main_roads_growing import apply_main_roads_growing, REVIEW

# The catalogue built before this step was added, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/main-roads-growing/before-main-roads-growing-step.json.gz')


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class MainRoadsGrowingTests(unittest.TestCase):
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
        apply_main_roads_growing(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, why, change):
        x = copy.deepcopy(self.review); change(x)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(x, catalog)
        self.assertIn(why, str(cm.exception)); self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        ids = {t['objectId'] for t in self.review['objects']}
        key = lambda c: {x['id']: x for x in c['objects']}
        for i in ids:
            self.assertEqual(key(catalog)[i], key(self.built)[i])
            # states, source links and the latest geometry are untouched
            for k in ('states', 'sourceLinks'):
                self.assertEqual(key(catalog)[i][k], key(self.pristine)[i][k])
            self.assertEqual(key(catalog)[i]['geometryPeriods'][-1], key(self.pristine)[i]['geometryPeriods'][-1])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in ids], [o for o in self.pristine['objects'] if o['id'] not in ids])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed growing main-road target', lambda x: x['objects'][0].update(inputHash='changed'))
        self.rejected('Invalid stages', lambda x: x['objects'][0]['stages'][0].update(year=1960))
        self.rejected('Invalid stages', lambda x: x['objects'][0]['stages'][0]['ranges'].append([9000, 9100]))
        self.rejected('do not cover the early periods', lambda x: x['objects'][0]['periods'].pop())
        self.rejected("stage less its base geometry", lambda x: x['objects'][0]['periods'][0]['ranges'].pop())
        self.rejected('not within its early period', lambda x: x['objects'][2]['periods'][0].update(baseGeometryId='geometry:x'))


if __name__ == '__main__':
    unittest.main()
