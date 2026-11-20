"""Keep Mariehamn's blocks beige through the 1920s stages (1920–1941).

The 1871 reconstruction stage draws the town plan's blocks. The 1920 and 1927 stages take their blocks only from the
street lines of the 1920s museum map that close a loop. Where they do not close (for example north of Norra
Esplanadgatan, where Mariegatan is not drawn), about ten blocks showed as bare green land from 1920 until the 1942
stage draws them again, although nothing says the blocks went away.

This step carries block fill into every city stage that starts in 1920–1941: the part of the 1871 stage's blocks that
the 1942 stage also covers with blocks (so only blocks drawn on both sides of the gap are carried), minus the stage's
own blocks, parks and squares (+1 m, so nothing is drawn twice) and minus 4 m around the stage's streets, as the
derived blocks are. Pieces under 150 m² are dropped. No objects are created or changed. The fill is an interpretation
of block extent, not evidence of individual houses. Same method as scripts/mariehamn_blocks_1985.py.
`data/mariehamn-blocks-1920.json` pins the stages, their block digests and the expected area; anything else is
rejected before a change.
"""
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
from mariehamn_frame_1942 import digest, TO_METRIC, TO_GEO
from mariehamn_blocks_1985 import _parts, _ring


def _area(stage, kinds):
    return unary_union([Polygon([TO_METRIC(*p) for p in path]).buffer(0) for f in stage['features'] if f['kind'] in kinds
                        for path in f['paths'][:1] if len(path) >= 3])


def apply_blocks_1920(read, catalog):
    review = read('data/mariehamn-blocks-1920.json')
    stages = {s['id']: s for s in catalog['cityStages']}
    if review['schemaVersion'] != 1:
        raise ValueError('Unknown block review version')
    ends = {}
    for k in ('before', 'after'):
        s = stages.get(review[k]['stageId'])
        blocks = sorted([f['paths'] for f in s['features'] if f['kind'] == 'block']) if s else None
        if not s or digest(blocks) != review[k]['blocksHash']:
            raise ValueError('Changed stage ' + review[k]['stageId'])
        ends[k] = _area(s, ('block',))
    persistent = ends['before'].intersection(ends['after'])
    gap = [s for s in catalog['cityStages'] if review['carryFrom'] <= s['from'] <= review['carryThrough']]
    if sorted(s['id'] for s in gap) != sorted(review['stageIds']):
        raise ValueError('Unexpected city stages for carried blocks')
    plans = []
    for s in gap:
        if any(f.get('carriedBlock') for f in s['features']):
            raise ValueError('Stage already has carried blocks: ' + s['id'])
        own = _area(s, ('block', 'park', 'square'))
        streets = unary_union([LineString([TO_METRIC(*p) for p in path]) for f in s['features'] if f['kind'] == 'street'
                               for path in f['paths'] if len(path) > 1])
        cut = unary_union([own.buffer(1), streets.buffer(review['streetMarginMeters'])])
        pieces = [p for p in _parts(persistent.difference(cut)) if p.area >= review['minPieceSquareMeters']]
        plans.append((s, pieces))
    for s, pieces in plans:
        total = sum(p.area for p in pieces)
        want = review['expectedSquareMeters'][s['id']]
        if not want * 0.9 <= total <= want * 1.1:
            raise ValueError(f"Unexpected carried block area in {s['id']}: {round(total)} m²")

    # All checks passed. Change the stages.
    for s, pieces in plans:
        for n, p in enumerate(pieces):
            s['features'].insert(0, dict(id=f"{s['id']}:carried-block:{n}", kind='block', name='Kvarter (stadsplanens kvarter 1871–1942)',
                                         carriedBlock=review['before']['stageId'], note=review['note'],
                                         paths=[_ring(p.exterior.coords), *[_ring(r.coords) for r in p.interiors]]))
        s['counts']['carriedBlocks'] = len(pieces)
    catalog['recordedAt'] = max(catalog['recordedAt'], review['reviewedAt'])
