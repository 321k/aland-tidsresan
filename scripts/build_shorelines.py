"""Regional excerpts of public Glare 2.2 / MML / maannousu.info COGs.
No chronological interpolation. Simplified vector outlines on a ~19 m ground grid.
Dependencies: rasterio, numpy, shapely. Remote reads use COG range requests.
"""
import json,math,time,sys
from pathlib import Path
import numpy as np
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.transform import from_bounds
from rasterio.enums import Resampling
from rasterio.features import shapes
from shapely.geometry import shape,mapping
from shapely.ops import unary_union
from concurrent.futures import ThreadPoolExecutor
import urllib.request
root=Path(__file__).resolve().parents[1];out=root/'dist/assets/shorelines';out.mkdir(exist_ok=True)
m=json.loads((root/'dist/assets/terrain.json').read_text());earth=40075016.68557849;unit=earth/m['world']
left=m['x0']*unit-earth/2;top=earth/2-m['y0']*unit;right=left+m['width']*unit;bottom=top-m['height']*unit
factor=4;width=m['width']*factor;height=m['height']*factor
years=json.loads((root/'data/shoreline-years.json').read_text())['years']
selected=[int(y) for y in sys.argv[1:]] or years
transform=from_bounds(left,bottom,right,top,width,height)
# Coordinates in the site's stable WebMercator base grid.
local_transform=from_bounds(0,m['height'],m['width'],0,width,height)
def round_coords(obj):
 if isinstance(obj,(tuple,list)):
  if obj and isinstance(obj[0],(float,int)):return [round(x,4) for x in obj]
  return [round_coords(x) for x in obj]
 return obj

def build(year):
 p=out/f'{year}.json'
 if p.exists():return year
 start=time.time();url=f'https://maannousu.info/api/v2/{year}'
 with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_TIMEOUT='45',GDAL_HTTP_MAX_RETRY='2',GDAL_HTTP_RETRY_DELAY='2',GDAL_CACHEMAX=128):
  with rasterio.open('/vsicurl/'+url,overview_level=2) as src:
   with WarpedVRT(src,crs='EPSG:3857',transform=transform,width=width,height=height,resampling=Resampling.nearest,src_nodata=255,nodata=255) as vrt:arr=vrt.read(1)
 result={'year':year,'source':url,'gridMetresAt60N':round(unit/factor*.5,1),'classes':{}}
 for val,name in [(0,'land'),(2,'ice'),(255,'noData')]:
  mask=arr==val
  if not mask.any():result['classes'][name]=[];continue
  geoms=[]
  for geom,value in shapes(np.asarray(mask,dtype='uint8'),mask=mask,transform=local_transform):
   g=shape(geom).simplify(.22,preserve_topology=True)
   if g.area>.02:geoms.append(g)
  result['classes'][name]=[round_coords(mapping(g)['coordinates']) for g in geoms]
 p.write_text(json.dumps(result,separators=(',',':')))
 print(year,'classes',dict(zip(*np.unique(arr,return_counts=True))), 'bytes',p.stat().st_size,'secs',round(time.time()-start),flush=True)
 return year
def try_build(year):
 try:return build(year)
 except Exception as e:print('FAILED',year,str(e),flush=True);return None
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(try_build,selected))
manifest={'years':sorted(int(p.stem) for p in out.glob('*.json') if p.stem.lstrip('-').isdigit()),'source':'https://maannousu.info/index_sv','attribution':'Antti Kekki / maannousu.info · Glare 2.2, Aki Hakonen · MML höjdmodell 2 m (2023)','license':'CC BY 4.0','derived':'Ålandsutsnitt omprojicerade till Web Mercator och förenklade till vektorkonturer; cirka 19 m beräkningsrutnät vid 60°N. Ingen interpolation mellan år.','unavailableYears':[y for y in years if not (out/f'{y}.json').exists()],'model':'Glare 2.2','meta':m,'downloaded':'2026-10-12'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')))
