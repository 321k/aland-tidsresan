"""Refresh the cached Åland extract. Visitors never call Overpass directly."""
import gzip
import json
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = 'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
QUERY = '''[out:json][timeout:180];
area["ISO3166-1"="AX"]->.aland;
(
  way["building"](area.aland);
  relation["building"]["type"="multipolygon"](area.aland);
  way["highway"](area.aland);
  node["place"~"^(town|village|hamlet)$"](area.aland);
);
out tags geom;'''

if __name__ == '__main__':
    request = urllib.request.Request(
        ENDPOINT + '?' + urllib.parse.urlencode({'data': QUERY}),
        headers={'User-Agent': 'AlandHistoryMap/1.0'})
    with urllib.request.urlopen(request, timeout=240) as response:
        data = json.load(response)
    # Overpass can return HTTP 200 with a runtime error and partial data.
    if data.get('remark') or len(data.get('elements', [])) < 16000:
        raise RuntimeError(data.get('remark', 'Incomplete Åland extract'))
    data['extract'] = {'endpoint': ENDPOINT, 'query': QUERY, 'area': 'Åland',
                       'license': 'ODbL 1.0', 'url': 'https://www.openstreetmap.org/copyright'}
    target = Path('data/aland-osm.json.gz')
    target.write_bytes(gzip.compress(json.dumps(data, ensure_ascii=False,
                                               separators=(',', ':')).encode(), mtime=0))
    print('Elements:', len(data['elements']), 'date:', data['osm3s']['timestamp_osm_base'])
