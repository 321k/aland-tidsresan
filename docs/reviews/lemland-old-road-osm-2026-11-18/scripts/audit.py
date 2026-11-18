"""Scope audit: the catalogue before and after this review. Usage: audit.py BEFORE.json.gz AFTER.json.gz OUT.json"""
import json, gzip, sys
a, b = (json.load(gzip.open(p)) for p in sys.argv[1:3])
def diff(key):
    A = {x['id']: x for x in a[key]}; B = {x['id']: x for x in b[key]}
    return dict(added=sorted(set(B) - set(A)), removed=sorted(set(A) - set(B)), changed=sorted(i for i in set(A) & set(B) if A[i] != B[i]))
out = {k: diff(k) for k in ('objects', 'geometries', 'sources')}
out['cityStagesUnchanged'] = a['cityStages'] == b['cityStages']
out['otherTopLevelUnchanged'] = all(a[k] == b[k] for k in a if k not in ('objects', 'geometries', 'sources', 'cityStages', 'recordedAt'))
out['recordedAt'] = [a['recordedAt'], b['recordedAt']]
json.dump(out, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: {kk: len(vv) for kk, vv in v.items()} if isinstance(v, dict) else v for k, v in out.items()}))
