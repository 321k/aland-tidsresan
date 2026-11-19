import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_marby, apply_hammarlandsvagen_shore, metric

# The catalogue built with each step disabled, kept in the local review cache.
CACHE = Path('data/map-scan-cache/review/hammarlandsvagen-main-road')
MB, LINK, SHORE = 'road:qgis:eckero:marbyvagen-100km1', 'road:eckero:gamla-landsvagen:sundkvist', 'road:eckero:gamla-landsvagen:strandvagen'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class Base:
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(CACHE / cls.SNAPSHOT) if (CACHE / cls.SNAPSHOT).exists() else None
        cls.review = read(cls.REVIEW)

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        type(self).STEP(lambda p: review if review is not None and p == self.REVIEW else read(p), catalog)
        return catalog

    def rejected(self, change, why):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(review, catalog)
        self.assertIn(why, str(cm.exception))
        self.assertEqual(before, catalog)

    def matches_the_build(self, ids, geometries):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        # the atlas review links these objects too, in a later pass of the build
        atlas = lambda o: {**o, 'evidence': [e for e in o['evidence'] if not e['id'].endswith(':regional-context:atlas-1894-1')]}
        for i in ids:
            self.assertEqual(atlas(key(catalog)[i]), atlas(key(self.built)[i]))
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in ids], [o for o in self.pristine['objects'] if o['id'] not in ids])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), geometries)
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)


class MarbyTests(Base, unittest.TestCase):
    REVIEW, SNAPSHOT, STEP = 'data/hammarlandsvagen-marby.json', 'before-marby-step.json.gz', staticmethod(apply_hammarlandsvagen_marby)

    def test_review_applies_once_and_matches_the_build(self):
        self.matches_the_build([MB, LINK], 3)                 # Marbyvägen's two stages and the link
        o = {x['id']: x for x in self.apply()['objects']}[MB]
        self.assertEqual([(p['from'], p['to']) for p in o['geometryPeriods']], [(1929, 1956), (1956, 1968), (1968, None)])

    def test_changed_inputs_are_rejected_before_any_change(self):
        e = lambda r: r['early'][0]
        self.rejected(lambda r: e(r).update(inputHash='changed'), 'Changed Hammarlandsvägen input')
        self.rejected(lambda r: e(r)['laterStage'].update(firstYear=1968), 'Invalid later stage')         # before the object's own first year
        self.rejected(lambda r: e(r)['maps'].pop('1956-eckero'), 'Invalid later stage')                   # the stage's map must be present
        self.rejected(lambda r: r['laterStageBasis'].clear(), 'Invalid later stage')
        self.rejected(lambda r: e(r)['laterStage']['ranges'].__setitem__(0, [200.0, 230.0]), 'Invalid later stage')
        self.rejected(lambda r: r['oldRoad']['maps'].update({'1968': 'present'}), 'Old road dates')
        def off(r):                 # the link's Marby end moved off the connection (length adjusted)
            p = r['oldRoad']['paths'][0]; p[0] = [p[0][0] + 0.0002, p[0][1]]
            r['oldRoad']['lengthMeters'] = round(metric(p).length, 1)
        self.rejected(off, 'does not end on today')
        self.rejected(lambda r: r['route']['order'].remove(r['oldRoad']['id']), 'does not list each dated piece once')


class ShoreTests(Base, unittest.TestCase):
    REVIEW, SNAPSHOT, STEP = 'data/hammarlandsvagen-shore.json', 'before-shore-step.json.gz', staticmethod(apply_hammarlandsvagen_shore)

    def test_review_applies_once_and_matches_the_build(self):
        self.matches_the_build([SHORE], 1)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected(lambda r: r['oldRoad']['maps'].update({'1956-eckero': 'present'}), 'Old road dates')    # gone on the 1956 edition
        def onto_marbyvagen(r):     # the southern end run 70 m along Marbyvägen again (as first read): it survives there
            p = r['oldRoad']['paths'][0]; mb = {x['id']: x for x in self.pristine['objects']}[MB]
            g = {x['id']: x for x in self.pristine['geometries']}[mb['geometryPeriods'][-1]['geometryId']]['paths'][0]
            k = min(range(len(g)), key=lambda i: metric([g[i], p[-1]]).length if g[i] != p[-1] else 0)
            p[-1:] = g[k - 6:k + 1][::-1] if k >= 6 else p[-1:]
            r['oldRoad']['lengthMeters'] = round(metric(p).length, 1)
        self.rejected(onto_marbyvagen, 'runs along road:qgis:eckero:marbyvagen')
        self.rejected(lambda r: r['oldRoad'].update(id=MB), 'Duplicate old-road identity')
        self.rejected(lambda r: r['route']['order'].remove(r['oldRoad']['id']), 'does not list each dated piece once')


if __name__ == '__main__':
    unittest.main()
