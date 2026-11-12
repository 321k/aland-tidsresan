"""Label candidate persistent road objects along a 1942 approach trace on the 1942 orthophoto (read-only).
Usage: label.py KEY 'Trace name' [radius_m]"""
import json,gzip,sys,colorsys
from pathlib import Path
from PIL import Image,ImageDraw
from pyproj import Transformer
from shapely.geometry import LineString
sys.path.insert(0,'scripts')
from postwar_city import METRIC
P=Path('data/map-scan-cache/review/trace-1942');span=512;res=2.0
key,name=sys.argv[1],sys.argv[2];R=float(sys.argv[3]) if len(sys.argv)>3 else 45
r=lambda p:json.loads(gzip.decompress(open(p,'rb').read()) if p.endswith('.gz') else open(p,'rb').read())
toE=Transformer.from_crs(4326,3874,always_xy=True).transform
d=json.load(open('data/historical-road-traces.json'))['sets'][3];ref=d['reference']
f=next(x for x in d['features'] if x['name']==name);pts=[(ref['west']+x*4,ref['north']-y*4) for x,y in f['pixels']]
trace=LineString(pts)
c=r('dist/assets/temporal-objects.json.gz');geoms={g['id']:g for g in c['geometries']}
cands=[]
for o in c['objects']:
  if o.get('kind')!='roadSegment':continue
  gp=o['geometryPeriods'][-1];g=geoms.get(gp['geometryId'])
  if not g:continue
  for path in g['paths']:
    L=LineString([toE(*p) for p in path])
    if L.length>5 and L.intersection(trace.buffer(R)).length>min(25,L.length*.5):
      cands.append((trace.project(L.interpolate(.5,normalized=True)),o,[toE(*p) for p in path]));break
cands.sort(key=lambda t:t[0])
e0=min(p[0] for p in pts)-200;e1=max(p[0] for p in pts)+200;n0=min(p[1] for p in pts)-150;n1=max(p[1] for p in pts)+150
a,b,cc,dd=int(e0//span),int(e1//span),int(n0//span),int(n1//span)
im=Image.new('RGB',((b-a+1)*256,(dd-cc+1)*256))
for x in range(a,b+1):
  for y in range(cc,dd+1): im.paste(Image.open(P/'tiles'/f'aerial-1942-16-{x}-{y}.png').convert('RGB'),((x-a)*256,(dd-y)*256))
px=lambda e,n:((e-a*span)/res,((dd+1)*span-n)/res)
plain=im.copy();dr=ImageDraw.Draw(im);legend=[]
for i,(pos,o,path) in enumerate(cands):
  col=tuple(int(255*v) for v in colorsys.hsv_to_rgb((i*0.137)%1,1,1))
  xy=[px(*p) for p in path];dr.line(xy,fill=col,width=2);mx,my=xy[len(xy)//2];dr.text((mx+4,my),str(i),fill=col,stroke_width=2,stroke_fill='black')
  first=min(s['from'] for s in o['states'] if s['state']=='open');legend.append(dict(n=i,objectId=o['id'],name=o.get('name'),firstOpen=first,alongMeters=round(pos)))
dr.line([px(*p) for p in pts],fill=(255,255,255),width=1)
im=im.resize((im.width*2,im.height*2));plain=plain.resize((plain.width*2,plain.height*2),Image.LANCZOS)
H=1100;n=0
for y0 in range(0,im.height,H-100):
  o=Image.new('RGB',(im.width*2+8,min(H,im.height-y0)),'white');o.paste(im.crop((0,y0,im.width,y0+H)),(0,0));o.paste(plain.crop((0,y0,plain.width,y0+H)),(im.width+8,0))
  o.save(P/f'{key}-label-{n}.jpg',quality=88);n+=1
(P/f'{key}-label.json').write_text(json.dumps(legend,ensure_ascii=False,indent=1));print(n,'sheets');[print(l) for l in legend]
