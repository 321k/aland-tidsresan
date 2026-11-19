const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const MAIN='road:qgis:lumparland:lemlandsvagen-100km3',SKOL='road:qgis:lumparland:skolsvangen-100km6',KLUB='road:qgis:lumparland:klubbensvagen-100km4',
 FISK='road:lumparland:fiskartorpsvagen',SODERBY='road:lemland:gamla-lemlandsvagen:mangard-soderby';
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
const near=(q,g)=>Math.min(...ends(g).map(e=>d(e,q)));
const len=g=>g.paths.reduce((n,p)=>n+p.slice(1).reduce((m,q,i)=>m+d(q,p[i]),0),0);

test('from 1917 the road east of the church village runs through Simons (Skolsvängen) and Granboda (Klubbensvägen)',()=>{
 for(const year of [1917,1928]){
  const m=model.resolveObject(MAIN,year).geometry,s=model.resolveObject(SKOL,year).geometry,k=model.resolveObject(KLUB,year).geometry;
  for(const id of [MAIN,SKOL,KLUB]){assert.equal(model.resolveObject(id,year).state,'open');assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year)}
  assert.equal(m.paths.length,2);
  assert.ok(near(m.paths[0][0],model.resolveObject(SODERBY,year).geometry)<1,'joins the old road from Söderby');
  assert.ok(near(s.paths[0][0],m)<1,'Skolsvängen leaves today\'s road');
  const gap=Math.min(...m.paths.map(p=>d(p[0],s.paths[0].at(-1))));
  assert.ok(gap>14&&gap<17,'its loop ends 15 m short (stated gap) '+gap);
  assert.ok(near(k.paths[0][0],m)<1,'Klubbensvägen leaves today\'s road at Granboda');
  assert.equal(model.resolveObject(FISK,year).geometry,null);
 }
 for(const id of [MAIN,SKOL,KLUB])assert.equal(model.resolveObject(id,1916).geometry,null);
});

test('from 1929 the road turns north on Fiskartorpsvägen and crosses Bergören to the sound',()=>{
 for(const year of [1929,1950,1967]){
  const m=model.resolveObject(MAIN,year).geometry,f=model.resolveObject(FISK,year).geometry,k=model.resolveObject(KLUB,year).geometry;
  assert.equal(m.paths.length,3);assert.ok(grid.ownsRoadObject(FISK,v(year)));
  assert.ok(near(f.paths[0][0],m)<1,'Fiskartorpsvägen meets the road across Bergören');
  assert.ok(k.paths[0].some(q=>d(q,f.paths[0].at(-1))<1),'and Klubbensvägen at its corner');
  assert.ok(d(m.paths[2].at(-1),model.resolveObject(MAIN,1968).geometry.paths[0].at(-1))<1,'to the sound');
 }
 assert.ok(len(model.resolveObject(MAIN,1929).geometry)-len(model.resolveObject(MAIN,1928).geometry)>500);
});

test('from 1968 today\'s road takes over; the old roads stay as they are mapped today',()=>{
 const m=model.resolveObject(MAIN,1968).geometry;assert.equal(m.paths.length,1);assert.ok(len(m)>7280);
 for(const id of [SKOL,KLUB,FISK])assert.equal(model.resolveObject(id,1968).state,'open');
 const way=read('dist/assets/modern.json.gz').features.find(f=>f.id==='way/349946211');
 assert.deepEqual(model.resolveObject(FISK,2026).geometry.paths,way.paths);
 for(const [ds,id] of [['osm-2026','way/349946211'],['osm-2021','road-2021-349946211'],['osm-2025','road-2025-349946211']])
  assert.ok(model.roadPartsForSource(ds,id).some(p=>p.objectId===FISK),ds);
 for(const id of [MAIN,SKOL,KLUB])assert.equal(model.objects.get(id).lemlandsvagenMainRoad.constructionYear,null);
});
