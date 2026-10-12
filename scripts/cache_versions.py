"""Content hashes prevent stale application code or datasets across private deployments."""
import re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'dist'
def version(path):return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
for p in root.glob('*.js'):
 s=p.read_text()
 s=re.sub(r"fetch\('((?:assets/)[^'?$]+)(?:\?v=[^']+)?'\)",lambda m:"fetch('"+m[1]+'?v='+version(root/m[1])+"')" if (root/m[1]).is_file() else m[0],s)
 p.write_text(s)
p=root/'index.html';s=p.read_text()
s=re.sub(r'(src|href)="([\w-]+\.(?:js|css))(?:\?v=[^\"]+)?"',lambda m:m[1]+'="'+m[2]+'?v='+version(root/m[2])+'"',s);p.write_text(s)
