import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_modern import build, join_rings

def geom(points): return [{'lon': x, 'lat': y} for x, y in points]
def way(id, points, **tags): return {'type': 'way', 'id': id, 'tags': tags, 'geometry': geom(points)}
def raw(*elements): return {'elements': list(elements), 'osm3s': {'timestamp_osm_base': '2026-10-11T20:21:06Z'}}

class ModernImport(unittest.TestCase):
    def test_joins_reversed_members_but_does_not_invent_closing_edges(self):
        self.assertEqual(join_rings([[[0,0],[1,0]],[[1,1],[1,0]],[[1,1],[0,0]]]), [[[0,0],[1,0],[1,1],[0,0]]])
        self.assertEqual(join_rings([[[0,0],[1,0]],[[1,1],[0,0]]]), [])
    def test_multipolygon_preserves_courtyard_and_deduplicates_outer_way(self):
        outer=[[0,0],[4,0],[4,4],[0,4],[0,0]];inner=[[1,1],[2,1],[2,2],[1,2],[1,1]]
        relation={'type':'relation','id':9,'tags':{'building':'yes','type':'multipolygon'},'members':[{'type':'way','ref':1,'role':'outer','geometry':geom(outer)},{'type':'way','ref':2,'role':'inner','geometry':geom(inner)}]}
        result=build(raw(way(1,outer,building='yes'),relation))
        self.assertEqual(len(result['features']),1)
        self.assertEqual(result['features'][0]['paths'],[outer,inner])
    def test_excludes_planned_roads_and_invalid_open_building_contours(self):
        result=build(raw(way(1,[[0,0],[1,1]],highway='construction'),way(2,[[0,0],[1,1]],building='yes'),way(3,[[0,0],[1,1]],highway='path')))
        self.assertEqual([f['id'] for f in result['features']],['way/3'])

if __name__ == '__main__': unittest.main()
