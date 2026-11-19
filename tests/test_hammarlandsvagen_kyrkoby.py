import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_kyrkoby, metric

REVIEW = 'data/hammarlandsvagen-kyrkoby.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-kyrkoby-step.json.gz')
ATLAS = ':regional-context:atlas-1894-1'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class KyrkobyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.review = read(REVIEW); cls.ids = [o['id'] for o in cls.review['oldRoads']]

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_hammarlandsvagen_kyrkoby(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
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
        atlas = lambda o: {**o, 'evidence': [e for e in o['evidence'] if not e['id'].endswith(ATLAS)]}     # the atlas review links them later
        for i in self.ids:
            self.assertEqual(atlas(key(catalog)[i]), atlas(key(self.built)[i]))
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in self.ids], self.pristine['objects'])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), 4)
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        o = lambda r, i=0: r['oldRoads'][i]
        self.rejected(lambda r: r.update(connectionHash='changed'), 'Changed connection')
        self.rejected(lambda r: o(r).update(mainUntilBasis=''), 'Old road dates')                        # the switch year is stated
        self.rejected(lambda r: o(r)['maps'].update({'1946': 'absent'}), 'Old road dates')
        self.rejected(lambda r: o(r, 1).update(id=o(r)['id']), 'Duplicate old-road identity')
        def off(r):                 # an end moved off the connection (length adjusted)
            p = o(r)['paths'][0]; p[0] = [p[0][0] + 0.0002, p[0][1]]; o(r)['lengthMeters'] = round(metric(p).length, 1)
        self.rejected(off, 'does not join the connection')
        self.rejected(lambda r: o(r)['laterPaths'][0].pop(), 'is not its OSM way')
        self.rejected(lambda r: o(r).update(sameRoadMeters=10), 'not on the 1929 road')
        self.rejected(lambda r: o(r)['sourceLinks'].pop(), 'one source link')


if __name__ == '__main__':
    unittest.main()
