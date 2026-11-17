const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const catalog=read('dist/assets/temporal-objects.json.gz'),review=read('data/mariehamn-museum-streets.json'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(catalog),grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'));grid.objects=model;
const street=k=>review.streets.find(s=>s.key===k);

test('Hamngatan and Parkgatan are shown from the museum decade on their own centre lines, with photo evidence for 1942',()=>{
 for(const s of review.streets)for(const m of s.members){
  const o=model.objects.get(m.objectId);
  assert.equal(model.resolveObject(m.objectId,1919).geometry,null,m.objectId);
  assert.equal(model.resolveObject(m.objectId,1920).state,'open');
  assert.deepEqual(o.states.slice(0,m.originalFrom===1942?1:2).map(x=>[x.from,x.to]),m.originalFrom===1942?[[1920,1942]]:[[1920,1942],[1942,1968]]);
  const museum=o.evidence.find(e=>e.id===m.objectId+':museum-1920');
  assert.equal(museum.datePrecision,'decade');assert.equal(museum.interpretation,true);assert.equal(museum.constructionYear,null);
  const photo=o.evidence.find(e=>e.observationType==='aerial'&&e.describes.from===1942);
  assert.equal(photo.observedAt,'1942-07-25');assert.equal(photo.constructionYear,null);
  assert.equal(o.museumStreetReview.constructionYear,null);
  if(!m.museumRange)assert.equal(model.resolveObject(m.objectId,1920).geometry.id,model.resolveObject(m.objectId,2026).geometry.id);
 }
 // Parkgatan north was already dated from the 1942 photo; its 1942 state and evidence are kept.
 assert.ok(model.objects.get('road:postwar:way-39585442').evidence.some(e=>e.id==='road:postwar:way-39585442:frame-photo-1942'));
});

test('the museum drawing covers only the north part of Parkgatan south-east; the photo shows it whole from 1942',()=>{
 const m=street('parkgatan').members.find(m=>m.museumRange),o=model.objects.get(m.objectId);
 assert.equal(o.geometryPeriods[0].coverage,'partial');assert.deepEqual(o.geometryPeriods[0].canonicalRange,m.museumRange);
 const early=model.resolveObject(m.objectId,1930).geometry,late=model.resolveObject(m.objectId,1942).geometry;
 assert.ok(Math.min(...early.paths.flat().map(p=>p[1]))>=m.cutLatitude-0.00002);
 assert.ok(Math.min(...late.paths.flat().map(p=>p[1]))<m.cutLatitude-0.0005);
 assert.equal(late.id,model.resolveObject(m.objectId,2026).geometry.id);
});

test('Hamngatan north of the junction is one persistent street that owns the modern lines',()=>{
 const n=street('hamngatan').newObjects[0],o=model.objects.get(n.id);
 assert.equal(o.kind,'roadSegment');assert.equal(o.independentRoad,true);assert.equal(o.museumStreetReview.createdFromModern,true);
 assert.deepEqual(o.states.map(s=>[s.from,s.to]),[[1920,1942],[1942,1968],[1968,null]]);
 assert.equal(model.resolveObject(n.id,1919).geometry,null);
 const g=model.resolveObject(n.id,1950).geometry;assert.equal(g.id,model.resolveObject(n.id,2026).geometry.id);
 // It starts where the catalogue's Hamngatan ends and runs north to Norragatan.
 const join=model.resolveObject(n.joinsObjectId,2026).geometry.paths[0].at(-1);assert.deepEqual(g.paths[0][0],join);
 assert.ok(g.paths[0].at(-1)[1]>60.0979);
 for(const piece of n.pieces)for(const l of piece.features){
  assert.equal(model.objectForSource(l.datasetId,l.featureId),n.id,l.featureId);
  assert.ok(!grid.featuresForStage(grid.sets.find(s=>s.id===l.datasetId)).some(f=>f.id===l.featureId),l.featureId);
 }
 for(const y of [1920,1942,1968,2014,2026])assert.equal(grid.featuresForStage(grid.stage(y)).filter(f=>f.objectId===n.id).length,1,String(y));
 assert.ok(o.evidence.filter(e=>e.observationType==='printed-map-review').every(e=>e.constructionYear===null));
});

test('the coarse museum drawings are source traces of one street each, not second streets',()=>{
 for(const s of review.streets){
  assert.equal(model.objectForSource(review.museumDatasetId,s.featureId),s.linkObjectId);
  for(const y of [1920,1927,1941,1942,1952,1967])assert.ok(!grid.featuresForStage(grid.stage(y)).some(f=>f.traceId===s.traceId),`${s.key} ${y}`);
  assert.ok(!catalog.cityStages.some(st=>st.features.some(f=>f.traceId===s.traceId)));
  const raw=catalog.geometries.find(g=>g.id===`geometry:museum-streets:${s.key}:museum-1920`);
  assert.deepEqual(raw.paths,read('dist/assets/mariehamn-city-grid.json').sets.find(x=>x.id===review.museumDatasetId).features.find(f=>f.id===s.featureId).paths);
  for(const y of [1920,1930])for(const m of s.members)assert.equal(grid.featuresForStage(grid.stage(y)).filter(f=>f.objectId===m.objectId).length,1,`${m.objectId} ${y}`);
 }
});
