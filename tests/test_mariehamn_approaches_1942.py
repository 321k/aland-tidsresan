import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_approaches_1942 import apply_approaches_1942

REVIEW = 'data/mariehamn-approaches-1942.json'


class Approaches1942Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')

    def run_with(self, change, catalog=None):
        review = self.read(REVIEW); change(review)
        catalog = catalog or self.pristine; before = copy.deepcopy(catalog)
        reader = lambda p: review if p == REVIEW else self.read(p)
        with self.assertRaises(ValueError):
            apply_approaches_1942(reader, catalog)
        self.assertEqual(before, catalog)

    def setUp(self):
        # The raw trace stage features are not in the built catalogue any more, so the pristine catalogue
        # is the pre-review snapshot when it is available locally; otherwise these tests are skipped.
        snapshot = Path('data/map-scan-cache/review/trace-1942/before.json.gz')
        if not snapshot.exists():
            self.skipTest('pre-review snapshot is kept in the local review cache')
        self.pristine = self.read(str(snapshot))

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_approaches_1942(self.read, catalog)
        self.assertEqual(json.loads(json.dumps(catalog, ensure_ascii=False))['cityStages'], self.built['cityStages'])
        ids = {o['id'] for o in catalog['objects'] if o.get('approach1942')}
        built = {o['id']: o for o in self.built['objects'] if o['id'] in ids}
        self.assertEqual(len(ids), 30)
        self.assertEqual({i: o for i, o in ((o['id'], o) for o in json.loads(json.dumps(catalog, ensure_ascii=False))['objects']) if i in ids}, built)
        with self.assertRaises(ValueError):
            apply_approaches_1942(self.read, catalog)

    def test_changed_original_trace_rejected(self):
        self.run_with(lambda r: r['rejected'][0]['pixels'][0].__setitem__(0, 0))
        self.run_with(lambda r: r['approaches'][0].update(inputHash='changed'))

    def test_changed_object_rejected(self):
        self.run_with(lambda r: r['approaches'][0]['members'][0].update(inputHash='changed'))
        self.run_with(lambda r: r['approaches'][1]['members'][0].update(originalFrom=1942))

    def test_object_far_from_the_trace_rejected(self):
        self.run_with(lambda r: r['approaches'][0].update(maxDeviationMeters=5))

    def test_unreviewed_stage_copy_rejected(self):
        self.run_with(lambda r: r['approaches'][1]['stageFeatures'].pop())

    def test_repeated_object_rejected(self):
        self.run_with(lambda r: r['approaches'][1]['members'].append(r['approaches'][0]['members'][0]))


if __name__ == '__main__':
    unittest.main()
