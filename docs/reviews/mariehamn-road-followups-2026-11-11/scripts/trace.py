"""Trace the red road fill centre on an original-scan review crop and convert to WGS84.
Usage: trace.py CROPKEY YEAR axis(v|h) lo hi step  win0 win1   (crop-pixel coordinates in the scaled crop)
v: for rows lo..hi find red run centre in columns win0..win1; h: for columns lo..hi find centre in rows win0..win1."""
import sys,json,gzip,numpy as np
from pathlib import Path
from PIL import Image
from pyproj import Transformer
sys.path.insert(0,'scripts')
from historical_map_observations import load_review,MERCATOR
from rural_registration import registration_pair
r=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
P=Path('data/map-scan-cache/review/mariehamn-major-roads/followups')
key,year=sys.argv[1],int(sys.argv[2]);axis=sys.argv[3];lo,hi,step,w0,w1=map(int,sys.argv[4:9])
meta=json.loads((P/f'{key}-{year}.json').read_text());x0,y0=meta['box'][:2];s=meta['scale']
if year<1995:
 _,regs=load_review(r);sheet,convert,_=regs[f'nls-mariehamn-{year}'];tolon=lambda px,py:tuple(convert(np.array([[px,py]]))[0])
else:
 sheet=next(q for q in r('data/rural-map-review.json')['sources'] if q['id']=='nls:101208:1995');fwd,inv=registration_pair(sheet);back=Transformer.from_crs(sheet['registration']['crs'],4326,always_xy=True).transform;tolon=lambda px,py:back(*fwd((px,py)))
a=np.asarray(Image.open(P/f'{key}-{year}.png').convert('RGB')).astype(int)
red=(a[...,0]>190)&(a[...,1]<150)&(a[...,2]<140)
pts=[]
for t in range(lo,hi+1,step):
 line=red[t,w0:w1] if axis=='v' else red[w0:w1,t]
 idx=np.nonzero(line)[0]
 if len(idx)<4:continue
 # longest contiguous run
 runs=np.split(idx,np.nonzero(np.diff(idx)>2)[0]+1);run=max(runs,key=len);c=w0+(run[0]+run[-1])/2
 px,py=(c,t) if axis=='v' else (t,c)
 lon,lat=tolon(x0+px/s,y0+py/s);pts.append([round(lon,7),round(lat,7),len(run)])
print(json.dumps(pts))
