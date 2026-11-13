"""Writes data/mariehamn-symbols-1968.json: printed-map symbol objects dated back to the 1968 edition of sheet 101208.

Retained for audit; it fingerprints the catalogue as it was before this step (before.json.gz in this folder).
Candidates come from sym_prepare.py (1968 symbol matched one-to-one in the b6–b8 matching, outside the hatched
built-up areas and hatched surroundings); every candidate was then checked on sym-contact-*.jpg (1968 | 1985 | 1995,
the object's first outline shifted by the local 1968 registration, the matched 1968 symbol circled) and rejections
are recorded in sym-overrides.json. The 1985 panel is unshifted and often offset; the object itself already rests on
the 1985 symbol, so only the 1968 drawing was judged. The 1968 map year is first evidence, not a construction year.
Run from the project root: .venv-geo/bin/python data/map-scan-cache/review/mariehamn-buildings/sym_review.py
"""
import hashlib, json, sys
from pathlib import Path
P = Path('data/map-scan-cache/review/mariehamn-buildings')
sys.path.insert(0, 'scripts')
from mariehamn_symbols_1968 import fingerprint
import importlib.util
spec = importlib.util.spec_from_file_location('conv', P / 'conv.py'); conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
cat = conv.read(str(P / 'before.json.gz')); O = {o['id']: o for o in cat['objects']}
cands = json.load(open(P / 'sym-candidates.json')); overrides = json.load(open(P / 'sym-overrides.json'))
sheet = json.load(open(P / 'b6-match.json'))['editions']['1968']['sourceId']
NOTE = ('Samma hussymbol finns redan på grundkartan 1968, i samma läge efter lokal registreringsjustering och utanför de '
        'streckade bebyggelseområdena. Kartåret är första belägg, inte byggår.')
decisions = [dict(objectId=c['objectId'], input=fingerprint(O[c['objectId']]), originalFrom=c['originalFrom'], batch=c['batch'],
                  pixel=c['pixel'], shiftMeters=c['shift'], distanceAfterShiftMeters=c['distanceAfterShift'], note=NOTE)
             for c in cands['candidates'] if c['objectId'] not in overrides]
review = dict(schemaVersion=1, reviewedAt='2026-11-13',
              source=dict(id='review:mariehamn-symbols-1968', title='Mariehamns hussymboler 1985 · granskade mot grundkartan 1968',
                          url='assets/mariehamn-symbols-1968.json'),
              sheet1968=sheet, rules=dict(matchLimitMeters=9, maxRawSymbolDistanceMeters=30, hatchDarkShare=0.40, hatchStripeDensity=0.22),
              method=__doc__.split('Run from')[0].strip(), decisions=decisions,
              hatched=sorted(h['objectId'] for h in cands['hatched']),
              visualRejections=dict(sorted(overrides.items())),
              reviewSheets=[dict(file=p.name, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(P.glob('sym-contact-*.jpg'))])
Path('data/mariehamn-symbols-1968.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
print(len(decisions), 'decisions,', len(review['hatched']), 'hatched,', len(overrides), 'rejected')
