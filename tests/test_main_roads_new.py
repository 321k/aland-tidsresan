import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from main_roads_new import apply_main_roads_new, REVIEW

# The catalogue built before this step was added, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/main-roads-new/before-main-roads-new-step.json.gz')


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class MainRoadsNewTests(unittest.TestCase):
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
        apply_main_roads_new(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, why, change):
        x = copy.deepcopy(self.review); change(x)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(x, catalog)
        self.assertIn(why, str(cm.exception)); self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        new = {r['id'] for r in self.review['newRoads']}
        key = lambda c: {x['id']: x for x in c['objects']}
        self.assertEqual(len(new), 10)
        for i in new:
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual(catalog['objects'][:len(self.pristine['objects'])], self.pristine['objects'])
        self.assertEqual(len(catalog['objects']), len(self.pristine['objects']) + 10)
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed OSM source', lambda x: x['newRoads'][0]['sourceLinks'][0].update(input='changed'))
        self.rejected('not its OSM pieces', lambda x: x['newRoads'][0]['paths'][0].pop(1))
        self.rejected('does not join', lambda x: x['newRoads'][2].update(end='road:qgis:lumparland:lemlandsvagen-100km3'))
        self.rejected('free end needs a stated basis', lambda x: x['newRoads'][4].pop('freeEndBasis'))
        self.rejected('New road dates', lambda x: x['newRoads'][0]['maps'].update({'1985-102307': 'absent'}))
        self.rejected('Duplicate new road', lambda x: x['newRoads'][1].update(id='road:qgis:saltvik:hagavagen'))


if __name__ == '__main__':
    unittest.main()
