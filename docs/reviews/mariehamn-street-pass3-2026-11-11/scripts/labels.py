"""Labelled modern-street overlay on a review crop. Usage: labels.py KEY YEAR"""
import sys,json,gzip,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,'scripts')
from historical_map_observations import load_review,MERCATOR
from rural_registration import registration_pair
from pyproj import Transformer
r=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith('.gz') else Path(p).read_bytes())
P=Path('data/map-scan-cache/review/mariehamn-major-roads/pass3');key,year=sys.argv[1],int(sys.argv[2]);meta=json.loads((P/f'{key}-{year}.json').read_text());x0,y0=meta['box'][:2];S=meta['scale']
if year<1995:
 _,regs=load_review(r);sheet,convert,_=regs[f'nls-mariehamn-{year}'];pix=np.array([[0,0,1],[1000,0,1],[0,1000,1]]);geo=np.array([MERCATOR(*p) for p in convert(pix[:,:2])]);mat=np.linalg.solve(pix,geo);inv=np.linalg.inv(mat[:2,:]);pixel=lambda lon,lat:(np.array(MERCATOR(lon,lat))-mat[2,:])@inv
else:
 sheet=next(s for s in r('data/rural-map-review.json')['sources'] if s['id']=='nls:101208:1995');fwd,inv=registration_pair(sheet);proj=Transformer.from_crs(4326,sheet['registration']['crs'],always_xy=True).transform;pixel=lambda lon,lat:np.array(inv(proj(lon,lat)))
im=Image.open(P/f'{key}-{year}.png').convert('RGB');d=ImageDraw.Draw(im)
for f in r('dist/assets/modern.json.gz')['features']:
 if f['kind']!='road' or f['class'] in ('footway','path','steps','track','cycleway','pedestrian'):continue
 for path in f['paths']:
  xy=[tuple((pixel(*q)-[x0,y0])*S) for q in path]
  if not any(0<x<im.width and 0<y<im.height for x,y in xy):continue
  d.line(xy,fill=(255,0,255),width=1)
  if f.get('name') and f['name']!='Väg eller stig':
   mx,my=xy[len(xy)//2];d.text((mx+2,my-6),f['name'],fill=(0,0,255))
im.save(P/f'{key}-{year}-labels.jpg',quality=85)
