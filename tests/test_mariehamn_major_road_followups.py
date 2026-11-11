import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mariehamn_major_road_followups import apply_major_road_followups

PREFIX = 'road:mariehamn:major-followup:'


class MajorRoadFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes()))
        built = cls.read('dist/assets/temporal-objects.json.gz')
        built['objects'] = [o for o in built['objects'] if not o['id'].startswith(PREFIX)]
        built['geometries'] = [g for g in built['geometries'] if not g['id'].startswith('geometry:city-major-followup:')]
        built['sources'] = [s for s in built['sources'] if s['id'] != 'review:mariehamn-major-road-followups']
        cls.base = built

    def run_with(self, change):
        review = self.read('data/mariehamn-major-road-followups.json'); change(review)
        catalog = copy.deepcopy(self.base); before = copy.deepcopy(catalog)
        reader = lambda p: review if p.endswith('mariehamn-major-road-followups.json') else self.read(p)
        with self.assertRaises(ValueError):
            apply_major_road_followups(reader, catalog)
        self.assertEqual(before, catalog)

    def decision(self, review, key):
        return next(d for d in review['decisions'] if d['id'] == PREFIX + key)

    def test_unchanged_review_applies_once(self):
        catalog = copy.deepcopy(self.base); apply_major_road_followups(self.read, catalog)
        self.assertEqual(len(catalog['objects']) - len(self.base['objects']), 37)
        with self.assertRaises(ValueError):
            apply_major_road_followups(self.read, catalog)

    def test_reconstruction_must_follow_its_scan_trace(self):
        self.run_with(lambda r: self.decision(r, 'strandnas-old-straight-crossing')['phases'][0]['paths'][0].insert(1, [19.9405, 60.1149]))

    def test_reconstruction_must_join_modern_junctions(self):
        def shift(r):
            ph = self.decision(r, 'godbyvagen-old-south-approach')['phases'][0]; ph['paths'][0][0] = [19.9421, 60.11605]; ph['anchors'][0]['point'] = [19.9421, 60.11605]
        self.run_with(shift)

    def test_removed_road_needs_the_first_edition_without_it(self):
        def keep(r):
            self.decision(r, 'nya-godbyvagen-old-godbyvagen-link')['observations'][3].update(outcome='unclear', coverage='unknown')
        self.run_with(keep)

    def test_start_cannot_precede_map_evidence(self):
        def early(r):
            d = self.decision(r, 'asvagen-north'); d['firstYear'] = 1978; d['states'][0]['from'] = 1978; d['phases'][0]['from'] = 1978
        self.run_with(early)

    def test_partial_extent_must_match_modern_road(self):
        self.run_with(lambda r: self.decision(r, 'nya-godbyvagen-kasberg')['phases'][0]['range'].__setitem__(1, 0.9))

    def test_member_cannot_have_two_owners(self):
        def steal(r):
            a, b = self.decision(r, 'bastuvagen'), self.decision(r, 'klintvagen-north')
            b['members'].append(a['members'][0]); b['modernLinks'] += a['modernLinks']
        self.run_with(steal)

    def test_changed_last_input_rejected_before_any_road(self):
        self.run_with(lambda r: r['decisions'][-1]['members'][0].update(inputHash='changed'))


if __name__ == '__main__':
    unittest.main()
