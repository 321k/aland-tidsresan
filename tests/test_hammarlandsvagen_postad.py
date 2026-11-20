import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_postad

REVIEW = 'data/hammarlandsvagen-postad.json'
# The catalogue built with this step disabled (and the main-road review already cutting the curve), kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/road-remnants/before-postad-step.json.gz')
K = 'road:rural:hammarland-korsberg-old-road'
ATLAS = ':regional-context:atlas-1894-1'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class PostadTests(unittest.TestCase):
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
        apply_hammarlandsvagen_postad(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
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
        atlas = lambda o: {**o, 'evidence': [e for e in o['evidence'] if not e['id'].endswith(ATLAS)]}     # the atlas review links it later
        self.assertEqual(atlas(key(catalog)[K]), atlas(key(self.built)[K]))
        self.assertEqual([o for o in catalog['objects'] if o['id'] != K], [o for o in self.pristine['objects'] if o['id'] != K])
        self.assertEqual([(p['from'], p['to']) for p in key(catalog)[K]['geometryPeriods']][:2], [(1929, 1968), (1968, 1978)])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected(lambda r: r.update(inputHash='changed'), 'Changed Postad input')
        self.rejected(lambda r: r.update(connectionHash='changed'), 'Changed Postad input')
        self.rejected(lambda r: r['outcomes'].update({'1929': 'absent'}), 'Postad dates')
        self.rejected(lambda r: r['path'].__setitem__(1, [r['path'][1][0] + 0.0001, r['path'][1][1]]), 'does not keep the surviving road')
        self.rejected(lambda r: r['remnant'].update(outlineHash='changed'), 'Changed register outline')
        self.rejected(lambda r: r['remnant'].update(minInsideMeters=490), 'leaves the register outline')
        def moved_end(r):                      # an end moved off today's road (length adjusted)
            sys.path.insert(0, 'scripts'); from hammarlandsvagen_main_road import metric
            r['path'][-1] = [r['path'][-1][0] + 0.0003, r['path'][-1][1]]; r['lengthMeters'] = round(metric(r['path']).length, 1)
        self.rejected(moved_end, 'does not join today')


if __name__ == '__main__':
    unittest.main()
