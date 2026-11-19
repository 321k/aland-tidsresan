import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_main_road, metric

REVIEW = 'data/hammarlandsvagen-main-road.json'
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before.json.gz')


class HammarlandsvagenMainRoadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        cls.pristine = cls.read(str(SNAPSHOT)) if SNAPSHOT.exists() else None
        cls.review = cls.read(REVIEW)

    def setUp(self):
        # The catalogue just before this review is kept in the local review cache; without it these tests are skipped.
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_hammarlandsvagen_main_road(lambda p: review if review is not None and p == REVIEW else self.read(p), catalog)
        return catalog

    def rejected(self, change):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            self.apply(review, catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        ids = [e['objectId'] for e in self.review['early']] + [self.review['oldRoad']['id']]
        key = lambda c, k: {x['id']: x for x in c[k]}
        # The 1894 atlas review links these objects too (data/regional-road-review.json), outside this step.
        atlas = lambda o: {**o, 'evidence': [e for e in o['evidence'] if not e['id'].endswith(':regional-context:atlas-1894-1')]}
        self.assertEqual({i: atlas(key(catalog, 'objects')[i]) for i in ids}, {i: atlas(key(self.built, 'objects')[i]) for i in ids})
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in ids], [o for o in self.pristine['objects'] if o['id'] not in ids])
        before, after = key(self.pristine, 'geometries'), key(catalog, 'geometries')
        self.assertEqual(len(after) - len(before), 6)
        self.assertTrue(all(after[g] == before[g] for g in before))
        self.assertEqual(catalog['cityStages'], self.pristine['cityStages'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_existing_periods_are_kept_and_only_preceded(self):
        catalog = self.apply(); before = {o['id']: o for o in self.pristine['objects']}
        for o in catalog['objects']:
            if 'hammarlandsvagenMainRoad' in o and o['id'] in before:
                b = before[o['id']]
                self.assertEqual(o['states'][1:], b['states']); self.assertEqual(o['geometryPeriods'][1:], b['geometryPeriods'])
                self.assertEqual(o['sourceLinks'], b['sourceLinks']); self.assertEqual(o['evidence'][:len(b['evidence'])], b['evidence'])

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected(lambda r: r['early'][0].update(inputHash='changed'))
        self.rejected(lambda r: r['early'][1].update(geometryHash='changed'))
        self.rejected(lambda r: r['early'][0].update(until=1978))                                  # must end where the object begins
        self.rejected(lambda r: r['early'][2]['maps'].update({'1929': 'absent'}))                    # first year must be the first map with the road
        self.rejected(lambda r: r['early'][0]['ranges'].__setitem__(1, [5000.0, 6261.1]))            # ranges must not overlap
        self.rejected(lambda r: r['early'][3]['ranges'].__setitem__(0, [0.0, 1300.0]))               # the stretch would break before the church corridor
        self.rejected(lambda r: r['oldRoad'].update(path=r['oldRoad']['path'][:-3], lengthMeters=round(metric(r['oldRoad']['path'][:-3]).length, 1)))  # the old line must end on today's road
        self.rejected(lambda r: r['oldRoad'].update(until=1978))                                     # ends with the first map that does not draw it
        self.rejected(lambda r: r['oldRoad'].update(lengthMeters=1000.0))                            # changed line


if __name__ == '__main__':
    unittest.main()
