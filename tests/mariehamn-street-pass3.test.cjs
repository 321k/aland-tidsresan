const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-street-pass3.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(catalog),grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'));grid.objects=model;
const id=k=>'road:mariehamn:street-pass3:'+k,decision=k=>review.decisions.find(d=>d.id===id(k)),at=(k,y)=>model.resolveObject(k.startsWith('road:')?k:id(k),y);
const dist=(a,b)=>Math.hypot((a[0]-b[0])*55600,(a[1]-b[1])*111320);
function segDist(p,a,b){const ax=(b[0]-a[0])*55600,ay=(b[1]-a[1])*111320,px=(p[0]-a[0])*55600,py=(p[1]-a[1])*111320,t=Math.max(0,Math.min(1,(ax*px+ay*py)/(ax*ax+ay*ay||1)));return Math.hypot(px-ax*t,py-ay*t)}
const onPaths=(p,paths,limit)=>paths.some(path=>path.some((q,i)=>i>0&&segDist(p,path[i-1],q)<=limit));
const roads=[...model.objects.values()].filter(o=>o.kind==='roadSegment');

test('pass totals are reported once by first edition and never as confirmations',()=>{
 assert.equal(review.decisions.length,53);assert.equal(review.totals.newPersistentMeters,10702.47);assert.equal(review.totals.confirmedExistingMeters,0);
 const sum=k=>Math.round(review.decisions.filter(k).reduce((s,d)=>s+d.lengthMeters,0)*100)/100;
 assert.equal(sum(()=>true),10702.47);
 assert.deepEqual(Object.fromEntries([1968,1978,1985,1995].map(y=>[String(y),sum(d=>d.firstYear===y)])),review.totals.byFirstYear);
 assert.deepEqual(review.totals.byFirstYear,{'1968':4742.89,'1978':192.1,'1985':5086.41,'1995':681.07});
 assert.ok(review.decisions.every(d=>d.countRule==='display'&&d.states.length===1&&d.states[0].to===null));
});

test('each street starts at its first reviewed edition and keeps one stable geometry to 2026',()=>{
 for(const d of review.decisions){
  assert.equal(at(d.id,d.firstYear-1).geometry,null,d.id);assert.equal(at(d.id,d.firstYear).state,'open',d.id);
  // Unclear and absent editions before the start never move the start earlier.
  assert.ok(d.observations.filter(o=>o.year<d.firstYear).every(o=>o.outcome!=='present'),d.id);
  for(const o of d.observations){const r=at(d.id,o.year);assert.equal(Boolean(r.geometry),o.outcome==='present',`${d.id} ${o.year}`);
   const e=r.object.evidence.find(e=>e.id===`${d.id}:map-${o.year}`);assert.equal(e.outcome,o.outcome);assert.equal(e.coverage,o.coverage);assert.equal(e.interpretation,true)}
  const full=at(d.id,2026).geometry;
  for(const y of [1995,2014,2021,2025,2026]){const r=at(d.id,y);assert.equal(r.state,'open');assert.equal(r.geometry.id,full.id,`${d.id} ${y}`)}
  const drawn=full.paths.flat().map(p=>p.join());for(const m of d.members)for(const p of m.feature.paths[0])assert.ok(drawn.includes(p.join()),d.id);
  for(const y of [2014,2021,2025,2026])assert.equal(grid.featuresForStage(grid.stage(y)).filter(f=>f.objectId===d.id).length,1,`${d.id} ${y}`);
  assert.equal(model.objects.get(d.id).mariehamnStreetPass3.constructionYear,null);
 }
});

test('every modern member and city-stage copy has exactly one owner',()=>{
 const members=review.decisions.flatMap(d=>d.members.map(m=>m.feature.id));assert.equal(new Set(members).size,members.length);
 const earlier=new Set([...read('data/mariehamn-major-roads.json').decisions.flatMap(d=>d.modernMembers.map(m=>m.feature.id)),...read('data/mariehamn-major-road-followups.json').decisions.flatMap(d=>d.members.map(m=>m.feature.id))]);
 assert.ok(members.every(m=>!earlier.has(m)));
 for(const d of review.decisions)for(const l of d.modernLinks){assert.equal(model.objectForSource(l.datasetId,l.featureId),d.id);assert.ok(!grid.featuresForStage(grid.sets.find(s=>s.id===l.datasetId)).some(f=>f.id===l.featureId))}
 // Deferred streets (path-like in 1985/1995, partial, unclear or not yet joined to the dated network) stay with their undated modern sources.
 for(const w of ['way/251840728','way/136775757','way/59319327','way/121987082','way/45478076','way/87088755','way/118247846','way/51356758','way/121898488','way/90673967','way/51356764','way/87088754','way/87088760','way/41339800','way/41339977'])assert.ok(!members.includes(w),w);
});

test('Mellangårdsvägen shows only its reviewed southern part before 1985',()=>{
 const d=decision('mellangardsvagen'),fridhem=decision('fridhemsvagen').members[0].feature.paths[0];
 for(const y of [1968,1978,1984]){const r=at(d.id,y);assert.equal(r.geometryPeriod.coverage,'partial');assert.deepEqual(r.geometry.paths,d.phases[0].paths)}
 const part=d.phases[0].paths[0];assert.ok(dist(part.at(-1),fridhem[0])<0.5,'the 1968 part ends at the Fridhemsvägen junction');
 assert.deepEqual(part[0],d.members[0].feature.paths[0][0]);
 assert.deepEqual(at(d.id,1985).geometry.paths,d.members[0].feature.paths);
});

test('reviewed streets join the road network drawn in their first edition',()=>{
 for(const d of review.decisions){const y=d.firstYear,mine=at(d.id,y).geometry.paths,ends=mine.flatMap(p=>[p[0],p.at(-1)]);
  const lon=ends.map(p=>p[0]),lat=ends.map(p=>p[1]),bb=[Math.min(...lon)-0.002,Math.min(...lat)-0.001,Math.max(...lon)+0.002,Math.max(...lat)+0.001];
  const others=roads.filter(o=>o.id!==d.id).map(o=>model.resolveObject(o.id,y).geometry).filter(g=>g&&g.paths.some(p=>p.some(q=>q[0]>bb[0]&&q[0]<bb[2]&&q[1]>bb[1]&&q[1]<bb[3]))).flatMap(g=>g.paths);
  assert.ok(ends.some(p=>onPaths(p,others,2)),`${d.id} is not connected in ${y}`)}
});

test('Hindersböle: the older lanes keep 1968, the grid starts in 1985 and the field streets in 1995',()=>{
 for(const k of ['ljungvagen','askuddsvagen']){assert.ok(at(k,1968).geometry);assert.equal(at(k,1967).geometry,null)}
 const grid85=review.decisions.filter(d=>d.group==='hindersbole'&&d.firstYear===1985);assert.equal(grid85.length,22);
 for(const d of grid85){assert.equal(at(d.id,1978).geometry,null);assert.ok(at(d.id,1985).geometry)}
 // Thin red 1978 overprint lines are recorded as unclear evidence, not as the street.
 for(const k of ['hogbackagatan-north','movagen','sandasvagen','prastkragegrand','karlbergsvagen','norrbolevagen'])assert.equal(decision(k).observations[1].outcome,'unclear');
 for(const k of ['odalvagen','odalgrand','riakersgrand-south','riakersgrand-north']){assert.equal(at(k,1985).geometry,null);assert.ok(at(k,1995).geometry)}
 // Multi-way streets are drawn as one continuous line.
 for(const k of ['solvandan','norrbolevagen','nabbvagen'])assert.equal(at(k,2026).geometry.paths.length,1);
 assert.equal(at('strandhagsvagen',1984).geometry,null);assert.ok(at('fridhemsvagen',1968).geometry);
 // Servicegatan's loop is the thick 1978 overprint road; Skarpansvägen is already a main road in 1968.
 assert.equal(at('servicegatan-north',1977).geometry,null);assert.ok(at('servicegatan-north',1978).geometry);assert.ok(at('skarpansvagen',1968).geometry);
});
