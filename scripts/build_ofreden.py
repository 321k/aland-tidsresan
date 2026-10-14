"""Package the sourced Ofreden stories; no inferred geometry or historical dates."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'data/ofreden.json').read_text())
(root/'dist/ofreden-data.js').write_text('window.OFREDEN='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
print(len(data['places']),'places;',len(data['events']),'timeline stops')
