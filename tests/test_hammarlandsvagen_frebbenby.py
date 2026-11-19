import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_frebbenby

REVIEW = 'data/hammarlandsvagen-frebbenby.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-frebbenby-step.json.gz')
MV, M = 'road:qgis:eckero:marsundsvagen-100km4', 'road:marsund:eckero-hammarland'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class HammarlandsvagenFrebbenbyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.review = read(REVIEW)

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_hammarlandsvagen_frebbenby(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, change, why):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(review, catalog)
        self.assertIn(why, str(cm.exception))
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        self.assertEqual(key(catalog)[MV], key(self.built)[MV])
        self.assertEqual([o for o in catalog['objects'] if o['id'] != MV], [o for o in self.pristine['objects'] if o['id'] != MV])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), 1)
        o, b = key(catalog)[MV], key(self.pristine)[MV]
        self.assertEqual(o['states'][1:], b['states']); self.assertEqual(o['geometryPeriods'][1:], b['geometryPeriods'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        e = lambda r: r['early'][0]
        self.rejected(lambda r: e(r).update(inputHash='changed'), 'Changed Hammarlandsvägen input')
        self.rejected(lambda r: e(r).update(until=1968), 'must end where the object now begins')      # until its current first year
        self.rejected(lambda r: e(r)['maps'].update({'1929-eckero': 'unclear'}), 'First year')
        self.rejected(lambda r: e(r)['ranges'].__setitem__(0, [0.0, 30.0]), 'Invalid same-road ranges')
        self.rejected(lambda r: r['route'].update(gaps=[]), 'route breaks')                             # the 27 m link is stated
        self.rejected(lambda r: r['route']['gaps'][0].update(meters=10.0), 'route breaks')
        self.rejected(lambda r: r['route']['order'].reverse(), 'route breaks')


if __name__ == '__main__':
    unittest.main()
