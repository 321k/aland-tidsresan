import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from plan_1860_buildings import apply_plan_1860_buildings

REVIEW = 'data/plan-1860-buildings.json'


class Plan1860BuildingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        cls.built = cls.read('dist/assets/temporal-objects.json.gz')
        snapshot = Path('data/map-scan-cache/review/plan-1860-buildings/before.json.gz')
        cls.pristine = cls.read(str(snapshot)) if snapshot.exists() else None

    def setUp(self):
        # The pre-review catalogue is kept in the local review cache; without it these tests are skipped.
        if self.pristine is None:
            self.skipTest('pre-review snapshot is kept in the local review cache')

    def run_with(self, change):
        review = self.read(REVIEW); change(review)
        catalog = copy.deepcopy(self.pristine); before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            apply_plan_1860_buildings(lambda p: review if p == REVIEW else self.read(p), catalog)
        self.assertEqual(before, catalog)

    def test_review_applies_once_adds_only_planned_buildings_and_rows_and_matches_the_build(self):
        catalog = copy.deepcopy(self.pristine); apply_plan_1860_buildings(self.read, catalog)
        catalog = json.loads(json.dumps(catalog, ensure_ascii=False))
        mine = lambda c, k: {x['id']: x for x in c[k] if 'plan-1860-buildings' in x['id'] or x['id'].startswith('building:plan-1860:')}
        self.assertEqual(len(mine(catalog, 'objects')), 53)
        self.assertEqual(len(mine(catalog, 'geometries')), 53)
        # Later build steps may link these objects to others (relationships); this step sets none.
        strip = lambda objs: {i: {k: v for k, v in o.items() if k != 'relationships'} for i, o in objs.items()}
        self.assertEqual(strip(mine(catalog, 'objects')), strip(mine(self.built, 'objects')))
        self.assertFalse(any('relationships' in o for o in mine(catalog, 'objects').values()))
        self.assertEqual(mine(catalog, 'geometries'), mine(self.built, 'geometries'))
        for k in ('objects', 'geometries'):
            self.assertEqual([x for x in catalog[k] if x['id'] not in mine(catalog, k)], self.pristine[k])
        self.assertEqual(len(catalog['sources']), len(self.pristine['sources']) + 1)
        self.assertEqual(catalog['cityStages'], self.pristine['cityStages'])
        with self.assertRaises(ValueError):
            apply_plan_1860_buildings(self.read, catalog)

    def test_invalid_review_is_rejected_before_any_change(self):
        self.run_with(lambda r: r['buildings'].append(copy.deepcopy(r['buildings'][0])))  # duplicate id
        self.run_with(lambda r: r['controlStreets']['eastWest'][0].__setitem__(0, 'Okänd gata'))
        self.run_with(lambda r: r['controlStreets']['northSouth'][0].__setitem__(1, ['Okänd gata']))
        self.run_with(lambda r: r['buildings'][0].update(pixels=r['buildings'][0]['pixels'][:3]))
        self.run_with(lambda r: r['buildings'][0].update(pixels=[[0, 0], [10, 10], [10, 0], [0, 10]]))  # self-crossing
        self.run_with(lambda r: r.update(maxExtrapolationCells=1))  # the swimming school lies 2.8 cells out
        self.run_with(lambda r: r.update(basis=''))
        self.run_with(lambda r: r['houseRows'][0].pop('location'))
        # Street-centre corrections live in the traces now (docs/plan-street-traces.md), not in this review.
        self.run_with(lambda r: r.update(planLineCorrections={'Norragatan i planen': dict(pixels=[[300, 337], [1200, 470]], note='x')}))


if __name__ == '__main__':
    unittest.main()
