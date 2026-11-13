"""Scope audit of the 1942 frame review: catalogue vs the pre-step snapshot and vs the previous publication."""
import gzip, json, hashlib, sys
r = lambda p: json.loads(gzip.decompress(open(p, 'rb').read()))
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
snap_p, cat_p, live_p = sys.argv[1:4]
before, after, live = r(snap_p), r(cat_p), r(live_p)
review = json.load(open('data/mariehamn-frame-1942.json'))
members = {m['objectId'] for t in review['traces'] for m in t['members']}
def changed(a, b):
    A = {o['id']: o for o in a['objects']}; B = {o['id']: o for o in b['objects']}
    assert A.keys() == B.keys()
    return {i for i in A if A[i] != B[i]}
def stage_diff(a, b):
    out = {}
    for sa, sb in zip(a['cityStages'], b['cityStages']):
        assert sa['id'] == sb['id']
        fa = {f['id']: f for f in sa['features']}; fb = {f['id']: f for f in sb['features']}
        rem = sorted(set(fa) - set(fb)); add = sorted(set(fb) - set(fa)); mod = sorted(i for i in set(fa) & set(fb) if fa[i] != fb[i])
        if rem or add or mod:
            out[sa['id']] = dict(removed=len(rem), removedAllReviewedTraceCopies=all(fa[i].get('traceId') in {t['traceId'] for t in review['traces']} and not fa[i].get('objectId') for i in rem),
                                 added=len(add), addedFrameOnly=all(':frame-' in i for i in add), modified=len(mod))
    return out
c1 = changed(before, after); c2 = changed(live, after)
keys = lambda a, b: sorted(k for k in set(a) | set(b) if k not in ('objects', 'cityStages', 'sources', 'recordedAt') and a.get(k) != b.get(k))
G = lambda c: {g['id']: g for g in c['geometries']}
print(json.dumps(dict(
    snapshotSha256=sha(snap_p), catalogueSha256=sha(cat_p), previousPublicationSha256=sha(live_p),
    vsSnapshot=dict(changedObjects=len(c1), changedEqualsMembers=c1 == members, geometriesUnchanged=G(before) == G(after),
                    otherTopLevelKeysChanged=keys(before, after),
                    addedSources=sorted({s['id'] for s in after['sources']} - {s['id'] for s in before['sources']}), stages=stage_diff(before, after)),
    vsPreviousPublication=dict(changedObjects=len(c2), changedEqualsMembers=c2 == members, geometriesUnchanged=G(live) == G(after),
                               addedSources=sorted({s['id'] for s in after['sources']} - {s['id'] for s in live['sources']}), stages=stage_diff(live, after)),
), indent=1, ensure_ascii=False))
