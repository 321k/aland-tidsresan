import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from sviby_connections import apply_sviby_connections, MAIN, EARLY

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/sviby-connections/before-sviby-connections-step.json.gz')
NM = 'road:mariehamn:major-followup:norra-mockelovagen'
JN, EW, SH = 'road:jomala:kasbergsvagen:norra-svibyvagen', 'road:jomala:sviby:vagen-mot-svibyvagen', 'road:jomala:norra-mockelovagen:norra-delen'
CHANGED = (NM, JN, EW, SH)


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class SvibyConnectionsTests(unittest.TestCase):
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
        apply_sviby_connections(lambda p: data[p] if p in data else read(p), catalog)
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
        for i in CHANGED:
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in CHANGED], [o for o in self.pristine['objects'] if o['id'] not in CHANGED])
        self.assertEqual(catalog['cityStages'], self.built['cityStages'])
        k = key(catalog)
        self.assertEqual([(k[i]['states'][0]['from']) for i in (NM, JN, EW, SH)], [1929, 1928, 1942, 1929])
        stub = 'city-reconstruction-1942:city-1942-street-0:approach-gap:0'
        self.assertFalse(any(f['id'] == stub for s in catalog['cityStages'] for f in s['features']))
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed Hammarlandsvägen input', EARLY, lambda x: x['early'][0].update(inputHash='changed'))
        self.rejected('Changed OSM source', MAIN, lambda x: x['newRoads'][0]['sourceLinks'][0].update(input='changed'))
        self.rejected('already owned', MAIN, lambda x: x['newRoads'][1]['sourceLinks'][1].update(sourceVertexRange=[0, 5.0]))
        self.rejected('does not abut', MAIN, lambda x: x['newRoads'][1]['sourceLinks'][1].update(sourceVertexRange=[0, 4.0]))
        self.rejected('not its OSM pieces', MAIN, lambda x: x['newRoads'][1]['paths'][0].pop(1))
        self.rejected('does not join', MAIN, lambda x: x['newRoads'][2].update(end='road:qgis:mariehamn:kasbergsvagen-200km2'))
        self.rejected('New road dates', MAIN, lambda x: x['newRoads'][0]['maps'].update({'1968-mariehamn': 'absent'}))
        self.rejected('city-stage feature', MAIN, lambda x: x['stageFeatures'][0].update(maxDistanceMeters=5))


if __name__ == '__main__':
    unittest.main()
