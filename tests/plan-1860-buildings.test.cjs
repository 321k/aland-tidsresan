const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/plan-1860-buildings.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog),ids=review.buildings.map(b=>'building:plan-1860:'+b.key),rowIds=review.houseRows.map(h=>'building:plan-1860:'+h.key);
const m=([x,y])=>[x*55600,y*111320],area=r=>Math.abs(r.reduce((s,p,i)=>{const a=m(p),b=m(r[(i+1)%r.length]);return s+a[0]*b[1]-b[0]*a[1]},0))/2;

test('every named building and house row of the 1860 plan is a planned city building, only in 1860',()=>{
 assert.equal(ids.length,18);assert.equal(rowIds.length,35);
 for(const id of [...ids,...rowIds]){const o=model.objects.get(id);assert.ok(o,id);assert.ok(model.buildings.includes(o),id);assert.equal(o.historicalBuilding,true);
  const r=model.resolveObject(id,1860);assert.equal(r.state,'planned',id);assert.ok(r.geometry,id);
  for(const y of [1859,1861,1900])assert.equal(model.resolveObject(id,y).geometry,null,`${id} ${y}`);
  assert.equal(o.states.length,1);assert.equal(o.planBuildingReview.constructionYear,null)}
});

test('evidence points to the plan with its traced pixels and placement; the plan is not a construction date',()=>{
 const traced=[...review.buildings,...review.houseRows];
 for(const [i,id] of [...ids,...rowIds].entries()){const o=model.objects.get(id),e=o.evidence[0];
  assert.equal(e.sourceId,'plan-1860');assert.equal(e.observationType,'plan');assert.equal(e.outcome,'planned');assert.equal(e.constructionYear,null);
  assert.deepEqual(e.planPixels,traced[i].pixels);assert.equal(e.placement.method,'bilinear-street-cell');
  assert.ok(e.placement.extrapolationCells<=review.maxExtrapolationCells);assert.ok(catalog.sources.some(s=>s.id===e.reviewId))}
});

test('placed outlines keep plausible sizes, and the hospital and church sit where the plan puts them',()=>{
 const g=id=>model.resolveObject(id,1860).geometry.paths[0],c=id=>{const r=g(id);return [r.reduce((s,p)=>s+p[0],0)/r.length,r.reduce((s,p)=>s+p[1],0)/r.length]};
 for(const id of [...ids,...rowIds]){const a=area(g(id));assert.ok(a>50&&a<20000,`${id} ${a}`)}
 assert.ok(area(g('building:plan-1860:packhus'))>area(g('building:plan-1860:radhus')));
 // The hospital is north-west of the church, which stands in the Esplanade between the two halves of the town.
 const [lx,ly]=c('building:plan-1860:lasarett'),[kx,ky]=c('building:plan-1860:kyrka');assert.ok(lx<kx&&ly>ky);
 assert.ok(c('building:plan-1860:simskola')[0]>kx,'the swimming school is out on the east shore');
});

test('house rows are block-side groups that sit in the reconstructed blocks, both rows of a plan block in the same block',()=>{
 const stage=catalog.cityStages.find(s=>s.id==='city-reconstruction-1860'),blocks=stage.features.filter(f=>f.kind==='block');
 const inside=(p,poly)=>{let c=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])c=!c}return c};
 const blockOf=id=>{const r=model.resolveObject(id,1860).geometry.paths[0].slice(0,-1),c=[r.reduce((s,p)=>s+p[0],0)/r.length,r.reduce((s,p)=>s+p[1],0)/r.length];
  return blocks.filter(b=>b.paths.some(pp=>inside(c,pp))).map(b=>b.id)};
 for(const id of rowIds)assert.equal(model.objects.get(id).kind,'buildingGroup');
 // The regular double blocks north and south of the Esplanade: a north and a south row each (the south row next to the Wärdshus hill is not drawn).
 for(const b of ['nb','nc','nd','ne','sc','sd','se']){const n=blockOf(`building:plan-1860:husrad-${b}-n`),s=blockOf(`building:plan-1860:husrad-${b}-s`);
  assert.equal(n.length,1,b);assert.deepEqual(n,s,b)}
 // The control lines are the traces' drawn street centres; the house-row-edge lines are kept only for registration.
 const plan=read('data/mariehamn-city-traces.json').sets.find(s=>s.id==='plan-1860');
 assert.equal(review.planLineCorrections,undefined);
 for(const n of ['Norragatan i planen','Storagatans planerade stråk'])assert.ok(plan.roads.find(r=>r.name===n).streetCentreCorrection.note,n);
});
