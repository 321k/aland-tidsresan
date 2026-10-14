const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const app=fs.readFileSync('dist/app.js','utf8'),data=JSON.parse(fs.readFileSync('data/ofreden.json'));
const box={window:{},URL};vm.createContext(box);
for(const file of ['ofreden-data.js','wrecks-data.js','bomarsund.js','places-data.js','timeline-model.js','explorer.js'])vm.runInContext(fs.readFileSync('dist/'+file,'utf8'),box);
box.WreckTimeline=box.window.WreckTimeline;
vm.runInContext(app.slice(0,app.indexOf('const LAST='))+';this.stops=eras;this.places=buildings;',box);
vm.runInContext('this.Layer=ExplorerLayers;this.time=EvidenceTime;',box);
function visible(year,on=true){const s={year,buildings:data.places,$:()=>({checked:on})};vm.createContext(s);vm.runInContext(app.slice(app.indexOf('function visible()'),app.indexOf('// Only explicitly')),s);return s.visible().map(p=>p.id)}
test('ofreden events exist in the real timeline, sorted with valid sources and place links',()=>{
 for(const e of data.events){assert.equal(box.stops.filter(s=>s.y===e.y).length,1);assert.ok(data.sources[e.src]);if(e.ofredenPlace)assert.ok(data.places.some(p=>p.id===e.ofredenPlace&&e.y>=p.start&&e.y<=p.end));}
 for(let i=1;i<box.stops.length;i++)assert.ok(box.stops[i].y>box.stops[i-1].y);
 assert.equal(new Set(box.places.map(p=>p.id)).size,box.places.length);
});
test('event places only show during attested years and the layer can hide them',()=>{
 for(const p of data.places){assert.ok(!visible(p.start-1).includes(p.id));assert.ok(visible(p.start).includes(p.id));assert.ok(visible(p.end).includes(p.id));assert.ok(!visible(p.end+1).includes(p.id));assert.ok(!visible(p.start,false).includes(p.id));}
 assert.deepEqual(visible(2026),[]);assert.deepEqual(visible(1719),['ofreden-lovo','ofreden-flaka']);assert.deepEqual(visible(1720),['ofreden-ledsund']);
});
test('registry evidence uses the attested interval and does not duplicate active curated places',()=>{
 const layer=new box.Layer(()=>{},()=>{});layer.storyPlaces=data.places;layer.flags.ofreden=true;
 const registry=JSON.parse(fs.readFileSync('dist/assets/heritage.json')).features;
 for(const p of data.places)for(const code of p.registryCodes){const f=registry.find(f=>f.code===code);assert.equal(box.time.state(f,p.start-1),'future');assert.equal(box.time.state(f,p.start),'attested');assert.equal(box.time.state(f,p.end+1),'trace');assert.equal(layer.available(f,p.start),false);layer.flags.ofreden=false;assert.equal(layer.available(f,p.start),true);layer.flags.ofreden=true;assert.equal(layer.available(f,2026),false);layer.flags.traces=true;assert.equal(layer.available(f,2026),true);layer.flags.traces=false;}
});
test('searching from the present opens the historical event without enabling archaeology traces',()=>{
 const s={window:{OFREDEN:data,WRECKS:[]},$:()=>({value:'Lövö'}),openOfreden:(...args)=>s.opened=args};vm.createContext(s);vm.runInContext(app.slice(app.indexOf('function jumpToSearch()'),app.indexOf("$('#searchPlace').onclick")),s);s.jumpToSearch();assert.deepEqual(s.opened,[1718,true]);
});
test('sources preserve location and dating limitations rather than inventing footprints or lifetimes',()=>{
 assert.deepEqual(JSON.parse(JSON.stringify(box.window.OFREDEN)),data);
 for(const p of data.places){assert.ok(p.precision);assert.ok(Number.isFinite(p.lon)&&Number.isFinite(p.lat));assert.ok(!p.paths&&!p.osmId&&!p.recon);assert.equal(new URL(data.sources[p.src][1]).protocol,'https:');}
 const skans=data.places.find(p=>p.id==='ofreden-degerby');assert.match(skans.more,/inte att den revs 1744/);assert.match(skans.precision,/Bymarkör/);
 const battle=data.places.find(p=>p.id==='ofreden-ledsund');assert.match(battle.more,/ingen entydig segrare/);
});
