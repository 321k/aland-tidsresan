"""Scope audit for the 1942 approach review: rebuild with the step disabled and compare."""
import gzip, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
import build_temporal_objects, mariehamn_approaches_1942 as step
R = Path('data/map-scan-cache/review/trace-1942')
after = json.load(gzip.open('dist/assets/temporal-objects.json.gz')); snapshot = json.load(gzip.open(R / 'before.json.gz'))
real = step.apply_approaches_1942; step.apply_approaches_1942 = lambda read, catalog: None
before = json.loads(json.dumps(build_temporal_objects.compile_catalog(), ensure_ascii=False)); step.apply_approaches_1942 = real
review = json.load(open('data/mariehamn-approaches-1942.json'))
members = {m['objectId'] for a in review['approaches'] for m in a['members']}
bo = {o['id']: o for o in before['objects']}; ao = {o['id']: o for o in after['objects']}
changed = sorted(i for i in bo if bo[i] != ao.get(i))
kept = all(ao[i]['states'][1:] == bo[i]['states'] and ao[i]['geometryPeriods'][1:] == bo[i]['geometryPeriods']
           and ao[i]['evidence'][:len(bo[i]['evidence'])] == bo[i]['evidence'] and ao[i]['sourceLinks'][:len(bo[i]['sourceLinks'])] == bo[i]['sourceLinks'] for i in members)
bs = {s['id']: s for s in before['cityStages']}; as_ = {s['id']: s for s in after['cityStages']}
stage_changes = {}
for sid in bs:
    bf = {f['id']: f for f in bs[sid]['features']}; af = {f['id']: f for f in as_[sid]['features']}
    removed = sorted(set(bf) - set(af)); added = sorted(set(af) - set(bf)); mod = sorted(i for i in bf if i in af and bf[i] != af[i])
    if removed or added or mod:
        stage_changes[sid] = dict(removed=removed, added=len(added), modified=mod)
trace_ids = {t['traceId'] for t in review['rejected'] + review['approaches']}
audit = dict(
    snapshotEqualsBaseline=snapshot == before, objects=[len(bo), len(ao)], geometries=[len(before['geometries']), len(after['geometries'])],
    changedObjects=len(changed), changedObjectsAreMembers=set(changed) == members, earlierRecordsKept=kept,
    geometriesUnchanged=before['geometries'] == after['geometries'],
    sourcesAdded=sorted({s['id'] for s in after['sources']} - {s['id'] for s in before['sources']}),
    stageChanges=stage_changes,
    removedStageFeaturesAreTraces=all(next(f for f in bs[sid]['features'] if f['id'] == fid).get('traceId') in trace_ids
                                      for sid, ch in stage_changes.items() for fid in ch['removed']),
    otherTopLevelChanged=sorted(k for k in set(before) | set(after) if k not in ['objects', 'sources', 'cityStages', 'recordedAt'] and before.get(k) != after.get(k)),
    afterSha256=hashlib.sha256(Path('dist/assets/temporal-objects.json.gz').read_bytes()).hexdigest())
(R / 'scope-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=1) + '\n'); print(json.dumps(audit, ensure_ascii=False)[:1500])
assert audit['changedObjectsAreMembers'] and kept and audit['geometriesUnchanged'] and audit['removedStageFeaturesAreTraces'] and not audit['otherTopLevelChanged']
assert audit['sourcesAdded'] == ['review:mariehamn-approaches-1942'] and all(not ch['modified'] for ch in stage_changes.values())
