import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_blocks_1920 import apply_blocks_1920

REVIEW = 'data/mariehamn-blocks-1920.json'


class Blocks1920Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        snapshot = Path('data/map-scan-cache/review/blocks-1920/before-blocks-1920-step.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None

    def setUp(self):
        # The pre-step catalogue is kept in the local review cache; without it these tests are skipped.
        if self.pristine is None:
            self.skipTest('pre-step snapshot is kept in the local review cache')

    def run_with(self, change=None, catalog_change=None):
        review = self.read(REVIEW)
        if change:
            change(review)
        catalog = copy.deepcopy(self.pristine)
        if catalog_change:
            catalog_change(catalog)
        before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            apply_blocks_1920(lambda p: review if p == REVIEW else self.read(p), catalog)
        self.assertEqual(before, catalog)

    def test_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_blocks_1920(self.read, catalog)
        catalog = json.loads(json.dumps(catalog, ensure_ascii=False))
        self.assertEqual(catalog['cityStages'], self.built['cityStages'])
        self.assertEqual(catalog['objects'], self.pristine['objects'])
        with self.assertRaises(ValueError):
            apply_blocks_1920(self.read, catalog)

    def test_changed_inputs_are_rejected(self):
        self.run_with(lambda r: r['before'].update(blocksHash='changed'))
        self.run_with(lambda r: r['after'].update(blocksHash='changed'))
        self.run_with(lambda r: r.update(stageIds=['city-reconstruction-1920']))
        self.run_with(lambda r: r['expectedSquareMeters'].update({'city-reconstruction-1927': 30000}))
        drop = lambda c: next(s for s in c['cityStages'] if s['id'] == 'city-reconstruction-1871')['features'].pop(
            next(i for i, f in enumerate(next(s for s in c['cityStages'] if s['id'] == 'city-reconstruction-1871')['features']) if f['kind'] == 'block'))
        self.run_with(catalog_change=drop)


if __name__ == '__main__':
    unittest.main()
