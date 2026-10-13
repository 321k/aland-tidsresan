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
 assert.deepEqual(Array.from(routes.active(1959),r=>r.id),['viking-1959','slite-1959']);assert.equal(routes.active(1960).length,1);assert.equal(routes.active(1961).length,1);assert.equal(routes.active(2026).length,23);
});
test('hidden routes leave no clickable line; visible line supports clicks and distant misses',()=>{
 const ctx=new Proxy({},{get:(_,key)=>key==='measureText'?text=>({width:text.length*6}):()=>{},set:()=>true}),screen=(lon,lat)=>[lon*10,lat*10],view={year:1959,width:1000,height:1000};
 assert.equal(routes.draw(ctx,view,screen,false).length,0);
 const hits=routes.draw(ctx,view,screen,true),p=hits[0].path[0];assert.equal(routes.hit(hits,...p).id,hits[0].route.id);assert.equal(routes.hit(hits,900,100),null);
 view.year=1958;assert.equal(routes.draw(ctx,view,screen,true).length,0);
});

test('discontinued services disappear, Birka gap is preserved and cable filters work',()=>{
 const ids=y=>Array.from(routes.active(y),r=>r.id);
 assert.ok(ids(2025).includes('tvargaende-2025'));assert.ok(!ids(2026).includes('tvargaende-2025'));
 assert.ok(ids(2023).includes('rosella-2008'));assert.ok(!ids(2024).includes('rosella-2008'));
 assert.ok(ids(2020).includes('birka-1971'));for(const y of [2021,2022,2023])assert.ok(!ids(y).some(id=>id.startsWith('birka')));
 assert.ok(ids(2024).includes('birka-gotland-2024'));
 assert.equal(routes.active(2026,true,'cable').length,6);assert.equal(routes.active(2026,true,'historical').length,0);
 assert.equal(routes.active(2026,false,'cable').length,0);assert.equal(routes.active(2026,true,'all','norra-2026').length,1);
 assert.equal(routes.active(2026,true,'cable','norra-2026').length,0);
});
test('selected overlapping route wins hit testing and filtered routes leave no hits',()=>{
 const ctx=new Proxy({},{get:(_,key)=>key==='measureText'?text=>({width:text.length*6}):()=>{},set:()=>true});
 const screen=(lon,lat)=>[lon*10,lat*10],view={year:2026,width:1000,height:1000};
 const hits=routes.draw(ctx,view,screen,true,'birka-gotland-2024');
 assert.equal(routes.hit(hits,...screen(18.116,59.315)).id,'birka-gotland-2024');
 view.onlyRoute=true;const solo=routes.draw(ctx,view,screen,true,'norra-2026');assert.deepEqual(Array.from(solo,h=>h.route.id),['norra-2026']);
 view.routeGroup='cable';assert.equal(routes.draw(ctx,view,screen,true,'norra-2026').length,0);
});
test('curated route data has evidence, finite geometry and ports close to the mapped line',()=>{
 const source=JSON.parse(fs.readFileSync('data/transport-routes.json','utf8'));
 assert.deepEqual(JSON.parse(JSON.stringify(routes.routes)),source);
 assert.equal(new Set(source.map(r=>r.id)).size,source.length);
 for(const r of source){
  assert.ok(r.sources.length&&r.dateNote&&r.dateLabel&&r.from<=r.to,r.id);
  assert.ok(r.group in routes.groups,r.id);assert.ok(r.path.length>=2);
  for(const [name,url] of r.sources){assert.ok(name);assert.equal(new URL(url).protocol,'https:')}
  for(const p of r.path)assert.ok(p.length===2&&p.every(Number.isFinite),r.id);
  for(const p of r.ports)assert.ok(r.path.some(([lon,lat])=>Math.hypot((p.lon-lon)*.5,p.lat-lat)<.001),r.id+' '+p.name);
 }
});

test('Danish itinerary has an approximate source period, not an invented service lifetime',()=>{
 const r=routes.routes.find(r=>r.id==='danska-itinerariet');
 assert.equal(r.group,'medieval');assert.equal(r.dateKind,'source-window');assert.equal(r.focusYear,1300);
 assert.match(r.dateLabel,/osäker/);assert.match(r.dateNote,/inte som fastställd brukstid/);
 assert.equal(routes.active(1300,true,'medieval')[0].id,r.id);
 for(const year of [1199,1350,1959,2026])assert.ok(!routes.active(year).some(x=>x.id===r.id));
 assert.ok(r.sources.some(([,url])=>url==='https://www.uppslagsverket.fi/sv/view-170045-DanskaItinerariet'));
 assert.deepEqual(Array.from(r.ports,p=>p.name),['Arholma','Lemböte','Föglö · Kyrksundet?','Kökar · Hamnö','Aspö / Aspösund?']);
 assert.match(r.geometryNote,/Jurmo.*inte som ett belagt anlöp/);
});
test('medieval route story uses places and a sailing question instead of modern ferry ports',()=>{
 box.htmlEscape=s=>String(s);box.safeURL=s=>s;
 const r=routes.routes.find(r=>r.id==='danska-itinerariet'),story=routes.story(r);
 assert.match(story,/Platser i ruttutsnittet/);assert.match(story,/dricksvatten/);
 assert.match(story,/Wikipedia: Kung Valdemars segelled/);
 assert.doesNotMatch(story,/Hamnar i kartan|nå med färjorna/);
 const ferry=routes.story(routes.routes.find(r=>r.id==='eckero-1961'));
 assert.match(ferry,/Hamnar i kartan/);assert.match(ferry,/nå med färjorna/);
});
test('medieval line is clickable only inside its period and matching filter',()=>{
 const ctx=new Proxy({},{get:(_,k)=>k==='measureText'?s=>({width:s.length*6}):()=>{},set:()=>true});
 const screen=(lon,lat)=>[(lon-19)*200,(61-lat)*200],v={year:1300,width:1000,height:500,routeGroup:'medieval'};
 const hits=routes.draw(ctx,v,screen,true);assert.equal(hits.length,1);
 assert.equal(routes.hit(hits,...hits[0].path[0]).id,'danska-itinerariet');
 assert.equal(routes.draw(ctx,{...v,year:2026},screen,true).length,0);
 assert.equal(routes.draw(ctx,{...v,routeGroup:'archipelago'},screen,true).length,0);
});

test('postal route reaches Sweden and mainland Finland and switches harbour in 1756',()=>{
 const postal={window:{}};vm.createContext(postal);
 vm.runInContext(fs.readFileSync('dist/archive.js','utf8').split('(()=>{')[0],postal);
 for(const y of [1700,1755,1756,1911]){
  const stops=postal.window.postalRouteForYear(y);
  assert.equal(stops[0].country,'Sverige');assert.equal(stops.at(-1).country,'Finland');
  assert.ok(stops[0].lon<19);assert.ok(stops.at(-1).lon>21.4);
  assert.equal(stops[0].name,y<1756?'Gamla Grisslehamn':'Grisslehamn');
  for(const name of ['Signilskär','Eckerö','Kumlinge','Brändö','Vartsala Söderby'])assert.ok(stops.some(p=>p.name===name));
  assert.ok(stops.every(p=>Number.isFinite(p.lon)&&Number.isFinite(p.lat)));
 }
 for(const y of [1638,1699,1912,2026])assert.equal(postal.window.postalRouteForYear(y).length,0);
 const l=new box.Layers(()=>{},()=>{}),labels=[];
 box.window=postal.window;l.project=(lon,lat)=>[lon,lat];l.screen=p=>p;
 const ctx=new Proxy({},{get:(_,key)=>key==='fillText'?(label)=>labels.push(label):()=>{},set:()=>true});
 l.drawPostal(ctx,{year:1750,zoom:.5});assert.ok(labels.includes('Sverige'));assert.ok(labels.includes('Finland'));assert.ok(labels.includes('Gamla Grisslehamn'));
 labels.length=0;l.drawPostal(ctx,{year:1756,zoom:.5});assert.ok(labels.includes('Grisslehamn'));assert.ok(!labels.includes('Gamla Grisslehamn'));
});
