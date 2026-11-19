import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from regional_road_review import reconcile

# The catalogue before the late atlas links (kept in the local review cache); the old Smedens and Näfsby lines exist
# in it, so both passes can be replayed.
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-atlas.json.gz')
LATE = {'road:hammarland:gamla-hammarlandsvagen:smedens', 'road:hammarland:gamla-hammarlandsvagen:nafsby'}
TAIL = ':regional-context:atlas-1894-1'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class HammarlandsvagenAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review, cls.document = read('data/regional-road-review.json'), read('dist/assets/historical-roads.json')
        cls.pristine = read(SNAPSHOT) if SNAPSHOT.exists() else None
        # The snapshot predates later late links (the old road through Överby, tests/test_hammarlandsvagen_overby.py);
        # replay only the links whose objects it has.
        if cls.pristine:
            have = {o['id'] for o in cls.pristine['objects']}
            for t in cls.review['traces']:
                t['replacements'] = [l for l in t['replacements'] if not l.get('afterStep') or l['objectId'] in have]

    def setUp(self):
        if self.pristine is None:
            self.skipTest('pre-change snapshot is kept in the local review cache')

    def links(self, catalog):
        return {o['id'] for o in catalog['objects'] for e in o['evidence'] if e['id'] == o['id'] + TAIL}

    def test_late_links_are_marked_and_split_between_passes(self):
        trace = next(t for t in self.review['traces'] if t['featureId'] == 'atlas-1894-1')
        self.assertEqual({l['objectId'] for l in trace['replacements'] if l.get('afterStep')}, LATE)
        early, _ = reconcile(self.review, self.document, self.pristine, links='early')
        self.assertFalse(self.links(early) & LATE)
        late, _ = reconcile(self.review, self.document, early, links='late')
        self.assertEqual(self.links(late) - self.links(early), LATE)
        # The late pass adds only its own evidence: every other object is unchanged, in order.
        before = {o['id']: o for o in early['objects']}
        for o in late['objects']:
            if o['id'] not in LATE:
                self.assertEqual(o, before[o['id']])
        self.assertEqual(late['sources'], early['sources']); self.assertEqual(late['geometries'], early['geometries'])
        # Running it again adds nothing.
        again, _ = reconcile(self.review, self.document, late, links='late')
        self.assertEqual(again, late)

    def test_late_link_needs_its_object(self):
        catalog = copy.deepcopy(self.pristine)
        catalog['objects'] = [o for o in catalog['objects'] if o['id'] != 'road:hammarland:gamla-hammarlandsvagen:smedens']
        reconcile(self.review, self.document, catalog, links='early')          # left out before the step
        with self.assertRaises(ValueError):
            reconcile(self.review, self.document, catalog, links='late')
        with self.assertRaises(ValueError):
            reconcile(self.review, self.document, catalog, links='later')


if __name__ == '__main__':
    unittest.main()
