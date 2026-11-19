const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const MAIN='road:qgis:lumparland:langnasvagen-100km3',SOD='road:lumparland:gamla-landsvagen:sodergard',SKAG='road:lumparland:gamla-landsvagen:skag',
 LEM='road:qgis:lumparland:lemlandsvagen-100km3';
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
const onEnd=(q,g)=>Math.min(...ends(g).map(e=>d(e,q)))<1;
const onLine=(q,g)=>g.paths.some(p=>p.some((a,i)=>i&&(()=>{const b=p[i-1],t=Math.max(0,Math.min(1,((q[0]-b[0])*(a[0]-b[0])*55600**2+(q[1]-b[1])*(a[1]-b[1])*111200**2)/(d(a,b)**2||1)));return d(q,[b[0]+t*(a[0]-b[0]),b[1]+t*(a[1]-b[1])])<1})()));

test('1917–1928: Skag–Södergård–Sjögård, with the old road through Södergård; no crossing yet',()=>{
 for(const year of [1917,1928]){
  const m=model.resolveObject(MAIN,year).geometry,s=model.resolveObject(SOD,year).geometry;
  assert.equal(m.paths.length,2);assert.ok(grid.ownsRoadObject(MAIN,v(year))&&grid.ownsRoadObject(SOD,v(year)));
  assert.ok(onLine(s.paths[0][0],m),'Södergård leaves the road at the junction');assert.ok(onEnd(s.paths[0].at(-1),m),'and rejoins at Krokstadviken');
  assert.equal(model.resolveObject(SKAG,year).geometry,null);
 }
 for(const id of [MAIN,SOD])assert.equal(model.resolveObject(id,1916).geometry,null);
});

test('1929–1967: from the crossing at Bergören over the Skag corner, joined to Lemlandsvägen',()=>{
 for(const year of [1929,1950,1967]){
  const m=model.resolveObject(MAIN,year).geometry,k=model.resolveObject(SKAG,year).geometry;
  assert.equal(m.paths.length,3);assert.ok(grid.ownsRoadObject(SKAG,v(year)));
  assert.ok(onEnd(m.paths[0][0],model.resolveObject(LEM,year).geometry),'continues Lemlandsvägen over the sound');
  assert.ok(onEnd(k.paths[0][0],m)&&onEnd(k.paths[0].at(-1),m),'the Skag corner joins both stretches');
 }
});

test('from 1968 today\'s road; the Skag corner survives as a track, Södergård is not claimed',()=>{
 assert.equal(model.resolveObject(MAIN,1968).geometry.paths.length,1);
 const k=model.resolveObject(SKAG,1968),way=read('dist/assets/modern.json.gz').features.find(f=>f.id==='way/349946241');
 assert.equal(k.state,'open');const w=JSON.stringify(way.paths[0]);assert.ok([w,JSON.stringify([...way.paths[0]].reverse())].includes(JSON.stringify(k.geometry.paths[0])),'the track with its OSM coordinates (in the old road\'s direction)');
 assert.ok(model.roadPartsForSource('osm-2026','way/349946241').some(p=>p.objectId===SKAG));
 assert.equal(model.resolveObject(SOD,1968).state,'unknown');
 assert.equal(model.objects.get(MAIN).mainRoadReview.constructionYear,null);
});
