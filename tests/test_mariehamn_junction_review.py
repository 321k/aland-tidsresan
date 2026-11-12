import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_junction_review import apply_junction_review

PREFIX = 'road:mariehamn:junction-review:'


class JunctionReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        built = cls.read('dist/assets/temporal-objects.json.gz')
        built['objects'] = [o for o in built['objects'] if not o['id'].startswith(PREFIX)]
        built['geometries'] = [g for g in built['geometries'] if not g['id'].startswith('geometry:city-junction-review:')]
        built['sources'] = [s for s in built['sources'] if s['id'] != 'review:mariehamn-junction-review']
        cls.base = built

    def run_with(self, change, catalog=None):
        review = self.read('data/mariehamn-junction-review.json'); change(review)
        catalog = catalog or copy.deepcopy(self.base); before = copy.deepcopy(catalog)
        reader = lambda p: review if p.endswith('mariehamn-junction-review.json') else self.read(p)
        with self.assertRaises(ValueError):
            apply_junction_review(reader, catalog)
        self.assertEqual(before, catalog)

    def decision(self, review, key):
        return next(d for d in review['decisions'] if d['id'] == PREFIX + key)

    def test_unchanged_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.base); apply_junction_review(self.read, catalog)
        self.assertEqual(len(catalog['objects']) - len(self.base['objects']), 6)
        built = {o['id']: o for o in json.loads(json.dumps(catalog, ensure_ascii=False))['objects'] if o['id'].startswith(PREFIX)}
        published = {o['id']: o for o in self.read('dist/assets/temporal-objects.json.gz')['objects'] if o['id'].startswith(PREFIX)}
        self.assertEqual(sorted(i for i in set(built) | set(published) if built.get(i) != published.get(i)), [])
        with self.assertRaises(ValueError):
            apply_junction_review(self.read, catalog)

    def test_requires_the_fifth_pass(self):
        catalog = copy.deepcopy(self.base)
        catalog['objects'] = [o for o in catalog['objects'] if not o.get('mariehamnStreetPass5')]
        self.run_with(lambda r: None, catalog)

    def test_west_approach_cannot_precede_the_1978_overprint(self):
        def early(r):
            d = self.decision(r, 'bolstavagen-west-approach'); d['firstYear'] = 1968; d['states'][0]['from'] = 1968; d['phases'][0]['from'] = 1968
        self.run_with(early)

    def test_second_carriageway_cannot_be_present_while_one_road_is_drawn(self):
        self.run_with(lambda r: self.decision(r, 'vastra-utfarten-crossing-east')['observations'][2].update(outcome='present', coverage='full'))

    def test_member_cannot_have_two_owners(self):
        def steal(r):
            a, b = self.decision(r, 'skarpansvagen-alandsplan'), self.decision(r, 'gesallgatan-alandsplan')
            b['members'].append(a['members'][0]); b['display'].append(a['display'][0]); b['modernLinks'] += a['modernLinks']
        self.run_with(steal)

    def test_changed_inputs_rejected(self):
        self.run_with(lambda r: r['decisions'][-1]['members'][0].update(inputHash='changed'))
        self.run_with(lambda r: r['decisions'][0]['modernLinks'][0].update(inputHash='changed'))

    def test_counting_rules_enforced(self):
        self.run_with(lambda r: self.decision(r, 'godbyvagen-bolstavagen').update(lengthMeters=131.8))
        self.run_with(lambda r: self.decision(r, 'gesallgatan-alandsplan').update(countRule='display'))
        self.run_with(lambda r: self.decision(r, 'alandsplan-ring').update(lengthMeters=200))
        self.run_with(lambda r: r['totals'].update(newPersistentMeters=500))


if __name__ == '__main__':
    unittest.main()
