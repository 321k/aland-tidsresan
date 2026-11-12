"""Scope audit for the third Mariehamn street pass: rebuild with the pass disabled and compare."""
import gzip, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
import build_temporal_objects, mariehamn_street_pass3 as pass3
R = Path('data/map-scan-cache/review/mariehamn-major-roads/pass3')
after = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); snapshot = json.load(gzip.open(R / 'before.json.gz'))
real = pass3.apply_street_pass3; pass3.apply_street_pass3 = lambda read, catalog: None
before = json.loads(json.dumps(build_temporal_objects.compile_catalog(), ensure_ascii=False)); pass3.apply_street_pass3 = real
review = json.load(open('data/mariehamn-street-pass3.json')); NEW = {d['id'] for d in review['decisions']}
bo = {o['id']: o for o in before['objects']}; ao = {o['id']: o for o in after['objects']}
bg = {g['id']: g for g in before['geometries']}; ag = {g['id']: g for g in after['geometries']}
owners = {}
for o in after['objects']:
    for l in o['sourceLinks']:
        if 'sourceVertexRange' not in l: owners.setdefault((l['datasetId'], l['featureId']), []).append(o['id'])
audit = dict(
    snapshotEqualsBaseline=snapshot == before,
    objects=[len(bo), len(ao)], geometries=[len(bg), len(ag)], addedObjects=len(set(ao) - set(bo)),
    changedObjects=sorted(i for i in bo if bo[i] != ao.get(i)), removedObjects=sorted(set(bo) - set(ao)),
    changedGeometries=sorted(i for i in bg if bg[i] != ag.get(i)), addedGeometries=len(set(ag) - set(bg)),
    addedGeometriesOutsidePrefix=sorted(g for g in set(ag) - set(bg) if not g.startswith('geometry:city-street-pass3:')),
    sourcesAdded=sorted({s['id'] for s in after['sources']} - {s['id'] for s in before['sources']}),
    cityStagesUnchanged=before['cityStages'] == after['cityStages'],
    otherTopLevelChanged=sorted(k for k in set(before) | set(after) if k not in ['objects', 'geometries', 'sources', 'recordedAt'] and before.get(k) != after.get(k)),
    newObjectsOwningSharedLinks=sorted(k[1] for k, v in owners.items() if len(v) > 1 and set(v) & NEW),
    newMeters=review['totals']['newPersistentMeters'], byFirstYear=review['totals']['byFirstYear'], byGroup=review['totals']['byGroup'],
    afterSha256=hashlib.sha256(Path('dist/assets/temporal-objects.json.gz').read_bytes()).hexdigest())
(R / 'scope-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=1) + '\n'); print(json.dumps(audit, ensure_ascii=False))
assert set(ao) - set(bo) == NEW and not audit['changedObjects'] and not audit['removedObjects'] and not audit['changedGeometries']
assert not audit['addedGeometriesOutsidePrefix'] and audit['cityStagesUnchanged'] and not audit['otherTopLevelChanged'] and not audit['newObjectsOwningSharedLinks']
assert audit['sourcesAdded'] == ['review:mariehamn-street-pass3']
