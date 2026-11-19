const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const OLD='road:eckero:gamla-landsvagen:holmberg',ORA='road:eckero:oravagen',M='road:marsund:eckero-hammarland';
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);

test('1929–1955: the road from the narrow sound runs straight across Holmberg to the ferry pier',()=>{
 for(const year of [1929,1950,1955]){
  const old=model.resolveObject(OLD,year);assert.equal(old.state,'open');assert.ok(grid.ownsRoadObject(OLD,v(year)));
  const m=model.resolveObject(M,year).geometry,start=old.geometry.paths[0][0];
  assert.ok(m.paths.some(p=>[p[0],p.at(-1)].some(q=>d(q,start)<1)),'joins the crossing');
 }
 assert.equal(model.resolveObject(OLD,1956).state,'unknown');assert.equal(model.resolveObject(OLD,1928).geometry,null);
 assert.equal(model.resolveObject(ORA,1955).geometry,null);
});

test('Öravägen from 1956, with its OSM line, owning the way in every extract so it is drawn once',()=>{
 const o=model.resolveObject(ORA,1956);assert.equal(o.state,'open');assert.equal(o.geometryPeriod.from,1956);
 const way=read('dist/assets/modern.json.gz').features.find(f=>f.id==='way/169282417');
 assert.deepEqual(o.geometry.paths,way.paths);assert.equal(model.resolveObject(ORA,2026).geometry.id,o.geometry.id);
 for(const [ds,id] of [['osm-2026','way/169282417'],['osm-2014','road-2014-169282417'],['osm-2021','road-2021-169282417'],['osm-2025','road-2025-169282417']])
  assert.ok(model.roadPartsForSource(ds,id).some(p=>p.objectId===ORA),ds);
});
