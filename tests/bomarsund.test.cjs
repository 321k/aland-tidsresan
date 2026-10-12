const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const box={window:{}};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/bomarsund.js','utf8'),box);
const plan=box.window.BomarsundPlan,places=box.window.BOMARSUND_PLACES,by=id=>places.find(f=>f.id===id);
test('Bomarsund buildings do not predate their documented start or overview attestation',()=>{
 for(const f of places){assert.equal(plan.visible(f,f.start-1,true,true),false);assert.equal(plan.state(f,f.start-1),'absent');assert.ok(plan.visible(f,f.start,true,false))}
 assert.equal(plan.state(by('bomarsund'),1832),'construction');assert.equal(plan.state(by('bomarsund'),1843),'standing');
 assert.equal(plan.state(by('bom-notvik'),1847),'construction');assert.equal(plan.state(by('bom-notvik'),1848),'standing');
 assert.equal(plan.state(by('bom-prasto'),1842),'construction');assert.match(by('bom-brannklint').dateNote,/inte ett uppgivet byggår/);
});
test('unfinished hospital and magazine never become complete buildings',()=>{
 for(const id of ['bom-new-hospital','bom-magazine']){const f=by(id);assert.equal(plan.state(f,1850),'absent');assert.equal(plan.state(f,1851),'construction');assert.equal(plan.state(f,1853),'construction');assert.equal(plan.state(f,1854),'ruin')}
});
test('1854 and present day preserve fortress ruins but hide expired settlements by default',()=>{
 for(const y of [1854,2026]){
  for(const id of ['bomarsund','bom-brannklint','bom-notvik','bom-prasto']){assert.ok(plan.visible(by(id),y,true,false));assert.equal(plan.state(by(id),y),'ruin')}
  for(const id of ['bom-nya-skarpans','bom-gamla-skarpans','bom-forstaden','bom-prasto-hospital','bom-office','bom-magazine','bom-new-hospital']){assert.equal(plan.visible(by(id),y,true,false),false);assert.ok(plan.visible(by(id),y,true,true))}
 }
 assert.ok(places.every(f=>!plan.visible(f,1853,false,true)));
});
test('the main plan and other mapped areas retain source geometry, while symbols are explicitly schematic',()=>{
 const p=JSON.parse(fs.readFileSync('data/bomarsund-provenance.json','utf8'));
 for(const f of places){assert.ok(f.lon>20.19&&f.lon<20.29&&f.lat>60.20&&f.lat<60.23);assert.ok(f.links.some(([label,url])=>url===p.reference));
  if(f.ring){assert.deepEqual(Array.from(f.ring[0]),Array.from(f.ring.at(-1)));assert.ok(f.ring.length>=4)}
 }
 const main=p.osmFeatures.find(f=>f.id==='way/218150765');assert.equal(JSON.stringify(by('bomarsund').ring),JSON.stringify(main.ring));assert.match(by('bomarsund').more,/schematisk/);
});
test('hit targets cover a building polygon and its label, and distant clicks miss',()=>{
 const source=fs.readFileSync('dist/app.js','utf8'),s={BomarsundPlan:plan};vm.createContext(s);vm.runInContext(source.slice(source.indexOf('function storyHit(')),s);
 const h={x:50,y:50,size:14,rings:[[[10,10],[100,10],[100,100],[10,100]]]};assert.ok(s.storyHit(h,90,90));assert.equal(s.storyHit(h,200,200),false);
 assert.ok(s.storyHit({labelRect:{x:20,y:20,w:150,h:20}},160,25));assert.equal(s.storyHit({labelRect:{x:20,y:20,w:150,h:20}},180,25),false);
});
test('overview suppresses tiny detailed plans while zoom reveals map geometry and clickable labels',()=>{
 const ctx=new Proxy({measureText:text=>({width:text.length*5})},{get:(o,k)=>o[k]||(()=>{}),set:()=>true}),screen=(lon,lat)=>[(lon-20.2)*12000,450-(lat-60.205)*20000];
 const low=plan.draw(ctx,places,screen,1853,5,null,1000,600);assert.equal(low.length,1);assert.equal(low[0].id,'bomarsund');
 const high=plan.draw(ctx,places,screen,1853,24,null,1000,600);assert.ok(high.some(h=>h.id==='bomarsund'&&h.rings));assert.ok(high.some(h=>h.id==='bom-notvik'&&h.labelRect));
});
