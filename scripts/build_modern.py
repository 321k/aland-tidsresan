import json,collections
from pathlib import Path
raw=json.loads(Path('data/mariehamn-osm.json').read_text());features=[]
member_ways={m['ref'] for e in raw['elements'] if e['type']=='relation' and 'building' in e.get('tags',{}) for m in e.get('members',[]) if m['type']=='way'}
def join_rings(paths):
 remaining=list(paths);result=[]
 while remaining:
  ring=remaining.pop(0)
  changed=True
  while changed and ring[0]!=ring[-1]:
   changed=False
   for i,part in enumerate(remaining):
    if ring[-1]==part[0]:ring+=part[1:]
    elif ring[-1]==part[-1]:ring+=part[-2::-1]
    elif ring[0]==part[-1]:ring=part[:-1]+ring
    elif ring[0]==part[0]:ring=part[:0:-1]+ring
    else:continue
    remaining.pop(i);changed=True;break
  if ring[0]==ring[-1]:result.append(ring)
 return result
for e in raw['elements']:
 if e['type']=='way' and e['id'] in member_ways and 'building' in e.get('tags',{}):continue
 t=e.get('tags',{});kind='building' if 'building' in t else 'road' if 'highway' in t else None
 if not kind:continue
 if e['type']=='relation':
  rings=[[[round(p['lon'],6),round(p['lat'],6)] for p in m.get('geometry',[])] for m in e.get('members',[]) if m['type']=='way' and m.get('geometry')]
  rings=join_rings(rings)
 else:rings=[[[round(p['lon'],6),round(p['lat'],6)] for p in e.get('geometry',[])]]
 rings=[r for r in rings if len(r)>1]
 if not rings:continue
 name=t.get('name:sv') or t.get('name') or (' '.join(x for x in [t.get('addr:street'),t.get('addr:housenumber')] if x))
 features.append({'id':e['type']+'/'+str(e['id']),'kind':kind,'name':name or ('Byggnad' if kind=='building' else 'Väg eller stig'),'class':t.get('highway') or t.get('building'),'paths':rings,'start_date':t.get('start_date'),'wiki':t.get('wikipedia')})
d={'source':'© OpenStreetMap contributors','license':'ODbL 1.0','url':'https://www.openstreetmap.org/copyright','snapshot':raw['osm3s']['timestamp_osm_base'],'area':'Mariehamn med omnejd','bbox':[19.86,59.98,20.12,60.15],'features':features}
Path('dist/assets/modern.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
print(collections.Counter(f['kind'] for f in features));print(Path('dist/assets/modern.json').stat().st_size)
