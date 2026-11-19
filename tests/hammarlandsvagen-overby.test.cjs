const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid','historical-roads'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid;this.Roads=HistoricalRoads',box);
const catalogue=read('dist/assets/temporal-objects.json.gz'),model=new box.Model(catalogue),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const OLD='road:eckero:gamla-landsvagen:overby',M='road:marsund:eckero-hammarland',review=read('data/hammarlandsvagen-overby.json');
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const ends=paths=>paths.flatMap(p=>[p[0],p.at(-1)]);

test('the main road runs through Överby village until the 1985 bypass, as one connected line',()=>{
 for(const year of [1929,1950,1958,1968,1978,1984]){
  const old=model.resolveObject(OLD,year),m=model.resolveObject(M,year);
  assert.equal(old.state,'open');assert.equal(old.geometry.paths.length,2);assert.ok(grid.ownsRoadObject(OLD,v(year)));
  // every end of the two loops lies on the connection drawn that year (within 1 m)
  for(const e of ends(old.geometry.paths))assert.ok(ends(m.geometry.paths).some(q=>d(e,q)<1),year+' '+e);
 }
 // the bypass is left out until 1985, then the connection is whole again
 assert.equal(model.resolveObject(M,1984).geometry.id,'geometry:hammarlandsvagen-overby:marsund-without-bypass');
 assert.equal(model.resolveObject(M,1985).geometry.paths.length,19);
 const ev=model.resolveObject(M,1985).object.evidence.filter(e=>e.reviewId==='review:hammarlandsvagen-overby');
 assert.deepEqual(ev.map(e=>[e.describes.from,e.outcome]),[[1968,'absent'],[1978,'unclear'],[1985,'present']]);
});

test('after the bypass only Brinkbacken and Gamla Landsvägen remain, with the same coordinates, owned in OSM',()=>{
 const early=model.resolveObject(OLD,1984).geometry.paths,later=model.resolveObject(OLD,1985).geometry.paths;
 assert.equal(later.length,2);
 const key=q=>q.join(',');
 for(const p of later){const s=new Set(early.flat().map(key));assert.ok(p.every(q=>s.has(key(q))),'a surviving part moved');}
 const modern=read('dist/assets/modern.json.gz').features;
 for(const [k,link] of review.oldRoad.sourceLinks.entries()){
  const parts=model.roadPartsForSource('osm-2026',link.featureId);
  assert.ok(parts.some(p=>p.objectId===OLD&&p.sourceVertexRange[0]===link.sourceVertexRange[0]&&p.sourceVertexRange[1]===link.sourceVertexRange[1]),link.featureId);
  const f=modern.find(x=>x.id===link.featureId),run=f.paths[0].slice(link.sourceVertexRange[0],link.sourceVertexRange[1]+1);
  assert.ok([run,[...run].reverse()].some(r=>JSON.stringify(r)===JSON.stringify(later[k])));
 }
 assert.equal(model.resolveObject(OLD,2026).state,'open');assert.equal(model.resolveObject(OLD,1928).geometry,null);
});

test('the 1894 atlas line is hidden beside the old road through Överby',()=>{
 const atlas=read('dist/assets/historical-roads.json').sets.find(s=>s.id==='atlas-1894').features.find(f=>f.id==='atlas-1894-1');
 for(const year of [1950,1975]){const g=model.resolveObject(OLD,year).geometry.id;assert.ok(atlas.replacementIntervals.some(r=>r.objectId===OLD&&r.geometryId===g),year);}
 assert.equal(catalogue.objects.find(o=>o.id===OLD).evidence.filter(e=>e.id===OLD+':regional-context:atlas-1894-1').length,1);
});
