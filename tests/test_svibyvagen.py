import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from svibyvagen import apply_svibyvagen, MAIN, KASBERG, OLD as OLD_REVIEW

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/sviby/before-sviby-step.json.gz')
NS, KB, SV = 'road:qgis:gottby:norra-svibyvagen-100km5', 'road:qgis:mariehamn:kasbergsvagen-200km2', 'road:qgis:mariehamn:svibyvagen-1-200km2'
OLD, CORNER, KG = 'road:jomala:gamla-vagen:sviby', 'road:jomala:gamla-kasbergsvagen:tallasen', 'road:jomala:kasbergsgatan'
CHANGED = (NS, KB, SV, OLD, CORNER, KG)


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class SvibyvagenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.files = {MAIN: read(MAIN), KASBERG: read(KASBERG), OLD_REVIEW: read(OLD_REVIEW)}

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, catalog=None, **over):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        data = {**self.files, **over}
        apply_svibyvagen(lambda p: data[p] if p in data else read(p), catalog)
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
        k = key(catalog)
        self.assertEqual([(p['from'], p['to'], p.get('coverage')) for p in k[KB]['geometryPeriods']], [(1929, 1985, 'partial'), (1985, None, None)])
        self.assertEqual([(p['from'], p['to']) for p in k[NS]['geometryPeriods']], [(1928, 1978), (1978, None)])
        self.assertEqual([(p['from'], p['to']) for p in k[SV]['geometryPeriods']][0], (1929, 1937))
        self.assertEqual([(p['from'], p['to']) for p in k[OLD]['geometryPeriods']], [(1928, 1978), (1978, None)])
        self.assertEqual([(s['state'], s['from'], s['to']) for s in k[CORNER]['states']], [('open', 1929, 1985), ('unknown', 1985, None)])
        self.assertEqual(k[KG]['states'][0]['from'], 1929)
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed Hammarlandsvägen input', MAIN, lambda x: x['early'][0].update(inputHash='changed'))
        self.rejected('First year is not the first map', MAIN, lambda x: x['early'][0].update(firstYear=1917))
        self.rejected('Changed or partial OSM source', MAIN, lambda x: x['newRoad']['sourceLinks'][0].update(input='changed'))
        self.rejected('Old road dates do not follow its maps', KASBERG, lambda x: x['oldRoad']['maps'].update({'1985-mariehamn': 'present'}))
        self.rejected('Old line does not end on', KASBERG, lambda x: x['oldRoad'].update(endObjects=[NS]))
        self.rejected('Old road does not end on', OLD_REVIEW, lambda x: x['oldRoads'][0]['endsOn'][0].update(objectId=KB))
        self.rejected('not on the 1929 road', OLD_REVIEW, lambda x: x['oldRoads'][0].update(sameRoadMeters=5))   # the service road lies 8–15 m from the drawing


if __name__ == '__main__':
    unittest.main()
