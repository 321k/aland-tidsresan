import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_building_maps import apply_building_maps
from mariehamn_frame_1942 import apply_frame_1942
from mariehamn_symbols_1968 import apply_symbols_1968

REVIEW = 'data/mariehamn-building-maps.json'


class BuildingMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        snapshot = Path('data/map-scan-cache/review/mariehamn-buildings/before.json.gz')
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
            apply_building_maps(reader, catalog)
        self.assertEqual(before, catalog)

    def decision(self, review, first, unclear=False):
        return next(d for d in review['decisions'] if d['firstYear'] == first
                    and any(x['outcome'] == 'unclear' for x in d['observations']) == unclear)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_building_maps(self.read, catalog)
        # The later 1942 frame review changes 43 road objects; apply it to compare with the build.
        frame = copy.deepcopy(catalog); apply_frame_1942(self.read, frame)
        # The 1968 symbol review then changes 125 printed-map symbol objects.
        apply_symbols_1968(self.read, frame)
        self.assertEqual(json.loads(json.dumps(frame, ensure_ascii=False))['objects'], self.built['objects'])
        with self.assertRaises(ValueError):
            apply_building_maps(self.read, catalog)

    def test_changed_building_rejected(self):
        self.run_with(lambda r: r['decisions'][0].update(input='changed'))
        self.run_with(lambda r: r['decisions'][0].update(originalFrom=1990))
        self.run_with(lambda r: r['decisions'].append(r['decisions'][0]))

    def test_symbol_far_from_the_building_rejected(self):
        def move(r):
            x = self.decision(r, 1985)['observations'][1]; x['pixel'] = [x['pixel'][0] + 15, x['pixel'][1]]
        self.run_with(move)

    def test_start_must_be_first_map_evidence(self):
        self.run_with(lambda r: self.decision(r, 1985).update(firstYear=1968))
        self.run_with(lambda r: self.decision(r, 1968)['observations'][2].update(outcome='absent'))
        # 1985 may be unclear only between 1968 and 1995 symbols.
        self.run_with(lambda r: self.decision(r, 1968, unclear=True)['observations'][2].update(outcome='unclear'))

    def test_curated_building_rejected(self):
        church = next(o for o in self.pristine['objects'] if o['id'] == 'building:osm:way-163034529')
        self.assertTrue(church.get('historicalReview'))
        def add(r):
            d = dict(r['decisions'][0]); d['objectId'] = church['id']
            from mariehamn_building_maps import fingerprint
            d['input'] = fingerprint(church); r['decisions'].append(d)
        self.run_with(add)

    def test_overlapping_printed_symbol_object_rejected(self):
        # A printed-map symbol object drawn on a dated outline would show the same house twice.
        review = self.read(REVIEW); d = next(d for d in review['decisions'] if d['batch'] == 'b6')
        catalog = copy.deepcopy(self.pristine)
        catalog['objects'].append(dict(id='map-building:test-symbol', kind='building', printedMapSymbol=True, states=[],
                                       geometryPeriods=[dict(geometryId=d['referenceGeometryId'], **{'from': 1983, 'to': None})]))
        before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            apply_building_maps(self.read, catalog)
        self.assertEqual(before, catalog)

    def test_1978_road_revision_is_not_building_evidence(self):
        def use_1978(r):
            d = self.decision(r, 1985); d['observations'][1]['year'] = 1978
        self.run_with(use_1978)


if __name__ == '__main__':
    unittest.main()
