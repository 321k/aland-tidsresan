import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_museum_duplicates import apply_museum_offsets

REVIEW = 'data/mariehamn-museum-offsets.json'


class MuseumOffsetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        # The catalogue after the overlap review and before this pass, kept in the local review cache.
        snapshot = Path('data/map-scan-cache/review/museum-duplicates/offsets-before.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def run_with(self, change):
        review = self.read(REVIEW); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        reader = lambda p: review if p == REVIEW else self.read(p)
        with self.assertRaises(ValueError):
            apply_museum_offsets(reader, catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_museum_offsets(self.read, catalog)
        self.assertEqual(json.loads(json.dumps(catalog, ensure_ascii=False))['objects'], self.built['objects'])
        with self.assertRaises(ValueError):
            apply_museum_offsets(self.read, catalog)

    def test_changed_input_rejected(self):
        self.run_with(lambda r: r['inputs'].update({r['merges'][0]['keep']: 'changed'}))

    def test_merge_partners_must_be_neighbours(self):
        self.run_with(lambda r: r.update(maxGapMeters=0.0))

    def test_no_more_than_two_museum_houses_join_one_building(self):
        def three(r):
            d = next(d for d in r['merges'] if d['keep'].endswith('489')); x = r['merges'][0]
            x['keep'] = d['keep']; x['keepFrom'] = d['keepFrom']
        self.run_with(three)

    def test_ending_needs_an_empty_footprint(self):
        self.run_with(lambda r: r['endings'][0].update(darkShare=0.5))

    def test_ending_cannot_also_merge(self):
        self.run_with(lambda r: r['endings'][0].update(museum=r['merges'][0]['donor']))


if __name__ == '__main__':
    unittest.main()
