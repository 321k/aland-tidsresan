"""Follow a pale road centre on the 1942 orthophoto near a rough guide line (read-only).
Usage: ridge.py KEY 'x0,y0;x1,y1;...' (guide in crop-display pixels of KEY.jpg). Writes KEY-ridge.json/.jpg."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
P=Path('data/map-scan-cache/review/trace-1942');key=sys.argv[1]
guide=np.array([[float(v) for v in p.split(',')] for p in sys.argv[2].split(';')])
meta=json.load(open(P/f'{key}.json'));im=Image.open(P/f'{key}.jpg').convert('L').filter(ImageFilter.GaussianBlur(3));a=np.asarray(im,dtype=float)
W=int(sys.argv[3]) if len(sys.argv)>3 else 24
pts=[]
# sample along the guide every ~12 px, search perpendicular to the guide for the brightest pixel
segs=list(zip(guide[:-1],guide[1:]))
for p,q in segs:
  d=q-p;L=np.hypot(*d);t=d/L;nrm=np.array([-t[1],t[0]])
  for s in np.arange(0,L,12):
    c=p+t*s;best=None
    for o in range(-W,W+1):
      x,y=(c+nrm*o).round().astype(int)
      if 0<=x<a.shape[1] and 0<=y<a.shape[0]:
        v=a[y,x]
        if best is None or v>best[0]:best=(v,x,y)
    pts.append(best[1:])
pts.append(tuple(guide[-1].astype(int)))
# light smoothing of the picked centre line
arr=np.array(pts,dtype=float);sm=arr.copy();sm[1:-1]=(arr[:-2]+2*arr[1:-1]+arr[2:])/4
col=Image.open(P/f'{key}.jpg').convert('RGB');dr=ImageDraw.Draw(col)
dr.line([tuple(p) for p in guide],fill=(0,160,255),width=1);dr.line([tuple(p) for p in sm],fill=(255,0,0),width=2)
col.save(P/f'{key}-ridge.jpg',quality=90)
S,res=meta['S'],meta['res'];geo=[[meta['e0']+x/S*res,meta['n1']-y/S*res] for x,y in sm]
json.dump(dict(displayPixels=sm.round(1).tolist(),epsg3874=[[round(e,2),round(n,2)] for e,n in geo],guide=guide.tolist()),open(P/f'{key}-ridge.json','w'));print(len(sm),'points')
