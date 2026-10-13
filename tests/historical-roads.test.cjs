const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),zlib=require('node:zlib');
class Path {constructor(){this.points=[]}moveTo(x,y){this.points.push([x,y])}lineTo(x,y){this.points.push([x,y])}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/historical-roads.js','utf8')+';this.Roads=HistoricalRoads;',box);const Roads=box.Roads;
const curated=JSON.parse(fs.readFileSync('dist/assets/historical-roads.json','utf8'));
test('road sources follow time without backdating current or later snapshots',()=>{
 const ids=y=>Array.from(Roads.sourceIds(y));
 assert.deepEqual(ids(1799),[]);assert.deepEqual(ids(1800),['alvin-1800']);assert.deepEqual(ids(1893),['alvin-1800']);
 assert.deepEqual(ids(1894),['atlas-1894']);assert.deepEqual(ids(1919),['atlas-1894']);
 assert.deepEqual(ids(1920),['atlas-1894','museum-1920']);assert.deepEqual(ids(1941),['atlas-1894','museum-1920']);
 assert.deepEqual(ids(1942),['atlas-1894','museum-1920','photo-1942']);
 for(const y of [2014,2020])assert.deepEqual(ids(y),['osm-2014']);for(const y of [2021,2024])assert.deepEqual(ids(y),['osm-2021']);
 assert.deepEqual(ids(2025),['osm-2025']);assert.deepEqual(ids(2026),[]);
});
test('curated road geometry is finite, sourced and keeps sea crossings separate',()=>{
 assert.equal(curated.sets.length,4);
 for(const d of curated.sets){assert.ok(d.source.startsWith('https://'));assert.ok(d.note);assert.ok(d.features.length>=5);for(const f of d.features)for(const p of f.paths.flat()){assert.ok(p.every(Number.isFinite));assert.ok(p[0]>19&&p[0]<21.5&&p[1]>59.7&&p[1]<60.6)}}
 const early=curated.sets.find(d=>d.year===1800);assert.ok(early.features.some(f=>f.name.includes('norra stranden')));assert.ok(early.features.some(f=>f.name.includes('södra sidan')));
 assert.ok(!curated.sets.some(d=>d.year===1860),'A planned city is not an existing road network');
});
test('historical OSM snapshots contain roads throughout Åland, not current building footprints',()=>{
 for(const year of [2014,2021,2025]){
  const d=JSON.parse(zlib.gunzipSync(fs.readFileSync(`dist/assets/roads-${year}.json.gz`)));
  assert.equal(d.year,year);assert.equal(d.snapshot.slice(0,4),String(year));assert.ok(d.features.length>4000);assert.equal(new Set(d.features.map(f=>f.id)).size,d.features.length);
  for(const [name,lon,lat]of [['Mariehamn',19.94,60.1],['Godby',19.99,60.24],['Brändö',21.045,60.41],['Kökar',20.9,59.92]])assert.ok(d.features.some(f=>f.paths.flat().some(p=>Math.abs(p[0]-lon)<.07&&Math.abs(p[1]-lat)<.04)),name+' '+year);
  for(const f of d.features){assert.ok(f.class&&!['proposed','construction','abandoned','razed','platform'].includes(f.class));assert.ok(f.osmId.startsWith('way/'));assert.ok(!('building' in f));for(const p of f.paths.flat())assert.ok(p.every(Number.isFinite))}
 }
});
test('old road lines and hit targets are removed when time or layer changes',()=>{
 const roads=new Roads(()=>{});roads.sets=structuredClone(curated.sets);roads.manifestReady=true;
 const ctx=new Proxy({isPointInStroke:()=>true},{get:(obj,k)=>obj[k]||(()=>{}),set:(o,k,v)=>(o[k]=v,true)}),v={year:1894,width:1000,height:600,scale:100,meta:{width:40,height:120,world:262144},panX:0,panY:0};
 const project=(lon,lat)=>[lon,lat];roads.draw(ctx,v,project);assert.ok(roads.drawn.length>0);const f=roads.drawn[0],p=f.paths[0][0],screen=[(p[0]-20)*100+500,(p[1]-60)*100+300];assert.ok(roads.hit(...screen,ctx));
 roads.enabled=false;roads.draw(ctx,v,project);assert.equal(roads.drawn.length,0);assert.equal(roads.hit(...screen,ctx),null);
 roads.enabled=true;v.year=1799;roads.draw(ctx,v,project);assert.equal(roads.drawn.length,0);assert.equal(roads.hit(...screen,ctx),null);
 v.year=2026;roads.draw(ctx,v,project);assert.equal(roads.drawn.length,0);
});
test('a pending newer source does not leave old roads on the map',()=>{
 const roads=new Roads(()=>{});roads.sets=structuredClone(curated.sets);assert.ok(roads.sources(1942).length>0);assert.equal(roads.sources(2014).length,0);
 roads.cache.set(2014,{id:'osm-2014',features:[]});assert.equal(roads.sources(2014)[0].id,'osm-2014');assert.equal(roads.sources(2021).length,0);assert.equal(roads.sources(1894)[0].id,'atlas-1894');
});
test('prebuilt spatial index returns the same features as a full scan',()=>{
 const roads=new Roads(()=>{}),d=structuredClone(curated.sets[0]);roads.prepare(d,(lon,lat)=>[lon*10,lat*10]);
 for(const b of [[190,590,200,605],[195,600,210,610],[0,0,1,1]]){
  const expected=d.features.filter(f=>f.bounds[0]<=b[2]&&f.bounds[2]>=b[0]&&f.bounds[1]<=b[3]&&f.bounds[3]>=b[1]).map(f=>f.id).sort();assert.deepEqual(Array.from(roads.inView(d,b),f=>f.id).sort(),expected)
 }
});
test('city grid replaces old city lines without losing the fallback layer',()=>{
 const roads=new Roads(()=>{});roads.sets=structuredClone(curated.sets);roads.manifestReady=true;
 const ctx=new Proxy({},{get:()=>()=>{},set:()=>true}),view={year:1942,width:1000,height:600,scale:100,meta:{width:40,height:120,world:262144},panX:0,panY:0,cityGrid:{replacesRoads:()=>true,stage:()=>({name:'Gatunät 1942'})}};
 roads.draw(ctx,view,(lon,lat)=>[lon,lat]);assert.ok(roads.drawn.every(f=>!['museum-1920','photo-1942'].includes(f.sourceSet.id)));assert.ok(roads.drawn.length>0);
 view.cityGrid.replacesRoads=()=>false;roads.draw(ctx,view,(lon,lat)=>[lon,lat]);assert.ok(roads.drawn.some(f=>f.sourceSet.id==='museum-1920'));assert.ok(roads.drawn.some(f=>f.sourceSet.id==='photo-1942'));
});
