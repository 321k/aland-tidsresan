"""Embed curated routes; route geometry and dates are reviewed independently of OSM."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
routes=json.loads((root/'data/transport-routes.json').read_text())
p=root/'dist/transport-routes.js'
s=p.read_text();start=s.index(' routes:');end=s.index(' groups:')
p.write_text(s[:start]+' routes:'+json.dumps(routes,ensure_ascii=False,separators=(',',':'))+',\n'+s[end:])

p=root/"data/transport-provenance.json"
provenance=json.loads(p.read_text());provenance["shipping"]["routes"]=routes
p.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+"\n")
