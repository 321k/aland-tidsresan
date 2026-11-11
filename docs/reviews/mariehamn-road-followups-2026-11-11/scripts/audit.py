"""Scope audit for the follow-up pass.

before.json.gz is the catalogue as found at the start of the pass. Other uncommitted work had
changed data/rural-map-review.json since that catalogue was built, so the audit also rebuilds a
baseline from the current sources with this pass disabled. The pass is checked against that
baseline; the snapshot-to-baseline difference is reported separately as unrelated work.
"""
import gzip, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
import build_temporal_objects, mariehamn_major_road_followups
R = Path('data/map-scan-cache/review/mariehamn-major-roads/followups')
snapshot = json.load(gzip.open(R / 'before.json.gz')); after = json.load(gzip.open('dist/assets/temporal-objects.json.gz'))
real = mariehamn_major_road_followups.apply_major_road_followups
mariehamn_major_road_followups.apply_major_road_followups = lambda read, catalog: None
before = json.loads(json.dumps(build_temporal_objects.compile_catalog(), ensure_ascii=False))
mariehamn_major_road_followups.apply_major_road_followups = real
so = {o['id']: o for o in snapshot['objects']}; bo0 = {o['id']: o for o in before['objects']}
unrelated = dict(note='Snapshot to baseline: other uncommitted source changes, not part of this pass.',
                 addedObjects=sorted(set(bo0) - set(so)), removedObjects=sorted(set(so) - set(bo0)),
                 changedObjects=sorted(i for i in so if i in bo0 and so[i] != bo0[i]),
                 geometries=[len(snapshot['geometries']), len(before['geometries'])])
review = json.load(open('data/mariehamn-major-road-followups.json'))
ids = {d['id'] for d in review['decisions']}
bo = {o['id']: o for o in before['objects']}; ao = {o['id']: o for o in after['objects']}
bg = {g['id']: g for g in before['geometries']}; ag = {g['id']: g for g in after['geometries']}
changed = sorted(i for i in bo if i in ao and bo[i] != ao[i]); removed = sorted(set(bo) - set(ao)); added = sorted(set(ao) - set(bo))
gchanged = sorted(i for i in bg if i in ag and bg[i] != ag[i]); gremoved = sorted(set(bg) - set(ag)); gadded = sorted(set(ag) - set(bg))
links = {}
for o in after['objects']:
    for l in o['sourceLinks']:
        links.setdefault((l['datasetId'], l['featureId']), []).append(o['id'])
audit = dict(unrelatedToThisPass=unrelated, snapshotSha256=hashlib.sha256((R / 'before.json.gz').read_bytes()).hexdigest(), baselineObjects=len(before['objects']), afterSha256=hashlib.sha256(Path('dist/assets/temporal-objects.json.gz').read_bytes()).hexdigest(),
             objects=[len(bo), len(ao)], geometries=[len(bg), len(ag)], addedObjects=len(added), addedAreReviewed=set(added) == ids,
             changedObjects=changed, removedObjects=removed, changedGeometries=gchanged, removedGeometries=gremoved,
             addedGeometriesPrefixed=all(g.startswith('geometry:city-major-followup:') for g in gadded), addedGeometries=len(gadded),
             sourcesAdded=sorted({s['id'] for s in after['sources']} - {s['id'] for s in before['sources']}),
             cityStagesUnchanged=before.get('cityStages') == after.get('cityStages'),
             newDuplicateSourceOwners=sorted(k[1] for k, v in links.items() if len(v) > 1 and any(i in ids for i in v)),
             newMetres=review['totals']['newPersistentMeters'], byGroup=review['totals']['byGroup'])
(R / 'scope-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=1) + '\n')
print(json.dumps({k: v for k, v in audit.items() if k != 'unrelatedToThisPass'}, ensure_ascii=False)[:1500]); print('unrelated', {k: (len(v) if isinstance(v, list) else v) for k, v in unrelated.items()})
assert audit['addedAreReviewed'] and not changed and not removed and not gchanged and not gremoved and audit['addedGeometriesPrefixed'] and audit['cityStagesUnchanged'] and not audit['newDuplicateSourceOwners']
