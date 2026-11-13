import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_building_photos import apply_building_photos

REVIEW = 'data/mariehamn-building-photos.json'


class BuildingPhotoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        # The catalogue as it was before this step, kept in the local review cache.
        snapshot = Path('data/map-scan-cache/review/photo-dating/photos-before.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def run_with(self, change):
        review = self.read(REVIEW); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        reader = lambda p: review if p == REVIEW else self.read(p)
        with self.assertRaises(ValueError):
            apply_building_photos(reader, catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_building_photos(self.read, catalog)
        self.assertEqual(json.loads(json.dumps(catalog, ensure_ascii=False))['objects'], self.built['objects'])
        with self.assertRaises(ValueError):
            apply_building_photos(self.read, catalog)

    def test_changed_input_rejected(self):
        self.run_with(lambda r: r['decisions'][0].update(input='changed'))
        self.run_with(lambda r: r['decisions'].append(r['decisions'][0]))

    def test_start_must_be_the_first_photo(self):
        self.run_with(lambda r: r['decisions'][0].update(firstYear=r['decisions'][0]['firstYear'] - 8))

    def test_later_photo_must_show_the_building(self):
        def drop(r):
            d = next(d for d in r['decisions'] if d['firstYear'] == 1991); d['observations'][-1]['outcome'] = 'absent'
        self.run_with(drop)

    def test_map_dated_building_rejected(self):
        def mapped(r):
            maps = self.read('data/mariehamn-building-maps.json')
            d = dict(r['decisions'][0]); d['objectId'] = maps['decisions'][0]['objectId']; r['decisions'].append(d)
        self.run_with(mapped)


if __name__ == '__main__':
    unittest.main()
