const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-major-road-followups.json'),first=read('data/mariehamn-major-roads.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(catalog),grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'));grid.objects=model;
const id=k=>'road:mariehamn:major-followup:'+k,decision=k=>review.decisions.find(d=>d.id===id(k)),at=(k,y)=>model.resolveObject(k.startsWith('road:')?k:id(k),y);
const modern=d=>d.members.map(m=>m.feature),ends=p=>[p[0],p[p.length-1]];
// Metres between two WGS84 points (local equirectangular; adequate at junction scale).
const dist=(a,b)=>Math.hypot((a[0]-b[0])*55600,(a[1]-b[1])*111320);
const near=(p,paths,limit=1)=>paths.some(path=>path.some((q,i)=>i>0&&segDist(p,path[i-1],q)<=limit));
function segDist(p,a,b){const ax=(b[0]-a[0])*55600,ay=(b[1]-a[1])*111320,px=(p[0]-a[0])*55600,py=(p[1]-a[1])*111320,t=Math.max(0,Math.min(1,(ax*px+ay*py)/(ax*ax+ay*ay||1)));return Math.hypot(px-ax*t,py-ay*t)}

test('follow-up roads start at their first reviewed edition and keep one stable geometry per phase',()=>{
 assert.equal(review.decisions.length,37);assert.equal(review.totals.newPersistentMeters,7641.79);assert.equal(review.totals.confirmedExistingMeters,0);
 assert.equal(Math.round(review.decisions.reduce((s,d)=>s+d.lengthMeters,0)*100)/100,7641.79);
 for(const d of review.decisions){
  assert.equal(at(d.id,d.firstYear-1).geometry,null,d.id);
  assert.equal(at(d.id,d.firstYear).state,'open',d.id);
  for(const o of d.observations){const r=at(d.id,o.year);assert.equal(Boolean(r.geometry),o.outcome==='present',`${d.id} ${o.year}`);
   const e=r.object.evidence.find(e=>e.id===`${d.id}:map-${o.year}`);assert.equal(e.outcome,o.outcome);assert.equal(e.coverage,o.coverage)}
  const open=!d.states.some(s=>s.state==='abandoned');
  for(const y of [2014,2021,2025,2026]){const r=at(d.id,y);
   if(!open){assert.equal(r.geometry,null);assert.equal(r.state,'abandoned');continue}
   assert.equal(r.state,'open');
   const drawn=r.geometry.paths.flat().map(p=>p.join());for(const f of d.display.map(w=>modern(d).find(m=>m.id===w)))for(const p of f.paths[0])assert.ok(drawn.includes(p.join()),`${d.id} ${y}`);
   assert.equal(grid.featuresForStage(grid.stage(y)).filter(f=>f.objectId===d.id).length,1)}
  assert.equal(r0(d).object.majorRoadFollowup.constructionYear,null);
 }
 function r0(d){return at(d.id,2026)}
});

test('every modern member has exactly one owner and later lanes do not double-count',()=>{
 const members=review.decisions.flatMap(d=>d.members.map(m=>m.feature.id));assert.equal(new Set(members).size,members.length);
 const firstMembers=new Set(first.decisions.flatMap(d=>d.modernMembers.map(m=>m.feature.id)));assert.ok(members.every(m=>!firstMembers.has(m)));
 for(const d of review.decisions)for(const l of d.modernLinks){assert.equal(model.objectForSource(l.datasetId,l.featureId),d.id);assert.ok(!grid.featuresForStage(grid.sets.find(s=>s.id===l.datasetId)).some(f=>f.id===l.featureId))}
 for(const k of ['sjukhusvagen-rokeri-lane','sjukhusvagen-vastra-lane'])assert.equal(decision(k).lengthMeters,0);
 for(const d of review.decisions.filter(d=>d.countRule==='longest'))assert.equal(d.members.length,2,'a counted-once pair');
 // Deferred or post-1995 parts stay with their undated modern sources.
 for(const w of ['way/40103437','way/40103274','way/43378155','way/50540398','way/162459763','way/165401317','way/165358624','way/1298839909','way/116272970','way/35039424'])assert.ok(!members.includes(w),w);
});

test('Godbyvägen\'s 1968 Strandnäs crossing is reconstructed and its remnant keeps the identity',()=>{
 const approach=decision('godbyvagen-old-south-approach'),gv=at('road:mariehamn:major:way-1298787802',1968).geometry.paths[0];
 for(const y of [1968,1978,1984]){const g=at('godbyvagen-old-south-approach',y).geometry;assert.deepEqual(g.paths,approach.phases[0].paths);
  assert.ok(dist(g.paths[0][0],gv[0])<1);assert.ok(near(g.paths[0].at(-1),[read('dist/assets/modern.json.gz').features.find(f=>f.id==='way/43448261').paths[0]]))}
 const stub=modern(approach)[0];for(const y of [1985,1995,2026])assert.deepEqual(at('godbyvagen-old-south-approach',y).geometry.paths,stub.paths);
 const crossing=at('strandnas-old-straight-crossing',1968).geometry.paths[0],sjukhus=at('road:mariehamn:major:way-44108106',1968).geometry.paths[0];
 assert.ok(ends(sjukhus).some(p=>dist(p,crossing[0])<1));
 assert.equal(at('strandnas-old-straight-crossing',1978).state,'open');assert.equal(at('strandnas-old-straight-crossing',1985).state,'abandoned');assert.equal(at('strandnas-old-straight-crossing',1985).geometry,null);
 // The new curve, ring and legs appear with the 1978 overprint and connect to the ring.
 for(const k of ['godbyvagen-strandnas-curve','rokerirondellen','godbyvagen-rokeri-approach','nya-godbyvagen-rokeri-approach','osterleden-rokeri-approach']){assert.equal(at(k,1977).geometry,null);assert.ok(at(k,1978).geometry)}
 const ring=at('rokerirondellen',1978).geometry.paths,curve=at('godbyvagen-strandnas-curve',1978).geometry.paths[0];
 assert.ok(ends(curve).some(p=>dist(p,gv[0])<1));
 for(const k of ['godbyvagen-rokeri-approach','nya-godbyvagen-rokeri-approach','osterleden-rokeri-approach'])assert.ok(at(k,1978).geometry.paths.flat().some(p=>near(p,ring)));
});

test('Nya Godbyvägen turns into Godbyvägen in 1985 and continues north from 1995 without moving',()=>{
 const kasberg=decision('nya-godbyvagen-kasberg'),full=modern(kasberg)[0].paths;
 for(const y of [1978,1985,1994]){const g=at('nya-godbyvagen-kasberg',y);assert.equal(g.geometryPeriod.coverage,'partial');assert.deepEqual(g.geometry.paths,kasberg.phases[0].paths)}
 assert.deepEqual(at('nya-godbyvagen-kasberg',1995).geometry.paths,full);
 const link=at('nya-godbyvagen-old-godbyvagen-link',1985).geometry.paths[0],stem=at('nya-godbyvagen-kasberg',1985).geometry.paths[0],godby=at('road:mariehamn:major:way-77082297',1985).geometry.paths[0];
 assert.ok(dist(link[0],stem.at(-1))<0.5);assert.ok(ends(godby).some(p=>dist(p,link.at(-1))<0.5));
 assert.equal(at('nya-godbyvagen-old-godbyvagen-link',1984).geometry,null);assert.equal(at('nya-godbyvagen-old-godbyvagen-link',1995).state,'abandoned');assert.equal(at('nya-godbyvagen-old-godbyvagen-link',1995).geometry,null);
 for(const k of ['nya-godbyvagen-michaels-south','nya-godbyvagen-michaels-north','nya-godbyvagen-north-continuation']){assert.equal(at(k,1994).geometry,null);assert.ok(at(k,1995).geometry)}
 // The southern end still joins the first-pass section, whose 1978 start is preserved.
 assert.ok(dist(at('nya-godbyvagen-junction-south',1978).geometry.paths[0][0],at('road:mariehamn:major:way-40103454',1978).geometry.paths[0].at(-1))<0.5);
 assert.equal(at('road:mariehamn:major:way-40103454',1977).geometry,null);
});

test('removed and reconstructed alignments preserve their raw scan traces as source geometry',()=>{
 for(const d of review.decisions)for(const [i,p] of d.phases.entries()){if(!p.geometry.startsWith('reconstructed:'))continue;
  const o=model.objects.get(d.id),e=o.evidence.find(e=>e.id===`${d.id}:trace-${i}`);assert.deepEqual(model.geometries.get(e.originalGeometryId).paths,[p.trace.points]);
  assert.equal(e.sourceId,review.sheets.find(s=>s.year===p.trace.year).sourceId);assert.equal(e.matchedGeometryId,o.geometryPeriods[i].geometryId)}
 assert.equal(review.decisions.filter(d=>d.phases.some(p=>p.geometry.startsWith('reconstructed:'))).length,3);
});

test('Åsvägen, roundabouts and later streets are dated separately from older neighbours',()=>{
 for(const k of ['asvagen-north','asvagen-south','knappelstensvagen','bastuvagen']){assert.equal(at(k,1984).geometry,null);assert.ok(at(k,1985).geometry)}
 assert.equal(at('vastra-rondellen',1994).geometry,null);assert.ok(at('vastra-rondellen',1995).geometry);
 assert.equal(at('hammarlandsvagen-rondell-approach',1994).geometry,null);assert.ok(at('hammarlandsvagen-east',1968).geometry);
 assert.ok(at('alandsvagen-north',1968).geometry);assert.ok(at('norra-mockelovagen',1968).geometry);
 // First-pass sections keep their own earlier dates.
 for(const d of first.decisions)assert.equal(at(d.id,d.firstYear).state,'open');
});
