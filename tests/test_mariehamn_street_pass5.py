import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_street_pass5 import apply_street_pass5

PREFIX = 'road:mariehamn:street-pass5:'


class StreetPass5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        built = cls.read('dist/assets/temporal-objects.json.gz')
        built['objects'] = [o for o in built['objects'] if not o['id'].startswith(PREFIX)]
        built['geometries'] = [g for g in built['geometries'] if not g['id'].startswith('geometry:city-street-pass5:')]
        built['sources'] = [s for s in built['sources'] if s['id'] != 'review:mariehamn-street-pass5']
        cls.base = built

    def run_with(self, change, catalog=None):
        review = self.read('data/mariehamn-street-pass5.json'); change(review)
        catalog = catalog or copy.deepcopy(self.base); before = copy.deepcopy(catalog)
        reader = lambda p: review if p.endswith('mariehamn-street-pass5.json') else self.read(p)
        with self.assertRaises(ValueError):
            apply_street_pass5(reader, catalog)
        self.assertEqual(before, catalog)

    def decision(self, review, key):
        return next(d for d in review['decisions'] if d['id'] == PREFIX + key)

    def test_unchanged_review_applies_once_and_matches_the_build(self):
        catalog = copy.deepcopy(self.base); apply_street_pass5(self.read, catalog)
        self.assertEqual(len(catalog['objects']) - len(self.base['objects']), 26)
        built = {o['id']: o for o in json.loads(json.dumps(catalog, ensure_ascii=False))['objects'] if o['id'].startswith(PREFIX)}
        published = {o['id']: o for o in self.read('dist/assets/temporal-objects.json.gz')['objects'] if o['id'].startswith(PREFIX)}
        self.assertEqual(sorted(i for i in set(built) | set(published) if built.get(i) != published.get(i)), [])
        with self.assertRaises(ValueError):
            apply_street_pass5(self.read, catalog)

    def test_requires_the_fourth_pass(self):
        catalog = copy.deepcopy(self.base)
        catalog['objects'] = [o for o in catalog['objects'] if not o.get('mariehamnStreetPass4')]
        self.run_with(lambda r: None, catalog)

    def test_start_cannot_precede_map_evidence(self):
        def early(r):
            d = self.decision(r, 'masvagen'); d['firstYear'] = 1968; d['states'][0]['from'] = 1968; d['phases'][0]['from'] = 1968
        self.run_with(early)

    def test_present_edition_before_the_start_rejected(self):
        self.run_with(lambda r: self.decision(r, 'havsgatan-new-section')['observations'][0].update(outcome='present', coverage='full'))

    def test_unreviewed_partial_extent_rejected(self):
        def partial(r):
            d = self.decision(r, 'masvagen'); d['phases'][0].update(geometry='substring:start', range=[0, 0.5], paths=d['members'][0]['feature']['paths'])
        self.run_with(partial)

    def test_member_cannot_have_two_owners(self):
        def steal(r):
            a, b = self.decision(r, 'masvagen'), self.decision(r, 'doppingvagen')
            b['members'].append(a['members'][0]); b['display'].append(a['display'][0]); b['modernLinks'] += a['modernLinks']
        self.run_with(steal)

    def test_discontinuous_section_rejected(self):
        def join(r):
            a, b = self.decision(r, 'fiskhamnsvagen'), self.decision(r, 'mariegatan-gap')
            a['members'] += b['members']; a['display'] += b['display']; a['modernLinks'] += b['modernLinks']; r['decisions'].remove(b)
        self.run_with(join)

    def test_changed_inputs_rejected(self):
        self.run_with(lambda r: r['decisions'][-1]['members'][0].update(inputHash='changed'))
        self.run_with(lambda r: r['decisions'][0]['modernLinks'][0].update(inputHash='changed'))

    def test_wrong_length_or_total_rejected(self):
        self.run_with(lambda r: self.decision(r, 'uppgardsvagen').update(lengthMeters=600))
        self.run_with(lambda r: r['totals'].update(newPersistentMeters=12000))

    def test_parallel_lane_counts_nothing_and_lanes_count_once(self):
        self.run_with(lambda r: self.decision(r, 'nya-godbyvagen-bolstavagen-junction').update(lengthMeters=77.5))
        self.run_with(lambda r: self.decision(r, 'lotsgatan-island').update(countRule='display'))

    def test_junction_cannot_precede_its_first_edition(self):
        self.run_with(lambda r: self.decision(r, 'nya-godbyvagen-bolstavagen-junction')['observations'][0].update(outcome='present', coverage='full'))


if __name__ == '__main__':
    unittest.main()
