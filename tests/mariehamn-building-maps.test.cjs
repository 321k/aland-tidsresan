const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-building-maps.json'),catalog=read('dist/assets/temporal-objects.json.gz'),data=read('dist/assets/city-buildings.json'),modern=read('dist/assets/modern.json.gz');
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null},htmlEscape:String,safeURL:String};vm.createContext(box);
for(const name of ['temporal-objects','timeline-model','city-buildings','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.City=CityBuildings;this.Model=TemporalObjects;this.Grid=CityGrid;',box);
const model=new box.Model(catalog),sheets=review.sheets;

test('the review is complete, sourced and keeps 1978 out of the building evidence',()=>{
 assert.equal(review.decisions.length,1107);assert.deepEqual(review.totals.byFirstYear,{1968:360,1985:508,1995:239});
 assert.deepEqual(Object.fromEntries(['b1','b2','b3','b4','b5','b6','b7','b8','b9','b10','r1'].map(k=>[k,review.decisions.filter(d=>d.batch===k).length])),{b1:361,b2:95,b3:119,b4:112,b5:0,b6:43,b7:18,b8:4,b9:69,b10:106,r1:180});
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
   if(x.year<d.firstYear){assert.ok(x.outcome==='absent'||x.outcome==='unclear'&&x.reason==='hatched-block'&&x.year===1968,e?.id);assert.equal(e,undefined);continue}
   assert.equal(e.constructionYear,null);assert.equal(e.sourceId,sheets[x.year]);
   if(x.outcome==='unclear'){unclear++;assert.equal(x.year,1985);assert.equal(d.firstYear,1968);assert.deepEqual(e.supports,['assessment']);assert.ok(!o.states[0].evidenceIds.includes(e.id));continue}
   assert.equal(x.outcome,'present');assert.deepEqual(e.sourcePixels.pixel,x.pixel);assert.ok(o.states[0].evidenceIds.includes(e.id));
   assert.ok(e.deviationMeters<=review.rules.maxRawSymbolDistanceMeters,e.id);
   assert.ok(x.distanceAfterShiftMeters<=(x.fillPass?review.rules.fillLimitMeters:review.rules.matchLimitMeters),e.id)}}
 assert.equal(unclear,96);
});

test('the city layer draws dated houses in their map years and never before',()=>{
 const layer=new box.City(()=>{});Object.assign(layer,data,{objects:model});
 const e={objects:model,ready:true,flags:{historic:true,modern:true,uncertain:true,traces:false},category:'all',query:'',historic:[],modern:modern.features,matches:()=>true,prepared:true,project:(x,y)=>[x*10000,y*10000]};
 const grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model,ready:true});
 for(const year of [1967,1968,1985,1995]){const ids=new Set(layer.records(year,e,grid).map(r=>r.id));layer.cache=null;assert.ok(ids.size>(year<1968?0:1000),year);
  for(const d of review.decisions)assert.equal(ids.has(d.objectId),year>=d.firstYear,`${d.objectId} ${year}`)}
});

test('houses rejected on the contact sheets are never dated, and each rejection has a reason and a sheet',()=>{
 const rejected=Object.entries(review.visualRejections);assert.equal(rejected.length,325);
 // Every b5 proposal was a shoreline, quay or lettering match; the strip dates nothing.
 assert.equal(rejected.filter(([,r])=>r.batch==='b5').length,8);
 assert.deepEqual(review.deferred['visual-reject'],rejected.map(([id])=>id).sort());
 const sheets=new Set(review.reviewSheets.map(s=>s.file));
 for(const [id,r] of rejected){
  assert.ok(!model.objects.get(id).buildingMapReview,id);assert.ok(!review.decisions.some(d=>d.objectId===id),id);
  assert.match(r.reason,/^(outline-empty|shoreline-or-pier|earlier-drawing|obscured|lettering|line|ambiguous-overlap|ambiguous-offset|hatched-block):/);
  assert.ok(sheets.has(r.sheetFile),id);assert.ok([1968,1985,1995].includes(r.proposedFirstYear))}
 // Every batch was reviewed on tile sheets and on contact sheets.
 for(const k of ['b1','b2','b3','b4','b5','b6','b7','b8','b9','b10'])for(const kind of ['sheet','contact'])assert.ok([...sheets].some(f=>f.startsWith(`${k}-${kind}-`)),k+kind);
});

test('in the centre, a dated house never overlaps a printed-map symbol object, and hatched 1968 blocks date nothing',()=>{
 const ring=g=>g.paths[0].map(([x,y])=>[x*55600,y*111320]);
 const area=r=>Math.abs(r.reduce((a,p,i)=>{const q=r[(i+1)%r.length];return a+p[0]*q[1]-q[0]*p[1]},0))/2;
 const inside=(p,r)=>{let c=false;for(let i=0,j=r.length-1;i<r.length;j=i++){const [xi,yi]=r[i],[xj,yj]=r[j];if((yi>p[1])!==(yj>p[1])&&p[0]<(xj-xi)*(p[1]-yi)/(yj-yi)+xi)c=!c}return c};
 const geom=new Map(catalog.geometries.map(g=>[g.id,g]));
 const symbols=catalog.objects.filter(o=>o.printedMapSymbol).flatMap(o=>o.geometryPeriods.map(p=>geom.get(p.geometryId)).filter(g=>g&&g.paths[0].length>=4).map(ring));
 const centre=review.decisions.filter(d=>['b6','b7','b8'].includes(d.batch));assert.equal(centre.length,65);
 for(const d of centre){const r=ring(geom.get(d.referenceGeometryId)),xs=r.map(p=>p[0]),ys=r.map(p=>p[1]);
  for(const s of symbols){const c=[s.reduce((a,p)=>a+p[0],0)/s.length,s.reduce((a,p)=>a+p[1],0)/s.length];
   if(c[0]<Math.min(...xs)-60||c[0]>Math.max(...xs)+60||c[1]<Math.min(...ys)-60||c[1]>Math.max(...ys)+60)continue;
   assert.ok(!inside(c,r),d.objectId);assert.ok(!s.some(p=>inside(p,r))&&!r.some(p=>inside(p,s)),d.objectId)}}
 assert.equal(review.rules.symbolObjectOverlapSquareMeters,5);
 const hatched=Object.values(review.visualRejections).filter(r=>r.reason.startsWith('hatched-block:'));assert.equal(hatched.length,8);
 for(const r of hatched){assert.equal(r.proposedFirstYear,1968);assert.ok(['b6','b7'].includes(r.batch))}
});

test('modern-only outlines in Ytternäs are deferred, never dated: they have no reconstruction to extend',()=>{
 const ext=review.deferred['external-modern'];assert.equal(ext.length,93);
 for(const id of ext){const o=model.objects.get(id);assert.ok(o.externalModern&&!o.reconstruction&&!o.buildingMapReview,id);assert.ok(!review.decisions.some(d=>d.objectId===id),id)}
 for(const d of review.decisions)assert.ok(model.objects.get(d.objectId).reconstruction,d.objectId);
});

test('the r1 recheck dates earlier-unclear buildings only where the earlier drawing was judged by eye',()=>{
 const r1=review.decisions.filter(d=>d.batch==='r1');assert.equal(r1.length,180);
 const codes={};for(const d of r1)codes[d.recheck.code]=(codes[d.recheck.code]||0)+1;assert.deepEqual(codes,{E1968:16,E1985:67,P:97});
 for(const d of r1){const o=model.objects.get(d.objectId);
  if(d.recheck.code==='P')assert.ok(!d.observations.some(x=>x.visualReview),d.objectId);
  else assert.equal(d.firstYear,+d.recheck.code.slice(1));
  for(const x of d.observations.filter(x=>x.visualReview)){const e=o.evidence.find(e=>e.id===`${d.objectId}:map-101208-${x.year}`);assert.equal(e.visualReview,true);assert.ok(x.year>=d.firstYear)}}
 assert.equal(review.deferred['earlier-unclear'].length,79);
});
