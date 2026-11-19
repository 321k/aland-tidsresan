const fs=require('fs'),vm=require('vm'),zlib=require('zlib');
const cat=JSON.parse(zlib.gunzipSync(fs.readFileSync('dist/assets/temporal-objects.json.gz')));
const box={};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.M=TemporalObjects',box);
const m=new box.M(cat);const s=cat.cityStages.find(s=>s.id==='city-reconstruction-1860');
const out=s.features.map(f=>{let paths=f.paths;if(f.objectId){const r=m.resolveObject(f.objectId,1860);paths=r.geometry?r.geometry.paths:[]}return {id:f.id,name:f.name,kind:f.kind,objectId:f.objectId||null,paths}});
fs.writeFileSync(process.argv[2],JSON.stringify(out));console.log(out.length);
