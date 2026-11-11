"""Scope audit for the Lemlandsvägen split: rebuild with the split disabled and compare."""
import gzip, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
import build_temporal_objects, mariehamn_lemlandsvagen_split as split
R = Path('data/map-scan-cache/review/mariehamn-major-roads/lemlandsvagen')
after = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); snapshot = json.load(gzip.open(R / 'before.json.gz'))
real = split.apply_lemlandsvagen_split; split.apply_lemlandsvagen_split = lambda read, catalog: None
before = json.loads(json.dumps(build_temporal_objects.compile_catalog(), ensure_ascii=False)); split.apply_lemlandsvagen_split = real
review = json.load(open('data/mariehamn-lemlandsvagen-split.json'))
Q2, Q3 = review['target']['objectId'], review['pairedLane']['objectId']; NEW = {o['id'] for o in review['objects']}
bo = {o['id']: o for o in before['objects']}; ao = {o['id']: o for o in after['objects']}
bg = {g['id']: g for g in before['geometries']}; ag = {g['id']: g for g in after['geometries']}
changed = sorted(i for i in bo if bo[i] != ao.get(i))
def only(old, new, allowed):
    return sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k) and k not in allowed)
q2, q3 = bo[Q2], ao[Q2]; p2, p3 = bo[Q3], ao[Q3]
audit = dict(
    snapshotEqualsBaseline=snapshot == before,
    objects=[len(bo), len(ao)], geometries=[len(bg), len(ag)], addedObjects=sorted(set(ao) - set(bo)), changedObjects=changed,
    removedObjects=sorted(set(bo) - set(ao)), changedGeometries=sorted(i for i in bg if bg[i] != ag.get(i)), addedGeometries=sorted(set(ag) - set(bg)),
    sourcesAdded=sorted({s['id'] for s in after['sources']} - {s['id'] for s in before['sources']}), cityStagesUnchanged=before['cityStages'] == after['cityStages'],
    target=dict(otherFieldsChanged=only(q2, q3, {'geometryPeriods', 'sourceLinks', 'evidence', 'strandnasSplit'}),
                statesUnchanged=q2['states'] == q3['states'], priorEvidenceKept=q3['evidence'][:len(q2['evidence'])] == q2['evidence'],
                periodsOnlyGeometryIdChanged=[{k: v for k, v in p.items() if k != 'geometryId'} for p in q2['geometryPeriods']] == [{k: v for k, v in p.items() if k != 'geometryId'} for p in q3['geometryPeriods']],
                originalGeometryKept=q2['geometryPeriods'][0]['geometryId'] in ag, links=[len(q2['sourceLinks']), len(q3['sourceLinks'])]),
    pairedLane=dict(otherFieldsChanged=only(p2, p3, {'states', 'geometryPeriods', 'sourceLinks', 'evidence', 'strandnasSplit'}),
                    laterPeriodsKept=p3['states'][1:] == p2['states'] and p3['geometryPeriods'][1:] == p2['geometryPeriods'],
                    priorEvidenceKept=p3['evidence'][:len(p2['evidence'])] == p2['evidence'], priorLinksKept=p3['sourceLinks'][:len(p2['sourceLinks'])] == p2['sourceLinks']),
    afterSha256=hashlib.sha256(Path('dist/assets/temporal-objects.json.gz').read_bytes()).hexdigest())
links = {}
for o in after['objects']:
    for l in o['sourceLinks']:
        if 'sourceVertexRange' not in l: links.setdefault((l['datasetId'], l['featureId']), []).append(o['id'])
audit['newWholeLinkDuplicates'] = sorted(k[1] for k, v in links.items() if len(v) > 1 and set(v) & (NEW | {Q2, Q3}))
(R / 'scope-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=1) + '\n'); print(json.dumps(audit, ensure_ascii=False))
assert set(audit['addedObjects']) == NEW and changed == sorted([Q2, Q3]) and not audit['removedObjects'] and not audit['changedGeometries'] and audit['cityStagesUnchanged']
assert all(g.startswith('geometry:lemlandsvagen-split:') for g in audit['addedGeometries']) and not audit['newWholeLinkDuplicates']
assert not audit['target']['otherFieldsChanged'] and audit['target']['statesUnchanged'] and audit['target']['priorEvidenceKept'] and audit['target']['periodsOnlyGeometryIdChanged']
assert not audit['pairedLane']['otherFieldsChanged'] and all(audit['pairedLane'][k] for k in ['laterPeriodsKept', 'priorEvidenceKept', 'priorLinksKept'])
