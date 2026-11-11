import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_temporal_objects, mariehamn_lemlandsvagen_split as split


class LemlandsvagenSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        real = split.apply_lemlandsvagen_split; split.apply_lemlandsvagen_split = lambda read, catalog: None
        try:
            cls.base = build_temporal_objects.compile_catalog()
        finally:
            split.apply_lemlandsvagen_split = real

    def run_with(self, change):
        review = self.read('data/mariehamn-lemlandsvagen-split.json'); change(review)
        catalog = copy.deepcopy(self.base); before = copy.deepcopy(catalog)
        reader = lambda p: review if p.endswith('mariehamn-lemlandsvagen-split.json') else self.read(p)
        with self.assertRaises(ValueError):
            split.apply_lemlandsvagen_split(reader, catalog)
        self.assertEqual(before, catalog)

    def test_reviewed_split_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.base); split.apply_lemlandsvagen_split(self.read, catalog)
        built, published = json.loads(json.dumps(catalog, ensure_ascii=False)), self.read('dist/assets/temporal-objects.json.gz')
        # Compare by id: assertEqual on two whole catalogues renders an unusably slow diff when they differ.
        a, b = ({o['id']: o for o in c['objects']} for c in (built, published))
        self.assertEqual(sorted(set(a) ^ set(b)), [])
        self.assertEqual(sorted(i for i in a if a[i] != b[i]), [])
        # Later build steps append their own records, so compare the other collections by id rather than position.
        for key in ['geometries', 'sources']:
            x, y = ({r['id']: r for r in c[key]} for c in (built, published))
            self.assertEqual(sorted(set(x) ^ set(y)), [], key); self.assertEqual(sorted(i for i in x if x[i] != y[i]), [], key)
        self.assertEqual(sorted(k for k in set(built) | set(published) if k not in ['objects', 'geometries', 'sources'] and built.get(k) != published.get(k)), [])
        with self.assertRaises(ValueError):
            split.apply_lemlandsvagen_split(self.read, catalog)

    def test_changed_rural_object_rejected(self):
        self.run_with(lambda r: r['target'].update(inputHash='changed'))

    def test_dropped_range_rejected(self):
        self.run_with(lambda r: r['remainder']['sourceLinks'].pop())

    def test_range_moved_to_the_wrong_road_rejected(self):
        def move(r):
            west = next(o for o in r['objects'] if o['part'] == 'west'); west['sourceLinks'].append(r['remainder']['sourceLinks'].pop())
        self.run_with(move)

    def test_split_position_must_match_each_source(self):
        def shift(r):
            l = next(l for l in r['objects'][0]['sourceLinks'] if 'splitAt' in l and l['datasetId'] == 'osm-2014'); l['splitAt'] += 0.5
        self.run_with(shift)

    def test_unexplained_failing_map_bin_rejected(self):
        self.run_with(lambda r: r['visualChecks'].pop())

    def test_split_point_cannot_move_into_the_realigned_curve(self):
        def later(r):
            t = r['target']; t['splitVertex'] = 12; t['slices']['west'][1] += 7; t['slices']['remainder'][0] += 7
        self.run_with(later)


if __name__ == '__main__':
    unittest.main()
