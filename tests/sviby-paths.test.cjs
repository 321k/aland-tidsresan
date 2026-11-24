const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{constructor(){this.points=[]}moveTo(x,y){this.points.push([x,y])}lineTo(x,y){this.points.push([x,y])}closePath(){}rect(){}addPath(){}}
const box={Path2D:Path,document:{getElementById:()=>null},htmlEscape:s=>String(s),safeURL:s=>s};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';'+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const catalog=read('dist/assets/temporal-objects.json.gz'),model=new box.Model(catalog);
const EW='road:jomala:sviby:vagen-mot-svibyvagen',NP='road:jomala:norra-mockelovagen:norra-delen';
const len=p=>p.slice(1).reduce((s,q,i)=>s+Math.hypot(q[0]-p[i][0],q[1]-p[i][1]),0);

test('the roads at Sviby that became paths are paths from their first evidence, and roads before it',()=>{
 const at=(id,y)=>box.Grid.roadClassPeriod(model.objects.get(id),y);
 // the east–west road: the west 252 m a cycleway from the OSM extract 2025, the whole road a road before
 assert.equal(at(EW,2024),null);assert.equal(at(EW,2025).class,'cycleway');assert.equal(at(EW,2026).canonicalRange.join(),'0,0.5969');
 assert.equal(model.objects.get(EW).modernRoadClass,'residential');
 // the north piece of Norra Möckelövägen: a road 1929–2006, a path (its modern class, cycleway) from the photo of 2007
 assert.equal(at(NP,1929).class,'residential');assert.equal(at(NP,2006).class,'residential');assert.equal(at(NP,2007),null);assert.equal(model.objects.get(NP).modernRoadClass,'cycleway');
 for(const id of [EW,NP]){assert.equal(model.resolveObject(id,2026).state,'open');for(const p of model.objects.get(id).roadClassPeriods)assert.ok(p.evidenceIds.every(e=>model.objects.get(id).evidence.some(x=>x.id===e)))}
});

test('a ranged class period splits the drawn line at its fraction of the length',()=>{
 const o=model.objects.get(EW),r=model.resolveObject(EW,2026),project=(lon,lat)=>[lon*55600,-lat*111200];
 const f={kind:'street',class:'residential',path:new Path(),objectResolution:r};
 const parts=box.Grid.classParts(f,r.geometry.paths,project,2026);
 assert.equal(parts.map(p=>p.cls).join(),'cycleway,residential');
 const total=len(r.geometry.paths[0].map(q=>project(...q))),west=len(parts[0].path.points);
 assert.ok(Math.abs(west/total-0.5969)<0.001,String(west/total));
 assert.equal(box.Grid.classParts(f,r.geometry.paths,project,2020),null);
 const n=model.resolveObject(NP,1950);assert.equal(box.Grid.classParts({kind:'street',class:'cycleway',path:new Path(),objectResolution:n},n.geometry.paths,project,1950).map(p=>p.cls).join(),'residential');
});

test('invalid road class periods are rejected',()=>{
 const bad=structuredClone(catalog),o=bad.objects.find(o=>o.id===EW);o.roadClassPeriods.push({from:2020,to:null,class:'footway',basis:'x',evidenceIds:o.roadClassPeriods[0].evidenceIds});
 assert.throws(()=>new box.Model(bad),/Invalid road class period/);
 const bad2=structuredClone(catalog);bad2.objects.find(o=>o.id===EW).roadClassPeriods[0].canonicalRange=[0,1.2];
 assert.throws(()=>new box.Model(bad2),/Invalid road class period/);
});
