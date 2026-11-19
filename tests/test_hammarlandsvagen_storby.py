import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_storby

REVIEW = 'data/hammarlandsvagen-storby.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-storby-step.json.gz')
M, OLD = 'road:marsund:eckero-hammarland', 'road:eckero:gamla-landsvagen:storby'
ATLAS = ':regional-context:atlas-1894-1'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class StorbyTests(unittest.TestCase):
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
        apply_hammarlandsvagen_storby(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, change, why):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(review, catalog)
        self.assertIn(why, str(cm.exception))
        self.assertEqual(before, catalog)                       # nothing changed, the bypass split included

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        atlas = lambda o: {**o, 'evidence': [e for e in o['evidence'] if not e['id'].endswith(ATLAS)]}
        for i in (M, OLD):
            self.assertEqual(atlas(key(catalog)[i]), atlas(key(self.built)[i]))
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in (M, OLD)], [o for o in self.pristine['objects'] if o['id'] != M])
        periods = [(p['from'], p['to']) for p in key(catalog)[M]['geometryPeriods']]
        self.assertEqual(periods, [(1929, 1959), (1959, 1978), (1978, 1985), (1985, None)])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_bypass_checks(self):
        b = lambda r: r['bypass']
        self.rejected(lambda r: b(r).update(inputHash='changed'), 'Changed bypass input')
        self.rejected(lambda r: b(r)['maps'].update({'1978': 'unclear'}), 'Bypass dates')                 # the first map with it ends the split
        self.rejected(lambda r: b(r)['maps'].update({'1968': 'unclear'}), 'Bypass dates')                 # and one without it
        self.rejected(lambda r: b(r).update(until=1990), 'Changed bypass geometry')                       # inside the period being split
        self.rejected(lambda r: b(r)['removed'][2].__setitem__(1, b(r)['removed'][2][2] - 30), 'Invalid bypass piece')
        self.rejected(lambda r: b(r)['canonicalRanges'].reverse(), 'Invalid bypass extents')

    def test_the_old_road_is_checked_before_the_split_is_kept(self):
        o = lambda r: r['oldRoads'][0]
        self.rejected(lambda r: r.update(connectionHash='changed'), 'Changed connection')
        self.rejected(lambda r: o(r).update(mainUntilBasis=''), 'Old road dates')
        self.rejected(lambda r: o(r)['laterPaths'][1].pop(), 'is not its OSM way')


if __name__ == '__main__':
    unittest.main()
