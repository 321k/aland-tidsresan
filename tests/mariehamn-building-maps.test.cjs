const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-building-maps.json'),catalog=read('dist/assets/temporal-objects.json.gz'),data=read('dist/assets/city-buildings.json'),modern=read('dist/assets/modern.json.gz');
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null},htmlEscape:String,safeURL:String};vm.createContext(box);
for(const name of ['temporal-objects','timeline-model','city-buildings','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.City=CityBuildings;this.Model=TemporalObjects;this.Grid=CityGrid;',box);
const model=new box.Model(catalog),sheets=review.sheets;

test('the review is complete, sourced and keeps 1978 out of the building evidence',()=>{
 assert.equal(review.decisions.length,687);assert.deepEqual(review.totals.byFirstYear,{1968:292,1985:289,1995:106});
 assert.deepEqual(Object.fromEntries(['b1','b2','b3','b4','b5'].map(k=>[k,review.decisions.filter(d=>d.batch===k).length])),{b1:361,b2:95,b3:119,b4:112,b5:0});
 for(const y of ['1968','1985','1995'])assert.ok(catalog.sources.some(s=>s.id===sheets[y]),y);
 assert.ok(catalog.sources.some(s=>s.id===review.source.id));
 assert.match(review.rules.roadRevision1978,/inte som eget byggnadsbelägg/);
 assert.ok(!catalog.objects.some(o=>o.buildingMapReview&&o.evidence.some(e=>e.sourceId===sheets['1978'])));
 assert.equal(new Set(review.decisions.map(d=>d.objectId)).size,review.decisions.length);
 // Buildings whose dates a curated review decides are never map-dated (a church, and the merged Ringvägen 66).
 assert.deepEqual(review.deferred['curated-review'],['building:osm:way-163034529','building:osm:way-498109513']);
 for(const d of review.decisions){const o=model.objects.get(d.objectId);assert.ok(!o.historicalReview&&!o.museumReview&&!o.printedMapSymbol&&!o.neighborhoodReviews,d.objectId)}
 // Deferred buildings are never dated by this review.
 for(const ids of Object.values(review.deferred))for(const id of ids)assert.ok(!model.objects.get(id)?.buildingMapReview,id);
 assert.deepEqual(catalog.objects.filter(o=>o.buildingMapReview).map(o=>o.id).sort(),review.decisions.map(d=>d.objectId).sort());
});

test('a dated building appears in its first map year with its earliest outline and is unchanged later',()=>{
 for(const d of review.decisions){const o=model.objects.get(d.objectId);
  assert.equal(model.resolveObject(d.objectId,d.firstYear-1).geometry,null,d.objectId);
  const first=model.resolveObject(d.objectId,d.firstYear),orig=model.resolveObject(d.objectId,d.originalFrom);
  assert.equal(first.state,'standing');assert.equal(first.geometry.id,d.referenceGeometryId);assert.equal(orig.geometry.id,d.referenceGeometryId);
  assert.equal(first.geometryPeriod.observationYear,o.sourceYears[0]);assert.ok(!o.sourceYears.includes(d.firstYear));assert.equal(first.geometryPeriod.certainty,'inferred');assert.equal(o.geometryPeriods[0].from,d.firstYear);assert.equal(o.geometryPeriods[0].previousFrom,d.originalFrom);assert.match(o.geometryPeriods[0].basis,/inte kartans ritning/);assert.doesNotMatch(o.geometryPeriods[0].basis,/Första kartbelägget används/);
  assert.deepEqual([o.states[0].from,o.states[0].to,o.states[1].from],[d.firstYear,d.originalFrom,d.originalFrom]);
  assert.ok(d.originalFrom>=2011&&d.firstYear<d.originalFrom);
  assert.equal(o.reconstruction.from,d.firstYear);assert.equal(o.reconstruction.mapDated,true);assert.equal(o.reconstruction.previous.from,d.originalFrom);assert.equal(o.reconstruction.basis,d.basis);
  assert.equal(o.buildingMapReview.constructionYear,null)}
});

test('every later edition shows the building; only 1985 may be unclear between 1968 and 1995',()=>{
 let unclear=0;
 for(const d of review.decisions){const o=model.objects.get(d.objectId);
  for(const x of d.observations){const e=o.evidence.find(e=>e.id===`${d.objectId}:map-101208-${x.year}`);
   if(x.year<d.firstYear){assert.equal(x.outcome,'absent');assert.equal(e,undefined);continue}
   assert.equal(e.constructionYear,null);assert.equal(e.sourceId,sheets[x.year]);
   if(x.outcome==='unclear'){unclear++;assert.equal(x.year,1985);assert.equal(d.firstYear,1968);assert.deepEqual(e.supports,['assessment']);assert.ok(!o.states[0].evidenceIds.includes(e.id));continue}
   assert.equal(x.outcome,'present');assert.deepEqual(e.sourcePixels.pixel,x.pixel);assert.ok(o.states[0].evidenceIds.includes(e.id));
   assert.ok(e.deviationMeters<=review.rules.maxRawSymbolDistanceMeters,e.id);
   assert.ok(x.distanceAfterShiftMeters<=(x.fillPass?review.rules.fillLimitMeters:review.rules.matchLimitMeters),e.id)}}
 assert.equal(unclear,82);
});

test('the city layer draws dated houses in their map years and never before',()=>{
 const layer=new box.City(()=>{});Object.assign(layer,data,{objects:model});
 const e={objects:model,ready:true,flags:{historic:true,modern:true,uncertain:true,traces:false},category:'all',query:'',historic:[],modern:modern.features,matches:()=>true,prepared:true,project:(x,y)=>[x*10000,y*10000]};
 const grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model,ready:true});
 for(const year of [1967,1968,1985,1995]){const ids=new Set(layer.records(year,e,grid).map(r=>r.id));layer.cache=null;assert.ok(ids.size>(year<1968?0:1000),year);
  for(const d of review.decisions)assert.equal(ids.has(d.objectId),year>=d.firstYear,`${d.objectId} ${year}`)}
});

test('houses rejected on the contact sheets are never dated, and each rejection has a reason and a sheet',()=>{
 const rejected=Object.entries(review.visualRejections);assert.equal(rejected.length,153);
 // Every b5 proposal was a shoreline, quay or lettering match; the strip dates nothing.
 assert.equal(rejected.filter(([,r])=>r.batch==='b5').length,8);
 assert.deepEqual(review.deferred['visual-reject'],rejected.map(([id])=>id).sort());
 const sheets=new Set(review.reviewSheets.map(s=>s.file));
 for(const [id,r] of rejected){
  assert.ok(!model.objects.get(id).buildingMapReview,id);assert.ok(!review.decisions.some(d=>d.objectId===id),id);
  assert.match(r.reason,/^(outline-empty|shoreline-or-pier|earlier-drawing|obscured|lettering|line|ambiguous-overlap|ambiguous-offset):/);
  assert.ok(sheets.has(r.sheetFile),id);assert.ok([1968,1985,1995].includes(r.proposedFirstYear))}
 // Every batch was reviewed on tile sheets and on contact sheets.
 for(const k of ['b1','b2','b3','b4','b5'])for(const kind of ['sheet','contact'])assert.ok([...sheets].some(f=>f.startsWith(`${k}-${kind}-`)),k+kind);
});
