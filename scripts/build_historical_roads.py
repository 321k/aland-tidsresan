"""Convert reviewable map-pixel traces to approximate geographic road lines."""
import json,math,copy
from pathlib import Path
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.optimize import root
from pyproj import Transformer
rootdir=Path(__file__).resolve().parents[1]
doc=json.loads((rootdir/'data/historical-road-traces.json').read_text());heritage={f['code']:f for f in json.loads((rootdir/'dist/assets/heritage.json').read_text())['features']}
merc=Transformer.from_crs(4326,3857,always_xy=True);inv=Transformer.from_crs(3857,4326,always_xy=True)
map1894=json.loads((rootdir/'dist/assets/historical-overlays.json').read_text())['readyOverlays'][0]['georeferencing'];coef=np.array(map1894['inversePolynomialCoefficientsPixelXY']);translation=np.array(map1894['translationPixels'])
def pixel1894(ll):
 x,y=ll[0]-20,ll[1]-60.25
 return np.array([1,x,y,x*y,x*x])@coef+translation
output=[]
for ds in doc['sets']:
 out={k:v for k,v in ds.items() if k not in ('features','anchors','reference','method')};out['features']=[]
 if ds['id']=='alvin-1800':
  ap=np.array([a['pixel'] for a in ds['anchors']],dtype=float);ag=np.array([merc.transform(heritage[a['code']]['lon'],heritage[a['code']]['lat']) for a in ds['anchors']]);rbf=RBFInterpolator(ap,ag,kernel='thin_plate_spline')
  def convert(points):return [inv.transform(*p) for p in rbf(np.array(points,dtype=float))]
  # Leave-one-out is diagnostic only: few hand-read symbols do not establish survey accuracy.
  errors=[]
  for i in range(len(ap)):
   keep=np.arange(len(ap))!=i;pred=RBFInterpolator(ap[keep],ag[keep],kernel='thin_plate_spline')(ap[i:i+1])[0];errors.append(float(np.linalg.norm(pred-ag[i])*math.cos(math.radians(60.2))))
  out['alignmentDiagnostics']={'churchLeaveOneOutGroundRmseMeters':round(float(np.sqrt(np.mean(np.square(errors))))),'note':'Hand-read registry correspondences, not surveyed independent control. Local errors may be larger.'}
 elif ds['id']=='atlas-1894':
  def convert(points):
   converted=[]
   for x,y in points:
    target=np.array([250+x/1.5,450+y/1.5]);fit=root(lambda ll:pixel1894(ll)-target,[20,60.25]);assert fit.success;converted.append(fit.x)
   return converted
 elif ds['id']=='museum-1920':
  A=np.array([[*a['pixel'],1] for a in ds['anchors']]);B=np.array([merc.transform(*a['geo']) for a in ds['anchors']]);M=np.linalg.solve(A,B)
  def convert(points):return [inv.transform(*p) for p in np.array([[*p,1] for p in points])@M]
 else:
  trans=Transformer.from_crs(3874,4326,always_xy=True);ref=ds['reference']
  def convert(points):return [trans.transform(ref['west']+x*4,ref['north']-y*4) for x,y in points]
 for f in ds['features']:
  coords=[[round(float(x),6),round(float(y),6)] for x,y in convert(f['pixels'])];mid=coords[len(coords)//2]
  out['features'].append({'id':f['id'],'name':f['name'],'class':f['class'],'paths':[coords],'lon':mid[0],'lat':mid[1]})
 output.append(out)
# Suppress the coarse regional interpretation inside the later city map's coverage.
# This avoids showing an inaccurate 1894 centreline across the finer city streets.
from shapely.geometry import LineString, box
museum=next(d for d in output if d['id']=='museum-1920')
points=[p for f in museum['features'] for path in f['paths'] for p in path]
city=box(min(p[0] for p in points)-.0005,min(p[1] for p in points)-.0003,max(p[0] for p in points)+.0005,max(p[1] for p in points)+.0003)
for d in output:
 if d['id']!='atlas-1894':continue
 for f in d['features']:
  clipped=LineString(f['paths'][0]).difference(city)
  lines=[] if clipped.is_empty else [clipped] if clipped.geom_type=='LineString' else list(clipped.geoms)
  f['pathsOutsideCity']=[[[round(x,6),round(y,6)] for x,y in line.coords] for line in lines if line.geom_type=='LineString']
(rootdir/'dist/assets/historical-roads.json').write_text(json.dumps({'policy':doc['policy'],'sets':output},ensure_ascii=False,separators=(',',':'))+'\n')
print([(x['id'],len(x['features']),x.get('alignmentDiagnostics')) for x in output])
