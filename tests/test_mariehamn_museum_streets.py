import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_museum_streets import apply_museum_streets

REVIEW = 'data/mariehamn-museum-streets.json'


class MuseumStreetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        snapshot = Path('data/map-scan-cache/review/museum-streets/before.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None

    def setUp(self):
        # The pre-review catalogue is kept in the local review cache; without it these tests are skipped.
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def run_with(self, change, catalog_change=None):
        review = self.read(REVIEW); change(review)
        catalog = copy.deepcopy(self.pristine)
        if catalog_change:
            catalog_change(catalog)
        before = copy.deepcopy(catalog)
        reader = lambda p: review if p == REVIEW else self.read(p)
        with self.assertRaises(ValueError):
            apply_museum_streets(reader, catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_museum_streets(self.read, catalog)
        catalog = json.loads(json.dumps(catalog, ensure_ascii=False))
        review = self.read(REVIEW)
        ids = [m['objectId'] for s in review['streets'] for m in s['members']] + [n['id'] for s in review['streets'] for n in s.get('newObjects', [])]
        mine = {o['id']: o for o in catalog['objects'] if o['id'] in ids}
        built = {o['id']: o for o in self.built['objects'] if o['id'] in ids}
        self.assertEqual(len(mine), 8)
        self.assertEqual(mine, built)
        geoms = {g['id']: g for g in self.built['geometries']}
        for g in catalog['geometries']:
            if g['id'].startswith('geometry:museum-streets:'):
                self.assertEqual(g, geoms[g['id']])
        # Only the four raw stage copies leave the city stages.
        a = {(s['id'], f['id']) for s in self.pristine['cityStages'] for f in s['features']}
        b = {(s['id'], f['id']) for s in catalog['cityStages'] for f in s['features']}
        self.assertEqual(a - b, {(x['stageId'], x['featureId']) for s in review['streets'] for x in s['stageFeatures']})
        self.assertEqual(b - a, set())
        with self.assertRaises(ValueError):
            apply_museum_streets(self.read, catalog)

    def test_changed_member_is_rejected(self):
        self.run_with(lambda r: r['streets'][0]['members'][0].update(inputHash='changed'))
        self.run_with(lambda r: r['streets'][1]['members'][1].update(originalFrom=1952))
        self.run_with(lambda r: r['streets'][1]['members'][1].update(cutLatitude=60.0935))
        self.run_with(lambda r: r['streets'][0].update(maxDistanceMeters=5))

    def test_changed_drawing_or_stage_copy_is_rejected(self):
        self.run_with(lambda r: r['streets'][0].update(inputHash='changed'))
        self.run_with(lambda r: r['streets'][1]['stageFeatures'].pop())
        self.run_with(lambda r: r['streets'][0].update(linkObjectId='road:postwar:way-39585442'))

    def test_new_street_needs_unowned_identical_modern_pieces(self):
        self.run_with(lambda r: r['streets'][0]['newObjects'][0]['pieces'][1].update(pathHash='changed'))
        self.run_with(lambda r: r['streets'][0]['newObjects'][0]['pieces'].reverse())
        self.run_with(lambda r: r['streets'][0]['newObjects'][0].update(joinsObjectId='road:postwar:way-35011941'))
        piece = self.read(REVIEW)['streets'][0]['newObjects'][0]['pieces'][0]['features'][0]
        owner = lambda c: next(o for o in c['objects'] if o['id'] == 'road:postwar:way-35011941')['sourceLinks'].append(dict(piece))
        self.run_with(lambda r: None, owner)


if __name__ == '__main__':
    unittest.main()
