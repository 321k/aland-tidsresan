"""Area crops of sheet 101208 (1968/1978/1985/1995) with today's building outlines (read-only on sources).
Usage: area.py KEY lon0 lat0 lon1 lat1 [SCALE]"""
import sys,json,gzip,hashlib,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
from pyproj import Transformer
sys.path.insert(0,'scripts')
from historical_map_observations import load_review,MERCATOR
from rural_registration import registration_pair
r=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes());_,regs=load_review(r)
P=Path('data/map-scan-cache/review/mariehamn-buildings');key=sys.argv[1];bbox=list(map(float,sys.argv[2:6]));S=int(sys.argv[6]) if len(sys.argv)>6 else 3
c=r(str(P/'before.json.gz'));G={g['id']:g for g in c['geometries']}
blds=[]
for o in c['objects']:
  if o.get('kind')!='building' or not o['geometryPeriods']:continue
  g=G.get(o['geometryPeriods'][-1]['geometryId'])
  if not g:continue
  pts=g['paths'][0];cx=sum(p[0] for p in pts)/len(pts);cy=sum(p[1] for p in pts)/len(pts)
  if bbox[0]<=cx<=bbox[2] and bbox[1]<=cy<=bbox[3]:
    op=[s['from'] for s in o['states'] if s['state'] in('standing','occupied')];blds.append((o['id'],g['paths'],min(op) if op else None))
for year in [1968,1978,1985,1995]:
  if year<1995:
    sheet,convert,_=regs[f'nls-mariehamn-{year}'];pix=np.array([[0,0,1],[1000,0,1],[0,1000,1]]);geo=np.array([MERCATOR(*p) for p in convert(pix[:,:2])]);mat=np.linalg.solve(pix,geo);inv=np.linalg.inv(mat[:2,:]);pixel=lambda lon,lat,inv=inv,mat=mat:(np.array(MERCATOR(lon,lat))-mat[2,:])@inv
  else:
    sheet=next(s for s in r('data/rural-map-review.json')['sources'] if s['id']=='nls:101208:1995');fwd,invf=registration_pair(sheet);proj=Transformer.from_crs(4326,sheet['registration']['crs'],always_xy=True).transform;pixel=lambda lon,lat,invf=invf,proj=proj:np.array(invf(proj(lon,lat)))
  raw=Path(f'data/map-scan-cache/101208_{year}.jpg');assert hashlib.sha256(raw.read_bytes()).hexdigest()==sheet['originalSha256'];im=Image.open(raw)
  q=[pixel(x,y) for x in [bbox[0],bbox[2]] for y in [bbox[1],bbox[3]]];x0,y0=np.min(q,axis=0).astype(int);x1,y1=np.max(q,axis=0).astype(int)
  crop=im.crop((x0,y0,x1,y1)).convert('RGB').resize(((x1-x0)*S,(y1-y0)*S),Image.LANCZOS);crop.save(P/f'{key}-{year}.png');dr=ImageDraw.Draw(crop)
  for oid,paths,first in blds:
    for path in paths:
      xy=[tuple((pixel(*p)-[x0,y0])*S) for p in path];dr.line(xy+[xy[0]],fill=(0,170,255) if (first or 9999)>1995 else (255,140,0),width=1)
  crop.save(P/f'{key}-{year}-overlay.png')
  (P/f'{key}-{year}.json').write_text(json.dumps(dict(bbox=bbox,box=[int(x0),int(y0),int(x1),int(y1)],scale=S,sourceId='nls:'+sheet['id'] if year<1995 else sheet['id'],sha256=sheet['originalSha256'])))
print(key,len(blds),'buildings')
