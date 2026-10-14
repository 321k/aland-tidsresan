const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const data=JSON.parse(fs.readFileSync('dist/assets/mariehamn-city-grid.json','utf8'));
class Path{moveTo(){}lineTo(){}closePath(){}}
const box={Path2D:Path,document:{getElementById:()=>null},htmlEscape:s=>String(s),safeURL:s=>s};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/city-grid.js','utf8')+';this.Grid=CityGrid',box);const Grid=box.Grid;
test('city grid changes only at source boundaries and never backdates the built city',()=>{
 const grid=new Grid(()=>{});grid.sets=structuredClone(data.sets);
 assert.equal(grid.stage(1859),undefined);
 for(const [year,source,kind]of [[1860,1860,'plan'],[1861,1860,'plan'],[1919,1860,'plan'],[1920,1920,'observed'],[1941,1920,'observed'],[1942,1942,'observed'],[2013,1942,'observed'],[2014,2014,'modern'],[2020,2014,'modern'],[2021,2021,'modern'],[2024,2021,'modern'],[2025,2025,'modern'],[2026,2026,'modern']]){assert.equal(grid.stage(year).year,source);assert.equal(grid.stage(year).kind,kind)}
 assert.equal(grid.stage(1860).counts.buildings,0);assert.equal(grid.stage(1920).counts.buildings,216);assert.equal(grid.stage(1942).counts.buildings,0);
 assert.ok(grid.replacesRoads(1942));assert.ok(!grid.replacesRoads(2014));grid.enabled=false;assert.ok(!grid.replacesRoads(1942));
});
test('traced grids have connected intersections, finite geometry and source metadata',()=>{
 const ids=new Set();
 for(const d of data.sets){assert.ok(d.note&&d.source);assert.ok(d.counts.blocks>20);for(const f of d.features){assert.ok(!ids.has(f.id));ids.add(f.id);for(const path of f.paths){assert.ok(path.length>=2);for(const [lon,lat] of path){assert.ok(Number.isFinite(lon)&&Number.isFinite(lat));assert.ok(lon>19.90&&lon<19.97&&lat>60.07&&lat<60.15)}if(f.kind!=='street')assert.deepEqual(path[0],path.at(-1))}}}
 for(const d of data.sets.filter(d=>d.kind!=='modern'))assert.equal(d.topology.components,1,d.id);
 assert.ok(data.sets.find(d=>d.year===1942).counts.streets>data.sets.find(d=>d.year===1920).counts.streets);
});
test('city geometry and hit targets disappear outside its period or when disabled',()=>{
 const grid=new Grid(()=>{});grid.sets=structuredClone(data.sets);
 const ctx=new Proxy({isPointInPath:()=>true,isPointInStroke:()=>true,measureText:s=>({width:s.length*6})},{get:(o,k)=>o[k]||(()=>{}),set:(o,k,v)=>(o[k]=v,true)});
 const v={year:1920,zoom:30,width:800,height:600,scale:1,panX:0,panY:0,meta:{width:800,height:600,world:262144}},project=(lon,lat)=>[(lon-19.92)*10000,(60.11-lat)*10000];
 grid.draw(ctx,v,project);assert.ok(grid.drawn.some(f=>f.kind==='building'));const f=grid.drawn[0],x=(f.bounds[0]+f.bounds[2])/2,y=(f.bounds[1]+f.bounds[3])/2;assert.ok(grid.hit(x,y,ctx));
 grid.draw(ctx,{...v,year:1942},project);assert.ok(!grid.drawn.some(f=>f.kind==='building'));
 grid.draw(ctx,{...v,year:1859},project);assert.equal(grid.drawn.length,0);assert.equal(grid.hit(x,y,ctx),null);
 grid.enabled=false;grid.draw(ctx,v,project);assert.equal(grid.drawn.length,0);assert.equal(grid.hit(x,y,ctx),null);
});
test('feature stories distinguish planned streets, inferred blocks and undated roof symbols',()=>{
 const grid=new Grid(()=>{});grid.sets=structuredClone(data.sets);
 for(const d of grid.sets)grid.prepare(d,(lon,lat)=>[lon,lat]);
 const plan=grid.stage(1860);assert.match(grid.story(plan.features.find(f=>f.kind==='street')),/planerat/);
 assert.match(grid.story(grid.stage(1920).features.find(f=>f.kind==='block')),/inte en fastighetsgräns/);
 const house=grid.story(grid.stage(1920).features.find(f=>f.kind==='building'));assert.match(house,/betyder inte att huset revs/);assert.match(house,/data-city-grid-year="1942"/);
});

test('established modern city streets retain identical geometry between 2014 and 2023',()=>{
 const recent=data.sets.filter(d=>d.year>=2014),grid=new Grid(()=>{});grid.sets=structuredClone(data.sets);
 assert.equal(grid.stage(2023).year,2021);
 const paths=(d,name)=>d.features.filter(f=>f.kind==='street'&&f.name===name).map(f=>JSON.stringify(f.paths)).sort();
 for(const name of ['Storagatan','Norragatan','Södragatan','Torggatan']){
  const reference=paths(recent[0],name);assert.ok(reference.length>0,name);
  for(const d of recent.slice(1))assert.deepEqual(paths(d,name),reference,name+' '+d.year);
 }
 for(const d of recent){assert.equal(d.geometryYear,2026);assert.equal(d.normalizedStreets,true);assert.match(d.note,/inte antaget byggår/)}
});
test('unified recent streets only replace underlying roads within the city and at visible zoom',()=>{
 const grid=new Grid(()=>{});grid.sets=structuredClone(data.sets);grid.coverage=data.coverage;
 const v={year:2023,zoom:20},project=(lon,lat)=>[lon,-lat];
 assert.equal(grid.ownsRecentPoint(project(19.94,60.10),v,project),true);
 assert.equal(grid.ownsRecentPoint(project(20.0,60.24),v,project),false);
 assert.equal(grid.ownsRecentPoint(project(19.94,60.10),{...v,zoom:1},project),false);
 grid.enabled=false;assert.equal(grid.ownsRecentPoint(project(19.94,60.10),v,project),false);
});
