import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_kattby

REVIEW = 'data/hammarlandsvagen-kattby.json'
# The catalogue as it is just before this step (built with the step disabled), kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-kattby-step.json.gz')


class HammarlandsvagenKattbyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        cls.pristine = cls.read(str(SNAPSHOT)) if SNAPSHOT.exists() else None
        cls.review = cls.read(REVIEW)

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_hammarlandsvagen_kattby(lambda p: review if review is not None and p == REVIEW else self.read(p), catalog)
        return catalog

    def rejected(self, change):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(review, catalog)
        if '-v' in sys.argv: print('   rejected:', cm.exception)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        oid = self.review['early'][0]['objectId']
        key = lambda c: {x['id']: x for x in c['objects']}
        self.assertEqual(key(catalog)[oid], key(self.built)[oid])
        self.assertEqual([o for o in catalog['objects'] if o['id'] != oid], [o for o in self.pristine['objects'] if o['id'] != oid])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), 1)
        before = key(self.pristine)[oid]
        self.assertEqual(key(catalog)[oid]['states'][1:], before['states']); self.assertEqual(key(catalog)[oid]['geometryPeriods'][1:], before['geometryPeriods'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected(lambda r: r['early'][0].update(inputHash='changed'))
        self.rejected(lambda r: r['early'][0].update(until=1968))                                   # must end where the object begins (1959)
        self.rejected(lambda r: r['early'][0]['maps'].update({'1929-eckero': 'absent', '1929-hammarby': 'absent'}))   # first year = first map with it
        self.rejected(lambda r: r['maps']['1929-eckero'].update(sourceId='nls:unknown'))             # every map must be a known or added source
        self.rejected(lambda r: r['route'].update(order=['road:rural:hammarland-hammarlandsvagen-postad-korsangen', r['early'][0]['objectId']],
                                                  endObjects=['road:rural:hammarland-hammarlandsvagen-postad-korsangen']))   # must meet the church corridor


if __name__ == '__main__':
    unittest.main()
