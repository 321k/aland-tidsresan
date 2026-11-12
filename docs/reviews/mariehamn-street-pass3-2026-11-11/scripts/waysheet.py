"""Per-street contact sheet from the original scans. One row per modern way:
1968 with the way outlined, then the unmarked 1968, 1978, 1985 and 1995 crops of the same ground area.
Read-only on sources. Usage: waysheet.py OUTKEY way/1 way/2 ...  (env MARGIN metres, PANEL px)"""
import sys,json,gzip,os,hashlib,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
from pyproj import Transformer
sys.path.insert(0,'scripts')
from historical_map_observations import load_review,MERCATOR
from rural_registration import registration_pair
r=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes());_,regs=load_review(r)
P=Path('data/map-scan-cache/review/mariehamn-major-roads/pass3');key=sys.argv[1];ways=sys.argv[2:]
MARGIN=float(os.environ.get('MARGIN','50'));PANEL=int(os.environ.get('PANEL','300'))
modern={f['id']:f for f in r('dist/assets/modern.json.gz')['features']}
px={};scans={};meta={}
for year in [1968,1978,1985,1995]:
 if year<1995:
  sheet,convert,_=regs[f'nls-mariehamn-{year}'];pix=np.array([[0,0,1],[1000,0,1],[0,1000,1]]);geo=np.array([MERCATOR(*p) for p in convert(pix[:,:2])]);mat=np.linalg.solve(pix,geo);inv=np.linalg.inv(mat[:2,:]);px[year]=(lambda inv,mat:lambda lon,lat:(np.array(MERCATOR(lon,lat))-mat[2,:])@inv)(inv,mat)
 else:
  sheet=next(s for s in r('data/rural-map-review.json')['sources'] if s['id']=='nls:101208:1995');fwd,inv=registration_pair(sheet);proj=Transformer.from_crs(4326,sheet['registration']['crs'],always_xy=True).transform;px[year]=lambda lon,lat,inv=inv,proj=proj:np.array(inv(proj(lon,lat)))
 raw=Path(f'data/map-scan-cache/101208_{year}.jpg');assert hashlib.sha256(raw.read_bytes()).hexdigest()==sheet['originalSha256'];scans[year]=Image.open(raw).convert('RGB');meta[year]=('nls:'+sheet['id'] if year<1995 else sheet['id'],sheet['originalSha256'])
rows=[];record=[]
for w in ways:
 f=modern[w];path=f['paths'][0];lons=[p[0] for p in path];lats=[p[1] for p in path]
 dl=MARGIN/55600;dt=MARGIN/111320;bbox=[min(lons)-dl,min(lats)-dt,max(lons)+dl,max(lats)+dt]
 cells=[];boxes={}
 for k,year in enumerate([1968,1968,1978,1985,1995]):
  pts=[px[year](x,y) for x in [bbox[0],bbox[2]] for y in [bbox[1],bbox[3]]];x0,y0=np.min(pts,axis=0).astype(int);x1,y1=np.max(pts,axis=0).astype(int)
  c=scans[year].crop((x0,y0,x1,y1));s=PANEL/max(c.width,c.height);c=c.resize((int(c.width*s),int(c.height*s)),Image.LANCZOS);boxes[year]=[int(x0),int(y0),int(x1),int(y1)]
  if k==0:
   d=ImageDraw.Draw(c);xy=[tuple((px[year](*q)-[x0,y0])*s) for q in path];d.line(xy,fill=(0,90,255),width=2)
  d=ImageDraw.Draw(c);d.rectangle([0,0,44,14],fill='black');d.text((2,2),'1968+' if k==0 else str(year),fill='yellow');cells.append(c)
 h=max(c.height for c in cells)+18;row=Image.new('RGB',(sum(c.width+6 for c in cells),h),'white');x=0
 for c in cells:row.paste(c,(x,18));x+=c.width+6
 ImageDraw.Draw(row).text((2,3),f"{w}  {f.get('name')}  {f['class']}",fill='black');rows.append(row)
 record.append(dict(way=w,bbox=[round(v,6) for v in bbox],boxes=boxes))
W=max(r_.width for r_ in rows);out=Image.new('RGB',(W,sum(r_.height+4 for r_ in rows)),'white');y=0
for r_ in rows:out.paste(r_,(0,y));y+=r_.height+4
out.save(P/f'ways-{key}.jpg',quality=86)
(P/f'ways-{key}.json').write_text(json.dumps(dict(ways=record,margin=MARGIN,panel=PANEL,sources={y:dict(sourceId=a,sha256=b) for y,(a,b) in meta.items()}),indent=1))
print(out.size)
