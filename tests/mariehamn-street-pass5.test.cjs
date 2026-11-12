const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-street-pass5.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(catalog),grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'));grid.objects=model;
const id=k=>'road:mariehamn:street-pass5:'+k,decision=k=>review.decisions.find(d=>d.id===id(k)),at=(k,y)=>model.resolveObject(k.startsWith('road:')?k:id(k),y);
function segDist(p,a,b){const ax=(b[0]-a[0])*55600,ay=(b[1]-a[1])*111320,px=(p[0]-a[0])*55600,py=(p[1]-a[1])*111320,t=Math.max(0,Math.min(1,(ax*px+ay*py)/(ax*ax+ay*ay||1)));return Math.hypot(px-ax*t,py-ay*t)}
const onPaths=(p,paths,limit)=>paths.some(path=>path.some((q,i)=>i>0&&segDist(p,path[i-1],q)<=limit));
const roads=[...model.objects.values()].filter(o=>o.kind==='roadSegment');

test('pass totals are reported once by first edition; junction pieces add nothing',()=>{
 assert.equal(review.decisions.length,26);assert.equal(review.totals.newPersistentMeters,3034.94);assert.equal(review.totals.confirmedExistingMeters,0);
 const sum=k=>Math.round(review.decisions.filter(k).reduce((s,d)=>s+d.lengthMeters,0)*100)/100;
 assert.equal(sum(()=>true),3034.94);
 assert.deepEqual(Object.fromEntries([1968,1978,1985,1995].map(y=>[String(y),sum(d=>d.firstYear===y)])),review.totals.byFirstYear);
 assert.deepEqual(review.totals.byFirstYear,{'1968':896.21,'1978':0,'1985':970.46,'1995':1168.27});
 const j=decision('nya-godbyvagen-bolstavagen-junction');assert.equal(j.countRule,'parallel');assert.equal(j.lengthMeters,0);assert.equal(j.members.length,13);
 for(const k of ['lotsgatan-island','uppgardsvagen-link'])assert.equal(decision(k).countRule,'longest');
});

test('each street starts at its first reviewed edition and keeps one stable geometry to 2026',()=>{
 for(const d of review.decisions){
  assert.equal(at(d.id,d.firstYear-1).geometry,null,d.id);assert.equal(at(d.id,d.firstYear).state,'open',d.id);
  assert.ok(d.observations.filter(o=>o.year<d.firstYear).every(o=>o.outcome!=='present'),d.id);
  for(const o of d.observations){const r=at(d.id,o.year);assert.equal(Boolean(r.geometry),o.outcome==='present',`${d.id} ${o.year}`);
   const e=r.object.evidence.find(e=>e.id===`${d.id}:map-${o.year}`);assert.equal(e.outcome,o.outcome);assert.equal(e.coverage,o.coverage);assert.equal(e.interpretation,true)}
  const full=at(d.id,2026).geometry;
  for(const y of [1995,2014,2021,2025,2026]){const r=at(d.id,y);assert.equal(r.state,'open');assert.equal(r.geometry.id,full.id,`${d.id} ${y}`)}
  const drawn=full.paths.flat().map(p=>p.join());for(const m of d.members)for(const p of m.feature.paths[0])assert.ok(drawn.includes(p.join()),d.id);
  for(const y of [2014,2021,2025,2026])assert.equal(grid.featuresForStage(grid.stage(y)).filter(f=>f.objectId===d.id).length,1,`${d.id} ${y}`);
  assert.equal(model.objects.get(d.id).mariehamnStreetPass5.constructionYear,null);
 }
});

test('every modern member and city-stage copy has exactly one owner',()=>{
 const members=review.decisions.flatMap(d=>d.members.map(m=>m.feature.id));assert.equal(new Set(members).size,members.length);
 const earlier=new Set([...read('data/mariehamn-major-roads.json').decisions.flatMap(d=>d.modernMembers.map(m=>m.feature.id)),
  ...['data/mariehamn-major-road-followups.json','data/mariehamn-street-pass3.json','data/mariehamn-street-pass4.json'].flatMap(p=>read(p).decisions.flatMap(d=>d.members.map(m=>m.feature.id)))]);
 assert.ok(members.every(m=>!earlier.has(m)));
 for(const d of review.decisions)for(const l of d.modernLinks){assert.equal(model.objectForSource(l.datasetId,l.featureId),d.id);assert.ok(!grid.featuresForStage(grid.sets.find(s=>s.id===l.datasetId)).some(f=>f.id===l.featureId))}
 // Deferred: cycleway-only connections, Bergshöjden, Framnäsvägen/Varvsvägen, Uppgårdsvägen's north end, the Lotsby plan streets, Segelmakargatan.
 for(const w of ['way/87088760','way/87088749','way/117232836','way/41339800','way/41339977','way/88561577','way/496196533','way/302829775','way/935561121'])assert.ok(!members.includes(w),w);
});

test('reviewed streets join the road network drawn in their first edition',()=>{
 for(const d of review.decisions){const y=d.firstYear,mine=at(d.id,y).geometry.paths,ends=mine.flatMap(p=>[p[0],p.at(-1)]);
  const lon=ends.map(p=>p[0]),lat=ends.map(p=>p[1]),bb=[Math.min(...lon)-0.002,Math.min(...lat)-0.001,Math.max(...lon)+0.002,Math.max(...lat)+0.001];
  const others=roads.filter(o=>o.id!==d.id).map(o=>model.resolveObject(o.id,y).geometry).filter(g=>g&&g.paths.some(p=>p.some(q=>q[0]>bb[0]&&q[0]<bb[2]&&q[1]>bb[1]&&q[1]<bb[3]))).flatMap(g=>g.paths);
  assert.ok(ends.some(p=>onPaths(p,others,2)),`${d.id} is not connected in ${y}`)}
});

test('the Stenliden block is anchored through the 1978 junction and the 1985 link',()=>{
 assert.equal(at('nya-godbyvagen-bolstavagen-junction',1977).geometry,null);assert.ok(at('nya-godbyvagen-bolstavagen-junction',1978).geometry);
 assert.equal(at('uppgardsvagen-link',1984).geometry,null);assert.ok(at('uppgardsvagen-link',1985).geometry);
 for(const k of ['uppgardsvagen','ostra-stenliden','krakbarsstigen-east','blabarsstigen-north','blabarsstigen-cross','blabarsstigen-south','hjortronstigen']){assert.equal(at(k,1994).geometry,null,k);assert.ok(at(k,1995).geometry,k)}
});

test('gap pieces take their neighbours\' first edition only when the map shows them',()=>{
 for(const k of ['sjukhusvagen-west-gap','sjukhusvagen-east-gap','mariegatan-gap','ostra-esplanadgatan-gap','fiskhamnsvagen','lotsgatan-island'])assert.ok(at(k,1968).geometry,k);
 // Havsgatan's middle and Neptunigatan's curve run through hatched blocks in 1968: unclear, not backdated.
 for(const k of ['havsgatan-new-section','neptunigatan-curve']){assert.equal(decision(k).observations[0].outcome,'unclear');assert.equal(at(k,1984).geometry,null);assert.ok(at(k,1985).geometry)}
 for(const k of ['hindersbolevagen-link','hindersbolevagen-ditch'])assert.equal(decision(k).observations[1].outcome,'unclear');
});
