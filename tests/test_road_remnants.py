import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from road_remnants import apply_road_remnants

REVIEW = 'data/road-remnants.json'
SNAPSHOT = Path('data/map-scan-cache/review/road-remnants/before-remnants-step.json.gz')
ATLAS = ':regional-context:atlas-1894-1'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class RoadRemnantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.review = read(REVIEW); cls.ids = sorted({r['objectId'] for r in cls.review['remnants']})

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-step snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_road_remnants(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, change, why):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(review, catalog)
        self.assertIn(why, str(cm.exception))
        self.assertEqual(before, catalog)

    def test_adds_only_evidence_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        atlas = lambda o: {**o, 'evidence': [e for e in o['evidence'] if not e['id'].endswith(ATLAS)]}
        for i in self.ids:
            got, before = key(catalog)[i], key(self.pristine)[i]
            self.assertEqual(atlas(got), atlas(key(self.built)[i]))
            self.assertEqual((got['states'], got['geometryPeriods']), (before['states'], before['geometryPeriods']))     # no dates or geometry change
        self.assertEqual(catalog['geometries'], self.pristine['geometries'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected(self):
        r = lambda x, i=0: x['remnants'][i]
        self.rejected(lambda x: r(x).update(inputHash='changed'), 'Changed road')
        self.rejected(lambda x: r(x).update(outlineHash='changed'), 'Changed register outline')
        self.rejected(lambda x: r(x, 1).update(maxDistanceMeters=2), 'is not on')
        self.rejected(lambda x: r(x, 1).update(supports=['geometry', 'identity'], minInsideMeters=10), 'Changed overlap')
        self.rejected(lambda x: r(x, 1).update(code=r(x)['code']), 'Not a single register road remnant')


if __name__ == '__main__':
    unittest.main()
