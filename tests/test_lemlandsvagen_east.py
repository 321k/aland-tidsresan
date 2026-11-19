import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lemlandsvagen_east import apply_lemlandsvagen_east

REVIEW = 'data/lemlandsvagen-east.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/lemlandsvagen-east/before-lemlandsvagen-east-step.json.gz')
MAIN, SKOL, KLUB, FISK = ('road:qgis:lumparland:lemlandsvagen-100km3', 'road:qgis:lumparland:skolsvangen-100km6',
                          'road:qgis:lumparland:klubbensvagen-100km4', 'road:lumparland:fiskartorpsvagen')


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class LemlandsvagenEastTests(unittest.TestCase):
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
        apply_lemlandsvagen_east(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, change, why):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(review, catalog)
        self.assertIn(why, str(cm.exception))
        self.assertEqual(before, catalog)                       # nothing changed

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        ids = (MAIN, SKOL, KLUB, FISK)
        for i in ids:
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in ids], [o for o in self.pristine['objects'] if o['id'] not in ids])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), 5)
        periods = [(p['from'], p['to']) for p in key(catalog)[MAIN]['geometryPeriods']]
        self.assertEqual(periods, [(1917, 1929), (1929, 1968), (1968, None)])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        e = lambda r, i=0: r['early'][i]
        self.rejected(lambda r: e(r).update(inputHash='changed'), 'Changed Hammarlandsvägen input')
        self.rejected(lambda r: e(r)['maps'].update({'1917': 'unclear'}), 'First year is not the first map')
        self.rejected(lambda r: e(r)['laterStage'].update(firstYear=1968), 'Invalid later stage')
        self.rejected(lambda r: e(r)['ranges'][1].__setitem__(0, e(r)['ranges'][1][0] + 30), 'Changed stated gap')   # the Skolsvängen junction
        self.rejected(lambda r: e(r)['ranges'][1].__setitem__(1, e(r)['ranges'][1][1] - 60), 'route breaks')         # the Klubbensvägen junction
        self.rejected(lambda r: r['statedGaps'][0].update(meters=5), 'Changed stated gap')

    def test_the_new_road_is_checked(self):
        n = lambda r: r['newRoad']
        self.rejected(lambda r: n(r).update(missingExtracts=[]), 'owned in every OSM extract')
        self.rejected(lambda r: n(r).update(missingExtractsBasis=''), 'owned in every OSM extract')
        self.rejected(lambda r: n(r)['maps'].update({'1917': 'absent'}), 'New road dates')
        self.rejected(lambda r: n(r)['sourceLinks'][0].update(input='changed'), 'Changed or partial OSM source')
        def moved(r):                   # its end no longer on a road open in 1929
            n(r)['firstYear'] = 1917; n(r)['maps'] = {'1917': 'present'}
        self.rejected(moved, 'does not join a road open in its first year')


if __name__ == '__main__':
    unittest.main()
