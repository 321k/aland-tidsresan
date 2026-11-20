const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const K='road:rural:hammarland-korsberg-old-road',P='road:rural:hammarland-hammarlandsvagen-postad-korsangen';
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);

test('1929–1967 the road at Postad runs in the old curve (register remnant Ha 17.8), not on today\'s straight line',()=>{
 for(const year of [1929,1950,1967]){
  const k=model.resolveObject(K,year),p=model.resolveObject(P,year).geometry;
  assert.equal(k.state,'open');assert.ok(grid.ownsRoadObject(K,v(year)));assert.equal(p.paths.length,2,'today\'s road leaves out the curve');
  for(const e of [k.geometry.paths[0][0],k.geometry.paths[0].at(-1)])assert.ok(ends(p).some(q=>d(e,q)<1),'the curve joins both stretches '+year);
 }
 assert.equal(model.resolveObject(K,1928).geometry,null);
 assert.equal(model.resolveObject(P,1968).geometry.paths.length,1);
 const k=model.objects.get(K);assert.ok(k.evidence.some(e=>e.observationType==='heritage-register'&&e.sourceId==='heritage-register:Ha 17.8'));
 assert.equal(k.mainRoadReview.constructionYear,null);
});

test('register road remnants are evidence on the roads they lie on, without changing their dates',()=>{
 const r=read('data/road-remnants.json');assert.ok(r.remnants.length>=10);
 for(const x of r.remnants){
  const o=model.objects.get(x.objectId);assert.ok(o.evidence.some(e=>e.sourceId===x.sourceId&&e.observationType==='heritage-register'),x.code);
  assert.ok(x.distanceMeters<=35,x.code);
 }
 assert.equal(model.resolveObject('road:qgis:lumparland:langnasvagen-100km3',1917).state,'open');
});
