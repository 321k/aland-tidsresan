const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-frame-1942.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(catalog),grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'));grid.objects=model;
const dist=(a,b)=>Math.hypot((a[0]-b[0])*55600,(a[1]-b[1])*111320);
const traceIds=review.traces.map(t=>t.traceId),members=review.traces.flatMap(t=>t.members.map(m=>({...m,traceId:t.traceId})));
const byName=Object.fromEntries(review.traces.map(t=>[t.name,t]));

test('no coarse 1942 city trace is drawn any more, and their original pixels are kept',()=>{
 assert.equal(review.traces.length,14);
 // Every 1942 city trace that was still drawn without an object is reviewed.
 for(const s of catalog.cityStages)assert.ok(!s.features.some(f=>/^city-1942-trace-/.test(f.traceId||'')&&!f.objectId&&!f.approachGap&&!f.frameGap),s.id);
 assert.deepEqual(review.traces.filter(t=>t.decision==='rejected').map(t=>t.name).sort(),['Förbindelse mellan infartsvägarna, 1942','Förbindelse till södra vägen · 1942','Storagatan · 1942','Södra kvarterens tvärgata · 1942','Södra stadsgatan · 1942','Väg till västra stadskanten, 1942']);
 for(const s of catalog.cityStages)for(const f of s.features.filter(f=>traceIds.includes(f.traceId)&&!f.objectId))assert.ok(f.frameGap&&['city-reconstruction-1942','city-reconstruction-1952'].includes(s.id),`${s.id} ${f.id}`);
 for(const y of [1942,1952,1968,1978,1985])assert.ok(!grid.featuresForStage(grid.stage(y)).some(f=>/· 1942$/.test(f.name||'')&&traceIds.includes(f.traceId)&&!f.objectId&&!f.frameGap),y);
 const city=read('data/mariehamn-city-traces.json').sets.find(s=>s.id==='city-1942');
 for(const t of review.traces)assert.deepEqual(city.roads.find(r=>r.traceId===t.traceId).pixels,t.pixels);
});

test('Södra stadsgatan is rejected without a replacement; it duplicated Skillnadsgatan',()=>{
 const t=byName['Södra stadsgatan · 1942'];assert.equal(t.decision,'rejected');assert.equal(t.members.length,0);assert.equal(t.retracedGaps.length,0);
 assert.match(t.basis,/Skillnadsgatan/);assert.ok(t.stageFeatures.some(x=>x.outside));
});

test('streets the 1942 photo shows start in 1942 on their own centre lines; their later history is unchanged',()=>{
 assert.equal(members.length,43);
 const names=t=>[...new Set(byName[t].members.map(m=>m.name))];
 assert.deepEqual(names('Västra strandens gata · 1942'),['Havsgatan']);assert.deepEqual(names('Norra kvarterens tvärgata · 1942'),['Köpmansgatan']);
 assert.deepEqual(names('Strandgatan · 1942').sort(),['Parkgatan','Strandgatan']);
 assert.deepEqual(names('Västra stadsgatan · 1942'),['Neptunigatan']);assert.deepEqual(names('Gata öster om esplanaden · 1942'),['Ålandsvägen']);
 assert.deepEqual(names('Torggatan · 1942'),['Torggatan']);assert.deepEqual(names('Norragatan · 1942'),['Norragatan']);assert.deepEqual(names('Tvärgata i norra staden · 1942'),['Styrmansgatan']);
 // The power-line clearing is not a street.
 assert.match(byName['Förbindelse mellan infartsvägarna, 1942'].basis,/kraftledning/);
 for(const m of members){const o=model.objects.get(m.objectId);
  assert.equal(model.resolveObject(m.objectId,1941).geometry,null,m.objectId);
  const r42=model.resolveObject(m.objectId,1942),rOrig=model.resolveObject(m.objectId,m.originalFrom);
  assert.equal(r42.state,'open');assert.equal(r42.geometry.id,rOrig.geometry.id);
  assert.deepEqual([o.states[0].from,o.states[0].to,o.states[1].from],[1942,m.originalFrom,m.originalFrom]);
  const e=o.evidence.find(e=>e.id===m.objectId+':frame-photo-1942');assert.equal(e.observedAt,'1942-07-25');assert.equal(e.constructionYear,null);assert.equal(e.sourceTraceId,m.traceId);
  for(const y of [1942,1952,1968])assert.equal(grid.featuresForStage(grid.stage(y)).filter(f=>f.objectId===m.objectId).length,1,`${m.objectId} ${y}`);
  assert.equal(o.frame1942.traceId,m.traceId);assert.ok(!o.approach1942)}
 // Köpmansgatan keeps the earlier school-street interpretation from 1952.
 for(const m of byName['Norra kvarterens tvärgata · 1942'].members)assert.equal(m.originalFrom,1952);
 assert.deepEqual(catalog.objects.filter(o=>o.frame1942).map(o=>o.id).sort(),members.map(m=>m.objectId).sort());
});

test('the Strandgatan gap is the photo retrace from the core to Parkgatan, only before 1968',()=>{
 const [g]=byName['Strandgatan · 1942'].retracedGaps;assert.match(g.basis,/Minsta-kostnadsväg/);
 const end=id=>{const p=model.resolveObject(id,1942).geometry.paths[0];return [p[0],p.at(-1)]};
 for(const id of ['city-reconstruction-1942','city-reconstruction-1952']){
  const f=catalog.cityStages.find(s=>s.id===id).features.filter(f=>f.frameGap);assert.equal(f.length,1,id);
  const p=f[0].paths[0];assert.ok(end(g.fromObjectId).some(e=>dist(e,p[0])<1));assert.ok(end(g.toObjectId).some(e=>dist(e,p.at(-1))<1))}
 for(const y of [1968,1985])assert.ok(!grid.featuresForStage(grid.stage(y)).some(f=>f.frameGap),y);
});
