"""Create a bounded modern land mask from OSM's land-on-the-left coastlines.
Requires shapely 2.x. Not used for historical shorelines.
"""
import json,math
from pathlib import Path
from shapely.geometry import LineString,box,Point,mapping
from shapely.ops import unary_union,polygonize
from shapely.strtree import STRtree
raw=json.loads(Path('data/mariehamn-coast.json').read_text())
bbox=[19.86,59.98,20.12,60.15];clip=box(*bbox)
lines=[LineString([(p['lon'],p['lat']) for p in e['geometry']]) for e in raw['elements']]
polys=list(polygonize(unary_union([clip.boundary]+[line.intersection(clip) for line in lines])))
tree=STRtree(polys);land=set()
for line in lines:
 for (ax,ay),(bx,by) in zip(line.coords,list(line.coords)[1:]):
  dx,dy=bx-ax,by-ay;length=math.hypot(dx,dy)
  if not length:continue
  p=Point((ax+bx)/2-dy/length*1e-7,(ay+by)/2+dx/length*1e-7)
  if not clip.contains(p):continue
  for i in tree.query(p,predicate='within'):land.add(int(i))
geom=unary_union([polys[i] for i in land])
assert geom.contains(Point(19.941,60.103)), 'City center must be land'
assert not geom.contains(Point(19.925,60.092)), 'Western harbour must be water'
assert not geom.contains(Point(19.966,60.096)), 'Eastern harbour must be water'
obj={'bbox':bbox,'source':'© OpenStreetMap contributors','license':'ODbL 1.0','snapshot':raw['osm3s']['timestamp_osm_base'],'geometry':mapping(geom)}
Path('dist/assets/coast.json').write_text(json.dumps(obj,separators=(',',':')))
print('Coast polygons:',len(polys),'land polygons:',len(land),'bytes:',Path('dist/assets/coast.json').stat().st_size)
