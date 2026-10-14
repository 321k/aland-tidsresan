const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),zlib=require('node:zlib');
const data=JSON.parse(fs.readFileSync('dist/assets/city-buildings.json')),modern=JSON.parse(zlib.gunzipSync(fs.readFileSync('dist/assets/modern.json.gz'))),history=JSON.parse(fs.readFileSync('dist/assets/historic-buildings.json')).features;
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null},htmlEscape:String,safeURL:String};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/timeline-model.js','utf8')+fs.readFileSync('dist/city-buildings.js','utf8')+';this.City=CityBuildings;this.Time=EvidenceTime;',box);
function setup(){const layer=new box.City(()=>{});Object.assign(layer,structuredClone(data));const e={flags:{historic:true,modern:true,uncertain:true,traces:false},category:'all',query:'',historic:structuredClone(history).map(f=>({...f,recordType:'building'})),modern:structuredClone(modern.features),matches:()=>true,available(f,y){return !['future','trace'].includes(box.Time.state(f,y))},prepared:true,project:(x,y)=>[x*10000,y*10000]};const grid={enabled:true,ready:true,stage(y){return y>=1920&&y<1942?JSON.parse(fs.readFileSync('dist/assets/mariehamn-city-grid.json')).sets.find(s=>s.year===1920):null}};return{layer,e,grid}}
test('historical outlines use archived dates, not current footprints or construction dates',()=>{
 const{layer,e,grid}=setup();assert.deepEqual(data.sets.map(s=>s.year),[2014,2021,2025]);
 for(const s of data.sets){assert.ok(s.features.length>900);assert.ok(s.snapshot.startsWith(String(s.year)));for(const f of s.features){assert.equal(f.kind,'building');for(const ring of f.paths)assert.deepEqual(ring[0],ring.at(-1))}}
 assert.equal(layer.snapshot(2013),undefined);assert.equal(layer.snapshot(2020).year,2014);assert.equal(layer.snapshot(2024).year,2021);
 const early=layer.records(1900,e,grid);assert.ok(early.length>10);assert.ok(early.every(r=>r.schematic));
 assert.ok(layer.records(2021,e,grid).filter(r=>!r.schematic).every(r=>r.sourceYear===2021));
});
test('named houses merge into source contours and never acquire duplicate markers',()=>{
 const{layer,e,grid}=setup();const today=layer.records(2026,e,grid),h=e.historic.find(h=>h.id==='mh-history:stadshuset');
 const matching=today.filter(r=>r.target.id===h.id);assert.equal(matching.length,1);assert.equal(matching[0].id,data.links[h.id]);assert.equal(matching[0].schematic,false);
 assert.equal(today.filter(r=>r.id===data.links[h.id]).length,1);
 const old=layer.records(1939,e,grid);assert.equal(old.filter(r=>r.target.id===h.id).length,1);
});
test('a demolished house is absent after demolition and never linked to its replacement',()=>{
 const{layer,e,grid}=setup(),id='mh-history:tvargrand2';assert.ok(!data.links[id]);
 assert.ok(layer.records(2004,e,grid).some(r=>r.id===id));assert.ok(!layer.records(2005,e,grid).some(r=>r.id===id));assert.ok(!layer.records(2026,e,grid).some(r=>r.target.id===id));
});
test('dated houses grow at their source years, and building visibility follows filters',()=>{
 const{layer,e,grid}=setup(),id='mh-history:stadshuset';assert.ok(!layer.records(1938,e,grid).some(r=>r.target.id===id));assert.ok(layer.records(1939,e,grid).some(r=>r.target.id===id));
 e.flags.historic=false;assert.equal(layer.records(1900,e,grid).length,0);assert.ok(layer.records(2026,e,grid).every(r=>!r.history));
 e.flags.modern=false;assert.equal(layer.records(2026,e,grid).length,0);
});
test('museum source symbols do not become undocumented surviving houses in 1942',()=>{
 const{layer,e,grid}=setup();assert.equal(layer.records(1920,e,grid).filter(r=>!r.schematic).length,216);assert.ok(layer.records(1942,e,grid).every(r=>r.schematic));
});
test('hit targets select the named story and are removed when zoomed out',()=>{
 const{layer,e,grid}=setup();const v={year:2026,zoom:40,width:800,height:600,scale:1,panX:0,panY:0,meta:{width:399000,height:1202000}},ctx=new Proxy({isPointInPath:()=>true},{get:(o,k)=>o[k]||(()=>{}),set:(o,k,v)=>(o[k]=v,true)});
 layer.draw(ctx,v,e,grid);const r=layer.drawn.find(r=>r.history);assert.ok(r);const b=r.renderBounds,x=(b[0]+b[2])/2-v.meta.width/2+v.width/2,y=(b[1]+b[3])/2-v.meta.height/2+v.height/2;assert.ok(layer.hit(x,y,ctx));layer.draw(ctx,{...v,zoom:1},e,grid);assert.equal(layer.hit(x,y,ctx),null);
});
test('city playback stops at its own next milestone and never resets to the ice age',()=>{
 const source=fs.readFileSync('dist/app.js','utf8'),s={year:1900,cityPlaybackYear:1919.99,cityStops:[1860,1900,1920,2026],lastTick:0,timer:null,playing:true,$:()=>({checked:true}),shorelines:{prepare:()=>true},goToYear:y=>s.year=y,pause:()=>s.playing=false,requestAnimationFrame:()=>1,playbackFrame(){}};
 vm.createContext(s);vm.runInContext(source.slice(source.indexOf('function cityPlaybackFrame(')),s);s.cityPlaybackFrame(100);assert.equal(s.year,1920);assert.equal(s.playing,false);
});
