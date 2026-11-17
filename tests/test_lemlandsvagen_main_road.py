import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lemlandsvagen_main_road import apply_lemlandsvagen_main_road

REVIEW = 'data/lemlandsvagen-main-road.json'


class LemlandsvagenMainRoadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        snapshot = Path('data/map-scan-cache/review/lemlandsvagen-main-road/before.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None
        cls.review = cls.read(REVIEW)

    def setUp(self):
        # The pre-review catalogue is kept in the local review cache; without it these tests are skipped.
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def ids(self):
        r = self.review
        return [s['id'] for s in r['sections']] + [o['id'] for o in r['oldRoad']['objects']] + [r['target']['objectId'], r['langskata']['objectId']]

    def rejected(self, change):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            apply_lemlandsvagen_main_road(lambda p: review if p == REVIEW else self.read(p), catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_lemlandsvagen_main_road(self.read, catalog)
        catalog = json.loads(json.dumps(catalog, ensure_ascii=False))
        ids = self.ids(); mine = {o['id']: o for o in catalog['objects'] if o['id'] in ids}
        self.assertEqual(len(mine), 13)
        self.assertEqual(mine, {o['id']: o for o in self.built['objects'] if o['id'] in ids})
        others = lambda c: [o for o in c['objects'] if o['id'] not in ids]
        self.assertEqual(others(catalog), others(self.pristine))
        self.assertEqual(catalog['cityStages'], self.pristine['cityStages'])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), 12)
        with self.assertRaises(ValueError):
            apply_lemlandsvagen_main_road(self.read, catalog)

    def test_source_ownership_is_partitioned_exactly(self):
        catalog = copy.deepcopy(self.pristine); apply_lemlandsvagen_main_road(self.read, catalog)
        before = next(o for o in self.pristine['objects'] if o['id'] == self.review['target']['objectId'])
        parts = [o for o in catalog['objects'] if o['id'] in self.ids()[:7] + [before['id']]]
        got = {}
        for o in parts:
            for l in o['sourceLinks']:
                got.setdefault((l['datasetId'], l['featureId']), []).append(tuple(l['sourceVertexRange']))
                self.assertEqual(l['basis'], next(x['basis'] for x in before['sourceLinks'] if x['featureId'] == l['featureId']))
        for l in before['sourceLinks']:
            ranges = sorted(got[(l['datasetId'], l['featureId'])])
            self.assertAlmostEqual(ranges[0][0], l['sourceVertexRange'][0], places=6); self.assertAlmostEqual(ranges[-1][1], l['sourceVertexRange'][1], places=6)
            for (a, b), (c, d) in zip(ranges, ranges[1:]): self.assertAlmostEqual(b, c, places=6)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected(lambda r: r['target'].update(inputHash='changed'))
        self.rejected(lambda r: r['langskata'].update(inputHash='changed'))
        self.rejected(lambda r: r['sections'][0].update(firstYear=1929))                       # first year must be the first map with the road
        self.rejected(lambda r: r['sections'][1]['range'].__setitem__(1, 3000.0))               # sections must meet
        self.rejected(lambda r: r['sourceLinks']['A'].pop())                                   # ownership must rebuild exactly
        self.rejected(lambda r: r['oldRoad']['objects'][0]['path'].pop())                     # old road must end on today's road
        self.rejected(lambda r: r['oldRoad']['objects'][1].update(lastPresent=1978))


if __name__ == '__main__':
    unittest.main()
