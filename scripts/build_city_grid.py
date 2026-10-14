"""Build traceable vector streets, street blocks and map symbols for Mariehamn.
Input pixels stay in data/mariehamn-city-traces.json for review. Dependencies:
numpy, pyproj, shapely. No historical building geometry is taken from modern OSM.
"""
import json,gzip,copy
from pathlib import Path
import numpy as np
from pyproj import Transformer
from shapely.geometry import LineString,Polygon,box,Point
from shapely.ops import unary_union,polygonize,transform
root=Path(__file__).resolve().parents[1]
doc=json.loads((root/'data/mariehamn-city-traces.json').read_text())
fwd=Transformer.from_crs(4326,3874,always_xy=True).transform
inv=Transformer.from_crs(3874,4326,always_xy=True).transform
clip=transform(fwd,box(*doc['coverage']))

def coords(points):return [[round(x,7),round(y,7)] for x,y in map(lambda p:inv(*p),points)]
def polygon_paths(p):return [coords(p.exterior.coords)]+[coords(r.coords) for r in p.interiors]
def parts(g,typ):
 if g.is_empty:return []
 if g.geom_type==typ:return [g]
 return [p for p in getattr(g,'geoms',[]) if p.geom_type==typ]
def build(ds,roads,areas,buildings):
 features=[];lines=[r[1] for r in roads]
 # Noding intersections makes the street grid a connected planar network.
 network=unary_union(lines);edges=parts(network,'LineString')
 nodes=set();adj={}
 for edge in edges:
  a,b=[tuple(round(v,3) for v in p) for p in [edge.coords[0],edge.coords[-1]]];nodes.update([a,b]);adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
 seen=set();components=0
 for a in nodes:
  if a in seen:continue
  components+=1;stack=[a]
  while stack:
   n=stack.pop()
   if n in seen:continue
   seen.add(n);stack.extend(adj.get(n,())-seen)
 parks=unary_union([p for _,p in areas])
 for i,p in enumerate(polygonize(network)):
  if p.area<250 or p.area>180000:continue
  for inner in parts(p.buffer(-4).difference(parks),'Polygon'):
   if inner.area<150:continue
   features.append({'id':ds['id']+'-block-'+str(len(features)), 'kind':'block','name':'Planerat kvarter' if ds['kind']=='plan' else 'Kvarter mellan gatorna','paths':polygon_paths(inner)})
 for f,p in areas:features.append({'id':ds['id']+'-area-'+str(len(features)),**f,'paths':polygon_paths(p)})
 for i,p in enumerate(buildings):features.append({'id':ds['id']+'-house-'+str(i),'kind':'building','name':'Hussymbol på museikartan','paths':polygon_paths(p)})
 # Render source polylines, keep their IDs and names; noded graph is diagnostics.
 if ds['kind']!='modern':
  for i,(f,line) in enumerate(roads):features.append({'id':ds['id']+'-street-'+str(i),'kind':'street','name':f['name'],'width':f.get('width',9),'paths':[coords(line.coords)]})
 ds['features']=features;ds['counts']={'streets':len(roads),'blocks':sum(f['kind']=='block' for f in features),'buildings':len(buildings),'parks':len(areas)}
 ds['topology']={'nodes':len(nodes),'edges':len(edges),'components':components}
 return ds
sets=[]
for raw in doc['sets']:
 ds={k:copy.deepcopy(v) for k,v in raw.items() if k not in ['roads','areas','buildings','anchors','reference']}
 if 'anchors' in raw:
  A=np.array([[*a['pixel'],1] for a in raw['anchors']]);B=np.array([fwd(*a['geo']) for a in raw['anchors']]);M=np.linalg.solve(A,B)
  def convert(p):return np.array([[*v,1] for v in p])@M
 else:
  ref=raw['reference']
  def convert(p):return [(ref['west']+x*ref['metersPerViewPixel'],ref['north']-y*ref['metersPerViewPixel']) for x,y in p]
 roads=[(r,LineString(convert(r['pixels']))) for r in raw['roads']]
 areas=[({k:v for k,v in a.items() if k!='pixels'},Polygon(convert(a['pixels']))) for a in raw['areas']]
 buildings=[Polygon(convert(b['pixels'])) for b in raw.get('buildings',[])]
 sets.append(build(ds,roads,areas,buildings))
for year in [2014,2021,2025,2026]:
 file=root/f'dist/assets/roads-{year}.json.gz' if year<2026 else root/'dist/assets/modern.json.gz'
 data=json.loads(gzip.decompress(file.read_bytes()));roads=[]
 for f in data['features']:
  if year==2026 and f.get('kind')!='road':continue
  if f.get('class') not in ['residential','living_street','unclassified','tertiary','secondary','primary','road','pedestrian']:continue
  for path in f['paths']:
   line=LineString([fwd(*p) for p in path]);
   if not line.intersects(clip):continue
   for part in parts(line.intersection(clip),'LineString'):roads.append((f,part))
 ds={'id':'city-'+str(year),'year':year,'kind':'modern','name':'Mariehamns gatunät · '+str(year),'source':'https://www.openstreetmap.org/copyright','note':'Gator från OpenStreetMap '+str(year)+'. Kvarteren har härletts mellan kartlagda gator och är inte fastighetsgränser. Skillnader mellan källåren kan bero på både ombyggnad och bättre kartläggning. Huslagret använder separata, daterade kartuttag och källbelagda husplatser.','snapshot':data.get('snapshot')}
 sets.append(build(ds,roads,[],[]))
for i,d in enumerate(sets):d['from']=d['year'];d['through']=sets[i+1]['year']-1 if i<len(sets)-1 else 2026
out={'policy':doc['policy'],'coverage':doc['coverage'],'sets':sets}
(root/'dist/assets/mariehamn-city-grid.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
print([(s['id'],s['counts'],s['topology']) for s in sets])
