const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const box={};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/transport-routes.js','utf8')+';this.Routes=TransportRoutes;',box);vm.runInContext(fs.readFileSync('dist/explorer.js','utf8')+';this.Layers=ExplorerLayers;',box);
const routes=box.Routes;
test('postal line ends after 1911 and is not restored by older-traces mode',()=>{
 const l=new box.Layers(()=>{},()=>{});let calls=0;const ctx=new Proxy({},{get:()=>()=>calls++,set:()=>true});l.flags.traces=true;
 for(const y of [1638,1699,1912,1959,2026]){assert.equal(box.Layers.postalVisible(y),false);l.drawPostal(ctx,{year:y});assert.equal(calls,0)}
 for(const y of [1700,1750,1900,1910,1911])assert.equal(box.Layers.postalVisible(y),true);
 l.prepared=true;l.drawHeritage=l.updateList=l.drawModern=l.drawCoast=()=>{};l.drawPostal=()=>calls++;
 l.render({}, {year:1911});assert.equal(calls,1);l.render({}, {year:1912});assert.equal(calls,1);
});
test('shipping routes obey their individual evidence intervals and layer switch',()=>{
 for(const route of routes.routes){assert.equal(routes.visible(route,route.from-1),false);assert.equal(routes.visible(route,route.from),true);assert.equal(routes.visible(route,route.to),true);assert.equal(routes.visible(route,route.to+1),false);assert.equal(routes.visible(route,route.from,false),false)}
 assert.deepEqual(Array.from(routes.active(1959),r=>r.id),['viking-1959']);assert.equal(routes.active(1960).length,0);assert.equal(routes.active(1961).length,1);assert.equal(routes.active(2026).length,2);
});
test('hidden routes leave no clickable line; visible line supports clicks and distant misses',()=>{
 const ctx=new Proxy({},{get:()=>()=>{},set:()=>true}),screen=(lon,lat)=>[lon*10,lat*10],view={year:1959,width:1000,height:1000};
 assert.equal(routes.draw(ctx,view,screen,false).length,0);
 const hits=routes.draw(ctx,view,screen,true),p=hits[0].path[0];assert.equal(routes.hit(hits,...p).id,'viking-1959');assert.equal(routes.hit(hits,900,100),null);
 view.year=1960;assert.equal(routes.draw(ctx,view,screen,true).length,0);
});
