"""Dump the catalogue just before each snapshot-tested step (run from scripts/ with the project venv).
Writes NEW snapshots next to the old ones as *.new.json.gz and prints a diff summary against the old snapshot."""
import copy, gzip, json, sys; sys.path.insert(0, ".")
from pathlib import Path
R = Path('../data/map-scan-cache/review')
TARGETS = {
    ('mariehamn_approaches_1942', 'apply_approaches_1942'): 'trace-1942/before',
    ('mariehamn_building_maps', 'apply_building_maps'): 'mariehamn-buildings/before',
    ('mariehamn_frame_1942', 'apply_frame_1942'): 'trace-1942/frame-before',
    ('mariehamn_symbols_1968', 'apply_symbols_1968'): 'mariehamn-buildings/symbols-before',
    ('mariehamn_museum_duplicates', 'apply_museum_duplicates'): 'museum-duplicates/museum-before',
    ('mariehamn_museum_duplicates', 'apply_museum_offsets'): 'museum-duplicates/offsets-before',
    ('mariehamn_building_photos', 'apply_building_photos'): 'photo-dating/photos-before',
    ('mariehamn_museum_streets', 'apply_museum_streets'): 'museum-streets/before',
}
dumps = {}
import importlib
for (mod, fn), name in TARGETS.items():
    m = importlib.import_module(mod); orig = getattr(m, fn)
    def wrap(read, catalog, _orig=orig, _name=name):
        dumps[_name] = json.loads(json.dumps(catalog, ensure_ascii=False))
        return _orig(read, catalog)
    setattr(m, fn, wrap)
import build_temporal_objects as t
t.compile_catalog()
for name, cat in dumps.items():
    if not (R / (name + '.json.gz')).exists():
        (R / (name + '.json.gz')).write_bytes(gzip.compress(json.dumps(cat, ensure_ascii=False).encode())); print(name, 'new snapshot'); continue
    old = json.loads(gzip.decompress((R / (name + '.json.gz')).read_bytes()))
    A = {o['id']: o for o in old['objects']}; B = {o['id']: o for o in cat['objects']}
    changed = sorted(i for i in B if A.get(i) != B[i]);
    stages = [s['id'] for s, u in zip(old['cityStages'], cat['cityStages']) if s != u]
    other = sorted(k for k in cat if k not in ('objects', 'cityStages') and cat[k] != old.get(k))
    print(name, 'ids same', set(A) == set(B), 'changed', len(changed), changed[:6], 'stages', stages, 'other', other)
    (R / (name + '.new.json.gz')).write_bytes(gzip.compress(json.dumps(cat, ensure_ascii=False).encode()))
