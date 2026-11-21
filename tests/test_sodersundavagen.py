import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from sodersundavagen import apply_sodersundavagen

MAIN, OLD_REVIEW = 'data/sodersundavagen.json', 'data/sodersundavagen-jomala.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/sodersundavagen/before-sodersundavagen-step.json.gz')
SV, OLD = 'road:rural:hammarland-way-86548779', 'road:jomala:gamla-sodersundavagen:jomala-kyrkby'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class SodersundavagenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = read('dist/assets/temporal-objects.json.gz')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        cls.main, cls.old = read(MAIN), read(OLD_REVIEW)

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, main=None, old=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        data = {MAIN: main, OLD_REVIEW: old}
        apply_sodersundavagen(lambda p: data[p] if data.get(p) is not None else read(p), catalog)
        return catalog

    def rejected(self, why, main=None, old=None):
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(main, old, catalog)
        self.assertIn(why, str(cm.exception))
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        for i in (SV, OLD):
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in (SV, OLD)], [o for o in self.pristine['objects'] if o['id'] not in (SV, OLD)])
        sv = key(catalog)[SV]
        self.assertEqual([(p['from'], p['to'], p.get('coverage')) for p in sv['geometryPeriods']],
                         [(1929, 1968, 'partial'), (1968, 1978, 'partial'), (1978, 1985, 'partial'), (1985, 1995, 'partial'), (1995, 2021, 'full'), (2021, None, None)])
        old = key(catalog)[OLD]
        self.assertEqual([(p['from'], p['to']) for p in old['geometryPeriods']], [(1928, 1995), (1995, None)])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        m = lambda: copy.deepcopy(self.main); o = lambda: copy.deepcopy(self.old)
        x = m(); x['early'][0]['inputHash'] = 'changed'; self.rejected('Changed Hammarlandsvägen input', main=x)
        x = m(); x['coverage'][0]['periods'][0]['maps'] = {'1995-jomala': 'present'}; self.rejected('No map draws the period', main=x)
        x = m(); x['coverage'][0]['periods'][-1]['geometryId'] = 'changed'; self.rejected('Changed period', main=x)
        x = o(); x['oldRoads'][0]['endsOn'][0]['objectId'] = SV; self.rejected('Old road does not end on', old=x)          # the church end is on Godbyvägen
        x = o(); x['oldRoads'][0]['endsOn'] = []; self.rejected('Old road does not join the connection', old=x)
        x = o(); x['oldRoads'][0]['maps']['1928-jomala'] = 'unclear'; self.rejected('Old road dates', old=x)
        x = o(); x['oldRoads'][0]['sameRoadMeters'] = 10; self.rejected('not on the 1929 road', old=x)                       # S:t Olofs vägen lies up to 30 m from the 1928 drawing


if __name__ == '__main__':
    unittest.main()
