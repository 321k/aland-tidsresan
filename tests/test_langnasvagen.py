import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from langnasvagen import apply_langnasvagen

A, B = 'data/langnasvagen.json', 'data/langnasvagen-skag.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/langnasvagen/before-langnasvagen-step.json.gz')
IDS = ('road:qgis:lumparland:langnasvagen-100km3', 'road:lumparland:gamla-landsvagen:sodergard', 'road:lumparland:gamla-landsvagen:skag')


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class LangnasvagenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.a, cls.b = read(A), read(B)

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, a=None, b=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_langnasvagen(lambda p: (a if p == A and a is not None else b if p == B and b is not None else read(p)), catalog)
        return catalog

    def rejected(self, which, change, why):
        r = copy.deepcopy(self.a if which == 'a' else self.b); change(r)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(r if which == 'a' else None, r if which == 'b' else None, catalog)
        self.assertIn(why, str(cm.exception))
        self.assertEqual(before, catalog)                       # nothing changed, not even the first review

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        for i in IDS:
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in IDS], [o for o in self.pristine['objects'] if o['id'] not in IDS])
        self.assertEqual([(p['from'], p['to']) for p in key(catalog)[IDS[0]]['geometryPeriods']], [(1917, 1929), (1929, 1968), (1968, None)])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        e, od = (lambda r: r['early'][0]), (lambda r: r['oldRoad'])
        self.rejected('a', lambda r: e(r).update(inputHash='changed'), 'Changed Hammarlandsvägen input')
        self.rejected('a', lambda r: e(r)['laterStage']['ranges'].pop(0), 'Changed connection')      # the Skag review was made for the road with its crossing stretch
        self.rejected('a', lambda r: od(r).update(untilBasis=''), 'Old road dates')                     # 1968 is unclear, not absent: the reason is stated
        self.rejected('a', lambda r: od(r)['maps'].update({'1968': 'present'}), 'Old road dates')
        self.rejected('b', lambda r: r.update(connectionHash='changed'), 'Changed connection')
        self.rejected('b', lambda r: r.update(connectionEarlyPeriods=1), 'does not join the connection')  # its south end is on the 1929 stretch
        self.rejected('b', lambda r: r['oldRoads'][0]['laterPaths'][0].pop(), 'is not its OSM way')


if __name__ == '__main__':
    unittest.main()
