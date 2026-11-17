"""Writes data/plan-north-street.json from the visual review, with fingerprints of the step's inputs.
Run from the project root with the catalogue as it is just before the step (dumped after apply_church_road):
    .venv-geo/bin/python docs/reviews/norra-planerade-tvargatan-2026-11-17/scripts/prepare.py BEFORE.json.gz
"""
import gzip, json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from mariehamn_frame_1942 import digest
cat = json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
STAGES = ['city-reconstruction-1860', 'city-reconstruction-1861', 'city-reconstruction-1871']
stages = {s['id']: s for s in cat['cityStages']}
def feature(stage, key):
    return next(f for f in stages[stage]['features'] if f['id'] == stage + ':' + key)
hashes = lambda key: {digest(feature(s, key)['paths']) for s in STAGES}
one = lambda key: (lambda h: h.pop() if len(h) == 1 else (_ for _ in ()).throw(ValueError('differs between stages: ' + key)))(hashes(key))
attached = ['plan-1860-street-0', 'plan-1860-street-1', 'plan-1860-street-2', 'plan-1860-street-5']
review = dict(
    schemaVersion=1, reviewedAt='2026-11-17',
    source=dict(id='review:plan-north-street', title='Norra planerade tvärgatan i 1860 års plan · granskning', url='assets/plan-north-street.json'),
    basis=('Planen ritar sin norra tvärgata ett kvartersdjup norr om den gata som planens gator har passats in efter (Norragatan). '
           'Kvartersraden mellan gatorna är 47 m djup i planens egen inpassning. Gatan visas därför parallellt med den rekonstruerade '
           'Norragatan, 47 m norr om den, från västra strandens gata till Strandgatan. Läget är en tolkning av planen, inte belägg för en byggd gata.'),
    traceId='plan-1860-trace-8', featureId='plan-1860-street-18', inputHash=one('plan-1860-street-18'), stages=STAGES,
    referenceName='Norragatan', offsetMeters=47, straightnessMeters=3, planDepthMeters=[47.0, 46.8, 46.9], maxMoveMeters=40,
    westEndFeatureId='plan-1860-street-0', eastEndObjectId='road:postwar:way-78489469',
    attached=[dict(featureId=k, inputHash=one(k)) for k in attached],
    block=dict(featureId='block:17', inputHash=one('block:17'), minArea=1500, maxArea=6000))
Path('data/plan-north-street.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print('ok')
