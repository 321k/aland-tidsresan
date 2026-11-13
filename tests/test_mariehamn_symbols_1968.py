import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_symbols_1968 import apply_symbols_1968

REVIEW = 'data/mariehamn-symbols-1968.json'


class Symbols1968Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        # The catalogue as it was before this step, kept in the local review cache.
        snapshot = Path('data/map-scan-cache/review/mariehamn-buildings/symbols-before.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def run_with(self, change, catalog_change=None):
        review = self.read(REVIEW); change(review)
        catalog = copy.deepcopy(self.pristine)
        if catalog_change:
            catalog_change(catalog)
        before = copy.deepcopy(catalog)
        reader = lambda p: review if p == REVIEW else self.read(p)
        with self.assertRaises(ValueError):
            apply_symbols_1968(reader, catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_symbols_1968(self.read, catalog)
        self.assertEqual(json.loads(json.dumps(catalog, ensure_ascii=False))['objects'], self.built['objects'])
        with self.assertRaises(ValueError):
            apply_symbols_1968(self.read, catalog)

    def test_changed_or_repeated_object_rejected(self):
        self.run_with(lambda r: r['decisions'][0].update(input='changed'))
        self.run_with(lambda r: r['decisions'][0].update(originalFrom=1990))
        self.run_with(lambda r: r['decisions'].append(r['decisions'][0]))

    def test_symbol_far_from_the_object_rejected(self):
        def move(r):
            d = r['decisions'][0]; d['pixel'] = [d['pixel'][0] + 15, d['pixel'][1]]
        self.run_with(move)

    def test_symbol_in_a_hatched_area_rejected(self):
        # A 1968 built-up area drawn over the recorded symbol makes the review invalid.
        def add_area(catalog):
            review = self.read(REVIEW); d = review['decisions'][0]
            o = next(o for o in catalog['objects'] if o['id'] == d['objectId'])
            catalog['objects'].append(dict(id='site:test-area', kind='site', printedMapArea=True, states=[],
                                           geometryPeriods=[dict(geometryId='geometry:test-area', **{'from': 1968, 'to': 1985})]))
            g = next(g for g in catalog['geometries'] if g['id'] == o['geometryPeriods'][0]['geometryId'])
            xs = [p[0] for p in g['paths'][0]]; ys = [p[1] for p in g['paths'][0]]
            pad = 0.001
            catalog['geometries'].append(dict(id='geometry:test-area', paths=[[[min(xs) - pad, min(ys) - pad], [max(xs) + pad, min(ys) - pad],
                                                                                [max(xs) + pad, max(ys) + pad], [min(xs) - pad, max(ys) + pad], [min(xs) - pad, min(ys) - pad]]]))
        self.run_with(lambda r: None, add_area)

    def test_object_without_printed_symbol_rejected(self):
        self.run_with(lambda r: r['decisions'][0].update(objectId='building:osm:way-163034529'))


if __name__ == '__main__':
    unittest.main()
