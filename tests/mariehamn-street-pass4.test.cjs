const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-street-pass4.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(catalog),grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'));grid.objects=model;
const id=k=>'road:mariehamn:street-pass4:'+k,decision=k=>review.decisions.find(d=>d.id===id(k)),at=(k,y)=>model.resolveObject(k.startsWith('road:')?k:id(k),y);
const dist=(a,b)=>Math.hypot((a[0]-b[0])*55600,(a[1]-b[1])*111320);
function segDist(p,a,b){const ax=(b[0]-a[0])*55600,ay=(b[1]-a[1])*111320,px=(p[0]-a[0])*55600,py=(p[1]-a[1])*111320,t=Math.max(0,Math.min(1,(ax*px+ay*py)/(ax*ax+ay*ay||1)));return Math.hypot(px-ax*t,py-ay*t)}
const onPaths=(p,paths,limit)=>paths.some(path=>path.some((q,i)=>i>0&&segDist(p,path[i-1],q)<=limit));
const roads=[...model.objects.values()].filter(o=>o.kind==='roadSegment');
const len=pts=>pts.slice(1).reduce((s,q,i)=>s+dist(pts[i],q),0);

test('pass totals are reported once by first edition; parallel lanes add nothing',()=>{
 assert.equal(review.decisions.length,63);assert.equal(review.totals.newPersistentMeters,10696.1);assert.equal(review.totals.confirmedExistingMeters,0);
 const sum=k=>Math.round(review.decisions.filter(k).reduce((s,d)=>s+d.lengthMeters,0)*100)/100;
 assert.equal(sum(()=>true),10696.1);
 assert.deepEqual(Object.fromEntries([1968,1978,1985,1995].map(y=>[String(y),sum(d=>d.firstYear===y)])),review.totals.byFirstYear);
 assert.deepEqual(review.totals.byFirstYear,{'1968':3431.26,'1978':36.63,'1985':4906.59,'1995':2321.62});
 assert.ok(review.decisions.every(d=>d.states.length===1&&d.states[0].to===null));
 // Västra Utfarten's west carriageway runs beside an already dated road: 0 m. The Klintvägen lanes count once.
 assert.equal(decision('vastra-utfarten-west').countRule,'parallel');assert.equal(decision('vastra-utfarten-west').lengthMeters,0);
 const lanes=decision('klintvagen-approach');assert.equal(lanes.countRule,'longest');assert.ok(lanes.lengthMeters<lanes.members.reduce((s,m)=>s+len(m.feature.paths[0]),0)*0.6);
 assert.ok(review.decisions.filter(d=>!['vastra-utfarten-west','klintvagen-approach'].includes(d.id.split(':').at(-1))).every(d=>d.countRule==='display'));
});

test('each street starts at its first reviewed edition and keeps one stable geometry to 2026',()=>{
 for(const d of review.decisions){
  assert.equal(at(d.id,(model.objects.get(d.id).approach1942?1942:d.firstYear)-1).geometry,null,d.id); /* the 1942 approach review may add earlier photo evidence */ assert.equal(at(d.id,d.firstYear).state,'open',d.id);
  // Unclear and absent editions before the start never move the start earlier.
  assert.ok(d.observations.filter(o=>o.year<d.firstYear).every(o=>o.outcome!=='present'),d.id);
  for(const o of d.observations){const r=at(d.id,o.year);assert.equal(Boolean(r.geometry),o.outcome==='present',`${d.id} ${o.year}`);
   const e=r.object.evidence.find(e=>e.id===`${d.id}:map-${o.year}`);assert.equal(e.outcome,o.outcome);assert.equal(e.coverage,o.coverage);assert.equal(e.interpretation,true)}
  const full=at(d.id,2026).geometry;
  for(const y of [1995,2014,2021,2025,2026]){const r=at(d.id,y);assert.equal(r.state,'open');assert.equal(r.geometry.id,full.id,`${d.id} ${y}`)}
  const drawn=full.paths.flat().map(p=>p.join());for(const m of d.members)for(const p of m.feature.paths[0])assert.ok(drawn.includes(p.join()),d.id);
  for(const y of [2014,2021,2025,2026])assert.equal(grid.featuresForStage(grid.stage(y)).filter(f=>f.objectId===d.id).length,1,`${d.id} ${y}`);
  assert.equal(model.objects.get(d.id).mariehamnStreetPass4.constructionYear,null);
 }
});

test('every modern member and city-stage copy has exactly one owner',()=>{
 const members=review.decisions.flatMap(d=>d.members.map(m=>m.feature.id));assert.equal(new Set(members).size,members.length);
 const earlier=new Set([...read('data/mariehamn-major-roads.json').decisions.flatMap(d=>d.modernMembers.map(m=>m.feature.id)),
  ...['data/mariehamn-major-road-followups.json','data/mariehamn-street-pass3.json'].flatMap(p=>read(p).decisions.flatMap(d=>d.members.map(m=>m.feature.id)))]);
 assert.ok(members.every(m=>!earlier.has(m)));
 for(const d of review.decisions)for(const l of d.modernLinks){assert.equal(model.objectForSource(l.datasetId,l.featureId),d.id);assert.ok(!grid.featuresForStage(grid.sets.find(s=>s.id===l.datasetId)).some(f=>f.id===l.featureId))}
 // Deferred: Framnäsvägen and Varvsvägen would end short of the network until 1995; the Stenliden block, Bergshöjden, Knipgränd and Alfågelgränd reach it only via
 // undated junction pieces or cycleways; Mästargränd's loop does not match today's Ekogränd; black 1995 lines wait for a path model.
 for(const w of ['way/41339800','way/41339977','way/165914226','way/88561577','way/87088755','way/51356764','way/87088754','way/87088760','way/87088753','way/51356763','way/117232836','way/134294421','way/163008799','way/186395792','way/186395787','way/84475443','way/170817212','way/496206164','way/186395789','way/52520721','way/35038862','way/35040469','way/54446892'])assert.ok(!members.includes(w),w);
});

test('partial streets show only the reviewed part before their full edition',()=>{
 for(const [k,full,junction] of [['klintvagen',1978,decision('klintgrand').members[0].feature.paths[0][0]],['mjolnargrand',1995,[19.93576,60.111086]]]){
  const d=decision(k),part=d.phases[0].paths[0];
  for(const y of [1968,full-1]){const r=at(d.id,y);assert.equal(r.geometryPeriod.coverage,'partial');assert.deepEqual(r.geometry.paths,d.phases[0].paths)}
  assert.deepEqual(part[0],d.members[0].feature.paths[0][0]);assert.ok(dist(part.at(-1),junction)<0.5,`${k} ends at its junction`);
  assert.deepEqual(at(d.id,full).geometry.paths,d.members[0].feature.paths);
 }
 // Klintvägen's 1968 part continues straight into Klintgränd; the south-west bend and its two lanes appear together in 1978.
 assert.ok(at('klintgrand',1968).geometry);assert.equal(at('klintvagen-approach',1977).geometry,null);assert.ok(at('klintvagen-approach',1978).geometry);
});

test('reviewed streets join the road network drawn in their first edition',()=>{
 for(const d of review.decisions){const y=d.firstYear,mine=at(d.id,y).geometry.paths,ends=mine.flatMap(p=>[p[0],p.at(-1)]);
  const lon=ends.map(p=>p[0]),lat=ends.map(p=>p[1]),bb=[Math.min(...lon)-0.002,Math.min(...lat)-0.001,Math.max(...lon)+0.002,Math.max(...lat)+0.001];
  const others=roads.filter(o=>o.id!==d.id).map(o=>model.resolveObject(o.id,y).geometry).filter(g=>g&&g.paths.some(p=>p.some(q=>q[0]>bb[0]&&q[0]<bb[2]&&q[1]>bb[1]&&q[1]<bb[3]))).flatMap(g=>g.paths);
  assert.ok(ends.some(p=>onPaths(p,others,2)),`${d.id} is not connected in ${y}`)}
});

test('Klintvägen\'s new connection and Stenhuggarvägen join the network that was already there',()=>{
 const lanes=decision('klintvagen-approach');assert.equal(lanes.members.length,7);assert.equal(lanes.firstYear,1978);
 assert.ok(at('stenhuggarvagen-north',1968).geometry);assert.ok(at('backgatan',1968).geometry);
 assert.equal(decision('skraddargrand-west').firstYear,1985);assert.equal(decision('hagnasgrand').firstYear,1985);
});

test('dating rules: single 1968 lines, thin 1978 overprint and black 1995 lines never start a street',()=>{
 for(const k of ['bagargrand','murargrand','formansgrand','gjutargrand']){const d=decision(k);assert.equal(d.observations[0].outcome,'unclear');assert.equal(d.firstYear,1985);assert.equal(at(k,1984).geometry,null)}
 for(const k of ['tallvagen','alvagen','granvagen','askvagen-west','videvagen','vikingagrand']){assert.equal(decision(k).observations[1].outcome,'unclear');assert.equal(at(k,1984).geometry,null);assert.ok(at(k,k==='vikingagrand'?1995:1985).geometry)}
 for(const k of ['storbatsvagen','skotbatsvagen','galeasvagen','svedgrand','maringrand','skolstigen','lovdalsvagen','vikingagrand','fallgardsvagen','brinkvagen']){assert.equal(at(k,1994).geometry,null);assert.ok(at(k,1995).geometry)}
 // The west carriageway is not drawn while the maps show one road.
 for(const y of [1968,1978,1985])assert.equal(at('vastra-utfarten-west',y).geometry,null);assert.ok(at('vastra-utfarten-west',1995).geometry);
 for(const k of ['matrosgatan','larlingsgrand','mockelobrinken','travvagen','parkstigen','arensgrand'])assert.ok(at(k,1968).geometry,k);
});
