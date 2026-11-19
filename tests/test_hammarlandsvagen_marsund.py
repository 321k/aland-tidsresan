import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_marsund

REVIEW = 'data/hammarlandsvagen-marsund.json'
# The catalogue before this step (the build with the step disabled gives the same), kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-marsund.json.gz')
OID = 'road:marsund:eckero-hammarland'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class HammarlandsvagenMarsundTests(unittest.TestCase):
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
        apply_hammarlandsvagen_marsund(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
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
        # The Överby review (a later step) splits this object's 1959 period and adds its own evidence; leave that out.
        built = copy.deepcopy(key(self.built)[OID]); built.pop('overbyBypass')
        built['evidence'] = [e for e in built['evidence'] if e.get('reviewId') != 'review:hammarlandsvagen-overby']
        split, whole = built['geometryPeriods'][1], built['geometryPeriods'][2]
        whole['from'] = split['from']; whole['evidenceIds'] = [i for i in whole['evidenceIds'] if ':overby-map-' not in i]
        built['geometryPeriods'] = [built['geometryPeriods'][0], whole]
        self.assertEqual(key(catalog)[OID], built)
        self.assertEqual([o for o in catalog['objects'] if o['id'] != OID], [o for o in self.pristine['objects'] if o['id'] != OID])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), 1)
        o, b = key(catalog)[OID], key(self.pristine)[OID]
        self.assertEqual(o['states'][1:], b['states']); self.assertEqual(o['geometryPeriods'][1:], b['geometryPeriods'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_cuts_are_rejected_before_any_change(self):
        e = lambda r: r['early'][0]
        self.rejected(lambda r: e(r).update(inputHash='changed'), 'Changed Hammarlandsvägen input')
        self.rejected(lambda r: e(r).pop('pathRanges'), 'Changed Hammarlandsvägen geometry')   # 19 paths: never implicit
        self.rejected(lambda r: e(r)['pathOrder'].reverse(), 'do not follow each other')          # paths must chain
        self.rejected(lambda r: e(r)['pathRanges'][1].__setitem__(2, 30.0), 'Invalid path cut')    # under 50 m only as a whole path
        self.rejected(lambda r: e(r)['pathRanges'].insert(0, e(r)['pathRanges'].pop(2)), 'not in order')
        self.rejected(lambda r: e(r)['ranges'][1].__setitem__(1, 8300.0), 'do not make the reviewed ranges')
        self.rejected(lambda r: e(r)['pathRanges'].pop(1), 'do not make the reviewed ranges')     # Frebbenby runs on over path 17 (36 m)
        self.rejected(lambda r: e(r)['maps'].update({'1929-eckero': 'unclear', '1929-morby': 'unclear'}), 'First year')   # both 1929 sheets


if __name__ == '__main__':
    unittest.main()
