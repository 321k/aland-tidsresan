const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const catalog=read('dist/assets/temporal-objects.json.gz'),review=read('data/mariehamn-shore-road.json'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+fs.readFileSync('dist/city-grid.js','utf8')+';this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(catalog),grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'));grid.objects=model;

test('the shore road is Sjöpromenaden from the museum decade, with the 1942 photo as evidence',()=>{
 for(const m of review.members){
  const o=model.objects.get(m.objectId);
  assert.deepEqual(o.states.map(s=>[s.from,s.to]),[[1920,1942],[1942,1968],[1968,null]]);
  assert.equal(model.resolveObject(m.objectId,1919).geometry,null);
  const e=o.evidence.find(e=>e.id===m.objectId+':shore-photo-1942');
  assert.equal(e.sourceId,'mariehamn-aerial-1942');assert.equal(e.constructionYear,null);
  const museum=o.evidence.find(e=>e.id===m.objectId+':museum-1920');
  assert.equal(museum.datePrecision,'decade');assert.equal(museum.interpretation,true);
 }
});
test('the long northern part is shown before 1968 only where the 1942 photo shows the road',()=>{
 const m=review.members[0],o=model.objects.get(m.objectId);
 const early=model.resolveObject(m.objectId,1942).geometry,late=model.resolveObject(m.objectId,1968).geometry;
 assert.equal(o.geometryPeriods[0].coverage,'partial');assert.deepEqual(o.geometryPeriods[0].canonicalRange,m.canonicalRange);
 assert.ok(Math.max(...early.paths.flat().map(p=>p[1]))<=m.cutLatitude+0.00002);
 assert.ok(Math.max(...late.paths.flat().map(p=>p[1]))>60.105);
 assert.deepEqual(early.paths[0].at(-1),late.paths[0].at(-1));
});
test('the coarse museum drawing is a source trace, not a second street',()=>{
 const raw=read('dist/assets/mariehamn-city-grid.json').sets.find(s=>s.id===review.museum.datasetId).features.find(f=>f.id===review.museum.featureId);
 for(const y of [1920,1927,1941,1942,1952,1967]){
  const features=grid.featuresForStage(grid.stage(y));
  assert.ok(!features.some(f=>f.traceId===review.museum.traceId),String(y));
  for(const m of review.members)assert.equal(features.filter(f=>f.objectId===m.objectId).length,1,y+' '+m.objectId);
 }
 assert.equal(model.objectForSource(review.museum.datasetId,review.museum.featureId),review.members[0].objectId);
 for(const m of review.members){
  const e=model.objects.get(m.objectId).evidence.find(e=>e.id===m.objectId+':museum-1920');
  assert.deepEqual(model.geometries.get(e.originalGeometryId).paths,raw.paths);
 }
});
