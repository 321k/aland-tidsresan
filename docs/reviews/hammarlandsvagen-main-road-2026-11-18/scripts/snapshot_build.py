"""Build the catalogue with some Hammarlandsvägen steps disabled (and their objects' late atlas links left out), copy
it to OUT, and restore the build script and the atlas review. Used for the step snapshots the prepare scripts and the
replay tests read. Usage: snapshot_build.py OUT.json.gz STEP [STEP ...]   (STEP: e.g. overby, kyrkoby, storby)"""
import sys, json, shutil, subprocess
from pathlib import Path
out, steps = sys.argv[1], sys.argv[2:]
bto, rrr = Path('scripts/build_temporal_objects.py'), Path('data/regional-road-review.json')
b0, r0 = bto.read_text(), rrr.read_text()
try:
    s = b0
    for st in steps:
        line = f'            apply_hammarlandsvagen_{st}(read, catalog)\n'
        assert s.count(line) <= 1, st
        s = s.replace(line, '            pass  # snapshot: step disabled\n')
    bto.write_text(s)
    r = json.loads(r0)
    for t in r['traces']:
        t['replacements'] = [l for l in t['replacements'] if l.get('afterStep', '').rsplit('_', 1)[-1] not in steps]
    rrr.write_text(json.dumps(r, ensure_ascii=False, indent=2) + ('\n' if r0.endswith('\n') else ''))
    res = subprocess.run(['.venv-geo/bin/python', 'scripts/build_temporal_objects.py'], capture_output=True, text=True)
    print((res.stdout + res.stderr).strip().splitlines()[-1])
    if res.returncode: sys.exit('build failed')
    shutil.copy('dist/assets/temporal-objects.json.gz', out)
finally:
    bto.write_text(b0); rrr.write_text(r0)
