"""Extract dated road geometry from a historical Geofabrik PBF, never from today's ways."""
import sys,json,gzip,tempfile,hashlib
from pathlib import Path
import osmium
from shapely.geometry import Point,LineString,Polygon
from shapely.ops import unary_union
from build_modern import join_rings
pbf=Path(sys.argv[1]);year=int(sys.argv[2]);boundary=None
for r in osmium.FileProcessor(str(pbf),osmium.osm.RELATION).with_filter(osmium.filter.KeyFilter('ISO3166-1')):
 if r.tags.get('ISO3166-1')=='AX':boundary=[(m.ref,m.role) for m in r.members if m.type=='w']
assert boundary,'Åland administrative boundary missing'
border_ids={i for i,_ in boundary};borders={};roads=[]
with tempfile.TemporaryDirectory(prefix='road-nodes-') as tmp:
 processor=osmium.FileProcessor(str(pbf)).with_locations('sparse_file_array,'+tmp+'/nodes').with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))
 timestamp=processor.header.get('osmosis_replication_timestamp')
 for w in processor:
  highway=w.tags.get('highway');border=w.id in border_ids
  if not border and (not highway or highway in ('proposed','construction','abandoned','razed','platform')):continue
  if not all(n.location.valid() for n in w.nodes):continue
  if not border and not any(19<n.lon<21.5 and 59.3<n.lat<60.85 for n in w.nodes):continue
  points=[(n.lon,n.lat) for n in w.nodes]
  if border:borders[w.id]=points
  if highway and len(points)>1:
   roads.append({'id':f'road-{year}-{w.id}','osmId':f'way/{w.id}','name':w.tags.get('name:sv') or w.tags.get('name') or 'Väg eller stig','class':highway,'paths':[points]})
assert border_ids<=borders.keys()
rings=join_rings([borders[i] for i,role in boundary if role in ('outer','')]);area=unary_union([Polygon(r) for r in rings]);assert area.contains(Point(19.941,60.103))
roads=[r for r in roads if area.intersects(LineString(r['paths'][0]))]
for r in roads:r['paths']=[[[round(x,6),round(y,6)] for x,y in r['paths'][0]]]
result={'id':f'osm-{year}','year':year,'snapshot':timestamp or f'{year}-01-01 (Geofabrik archive label)','name':f'OSM:s vägkarta {year}','source':'https://download.geofabrik.de/europe/finland.html','archiveUrl':'https://download.geofabrik.de/europe/'+pbf.name,'license':'ODbL 1.0','attribution':'© OpenStreetMap contributors / Geofabrik','features':roads,'note':'Historisk databasbild. Skillnader mellan uttag kan vara förbättrad kartläggning och betyder inte automatiskt att en väg byggts eller rivits. Kartlagda namn gäller källans år.'}
Path(f'dist/assets/roads-{year}.json.gz').write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
provenance={k:v for k,v in result.items() if k!='features'};provenance.update(count=len(roads),archive_sha256=hashlib.file_digest(pbf.open('rb'),'sha256').hexdigest(),method='Road ways intersecting the historical Åland administrative boundary in the same PBF. Whole ways retained. No current geometry used.')
Path(f'data/roads-{year}-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n');print(year,len(roads),timestamp,flush=True)
