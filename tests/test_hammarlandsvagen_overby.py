import copy, gzip, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hammarlandsvagen_main_road import apply_hammarlandsvagen_overby, metric

REVIEW = 'data/hammarlandsvagen-overby.json'
# The catalogue built with this step disabled, kept in the local review cache.
SNAPSHOT = Path('data/map-scan-cache/review/hammarlandsvagen-main-road/before-overby-step.json.gz')
M, OLD = 'road:marsund:eckero-hammarland', 'road:eckero:gamla-landsvagen:overby'
ATLAS = ':regional-context:atlas-1894-1'


def read(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())


class HammarlandsvagenOverbyTests(unittest.TestCase):
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
        apply_hammarlandsvagen_overby(lambda p: review if review is not None and p == REVIEW else read(p), catalog)
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
        # the atlas review links the old road too, in a later pass of the build
        atlas = lambda o: {**o, 'evidence': [e for e in o['evidence'] if not e['id'].endswith(ATLAS)]}
        # The Storby review (a later step) splits the connection's 1959–1985 period again; leave that out.
        def without_storby(o):
            if o['id'] != M: return o
            o = copy.deepcopy(o); o.pop('bypassReviews', None)
            dropped = {e['id'] for e in o['evidence'] if e.get('reviewId') == 'review:hammarlandsvagen-storby'}
            o['evidence'] = [e for e in o['evidence'] if e['id'] not in dropped]
            ps = o['geometryPeriods']; k = next(i for i, p in enumerate(ps) if p['geometryId'] == 'geometry:hammarlandsvagen-storby:without-bypass')
            ps[k + 1]['from'] = ps[k]['from']; ps[k + 1]['evidenceIds'] = [i for i in ps[k + 1]['evidenceIds'] if i not in dropped]; del ps[k]
            return o
        for i in (M, OLD):
            self.assertEqual(atlas(key(catalog)[i]), atlas(without_storby(key(self.built)[i])))
        self.assertEqual([o for o in catalog['objects'] if o['id'] not in (M, OLD)], [o for o in self.pristine['objects'] if o['id'] != M])
        self.assertEqual(len(catalog['geometries']) - len(self.pristine['geometries']), 3)
        before, after = key(self.pristine)[M], key(catalog)[M]
        self.assertEqual(after['states'], before['states'])
        self.assertEqual(after['geometryPeriods'][0], before['geometryPeriods'][0])                  # the 1929 stretches
        self.assertEqual(after['geometryPeriods'][2]['geometryId'], before['geometryPeriods'][1]['geometryId'])
        self.assertEqual([after['geometryPeriods'][1]['from'], after['geometryPeriods'][1]['to'], after['geometryPeriods'][2]['from']], [1959, 1985, 1985])
        with self.assertRaises(ValueError):
            self.apply(catalog=catalog)

    def test_bypass_checks(self):
        b = lambda r: r['bypass']
        self.rejected(lambda r: b(r).update(inputHash='changed'), 'Changed Marsund input')
        self.rejected(lambda r: b(r)['maps'].update({'1978': 'present'}), 'Bypass dates')               # first drawn 1985, not 1978
        self.rejected(lambda r: b(r)['maps'].update({'1968': 'unclear'}), 'Bypass dates')               # needs a map without it
        self.rejected(lambda r: r.update(bypassBasis=''), 'Bypass dates')
        self.rejected(lambda r: b(r)['keep'][1].__setitem__(0, 100.0), 'Invalid kept ranges')           # a removed piece of 24 m
        self.rejected(lambda r: b(r).update(pathLength=1.0), 'Changed Marsund path length')

    def test_old_road_checks(self):
        o = lambda r: r['oldRoad']
        self.rejected(lambda r: o(r).update(id=M), 'Duplicate old-road identity')
        self.rejected(lambda r: o(r).update(mainUntil=1978), 'Old road dates')                          # the main road until the bypass
        self.rejected(lambda r: o(r)['maps'].update({'1968': 'absent'}), 'Old road dates')
        def move_end(r):            # an end off the connection (moved about 5 m), length adjusted, so only the join fails
            p = o(r)['paths'][0]; p[0] = [p[0][0] + 0.0001, p[0][1]]
            o(r)['lengthMeters'] = round(sum(metric(q).length for q in o(r)['paths']), 1)
        self.rejected(move_end, 'does not join')
        self.rejected(lambda r: o(r)['laterPaths'][1].pop(), 'is not its OSM way')                     # the OSM coordinates exactly
        self.rejected(lambda r: o(r)['sourceLinks'][1]['sourceVertexRange'].__setitem__(0, 0), 'is not its OSM way')
        self.rejected(lambda r: o(r)['sourceLinks'].pop(), 'one source link')
        self.rejected(lambda r: o(r).update(sameRoadMeters=10), 'not on the 1929 road')                 # Gamla Landsvägen is 17 m off
        def survivor_moves(r):       # a surviving part not in the 1929-1985 line (its coordinates nudged there)
            p = o(r)['paths'][1]; i = p.index(o(r)['laterPaths'][1][3]); p[i] = [p[i][0] + 1e-6, p[i][1]]
        self.rejected(survivor_moves, 'moves at the bypass')


if __name__ == '__main__':
    unittest.main()
