import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from saltviksvagen import apply_saltviksvagen_east

REVIEW = 'data/saltviksvagen-east.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/saltviksvagen/before-saltviksvagen-east-step.json.gz')
TS, AND = 'road:qgis:tjudo:saltviksvagen-100km1', 'road:tjudo:gamla-saltviksvagen:andelsby'
DG, KAV = 'road:qgis:tjudo:daglosavagen-100km1', 'road:qgis:saltvik:kavelbrovagen'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class SaltviksvagenEastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.review = read(REVIEW); cls.ids = [e['objectId'] for e in cls.review['early']] + [AND]

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_saltviksvagen_east(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
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
        for i in self.ids:
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in self.ids], [o for o in self.pristine['objects'] if o['id'] not in self.ids])
        self.assertEqual([(s['from'], s['to'], s['state']) for s in key(catalog)[AND]['states']], [(1927, 1984, 'open'), (1984, None, 'unknown')])
        self.assertEqual([(p['from'], p['to']) for p in key(catalog)[KAV]['geometryPeriods']], [(1929, 1968), (1968, None)])
        self.assertEqual(key(catalog)[DG]['mainRoadReview']['ranges'], [[4351.6, 4552.1]])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        e = lambda r: r['early'][0]; od = lambda r: r['oldRoad']; rt = lambda r: r['route']
        self.rejected(lambda r: e(r).update(inputHash='changed'), 'Changed Hammarlandsvägen input')
        self.rejected(lambda r: e(r)['maps'].update({'1927-tjudo': 'absent'}), 'First year')
        self.rejected(lambda r: od(r)['maps'].update({'1984-tjudo': 'present'}), 'Old road dates')
        self.rejected(lambda r: rt(r)['gaps'][0].update(meters=300.0), 'route breaks')                   # the stated seam at Västergård
        self.rejected(lambda r: rt(r).update(gaps=[]), 'route breaks')
        self.rejected(lambda r: e(r)['ranges'][0].__setitem__(1, e(r)['ranges'][0][1] - 60), 'route breaks')   # the curve must meet today's road


if __name__ == '__main__':
    unittest.main()
