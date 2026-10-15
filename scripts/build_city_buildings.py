"""Package source-dated building outlines and explicit place-to-outline links.
Never infer a construction date from the first OSM edit. Historic points remain
schematic before a source-dated outline is available. Demolished sites are not
linked to buildings currently occupying the same location.
"""
import json,gzip
from pathlib import Path
from build_modern import build
from city_continuity import reconcile
root=Path(__file__).resolve().parents[1]
def inside(point,paths):
 x,y=point;yes=False
 for ring in paths:
  for a,b in zip(ring,ring[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes
coverage=[19.912,60.079,19.962,60.139]
def within(f):
 ps=f['paths'][0];x=sum(p[0] for p in ps)/len(ps);y=sum(p[1] for p in ps)/len(ps)
 return coverage[0]<=x<=coverage[2] and coverage[1]<=y<=coverage[3]
sets=[]
for year in [2014,2021,2025]:
 path=root/f'data/city-buildings-{year}.json.gz'
 if not path.exists():continue
 raw=json.loads(gzip.decompress(path.read_bytes()));features=[f for f in build(raw)['features'] if f['kind']=='building' and within(f)]
 sets.append({'year':year,'snapshot':raw['extract']['snapshot'],'source':'https://www.openstreetmap.org/copyright','query':raw['extract']['query'],'endpoint':raw['extract']['endpoint'],'features':features})
modern=json.loads(gzip.decompress((root/'dist/assets/modern.json.gz').read_bytes()))
continuity=reconcile(sets+[{'year':2026,'features':[f for f in modern['features'] if f['kind']=='building' and within(f)]}])
history=json.loads((root/'dist/assets/historic-buildings.json').read_text())['features']
links={}
for h in history:
 if h.get('end') is not None:continue
 candidates=[f for f in modern['features'] if f['kind']=='building' and inside([h['lon'],h['lat']],f['paths'])]
 if len(candidates)==1:links[h['id']]=candidates[0]['id']
result={'coverage':coverage,'sets':sets,'links':links,'continuity':continuity,'policy':'Links attach a documented place story to the present map object containing its source point. They do not establish historic building shape, continuity of every wing, or construction dates. Historical snapshots show mapping coverage, not a complete census. Small survey corrections for the same OSM identity use a common outline; larger changes remain source-specific. An intermediate omission is bridged only between equivalent observations, never beyond the last observation or before the first. A missing outline is not evidence of demolition.'}
(root/'dist/assets/city-buildings.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
print([(d['year'],len(d['features'])) for d in sets],len(links),'place links')
print(continuity)
