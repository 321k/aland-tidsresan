"""Review crops for the fourth Mariehamn street pass. Read-only on sources; writes only into this folder.
Usage: crop.py KEY lon0 lat0 lon1 lat1 [way ids to highlight...]"""
import sys,json,gzip,numpy as np,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
from pyproj import Transformer
sys.path.insert(0,'scripts')
from historical_map_observations import load_review,MERCATOR
from rural_registration import registration_pair
r=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes());_,regs=load_review(r)
out=Path('data/map-scan-cache/review/mariehamn-major-roads/pass4')
key=sys.argv[1];bbox=list(map(float,sys.argv[2:6]));hi=set(sys.argv[6:])
fs=[f for f in r('dist/assets/modern.json.gz')['features'] if f['kind']=='road']
import os;SCALE=int(os.environ.get("SCALE","2"))
for year in [1968,1978,1985,1995]:
 if year<1995:
  sheet,convert,_=regs[f'nls-mariehamn-{year}'];pix=np.array([[0,0,1],[1000,0,1],[0,1000,1]]);geo=np.array([MERCATOR(*p) for p in convert(pix[:,:2])]);mat=np.linalg.solve(pix,geo);inv=np.linalg.inv(mat[:2,:]);pixel=lambda lon,lat:(np.array(MERCATOR(lon,lat))-mat[2,:])@inv
 else:
  sheet=next(s for s in r('data/rural-map-review.json')['sources'] if s['id']=='nls:101208:1995');fwd,inv=registration_pair(sheet);proj=Transformer.from_crs(4326,sheet['registration']['crs'],always_xy=True).transform;pixel=lambda lon,lat:np.array(inv(proj(lon,lat)))
 raw=Path(f'data/map-scan-cache/101208_{year}.jpg');assert hashlib.sha256(raw.read_bytes()).hexdigest()==sheet['originalSha256'];im=Image.open(raw)
 pts=[pixel(x,y) for x in [bbox[0],bbox[2]] for y in [bbox[1],bbox[3]]];x0,y0=np.min(pts,axis=0).astype(int);x1,y1=np.max(pts,axis=0).astype(int)
 crop=im.crop((x0,y0,x1,y1)).convert('RGB');big=crop.resize((crop.width*SCALE,crop.height*SCALE),Image.LANCZOS);big.save(out/f'{key}-{year}.png')
 draw=ImageDraw.Draw(big)
 for f in fs:
  for path in f['paths']:
   xy=[tuple((pixel(*q)-[x0,y0])*SCALE) for q in path]
   if not any(-50<x<big.width+50 and -50<y<big.height+50 for x,y in xy):continue
   draw.line(xy,fill='red' if f['id'] in hi else 'magenta',width=2 if f['id'] in hi else 1)
   if f['id'] in hi:
    mx,my=xy[len(xy)//2];draw.text((mx+3,my),f['id'].split('/')[1],fill='blue')
 big.save(out/f'{key}-{year}-overlay.png')
 (out/f'{key}-{year}.json').write_text(json.dumps(dict(bbox=bbox,box=list(map(int,[x0,y0,x1,y1])),scale=SCALE,sourceId='nls:'+sheet['id'] if year<1995 else sheet['id'],sha256=sheet['originalSha256'],highlighted=sorted(hi))))
 print(year,crop.size)
