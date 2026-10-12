const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const sandbox={URL,console};vm.createContext(sandbox);vm.runInContext(fs.readFileSync('dist/timeline-model.js','utf8'),sandbox);vm.runInContext(fs.readFileSync('dist/explorer.js','utf8')+'\nthis.ExplorerLayers=ExplorerLayers;',sandbox);
const data=JSON.parse(fs.readFileSync('dist/assets/heritage.json')).features;
test('dated, curated and uncertain archaeology are filtered separately',()=>{
 const layer=new sandbox.ExplorerLayers(()=>{},()=>{});
 const jett=data.find(f=>f.name==='Jettböle');assert.ok(jett);
 assert.equal(layer.available(jett,-4000),false);assert.equal(layer.available(jett,-3400),true);assert.equal(layer.available(jett,2026),true);
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
