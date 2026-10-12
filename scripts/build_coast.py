"""Create a bounded modern land mask from OSM's land-on-the-left coastlines.
Requires shapely 2.x. Not used for historical shorelines.
"""
import json,gzip
import numpy as np
import shapely
from pathlib import Path
from shapely.geometry import LineString,box,Point,mapping
from shapely.ops import unary_union,polygonize
from shapely.strtree import STRtree
raw=json.loads(gzip.decompress(Path('data/aland-coast.json.gz').read_bytes()))
bbox=[19.2,59.65,21.4,60.65];clip=box(*bbox)
lines=[LineString([(p['lon'],p['lat']) for p in e['geometry']]) for e in raw['elements']]
polys=list(polygonize(unary_union([clip.boundary]+[line.intersection(clip) for line in lines])))
tree=STRtree(polys);land=set()
for line in lines:
 coords=np.asarray(line.coords);a=coords[:-1];b=coords[1:];delta=b-a
 lengths=np.linalg.norm(delta,axis=1);valid=lengths>0
 delta=delta[valid];lengths=lengths[valid]
 offsets=np.column_stack((-delta[:,1],delta[:,0]))/lengths[:,None]*1e-7
 samples=shapely.points((a[valid]+b[valid])/2+offsets)
 # Vectorized lookup preserves every segment's orientation, including clipped shores.
 hits=tree.query(samples,predicate='within')
 land.update(int(i) for i in np.unique(hits[1]))
geom=unary_union([polys[i] for i in land])
assert geom.contains(Point(19.941,60.103)), 'City center must be land'
assert not geom.contains(Point(19.925,60.092)), 'Western harbour must be water'
assert not geom.contains(Point(19.966,60.096)), 'Eastern harbour must be water'
# Rural mainland, southern archipelago and eastern archipelago must remain land.
# Exact OSM settlement points from the same extract, not guessed coast positions.
for lon,lat in [(19.9880463,60.2298728),(20.3918676,60.030109),(20.9059414,59.9211442),(21.0440498,60.4135873)]:
 assert geom.contains(Point(lon,lat)), f'Missing land at {lon},{lat}'
obj={'bbox':bbox,'source':'© OpenStreetMap contributors','license':'ODbL 1.0','snapshot':raw['osm3s']['timestamp_osm_base'],'geometry':mapping(geom),'overview':mapping(geom.simplify(0.0001,preserve_topology=True))}
Path('dist/assets/coast.json.gz').write_bytes(gzip.compress(json.dumps(obj,separators=(',',':')).encode(),mtime=0))
print('Coast polygons:',len(polys),'land polygons:',len(land),'bytes:',Path('dist/assets/coast.json.gz').stat().st_size)
