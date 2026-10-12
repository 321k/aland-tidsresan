const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const sandbox={URL,console};vm.createContext(sandbox);vm.runInContext(fs.readFileSync('dist/timeline-model.js','utf8'),sandbox);vm.runInContext(fs.readFileSync('dist/explorer.js','utf8')+'\nthis.ExplorerLayers=ExplorerLayers;this.EvidenceTime=EvidenceTime;',sandbox);
const data=JSON.parse(fs.readFileSync('dist/assets/heritage.json')).features;
test('dated, curated and uncertain archaeology are filtered separately',()=>{
 const layer=new sandbox.ExplorerLayers(()=>{},()=>{});
 const jett=data.find(f=>f.name==='Jettböle');assert.ok(jett);
 assert.equal(layer.available(jett,-4000),false);assert.equal(layer.available(jett,-3400),true);assert.equal(layer.available(jett,2026),false);
 const undated=data.find(f=>!f.periods.length&&!Number.isFinite(f.earliestYear));assert.ok(undated);assert.equal(layer.available(undated,2026),false);layer.flags.undated=true;assert.equal(layer.available(undated,2026),true);
 assert.equal(layer.available({periods:[{from:-1500,to:-400}]},-1501),false);assert.equal(layer.available({periods:[{from:-1500,to:-400}]},-1500),true);
});
test('modern geometry never renders at historical dates',()=>{
 const layer=new sandbox.ExplorerLayers(()=>{},()=>{});layer.prepared=true;let modern=0,coast=0;
 layer.drawModern=()=>modern++;layer.drawCoast=()=>coast++;layer.drawPostal=layer.drawHeritage=layer.updateList=()=>{};
 for(const year of [-4000,1750,1942,2021,2025])layer.render({}, {year});assert.equal(modern,0);assert.equal(coast,0);
 layer.render({}, {year:2026});assert.equal(modern,1);assert.equal(coast,1);layer.flags.modern=false;layer.render({}, {year:2026});assert.equal(modern,1);
});
test('published datasets have unique objects, real geometry and expected counts',()=>{
 assert.equal(data.length,1868);assert.equal(new Set(data.map(f=>f.id)).size,1868);
 for(const f of data){assert.ok(f.lon>19&&f.lon<22&&f.lat>59&&f.lat<61);assert.ok(f.sourceUrl.startsWith('https://'));}
 const dataset=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync('dist/assets/modern.json.gz'))),modern=dataset.features;
 assert.equal(modern.filter(f=>f.kind==='building').length,dataset.counts.building);assert.ok(dataset.counts.building>30000);assert.equal(modern.filter(f=>f.kind==='road').length,dataset.counts.road);assert.ok(dataset.counts.road>20000);assert.equal(new Set(modern.map(f=>f.id)).size,modern.length);
 for(const f of modern)for(const path of f.paths){assert.ok(path.length>=2);for(const coord of path)assert.ok(coord.every(Number.isFinite));}
});

test('expired sites disappear at period boundaries and gaps, with older traces opt-in',()=>{
 const layer=new sandbox.ExplorerLayers(()=>{},()=>{});
 const dated={periods:[{from:-1500,to:-400}]};
 assert.equal(layer.available(dated,-400),true);
 assert.equal(layer.available(dated,-399),false);
 const phased=data.find(f=>f.code==='Sa 20.7');
 assert.equal(layer.available(phased,-3500),true);
 assert.equal(layer.available(phased,-3200),false);
 assert.equal(layer.available(phased,-3000),true);
 for(const f of data.filter(f=>sandbox.EvidenceTime.state(f,2026)==='trace'))assert.equal(layer.available(f,2026),false,f.code);
 layer.flags.traces=true;assert.equal(layer.available(dated,2026),true);
 layer.flags.traces=false;assert.equal(layer.available(dated,2026),false);
});
test('searching an expired settlement jumps to its period without enabling old traces',()=>{
 const layer=new sandbox.ExplorerLayers(()=>{},()=>{}),jett=data.find(f=>f.name==='Jettböle');layer.heritage=[jett];
 const elements=new Map(),element=id=>{if(!elements.has(id))elements.set(id,{value:id==='#placeSearch'?'Jettböle':''});return elements.get(id)};
 const s={explorer:layer,year:2026,$:element,EvidenceTime:sandbox.EvidenceTime,goToYear:y=>{s.year=y},selectFeature:f=>{s.selected=f}};vm.createContext(s);
 const source=fs.readFileSync('dist/app.js','utf8');vm.runInContext(source.slice(source.indexOf('function jumpToSearch()'),source.indexOf("$('#searchPlace').onclick")),s);
 s.jumpToSearch();assert.equal(s.selected.id,jett.id);assert.ok(s.year<2026);assert.equal(layer.available(jett,s.year),true);assert.equal(layer.flags.traces,false);assert.equal(layer.available(jett,2026),false);
});

test('broad registry dates do not turn the present into an archaeology map',()=>{
 const layer=new sandbox.ExplorerLayers(()=>{},()=>{});
 const broad=data.find(f=>!f.temporal&&f.periods.some(p=>p.to===2026));assert.ok(broad);
 assert.equal(layer.available(broad,1750),true);assert.equal(layer.available(broad,2026),false);
 assert.equal(data.filter(f=>layer.available(f,2026)).length,0);
 layer.flags.traces=true;assert.equal(layer.available(broad,2026),true);
 assert.equal(layer.available({recordType:'building',start:1939},2026),true);
});
