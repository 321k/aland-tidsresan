import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mattas_link import apply_mattas_link, REVIEW

# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/mattas/before-mattas-step.json.gz')
SV, B1, B2 = 'road:rural:hammarland-way-86548779', 'road:rural:hammarland-way-495221553', 'road:rural:hammarland-way-160987689'
OLD = 'road:hammarland:gamla-sodersundavagen:mattas'
CHANGED = (SV, B1, B2, OLD)


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class MattasLinkTests(unittest.TestCase):
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
        apply_mattas_link(lambda p: (review or self.review) if p == REVIEW else read(p), catalog)
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
        for i in CHANGED:
            self.assertEqual(key(catalog)[i], key(self.built)[i])
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in CHANGED], [o for o in self.pristine['objects'] if o['id'] not in CHANGED])
        k = key(catalog)
        self.assertEqual([(s['from'], s['to']) for s in k[OLD]['states']], [(1929, 1995), (1995, None)])
        self.assertEqual([k[b]['states'][0]['from'] for b in (B1, B2)], [1929, 1929])
        self.assertEqual({g['canonicalRange'][1] for g in k[SV]['geometryPeriods'] if g['to'] and g['to'] <= 1995}, {0.926626})
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_changed_inputs_are_rejected_before_any_change(self):
        self.rejected('Changed Hammarlandsvägen input', lambda x: x['early'][0].update(inputHash='changed'))
        self.rejected('Changed coverage input', lambda x: x['coverage'][0].update(inputHash='changed'))
        self.rejected('Changed period', lambda x: x['coverage'][0]['periods'][0].update(geometryId='changed'))
        self.rejected('Old road dates', lambda x: x['oldRoad']['maps'].update({'1995-hammarby': 'present'}))
        self.rejected('does not end on', lambda x: x['oldRoad'].update(endObjects=[B1, SV]))


if __name__ == '__main__':
    unittest.main()
