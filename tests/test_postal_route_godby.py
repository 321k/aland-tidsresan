import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from postal_route_godby import apply_postal_route_godby, REVIEW

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/postal-godby/before-postal-godby-step.json.gz')
EM = 'road:emkarbyvagen'
NEW = ('road:jomala:postgardsvagen', 'road:jomala:godbyvagen:golby-junction', 'road:jomala:godbyvagen:bjorkang', 'road:finstrom:godby-korsningen', 'road:finstrom:sundsvagen:godby-farjsundet')


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class PostalRouteGodbyTests(unittest.TestCase):
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
        apply_postal_route_godby(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
        return catalog

    def rejected(self, why, change):
        x = copy.deepcopy(self.review); change(x)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError) as cm:
            self.apply(x, catalog)
        self.assertIn(why, str(cm.exception)); self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        key = lambda c: {x['id']: x for x in c['objects']}
        # Later reviews (docs/postal-route-1929.md, docs/postal-route-haraldsby.md) date some of these objects earlier from
        # the parish maps; from 1968 on the build still holds exactly what this review made, and all of its evidence.
        G0 = {g['id']: g for g in catalog['geometries']}; GB = {g['id']: g for g in self.built['geometries']}
        since = lambda o, k: [x for x in o[k] if x['from'] >= 1968]
        for i in (EM,) + NEW:
            mine, built = key(catalog)[i], key(self.built)[i]
            self.assertEqual(since(mine, 'states'), since(built, 'states'))
            self.assertEqual(since(mine, 'geometryPeriods'), since(built, 'geometryPeriods'))
            self.assertEqual([G0[p['geometryId']] for p in since(mine, 'geometryPeriods')], [GB[p['geometryId']] for p in since(built, 'geometryPeriods')])
            self.assertLessEqual({e['id'] for e in mine['evidence']}, {e['id'] for e in built['evidence']})
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in (EM,) + NEW], [o for o in self.pristine['objects'] if o['id'] not in (EM,) + NEW])
        em, before = key(catalog)[EM], key(self.pristine)[EM]
        G = {g['id']: g for g in catalog['geometries']}
        for gp, old in zip(em['geometryPeriods'], before['geometryPeriods']):
            if gp['from'] in (1968, 1978):
                self.assertEqual(G[gp['geometryId']]['paths'][:-1], G[old['geometryId']]['paths'])     # old paths kept, one path added
            else:
                self.assertEqual(gp, old)
        self.assertEqual({key(catalog)[i]['states'][0]['from'] for i in NEW}, {1968})
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed extension input', lambda x: x['extend'][0].update(inputHash='changed'))
        self.rejected('Changed period', lambda x: x['extend'][0]['periods'][0].update(geometryHash='changed'))
        self.rejected('No map draws the extension', lambda x: x['extend'][0]['periods'][0].update(maps={'1978-jomala': 'present'}))
        self.rejected('does not leave and rejoin', lambda x: x['extend'][0]['periods'][0]['bend']['points'].pop(0))
        self.rejected('does not abut', lambda x: next(l for l in x['newRoads'][3]['sourceLinks'] if l['featureId'] == 'way/1193284948').pop('partialBasis'))
        self.rejected('does not join', lambda x: x['newRoads'][0].update(start='road:atlas1894:godbyvagen', end='road:qgis:saltvik:von-knorringsvagen-1-batch4'))


if __name__ == '__main__':
    unittest.main()
