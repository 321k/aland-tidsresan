import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lemland_old_road_osm import apply_lemland_old_road_osm

REVIEW = 'data/lemland-old-road-osm.json'
SNAPSHOT = Path('data/map-scan-cache/review/lemlandsvagen-main-road/before-old-road-osm.json.gz')


class LemlandOldRoadOsmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        # The road-remnant step (scripts/road_remnants.py) runs later and adds register evidence; this step is compared without it.
        for o in cls.built['objects']:
            if o.pop('registerRemnants', None) is not None:
                o['evidence'] = [e for e in o['evidence'] if e.get('observationType') != 'heritage-register']
        cls.pristine = cls.read(str(SNAPSHOT)) if SNAPSHOT.exists() else None
        cls.review = cls.read(REVIEW)

    def setUp(self):
        # The catalogue just before this review is kept in the local review cache; without it these tests are skipped.
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def apply(self, review=None, catalog=None):
        catalog = catalog if catalog is not None else copy.deepcopy(self.pristine)
        apply_lemland_old_road_osm(lambda p: review if review is not None and p == REVIEW else self.read(p), catalog)
        return catalog

    def rejected(self, change):
        review = copy.deepcopy(self.review); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            self.apply(review, catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_and_matches_the_build(self):
        catalog = json.loads(json.dumps(self.apply(), ensure_ascii=False))
        ids = [o['id'] for o in self.review['objects']]
        key = lambda c, k: {x['id']: x for x in c[k]}
        self.assertEqual({i: key(catalog, 'objects')[i] for i in ids}, {i: key(self.built, 'objects')[i] for i in ids})
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in ids], [o for o in self.pristine['objects'] if o['id'] not in ids])
        before, after = key(self.pristine, 'geometries'), key(catalog, 'geometries')
        self.assertEqual(len(after) - len(before), 7)
        self.assertTrue(all(after[g] == before[g] for g in before))               # the raw 1929 traces are unchanged
        self.assertEqual(catalog['cityStages'], self.pristine['cityStages'])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_ownership_never_overlaps_existing_owners(self):
        catalog = self.apply(); parts = {}
        for o in catalog['objects']:
            for l in o.get('sourceLinks', []):
                parts.setdefault((l['datasetId'], l['featureId']), []).append(l.get('sourceVertexRange'))
        for o in catalog['objects']:
            if 'lemlandOldRoadOsm' not in o:
                continue
            for l in o['sourceLinks']:
                ranges = sorted(parts[(l['datasetId'], l['featureId'])])
                self.assertNotIn(None, ranges)
                for (a, b), (c, d) in zip(ranges, ranges[1:]):
                    self.assertLessEqual(b, c + 1e-8)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected(lambda r: r['objects'][0].update(inputHash='changed'))
        self.rejected(lambda r: r['objects'][1].update(traceGeometryHash='changed'))
        self.rejected(lambda r: r['wayHashes'].update({'way/349910225': 'changed'}))                 # a changed OSM way
        self.rejected(lambda r: r['snapshotHashes']['osm-2021'].update({'road-2021-173992646': 'changed'}))
        self.rejected(lambda r: r['snapshotHashes']['osm-2021'].pop('road-2021-173992646'))       # a reviewed snapshot feature left out
        self.rejected(lambda r: r['unchanged'][0].update(inputHash='changed'))
        self.rejected(lambda r: r['objects'][0]['phases'][1].update({'from': 1970}))                # phases must meet
        self.rejected(lambda r: (r['objects'][1]['phases'][0].update({'to': 1985}), r['objects'][1]['phases'][-1].update({'from': 1985})))  # survival starts where the maps end
        self.rejected(lambda r: r['objects'][1]['phases'][0]['pieces'].pop(0))                      # without its first gap the line leaves its trace
        self.rejected(lambda r: r['objects'][2]['phases'][0]['pieces'].pop(2))                      # a missing gap breaks the line
        self.rejected(lambda r: r['objects'][0]['phases'][0].update(pieces=[{'trace': True}, {'way': 'way/119232836', 'range': [2, 23], 'reverse': False}, {'trace': True}]))  # the 1968 curve is not the 1929 road
        self.rejected(lambda r: r['objects'][1]['phases'][-1]['pieces'][0].update(range=[0, 23]))  # the later link to the bypass is not the old road
        self.rejected(lambda r: r['limits'].update(overlapMeters=20))                               # junction contacts are short, not zero


if __name__ == '__main__':
    unittest.main()
