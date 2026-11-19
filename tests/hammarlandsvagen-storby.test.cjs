const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const M='road:marsund:eckero-hammarland',OLD='road:eckero:gamla-landsvagen:storby';
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
const len=p=>p.slice(1).reduce((n,q,i)=>n+d(q,p[i]),0);

test('until 1978 the main road runs through Storby village; the connection leaves out the bypass',()=>{
 for(const year of [1929,1950,1959,1968,1977]){
  const old=model.resolveObject(OLD,year),m=model.resolveObject(M,year).geometry;
  assert.equal(old.state,'open');assert.ok(grid.ownsRoadObject(OLD,v(year)));assert.equal(old.geometry.paths.length,1);
  for(const e of ends(old.geometry))assert.ok(ends(m).some(q=>d(e,q)<1),year+' '+e);
 }
 const total=g=>g.paths.reduce((n,p)=>n+len(p),0);
 assert.ok(total(model.resolveObject(M,1978).geometry)-total(model.resolveObject(M,1977).geometry)>850,'the 870 m bypass from 1978');
 assert.equal(model.resolveObject(M,1977).geometry.id,'geometry:hammarlandsvagen-storby:without-bypass');
});

test('from 1978 only the village roads that survive are drawn, owned in OSM',()=>{
 const od=read('data/hammarlandsvagen-storby.json').oldRoads[0];
 const later=model.resolveObject(OLD,1978).geometry.paths,early=new Set(model.resolveObject(OLD,1977).geometry.paths.flat().map(q=>q.join(',')));
 assert.deepEqual(later,od.laterPaths);for(const p of later)assert.ok(p.every(q=>early.has(q.join(','))));
 for(const l of od.sourceLinks)assert.ok(model.roadPartsForSource('osm-2026',l.featureId).some(p=>p.objectId===OLD),l.featureId);
 assert.equal(model.resolveObject(OLD,1928).geometry,null);
});
