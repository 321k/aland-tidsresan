const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-approaches-1942.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(catalog),grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'));grid.objects=model;
const dist=(a,b)=>Math.hypot((a[0]-b[0])*55600,(a[1]-b[1])*111320);
const members=review.approaches.flatMap(a=>a.members.map(m=>({...m,trace:a.traceId})));
const traceIds=[...review.rejected,...review.approaches].map(t=>t.traceId);
const stagesByYear=[1942,1952,1960,1968,1978,1985,1995,2013];

test('the rejected 1942 trace is drawn nowhere but its original pixels are kept',()=>{
 const [rejected]=review.rejected;assert.equal(rejected.name,'Södra vägen på halvön, 1942');assert.ok(rejected.basis.includes('Ingen väg syns'));
 for(const s of catalog.cityStages)assert.ok(!s.features.some(f=>f.traceId===rejected.traceId),s.id);
 for(const y of stagesByYear)assert.ok(!grid.featuresForStage(grid.stage(y)).some(f=>/halvön/.test(f.name||'')),y);
 const layer=read('dist/assets/historical-roads.json').sets.find(s=>s.id==='photo-1942');assert.ok(!layer.features.some(f=>f.id===rejected.photoFeatureId));assert.equal(layer.features.length,4);
 assert.deepEqual(read('data/mariehamn-city-traces.json').sets.find(s=>s.id==='city-1942').roads.find(r=>r.traceId===rejected.traceId).pixels,rejected.pixels);
});

test('raw approach traces are gone; only short reviewed gaps remain, and only 1942–1967',()=>{
 for(const s of catalog.cityStages)for(const f of s.features.filter(f=>traceIds.includes(f.traceId))){
  assert.ok(f.approachGap,`${s.id} ${f.id}`);assert.ok(['city-reconstruction-1942','city-reconstruction-1952'].includes(s.id),f.id)}
 for(const y of [1968,1978,1985,2013])assert.ok(!grid.featuresForStage(grid.stage(y)).some(f=>/infarten norrifrån, 1942/.test(f.name||'')),y);
 // Each gap ends on a backdated object (or is the untouched start of the trace).
 const ends=members.flatMap(m=>{const g=model.resolveObject(m.objectId,1942).geometry.paths[0];return [g[0],g.at(-1)]});
 const gaps=catalog.cityStages.find(s=>s.id==='city-reconstruction-1942').features.filter(f=>f.approachGap);
 assert.equal(gaps.length,7);
 for(const g of gaps){const p=g.paths[0];const near=[p[0],p.at(-1)].filter(q=>ends.some(e=>dist(e,q)<0.5)).length;assert.ok(near>=1,g.id)}
});

test('objects the 1942 photo shows start in 1942 with their own centre line; later dates are kept',()=>{
 assert.equal(members.length,30);
 for(const m of members){const o=model.objects.get(m.objectId);
  assert.equal(model.resolveObject(m.objectId,1941).geometry,null,m.objectId);
  const r42=model.resolveObject(m.objectId,1942),rOrig=model.resolveObject(m.objectId,m.originalFrom);
  assert.equal(r42.state,'open');assert.equal(r42.geometry.id,rOrig.geometry.id,m.objectId);assert.equal(r42.geometryPeriod.coverage||'full',rOrig.geometryPeriod.coverage||'full');
  // The earlier first state and period follow unchanged (the full comparison is in the scope audit).
  assert.equal(o.states[1].from,m.originalFrom);assert.equal(o.geometryPeriods[1].from,m.originalFrom);assert.equal(o.geometryPeriods[0].geometryId,o.geometryPeriods[1].geometryId);
  assert.deepEqual(o.states[0].from,1942);assert.equal(o.states[0].to,m.originalFrom);
  const e=o.evidence.find(e=>e.id===m.objectId+':approach-photo-1942');assert.equal(e.observedAt,'1942-07-25');assert.equal(e.constructionYear,null);assert.equal(e.outcome,'present');
  for(const y of [1942,1952,1968])assert.equal(grid.featuresForStage(grid.stage(y)).filter(f=>f.objectId===m.objectId).length,1,`${m.objectId} ${y}`)}
 // Klintvägen keeps its partial northern extent until its 1978 bend.
 assert.equal(model.resolveObject('road:mariehamn:street-pass4:klintvagen',1942).geometryPeriod.coverage,'partial');
});

test('the two long gaps use centre lines retraced from the photo, joined to their objects',()=>{
 for(const a of review.approaches){assert.equal(a.retracedGaps.length,1);const g=a.retracedGaps[0];
  const from=model.resolveObject(g.fromObjectId,1942).geometry.paths[0],to=model.resolveObject(g.toObjectId,1942).geometry.paths[0];
  const stage=catalog.cityStages.find(s=>s.id==='city-reconstruction-1942').features.filter(f=>f.approachGap&&f.traceId===a.traceId);
  assert.ok(stage.some(f=>{const p=f.paths[0];return [from[0],from.at(-1)].some(e=>dist(e,p[0])<0.5)&&[to[0],to.at(-1)].some(e=>dist(e,p.at(-1))<0.5)&&p.length===g.epsg3874.length}),a.key);
  assert.ok(g.basis.includes('minsta-kostnadsväg'))}
});

test('excluded objects are not backdated and only reviewed objects carry the 1942 photo',()=>{
 for(const a of review.approaches)for(const x of a.excluded){const o=model.objects.get(x.objectId);assert.ok(!o.approach1942);assert.ok(x.reason);
  // way-35011592 was left to the city map's Strandgatan trace; the 1942 frame review later replaced that trace with it.
  if(o.frame1942){assert.equal(o.frame1942.traceId,'city-1942-trace-11');continue}
  assert.ok(o.states[0].from>1942,x.objectId)}
 assert.deepEqual(catalog.objects.filter(o=>o.approach1942).map(o=>o.id).sort(),members.map(m=>m.objectId).sort());
});
