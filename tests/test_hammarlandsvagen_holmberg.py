import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_holmberg, metric

REVIEW = 'data/hammarlandsvagen-holmberg.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-holmberg-step.json.gz')
OLD, ORA = 'road:eckero:gamla-landsvagen:holmberg', 'road:eckero:oravagen'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class HolmbergTests(unittest.TestCase):
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
        apply_hammarlandsvagen_holmberg(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
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
        for i in (OLD, ORA):
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in (OLD, ORA)], self.pristine['objects'])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), 2)
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        n = lambda r: r['newRoad']; o = lambda r: r['oldRoad']
        self.rejected(lambda r: n(r)['sourceLinks'][1].update(input='changed'), 'Changed or partial OSM source')
        self.rejected(lambda r: n(r)['sourceLinks'][0]['sourceVertexRange'].__setitem__(0, 1), 'Changed or partial OSM source')
        self.rejected(lambda r: n(r)['sourceLinks'].pop(), 'owned in every OSM extract')
        self.rejected(lambda r: n(r)['paths'][0].pop(), 'is not its OSM way')
        self.rejected(lambda r: n(r)['maps'].update({'1968': 'absent'}), 'New road dates')
        self.rejected(lambda r: n(r)['sourceLinks'][0].update(featureId='way/347944791'), 'Changed or partial OSM source')
        self.rejected(lambda r: o(r).update(freeEnds=[]), 'does not end on today')                # the pier end is stated
        self.rejected(lambda r: o(r).update(freeEndBasis=''), 'Invalid free end')
        self.rejected(lambda r: o(r).update(freeEnds=[[0, 0]]), 'does not end on today')          # only the pier end is free
        self.rejected(lambda r: o(r)['maps'].update({'1956-eckero': 'present'}), 'Old road dates')

    def test_an_owned_source_cannot_be_owned_again(self):
        catalog = copy.deepcopy(self.pristine)
        catalog['objects'][0] = {**catalog['objects'][0], 'sourceLinks': catalog['objects'][0].get('sourceLinks', []) + [{'datasetId': 'osm-2026', 'featureId': 'way/169282417'}]}
        with self.assertRaises(ValueError) as cm:
            self.apply(catalog=catalog)
        self.assertIn('already owned', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
