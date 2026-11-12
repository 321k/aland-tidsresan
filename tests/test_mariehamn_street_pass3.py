import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_street_pass3 import apply_street_pass3

PREFIX = 'road:mariehamn:street-pass3:'


class StreetPass3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        built = cls.read('dist/assets/temporal-objects.json.gz')
        built['objects'] = [o for o in built['objects'] if not o['id'].startswith(PREFIX)]
        built['geometries'] = [g for g in built['geometries'] if not g['id'].startswith('geometry:city-street-pass3:')]
        built['sources'] = [s for s in built['sources'] if s['id'] != 'review:mariehamn-street-pass3']
        cls.base = built

    def run_with(self, change, catalog=None):
        review = self.read('data/mariehamn-street-pass3.json'); change(review)
        catalog = catalog or copy.deepcopy(self.base); before = copy.deepcopy(catalog)
        reader = lambda p: review if p.endswith('mariehamn-street-pass3.json') else self.read(p)
        with self.assertRaises(ValueError):
            apply_street_pass3(reader, catalog)
        self.assertEqual(before, catalog)

    def decision(self, review, key):
        return next(d for d in review['decisions'] if d['id'] == PREFIX + key)

    def test_unchanged_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.base); apply_street_pass3(self.read, catalog)
        self.assertEqual(len(catalog['objects']) - len(self.base['objects']), 53)
        built = {o['id']: o for o in json.loads(json.dumps(catalog, ensure_ascii=False))['objects'] if o['id'].startswith(PREFIX)}
        published = {o['id']: o for o in self.read('dist/assets/temporal-objects.json.gz')['objects'] if o['id'].startswith(PREFIX)}
        for o in published.values():
            if o.pop('approach1942', None):  # later 1942 approach review: undo its additions before comparing
                o['states'].pop(0); o['geometryPeriods'].pop(0)
                o['evidence'] = [e for e in o['evidence'] if not e['id'].endswith(':approach-photo-1942')]
                o['sourceLinks'] = [l for l in o['sourceLinks'] if ':approach-1942:' not in l['featureId']]
        self.assertEqual(sorted(i for i in set(built) | set(published) if built.get(i) != published.get(i)), [])
        with self.assertRaises(ValueError):
            apply_street_pass3(self.read, catalog)

    def test_requires_the_second_pass(self):
        catalog = copy.deepcopy(self.base)
        catalog['objects'] = [o for o in catalog['objects'] if not o.get('majorRoadFollowup')]
        self.run_with(lambda r: None, catalog)

    def test_start_cannot_precede_map_evidence(self):
        def early(r):
            d = self.decision(r, 'strandhagsvagen'); d['firstYear'] = 1968; d['states'][0]['from'] = 1968; d['phases'][0]['from'] = 1968
        self.run_with(early)

    def test_present_edition_before_the_start_rejected(self):
        self.run_with(lambda r: self.decision(r, 'movagen')['observations'][1].update(outcome='present', coverage='full'))

    def test_partial_extent_must_follow_the_modern_road(self):
        self.run_with(lambda r: self.decision(r, 'mellangardsvagen')['phases'][0]['range'].__setitem__(1, 0.8))

    def test_partial_geometry_needs_a_partial_observation(self):
        self.run_with(lambda r: self.decision(r, 'mellangardsvagen')['observations'][0].update(coverage='full'))

    def test_member_cannot_have_two_owners(self):
        def steal(r):
            a, b = self.decision(r, 'krokensvagen'), self.decision(r, 'grantorpsvagen')
            b['members'].append(a['members'][0]); b['display'].append(a['display'][0]); b['modernLinks'] += a['modernLinks']
        self.run_with(steal)

    def test_discontinuous_section_rejected(self):
        def join(r):
            a, b = self.decision(r, 'gesallgatan'), self.decision(r, 'stenhuggarvagen')
            a['members'] += b['members']; a['display'] += b['display']; a['modernLinks'] += b['modernLinks']; r['decisions'].remove(b)
        self.run_with(join)

    def test_changed_inputs_rejected(self):
        self.run_with(lambda r: r['decisions'][-1]['members'][0].update(inputHash='changed'))
        self.run_with(lambda r: r['decisions'][0]['modernLinks'][0].update(inputHash='changed'))

    def test_wrong_length_or_total_rejected(self):
        self.run_with(lambda r: self.decision(r, 'askuddsvagen').update(lengthMeters=600))
        self.run_with(lambda r: r['totals'].update(newPersistentMeters=12000))


if __name__ == '__main__':
    unittest.main()
