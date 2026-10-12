from PIL import Image
import math, urllib.request, io, json, concurrent.futures
from pathlib import Path
root=Path(__file__).parent/'dist/assets'
z=10
world=256*2**z
def px(lon,lat):
 return ((lon+180)/360*world,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*world)
x0,y0=map(int,px(19.2,60.65)); x1,y1=map(int,px(21.4,59.65))
out=Image.new('RGB',(x1-x0,y1-y0))
def tile(p):
 x,y=p
 url=f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'
 for i in range(3):
  try:
   with urllib.request.urlopen(url,timeout=30) as f: im=Image.open(io.BytesIO(f.read())).convert('RGB')
   return x,y,im
  except Exception:
   if i==2: raise
coords=[(x,y) for x in range(x0//256,x1//256+1) for y in range(y0//256,y1//256+1)]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for x,y,im in pool.map(tile,coords): out.paste(im,(x*256-x0,y*256-y0))
out.save(root/'terrain.png')
(root/'terrain.json').write_text(json.dumps(dict(x0=x0,y0=y0,width=out.width,height=out.height,world=world)))
print('Downloaded',len(coords),'tiles;',out.size)
