const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const box={window:{}};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/wrecks-data.js','utf8'),box);
const wrecks=box.window.WRECKS,time=box.window.WreckTimeline,source=fs.readFileSync('dist/app.js','utf8');
const byId=id=>wrecks.find(w=>w.id==='wreck-'+id);
function appContext(year,enabled=false){
 const elements=new Map(),s={year,buildings:wrecks,window:box.window,WreckTimeline:time,explorer:{available:()=>true},$:id=>{if(!elements.has(id))elements.set(id,{checked:id==='#layerWrecks'?enabled:true});return elements.get(id)}};
 vm.createContext(s);vm.runInContext(source.slice(source.indexOf('function visible()'),source.indexOf('// Only explicitly')),s);return s;
}
test('wrecks are absent before sinking, even with the older-wreck layer enabled',()=>{
 for(const w of wrecks){assert.equal(time.visible(w,w.start-1,true),false);assert.equal(time.visible(w,w.start-1,false),false)}
 assert.equal(appContext(1915,true).visible().length,0);
});
test('events are visible at their year and disappear afterwards unless explicitly enabled',()=>{
 for(const w of wrecks)for(const y of [w.sinkingYear,w.discoveryYear].filter(Number.isFinite)){
  assert.ok(appContext(y).visible().includes(w));assert.ok(!appContext(y+1).visible().includes(w));assert.ok(appContext(y+1,true).visible().includes(w));
 }
 const present=appContext(2026);assert.equal(present.visible().length,0);present.$('#layerWrecks').checked=true;assert.equal(present.visible().length,4);present.$('#layerWrecks').checked=false;assert.equal(present.visible().length,0);
});
test('uncertain Champagne dating never invents a sinking year or an early marker',()=>{
 const w=byId('champagne');assert.equal(w.sinkingYear,null);assert.equal(w.discoveryYear,2010);
 for(const y of [1841,1848,1900,2009])assert.equal(time.visible(w,y,true),false);
 assert.match(w.uncertainty,/1841–1848/);assert.match(w.more,/obekräftad/);
});
test('five distinct events separate sinkings from discoveries, preserving uncertainty',()=>{
 const events=time.events(wrecks);assert.deepEqual(Array.from(events,e=>e.y).sort((a,b)=>a-b),[1916,1918,1933,1986,2010]);
 assert.equal(time.tag(byId('hindenburg'),1918),'Förlisning');assert.equal(time.tag(byId('hindenburg'),1986),'Vraket upptäcks');assert.equal(time.tag(byId('hindenburg'),2026),'Skeppsvrak · äldre spår');
 assert.match(time.text(byId('hindenburg'),1986),/enligt|Enligt/);assert.match(byId('hindenburg').uncertainty,/1995/);
 assert.match(byId('skiftet').uncertainty,/14 december/);assert.match(byId('skiftet').uncertainty,/21 december/);
 for(const e of events){assert.ok(e.text&&e.q&&e.sourceUrl);assert.ok(wrecks.some(w=>w.id===e.wreckId))}
});
test('curated wreck positions match original public registry points and attribution',()=>{
 const provenance=JSON.parse(fs.readFileSync('data/wreck-provenance.json','utf8'));assert.equal(provenance.license,'CC BY 4.0');
 for(const w of wrecks){const f=provenance.features.find(f=>f.attributes.OBJECTID===w.objectId);assert.equal(w.lon,f.geometry.x);assert.equal(w.lat,f.geometry.y);assert.equal(w.registryCode,f.attributes.FornID);assert.ok(w.sourceUrl.includes('objectIds='+w.objectId))}
});
test('searching for a wreck opens its event without turning on archaeology or wreck layers',()=>{
 const s={window:box.window,$:()=>({value:'Champagnevraket'}),openWreck:w=>{s.opened=w}};vm.createContext(s);vm.runInContext(source.slice(source.indexOf('function jumpToSearch()'),source.indexOf("$('#searchPlace').onclick")),s);s.jumpToSearch();assert.equal(s.opened,byId('champagne'));
});
test('ship symbols get a clickable map marker rather than a present-day footprint',()=>{
 const s=appContext(1933);Object.assign(s,{hits:[],W:100,H:100,screen:()=>[50,50],selected:null,ctx:new Proxy({},{get:()=>()=>{},set:()=>true}),iconFor:()=>({complete:true})});
 vm.runInContext(source.slice(source.indexOf('function storyMarkerMode('),source.indexOf('function sourceLink(')),s);assert.equal(s.storyMarkerMode(byId('plus')),'wreck');s.drawStoryPlaces();assert.equal(s.hits.length,1);assert.equal(s.hits[0].id,'wreck-plus');assert.equal(s.hits[0].size,26);
 s.year=1934;s.drawStoryPlaces();assert.equal(s.hits.length,0);
});

test('selecting a building during a wreck year does not attach the wreck dates or sources',()=>{
 const s={window:box.window};vm.createContext(s);vm.runInContext(source.slice(source.indexOf('function wreckForStory(')),s);
 const period={wreckId:'wreck-plus'};assert.equal(s.wreckForStory(null,period),byId('plus'));assert.equal(s.wreckForStory({id:'kastelholm'},period),null);assert.equal(s.wreckForStory(byId('skiftet'),period),byId('skiftet'));
});
