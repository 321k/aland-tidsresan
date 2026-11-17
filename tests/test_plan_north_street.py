import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from plan_north_street import apply_plan_north_street

REVIEW = 'data/plan-north-street.json'


class PlanNorthStreetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        snapshot = Path('data/map-scan-cache/review/plan-north-street/before.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None

    def setUp(self):
        # The pre-review catalogue (dumped right after apply_church_road) is kept in the local review cache.
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def run_with(self, change):
        review = self.read(REVIEW); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            apply_plan_north_street(lambda p: review if p == REVIEW else self.read(p), catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_plan_north_street(self.read, catalog)
        catalog = json.loads(json.dumps(catalog, ensure_ascii=False))
        review = self.read(REVIEW)
        keys = {review['featureId'], review['block']['featureId'], *(a['featureId'] for a in review['attached'])}
        stage = lambda c, s: next(x for x in c['cityStages'] if x['id'] == s)
        for s in review['stages']:
            mine = {f['id']: f for f in stage(catalog, s)['features'] if f['id'].split(':', 1)[1] in keys}
            built = {f['id']: f for f in stage(self.built, s)['features'] if f['id'].split(':', 1)[1] in keys}
            self.assertEqual(len(mine), 6, s)
            self.assertEqual(mine, built, s)
            others = lambda c: [f for f in stage(c, s)['features'] if f['id'].split(':', 1)[1] not in keys]
            self.assertEqual(others(catalog), others(self.pristine), s)
        rest = lambda c: [x for x in c['cityStages'] if x['id'] not in review['stages']]
        self.assertEqual(rest(catalog), rest(self.pristine))
        self.assertEqual(catalog['objects'], self.pristine['objects'])
        with self.assertRaises(ValueError):
            apply_plan_north_street(self.read, catalog)

    def test_changed_inputs_are_rejected(self):
        self.run_with(lambda r: r.update(inputHash='changed'))
        self.run_with(lambda r: r['attached'][2].update(inputHash='changed'))
        self.run_with(lambda r: r['block'].update(inputHash='changed'))
        self.run_with(lambda r: r.update(traceId='plan-1860-trace-9'))
        self.run_with(lambda r: r['stages'].append('city-reconstruction-1999'))

    def test_existing_source_geometry_is_never_overwritten(self):
        catalog = copy.deepcopy(self.pristine)
        stage = next(s for s in catalog['cityStages'] if s['id'] == 'city-reconstruction-1871')
        f = next(f for f in stage['features'] if f['id'].endswith(':plan-1860-street-2'))
        f['sourcePaths'] = copy.deepcopy(f['paths'])
        before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            apply_plan_north_street(self.read, catalog)
        self.assertEqual(before, catalog)

    def test_geometry_guards(self):
        self.run_with(lambda r: r.update(straightnessMeters=0.5))   # Norragatan is straight only to about 1.6 m
        self.run_with(lambda r: r.update(maxMoveMeters=10))         # Torggatan's plan neighbour moves 24 m
        self.run_with(lambda r: r.update(offsetMeters=-47))         # must lie north of Norragatan
        self.run_with(lambda r: r['block'].update(maxArea=3000))    # the recomputed block is about 3,640 m²
        self.run_with(lambda r: r.update(eastEndObjectId='road:postwar:missing'))


if __name__ == '__main__':
    unittest.main()
