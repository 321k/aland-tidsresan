"""Retrace a visible 1942 road between two object ends as a least-cost path over the orthophoto (read-only).
The road surface is paler than the forest and fields around it; the path follows the continuous pale strip.
Usage: retrace.py KEY E0 N0 E1 N1 CORRIDOR_M   (EPSG:3874). Writes KEY.json (EPSG:3874 points) and KEY.jpg."""
import heapq,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from shapely.geometry import LineString,Point
P=Path('data/map-scan-cache/review/trace-1942');span=512;res=2.0
key=sys.argv[1];e0,n0,e1,n1,corr=map(float,sys.argv[2:7])
m=corr+20;E0,E1=min(e0,e1)-m,max(e0,e1)+m;N0,N1=min(n0,n1)-m,max(n0,n1)+m
a,b,c,d=int(E0//span),int(E1//span),int(N0//span),int(N1//span)
mos=Image.new('RGB',((b-a+1)*256,(d-c+1)*256))
for x in range(a,b+1):
  for y in range(c,d+1): mos.paste(Image.open(P/'tiles'/f'aerial-1942-16-{x}-{y}.png').convert('RGB'),((x-a)*256,(d-y)*256))
topx=lambda e,n:((e-a*span)/res,((d+1)*span-n)/res);toE=lambda x,y:(a*span+x*res,(d+1)*span-y*res)
L=np.asarray(mos.convert('L').filter(ImageFilter.GaussianBlur(1.2)),dtype=float)/255
H,W=L.shape;sx,sy=map(int,map(round,topx(e0,n0)));tx,ty=map(int,map(round,topx(e1,n1)))
axis=LineString([(sx,sy),(tx,ty)])
# relative brightness: compare with the local mean so cloud shadows and fields do not dominate
from scipy.ndimage import uniform_filter
rel=L-uniform_filter(L,15)
cost=np.exp(-12*rel)+0.05
inside=np.zeros_like(L,dtype=bool)
yy,xx=np.mgrid[0:H,0:W]
for y0 in range(0,H,64):
  for x0 in range(0,W,64):
    pass
dist=np.full(L.shape,np.inf);dist[sy,sx]=0;prev={};pq=[(0.0,sy,sx)];lim=corr/res
def ok(y,x): return 0<=y<H and 0<=x<W and axis.distance(Point(x,y))<=lim
okc={}
while pq:
  dd,y,x=heapq.heappop(pq)
  if (y,x)==(ty,tx):break
  if dd>dist[y,x]:continue
  for dy,dx,w in ((1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)):
    ny,nx=y+dy,x+dx
    k=(ny,nx)
    if k not in okc: okc[k]=ok(ny,nx)
    if not okc[k]:continue
    nd=dd+w*cost[ny,nx]
    if nd<dist[ny,nx]:dist[ny,nx]=nd;prev[k]=(y,x);heapq.heappush(pq,(nd,ny,nx))
path=[(ty,tx)]
while path[-1]!=(sy,sx):path.append(prev[path[-1]])
path=path[::-1];line=LineString([(x,y) for y,x in path]).simplify(1.0)
pts=[toE(x,y) for x,y in line.coords];pts[0]=(e0,n0);pts[-1]=(e1,n1)
S=3;big=mos.resize((W*S,H*S),Image.LANCZOS);dr=ImageDraw.Draw(big)
dr.line([(topx(*p)[0]*S,topx(*p)[1]*S) for p in pts],fill=(255,0,0),width=2)
for p in [(e0,n0),(e1,n1)]:u,v=topx(*p);dr.ellipse([u*S-7,v*S-7,u*S+7,v*S+7],outline=(0,255,255),width=2)
xs=[topx(*p)[0]*S for p in pts];ys=[topx(*p)[1]*S for p in pts];box=(max(0,int(min(xs))-150),max(0,int(min(ys))-120),min(W*S,int(max(xs))+150),min(H*S,int(max(ys))+120))
plain=mos.resize((W*S,H*S),Image.LANCZOS).crop(box);ov=big.crop(box)
o=Image.new('RGB',(ov.width*2+8,ov.height),'white');o.paste(ov,(0,0));o.paste(plain,(ov.width+8,0));o.save(P/f'{key}.jpg',quality=88)
json.dump(dict(start=[e0,n0],end=[e1,n1],corridorMeters=corr,points=[[round(e,2),round(n,2)] for e,n in pts],method='Least-cost path over local relative brightness of the 1942 orthophoto at 2 m/px, simplified to 2 m.'),open(P/f'{key}.json','w'),indent=1)
print(key,len(pts),'points',round(LineString(pts).length,1),'m',o.size)
