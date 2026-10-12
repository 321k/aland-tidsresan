import urllib.request, urllib.parse,json
from pathlib import Path
query='''[out:json][timeout:90];(way["building"](59.98,19.86,60.15,20.12);relation["building"](59.98,19.86,60.15,20.12);way["highway"](59.98,19.86,60.15,20.12););out tags geom;'''
req=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'AlandHistoryMap/1.0'})
with urllib.request.urlopen(req,timeout=150) as f: data=json.load(f)
Path('data/mariehamn-osm.json').write_text(json.dumps(data,ensure_ascii=False))
print('Elements:',len(data.get('elements',[])), 'date:',data.get('osm3s',{}).get('timestamp_osm_base'))
