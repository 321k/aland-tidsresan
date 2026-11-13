import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_frame_1942 import apply_frame_1942
from mariehamn_symbols_1968 import apply_symbols_1968
from mariehamn_museum_duplicates import apply_museum_duplicates

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
        # The 1968 symbol review runs after this step and touches only printed-map symbol objects.
        frame_only = copy.deepcopy(catalog); apply_symbols_1968(self.read, catalog)
        apply_museum_duplicates(self.read, catalog)
        catalog = json.loads(json.dumps(catalog, ensure_ascii=False))
        self.assertEqual(catalog['cityStages'], self.built['cityStages'])
        # Building-map batches added after the snapshot (b6–b10: the centre and Ytternäs; r1, r2: the rechecks) change only buildings the
        # frame review never touches; every other object must match the build exactly.
        later = {o['id'] for o in self.built['objects'] if (o.get('buildingMapReview') or {}).get('batch') in ('b6', 'b7', 'b8', 'b9', 'b10', 'r1', 'r2')}
        self.assertEqual(len(later), 501)
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in later],
                         [o for o in self.built['objects'] if o['id'] not in later])
        with self.assertRaises(ValueError):
            apply_frame_1942(self.read, frame_only)

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
