"""Extract Mariehamn buildings from a dated Geofabrik PBF (ways + multipolygons)."""
import sys,json,gzip,tempfile,hashlib
from pathlib import Path
import osmium
pbf=Path(sys.argv[1]);year=int(sys.argv[2]);relations=[];member_ids=set();ways={};elements=[]
for r in osmium.FileProcessor(str(pbf),osmium.osm.RELATION).with_filter(osmium.filter.KeyFilter('building')):
 if r.tags.get('type')!='multipolygon':continue
 members=[{'type':'way','ref':m.ref,'role':m.role} for m in r.members if m.type=='w']
 relations.append({'type':'relation','id':r.id,'tags':dict(r.tags),'members':members});member_ids.update(m['ref'] for m in members)
def local(points):return any(19.912<=p['lon']<=19.962 and 60.079<=p['lat']<=60.139 for p in points)
with tempfile.TemporaryDirectory(prefix='city-nodes-') as tmp:
 processor=osmium.FileProcessor(str(pbf)).with_locations('sparse_file_array,'+tmp+'/nodes').with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))
 timestamp=processor.header.get('osmosis_replication_timestamp')
 for w in processor:
  if not w.tags.get('building') and w.id not in member_ids:continue
  if not all(n.location.valid() for n in w.nodes):continue
  points=[{'lon':n.lon,'lat':n.lat} for n in w.nodes]
  if w.id in member_ids:ways[w.id]=points
  if w.tags.get('building') and local(points):elements.append({'type':'way','id':w.id,'tags':dict(w.tags),'geometry':points})
for r in relations:
 if not any(local(ways.get(m['ref'],[])) for m in r['members']):continue
 if any(m['ref'] not in ways for m in r['members']):raise ValueError('Incomplete building relation')
 for m in r['members']:m['geometry']=ways[m['ref']]
 elements.append(r)
raw={'osm3s':{'timestamp_osm_base':timestamp},'elements':elements,'extract':{'snapshot':timestamp,'endpoint':'https://download.geofabrik.de/europe/finland.html','query':'Buildings intersecting Mariehamn coverage in historical Finland PBF; full rings retained.','archiveUrl':'https://download.geofabrik.de/europe/'+pbf.name.replace('city-',''),'sha256':hashlib.file_digest(pbf.open('rb'),'sha256').hexdigest()}}
Path(f'data/city-buildings-{year}.json.gz').write_bytes(gzip.compress(json.dumps(raw,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
print(year,len(elements),timestamp)
