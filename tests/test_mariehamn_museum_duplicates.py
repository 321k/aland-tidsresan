import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_museum_duplicates import apply_museum_duplicates

REVIEW = 'data/mariehamn-museum-duplicates.json'


class MuseumDuplicateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        # The catalogue as it was before this step, kept in the local review cache.
        snapshot = Path('data/map-scan-cache/review/museum-duplicates/museum-before.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def run_with(self, change):
        review = self.read(REVIEW); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        reader = lambda p: review if p == REVIEW else self.read(p)
        with self.assertRaises(ValueError):
            apply_museum_duplicates(reader, catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_museum_duplicates(self.read, catalog)
        # Buildings dated by the later r1/r2 rechecks and the Ytternäs modern-only outlines postdate this snapshot;
        # compare the rest exactly.
        later = {o['id'] for o in self.built['objects'] if (o.get('buildingMapReview') or {}).get('batch') in ('r1', 'r2')
                 or (o.get('reconstruction') or {}).get('createdByBuildingMapReview')}
        self.assertEqual(len(later), 354)
        self.assertEqual([o for o in json.loads(json.dumps(catalog, ensure_ascii=False))['objects'] if o['id'] not in later],
                         [o for o in self.built['objects'] if o['id'] not in later])
        with self.assertRaises(ValueError):
            apply_museum_duplicates(self.read, catalog)

    def test_changed_input_rejected(self):
        self.run_with(lambda r: r['inputs'].update({r['merges'][0]['keep']: 'changed'}))
        self.run_with(lambda r: r['merges'][0].update(keepFrom=1990))

    def test_one_museum_house_cannot_both_merge_and_end(self):
        def both(r):
            d = r['replacements'][0]; d['museum'] = r['merges'][0]['donor']
        self.run_with(both)

    def test_two_museum_houses_cannot_merge_into_one(self):
        def twice(r):
            r['merges'][1]['keep'] = r['merges'][0]['keep']
        self.run_with(twice)

    def test_replacement_must_end_at_the_successor(self):
        self.run_with(lambda r: r['replacements'][0].update(endYear=1930))

    def test_partners_must_overlap(self):
        def far(r):
            r['merges'][0]['keep'], r['merges'][-1]['keep'] = r['merges'][-1]['keep'], r['merges'][0]['keep']
        self.run_with(far)


if __name__ == '__main__':
    unittest.main()
