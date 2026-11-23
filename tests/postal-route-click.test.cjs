const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const data=read('data/postal-route-stations.json'),cat=read('dist/assets/temporal-objects.json.gz'),ids=new Set(cat.objects.map(o=>o.id));
const b={URL};vm.createContext(b);b.window=b;
vm.runInContext(fs.readFileSync('dist/postal-route-roads.js','utf8')+fs.readFileSync('dist/archive.js','utf8').split('(()=>{')[0]+fs.readFileSync('dist/explorer.js','utf8')+';this.Layers=ExplorerLayers;',b);
const legs=JSON.parse(JSON.stringify(b.POSTAL_ROUTE_ROADS));
const layer=year=>{const l=new b.Layers(()=>{},()=>{});l.project=(lon,lat)=>[lon*20000,-lat*40000];l.screen=p=>p;
 l.drawPostal(new Proxy({},{get:(_,k)=>k==='measureText'?()=>({width:1}):()=>{},set:()=>true}),{year,zoom:1});return l};

test('Vårdö to Kumlinge: by road through Vårdö by to Hullvik, by boat over Delet, by Södra and Norra postvägen to Krokarna',()=>{
 const leg=legs.find(l=>l.from==='vargata'&&l.to==='kumlinge');assert.deepEqual(leg.years,[1638,1911]);
 assert.deepEqual(leg.parts.map(p=>p.by),['road','boat','road']);
 assert.ok(leg.parts[0].objects.some(o=>o.id==='road:qgis:vardo:postrotevagen-200km1'),'Postrotevägen to Hullvik');
 assert.ok(leg.parts[2].objects.some(o=>o.id==='road:qgis:kumlinge:sodra-postvagen-200km2'),'Södra postvägen on Kumlinge');
 assert.ok(leg.parts[1].path.length>5);
 const k=data.stations.find(s=>s.id==='kumlinge');assert.equal(k.registryId,'Ku 4.5');
});

test('the postal route is clickable: a leg opens its story with its roads, a station its place',()=>{
 const l=layer(1700),legHit=l.postalHits.find(h=>h.path&&h.feature.leg?.from==='emkarby');
 const mid=legHit.path[Math.floor(legHit.path.length/2)],f=l.hit(mid[0]+1,mid[1]);
 assert.equal(f.recordType,'postalRoute');assert.equal(f.leg.from,'emkarby');assert.deepEqual(JSON.parse(JSON.stringify(f.leg.years)),[1638,1760]);
 const story=l.story(f,1700);assert.match(story,/Emkarby–Haraldsby/);assert.match(story,/data-temporal-object="road:finstrom:gamla-farjvagen:farjsundet"/);assert.match(story,/Färjsundet \(till 1761\)/);
 const sea=l.postalHits.find(h=>h.path&&!h.feature.leg);assert.match(l.story(sea.feature,1700),/schematisk/);
 const st=l.postalHits.find(h=>h.feature.stop?.station==='storby');const sf=l.hit(st.x,st.y);
 assert.equal(sf.recordType,'postalStation');assert.match(l.story(sf,1700),/data-temporal-object="building:osm:way-342899630"/);
 l.selected=f.id;l.drawPostal(new Proxy({},{get:()=>()=>{},set:()=>true}),{year:1700,zoom:1});
});

test('stations tied to a building or site point at catalogue objects, at their position',()=>{
 const m=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
 for(const s of data.stations.filter(s=>s.objectId)){
  assert.ok(ids.has(s.objectId),s.objectId);
  const o=cat.objects.find(o=>o.id===s.objectId),g=cat.geometries.find(g=>g.id===o.geometryPeriods.at(-1).geometryId).paths.flat();
  assert.ok(g.some(p=>m(p,[s.lon,s.lat])<60),s.id+' lies at its object');
 }
 assert.deepEqual(data.stations.filter(s=>s.objectId||s.registryId).map(s=>s.id).sort(),['kumlinge','skarpans','storby']);
});
