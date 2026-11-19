const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const M='road:marsund:eckero-hammarland',K='road:eckero:gamla-landsvagen:kyrkoby-bole',B='road:eckero:gamla-landsvagen:bagars';
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);

test('1929–1958: from Kyrkoby the road runs on the old lines and the connection’s stretches, one connected line to Storby',()=>{
 for(const year of [1929,1950,1958]){
  const m=model.resolveObject(M,year).geometry;
  for(const id of [K,B]){const o=model.resolveObject(id,year);assert.equal(o.state,'open');assert.ok(grid.ownsRoadObject(id,v(year)));
   for(const e of ends(o.geometry))assert.ok(ends(m).some(q=>d(e,q)<1),id+' '+year);}
 }
});

test('from 1959 only the surviving parts are drawn, with their old coordinates, owned in OSM',()=>{
 const review=read('data/hammarlandsvagen-kyrkoby.json');
 for(const od of review.oldRoads){
  const early=model.resolveObject(od.id,1958).geometry.paths,later=model.resolveObject(od.id,1959).geometry.paths;
  assert.deepEqual(later,od.laterPaths);const all=new Set(early.flat().map(q=>q.join(',')));
  for(const p of later)assert.ok(p.every(q=>all.has(q.join(','))),od.id);
  for(const l of od.sourceLinks)assert.ok(model.roadPartsForSource('osm-2026',l.featureId).some(p=>p.objectId===od.id),l.featureId);
  assert.equal(model.resolveObject(od.id,2026).state,'open');assert.equal(model.resolveObject(od.id,1928).geometry,null);
 }
});
