import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_frame_1942 import apply_frame_1942

REVIEW = 'data/mariehamn-frame-1942.json'


class Frame1942Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        snapshot = Path('data/map-scan-cache/review/trace-1942/frame-before.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None

    def setUp(self):
        # The pre-review catalogue is kept in the local review cache; without it these tests are skipped.
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def run_with(self, change):
        review = self.read(REVIEW); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        reader = lambda p: review if p == REVIEW else self.read(p)
        with self.assertRaises(ValueError):
            apply_frame_1942(reader, catalog)
        self.assertEqual(before, catalog)

    def trace(self, review, name):
        return next(t for t in review['traces'] if t['name'] == name)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_frame_1942(self.read, catalog)
        catalog = json.loads(json.dumps(catalog, ensure_ascii=False))
        self.assertEqual(catalog['cityStages'], self.built['cityStages'])
        self.assertEqual(catalog['objects'], self.built['objects'])
        with self.assertRaises(ValueError):
            apply_frame_1942(self.read, catalog)

    def test_changed_trace_or_object_rejected(self):
        self.run_with(lambda r: self.trace(r, 'Södra stadsgatan · 1942')['pixels'][0].__setitem__(0, 0))
        self.run_with(lambda r: self.trace(r, 'Västra strandens gata · 1942')['members'][0].update(inputHash='changed'))
        self.run_with(lambda r: self.trace(r, 'Norra kvarterens tvärgata · 1942')['stageFeatures'].pop())

    def test_object_far_from_its_trace_rejected(self):
        self.run_with(lambda r: self.trace(r, 'Västra strandens gata · 1942').update(maxDistanceMeters=5))
        # Köpmansgatan cannot stand in for the western Havsgatan trace.
        self.run_with(lambda r: self.trace(r, 'Västra strandens gata · 1942')['members'].append(self.trace(r, 'Norra kvarterens tvärgata · 1942')['members'].pop()))

    def test_rejected_trace_cannot_carry_members(self):
        self.run_with(lambda r: self.trace(r, 'Södra stadsgatan · 1942')['members'].append(self.trace(r, 'Strandgatan · 1942')['members'].pop()))

    def test_gap_must_join_its_objects(self):
        self.run_with(lambda r: self.trace(r, 'Strandgatan · 1942')['retracedGaps'][0]['epsg3874'][0].__setitem__(0, 20496890.0))


if __name__ == '__main__':
    unittest.main()
