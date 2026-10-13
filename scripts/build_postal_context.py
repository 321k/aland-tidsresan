"""Small modern reference coastline for Sweden, outside the Åland shoreline model.
Requires shapely. Natural Earth 1:10m land, public domain; not a dated shoreline.
"""
import json, urllib.request
from pathlib import Path
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
root=Path(__file__).resolve().parents[1]
url='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_land.geojson'
data=json.load(urllib.request.urlopen(url))
clip=box(16,58,19.19,63)
land=unary_union([shape(f['geometry']).intersection(clip) for f in data['features']]).simplify(.0005,preserve_topology=True)
output={'source':url,'license':'Public Domain','note':'Modern reference coast for orientation only, not reconstructed for the selected year. West of the Åland model; shown only with the postal route.','geometry':mapping(land)}
(root/'dist/assets/postal-context.json').write_text(json.dumps(output,separators=(',',':'))+'\n')
