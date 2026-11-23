const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz'));
const w={};vm.createContext(w);w.window=w;vm.runInContext(fs.readFileSync('dist/postal-route-roads.js','utf8'),w);
const legs=JSON.parse(JSON.stringify(w.POSTAL_ROUTE_ROADS)),data=read('data/postal-route-stations.json');
const m=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const OLD='road:finstrom:gamla-farjvagen:farjsundet';

test('the old ferry road at Färjsundet (Fi 8.17) is the road until 1761 and the route crosses there until then',()=>{
 assert.equal(model.resolveObject(OLD,1650).state,'open');assert.equal(model.resolveObject(OLD,1760).state,'open');
 assert.notEqual(model.resolveObject(OLD,1761).state,'open');
 const ev=model.objects.get(OLD).evidence;
 assert.ok(ev.some(e=>e.sourceId==='review:postal-route-1761:fi-8-17'&&e.observationType==='heritage-register'&&e.describes.from===1761));
 const early=legs.find(l=>l.from==='emkarby'&&l.years[1]===1760),late=legs.find(l=>l.from==='emkarby'&&l.years[0]===1761);
 assert.deepEqual(early.ferries,['farjsundet-1761']);assert.ok(early.objects.some(o=>o.id===OLD));
 assert.deepEqual(late.ferries,['farjsundet']);assert.ok(!late.objects.some(o=>o.id===OLD));
});

test('the boat to Vårdö leaves from Delvik before 1670 and from the Bomarsund pier after, to Båthusviken in Vargata',()=>{
 const delvik=legs.find(l=>l.from==='delvik'),bomar=legs.find(l=>l.from==='skarpans');
 assert.deepEqual(delvik.years,[1638,1669]);assert.deepEqual(bomar.years,[1670,1911]);
 assert.deepEqual(legs.find(l=>l.to==='delvik').years,[1638,1669]);assert.deepEqual(legs.find(l=>l.to==='skarpans').years,[1670,1911]);
 for(const leg of [delvik,bomar]){
  const boat=leg.parts.find(p=>p.by==='boat'),land=leg.parts.at(-1);
  assert.ok(boat.path.length>3&&m(boat.path.at(-1),[20.327576,60.241812])<1,'lands at Båthusviken');
  assert.equal(land.by,'road');assert.ok(land.objects.some(o=>o.id==='road:qgis:vardo:bathusviksvagen-200km1'));
 }
 assert.equal(bomar.parts[0].by,'road');assert.ok(bomar.parts[0].objects.some(o=>o.id==='road:sund:gamla-landsvagen:bomarsund'),'to the Bomarsund pier on the 1928 road');
 assert.equal(delvik.parts[0].by,'boat','Delvik is itself the pier');
});

test('the map draws each year\'s legs: road parts solid, boat lines dashed, the old Färjsundet ferry place until 1760',()=>{
 const b={};vm.createContext(b);b.window=b;
 vm.runInContext(fs.readFileSync('dist/postal-route-roads.js','utf8')+fs.readFileSync('dist/archive.js','utf8').split('(()=>{')[0]+fs.readFileSync('dist/explorer.js','utf8')+';this.Layers=ExplorerLayers;',b);
 const draw=year=>{
  const strokes=[];let dash=[],pts=[];
  const ctx=new Proxy({},{get:(_,k)=>k==='setLineDash'?d=>{dash=[...d]}:k==='beginPath'?()=>{pts=[]}:k==='moveTo'||k==='lineTo'?(x,y)=>pts.push([x,y]):k==='stroke'?()=>{if(pts.length)strokes.push({dashed:dash.length>0,pts})}:k==='measureText'?()=>({width:1}):()=>{},set:()=>true});
  const l=new b.Layers(()=>{},()=>{});l.project=(lon,lat)=>[lon,lat];l.screen=p=>p;l.drawPostal(ctx,{year,zoom:1});return strokes};
 const near=(s,p)=>s.pts.some(q=>m(q,p)<5);
 const OLDPIER=JSON.parse(JSON.stringify(data.crossings.find(c=>c.id==='farjsundet-1761').from)),NEWPIER=JSON.parse(JSON.stringify(data.crossings.find(c=>c.id==='farjsundet').from));
 const DELVIK=[20.211197,60.246827],PIER=legs.find(l=>l.from==='skarpans').parts[1].path[0];
 const y1650=draw(1650),y1700=draw(1700),y1800=draw(1800);
 assert.ok(y1650.some(s=>s.dashed&&near(s,DELVIK))&&!y1650.some(s=>near(s,PIER)),'1650: the boat from Delvik');
 assert.ok(y1700.some(s=>s.dashed&&near(s,PIER))&&!y1700.some(s=>s.dashed&&near(s,DELVIK)),'1700: the boat from Bomarsund');
 assert.ok(y1700.some(s=>!s.dashed&&near(s,OLDPIER))&&!y1700.some(s=>near(s,NEWPIER)),'1700: the old ferry place at Färjsundet');
 assert.ok(y1800.some(s=>!s.dashed&&near(s,NEWPIER))&&!y1800.some(s=>near(s,OLDPIER)),'1800: the new ferry place');
});
