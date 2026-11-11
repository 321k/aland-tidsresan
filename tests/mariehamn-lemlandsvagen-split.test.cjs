const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const review=read('data/mariehamn-lemlandsvagen-split.json'),model=new box.Model(read('dist/assets/temporal-objects.json.gz'));
const grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const modern=new Map(read('dist/assets/modern.json.gz').features.map(f=>[f.id,f]));
const Q2=review.target.objectId,Q3=review.pairedLane.objectId,WEST='road:mariehamn:lemlandsvagen:strandnas-sodergard',LANE='road:mariehamn:lemlandsvagen:rokeri-approach';
const at=(id,y)=>model.resolveObject(id,y),same=(a,b)=>a[0]===b[0]&&a[1]===b[1],dist=(a,b)=>Math.hypot((a[0]-b[0])*55600,(a[1]-b[1])*111320);

test('the unchanged western corridor starts in 1968 with one stable geometry',()=>{
 assert.equal(at(WEST,1967).geometry,null);
 const g=at(WEST,1968).geometry;for(const y of [1978,1985,1995,2014,2021,2026]){assert.equal(at(WEST,y).state,'open');assert.equal(at(WEST,y).geometry.id,g.id)}
 for(const y of [1968,1978,1985,1995]){const e=model.objects.get(WEST).evidence.find(e=>e.id===`${WEST}:map-${y}`);assert.equal(e.outcome,'present');assert.ok(e.traceSamples>=60);
  assert.ok(e.binMediansMeters.every((m,i)=>m!=null&&m<=12||e.visualBins.includes(i)),String(y))}
 assert.equal(model.objects.get(WEST).lemlandsvagenSplit.constructionYear,null);
});

test('Strandnäs is connected in 1968 and the road stays continuous after the split',()=>{
 const west=at(WEST,1968).geometry.paths[0],crossing=at('road:mariehamn:major-followup:strandnas-old-straight-crossing',1968).geometry.paths[0];
 assert.ok(dist(west[0],crossing.at(-1))<1,'old straight through-route meets Lemlandsvägen');
 const approach=at('road:mariehamn:major-followup:godbyvagen-old-south-approach',1968).geometry.paths[0].at(-1);
 assert.ok(west.some((p,i)=>i&&Math.abs((p[1]-west[i-1][1])*(approach[0]-west[i-1][0])-(p[0]-west[i-1][0])*(approach[1]-west[i-1][1]))<1e-9),'old Godbyvägen ends on the crossing');
 assert.ok(same(west.at(-1),review.target.splitPoint));
 assert.equal(at(Q2,1984).geometry,null);assert.ok(same(at(Q2,1985).geometry.paths[0][0],west.at(-1)));
 assert.ok(same(at(LANE,1978).geometry.paths[0].at(-1),west[0]));
});

test('the original rural object keeps identity, dates, evidence and original geometry',()=>{
 const o=model.objects.get(Q2);assert.deepEqual(o.states.map(s=>[s.state,s.from,s.to]),[['open',1985,null]]);
 const reviewed=o.evidence.filter(e=>e.observationType==='qgis-reconciled-road');assert.equal(reviewed.length,48);assert.ok(reviewed.every(e=>e.matchedGeometryId===review.target.geometryId));
 assert.ok(model.geometries.has(review.target.geometryId));assert.equal(o.strandnasSplit.previousGeometryPeriods[0].geometryId,review.target.geometryId);
 for(const y of [1968,1978])assert.equal(o.evidence.find(e=>e.id===`${Q2}:solstrand-${y}`).outcome,'absent');
 assert.equal(at(LANE,1977).geometry,null);assert.equal(at(LANE,1978).state,'open');
 assert.equal(at(Q3,1977).geometry,null);assert.equal(at(Q3,1978).state,'open');assert.equal(at(Q3,1985).geometryPeriod.from,1985);
});

test('every reviewed modern range has exactly one owner and no city copy is drawn twice',()=>{
 for(const w of review.target.ways){
  const n=modern.get(w).paths[0].length,parts=model.roadPartsForSource('osm-2026',w).sort((a,b)=>a.sourceVertexRange[0]-b.sourceVertexRange[0]);
  assert.ok([WEST,LANE,Q2].includes(parts[0].objectId));assert.equal(parts[0].sourceVertexRange[0],0);assert.equal(parts.at(-1).sourceVertexRange[1],n-1);
  for(let i=1;i<parts.length;i++)assert.equal(parts[i].sourceVertexRange[0],parts[i-1].sourceVertexRange[1],w);
  assert.equal(grid.roadSourceFeature('osm-2026',modern.get(w),{year:2026,zoom:240},(x,y)=>[x,y]),null,w);
 }
 assert.equal(JSON.stringify(model.roadPartsForSource('osm-2026',review.target.splitWay).map(p=>p.objectId).sort()),JSON.stringify([WEST,Q2].sort()));
 for(const y of [2014,2021,2025,2026]){const f=grid.featuresForStage(grid.stage(y));
  for(const o of review.objects)for(const l of o.stageLinks.filter(l=>l.datasetId==='city-'+y))assert.ok(!f.some(x=>x.id===l.featureId));
  for(const id of [WEST,LANE,Q3])assert.equal(f.filter(x=>x.objectId===id).length,1)}
});
