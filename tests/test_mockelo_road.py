import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mockelo_road import apply_mockelo_road, MAIN, EARLY

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/mockelo/before-mockelo-step.json.gz')
MV, ID = 'road:qgis:gottby:mockelovagen-100km5', 'road:jomala:mockelovagen:lonnelund'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class MockeloRoadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.files = {MAIN: read(MAIN), EARLY: read(EARLY)}

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, catalog=None, **over):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        data = {**self.files, **over}
        apply_mockelo_road(lambda p: data[p] if p in data else read(p), catalog)
        return catalog

    def rejected(self, why, path, change):
        x = copy.deepcopy(self.files[path]); change(x)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(catalog, **{path: x})
        self.assertIn(why, str(cm.exception))
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        for i in (MV, ID):
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in (MV, ID)], [o for o in self.pristine['objects'] if o['id'] not in (MV, ID)])
        self.assertEqual([(s['from'], s['to']) for s in key(catalog)[MV]['states']], [(1928, 1978), (1978, None)])
        self.assertEqual(key(catalog)[ID]['states'][0]['from'], 1928)
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed Hammarlandsvägen input', EARLY, lambda x: x['early'][0].update(inputHash='changed'))
        self.rejected('Changed OSM source', MAIN, lambda x: x['newRoads'][0]['sourceLinks'][0].update(input='changed'))
        self.rejected('does not abut', MAIN, lambda x: next(l for l in x['newRoads'][0]['sourceLinks'] if l['featureId'] == 'road-2025-166080081').update(sourceVertexRange=[0, 9.0]))
        self.rejected('do not follow each other', MAIN, lambda x: x['newRoads'][0]['sourceLinks'].pop(2))
        self.rejected('does not join', MAIN, lambda x: x['newRoads'][0].update(start='road:qgis:gottby:norra-svibyvagen-100km5'))


if __name__ == '__main__':
    unittest.main()
