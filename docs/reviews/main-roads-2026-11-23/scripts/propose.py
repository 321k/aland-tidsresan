"""Proposed ranges from match_editions output: the first edition's ranges with gaps up to GAP m bridged and runs under
STUB m dropped; a later stage from the next edition (before the object's first year) when it adds at least MORE m.
Usage: propose.py MATCH.json OUT.json"""
import sys, json
GAP, STUB, MORE = 100, 150, 200
def clean(rs):
    out = []
    for a, b in rs:
        if out and a - out[-1][1] <= GAP: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return [r for r in out if r[1] - r[0] >= STUB]
m = json.load(open(sys.argv[1])); res = {}
for oid, v in m.items():
    eds = v['editions']
    if not eds or v['paths'] != 1: continue
    r0 = clean(eds[0][0]['ranges']); y0 = min(y for y, _ in eds[0][0]['editions']) if eds[0][0]['editions'] else None
    if not r0: continue
    p = dict(name=v['name'], firstYear=v['firstYear'], length=eds[0][0]['length'], year0=y0, ranges=r0, sheets0=sorted({s for _, s in eds[0][0]['editions']}))
    for e in eds[1:]:
        r1 = clean(e[0]['ranges']); y1 = min(y for y, _ in e[0]['editions']) if e[0]['editions'] else None
        r1 = clean(sorted(r0 + r1))           # a road the first edition draws is still there; the later edition adds to it
        if y1 and y1 < v['firstYear'] and sum(b - a for a, b in r1) - sum(b - a for a, b in r0) >= MORE:
            p['later'] = dict(year=y1, ranges=r1, sheets=sorted({s for _, s in e[0]['editions']})); break
    res[oid] = p
    print(f"{oid[-36:]:36s} {v['firstYear']} len {p['length']:7.0f}  {y0}: {r0}  {('later '+str(p['later']['year'])+': '+str(p['later']['ranges'])) if 'later' in p else ''}")
json.dump(res, open(sys.argv[2], 'w'), indent=1, ensure_ascii=False)
