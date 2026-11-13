const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-museum-duplicates.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog),geom=new Map(catalog.geometries.map(g=>[g.id,g]));
const ring=id=>{const o=model.objects.get(id);return geom.get(o.geometryPeriods.at(-1).geometryId).paths[0].map(([x,y])=>[x*55600,y*111320])};
const inside=(p,r)=>{let c=false;for(let i=0,j=r.length-1;i<r.length;j=i++){const [xi,yi]=r[i],[xj,yj]=r[j];if((yi>p[1])!==(yj>p[1])&&p[0]<(xj-xi)*(p[1]-yi)/(yj-yi)+xi)c=!c}return c};
const overlapArea=(a,b)=>{const bb=r=>[Math.min(...r.map(p=>p[0])),Math.min(...r.map(p=>p[1])),Math.max(...r.map(p=>p[0])),Math.max(...r.map(p=>p[1]))];const A=bb(a),B=bb(b);let n=0;for(let x=Math.max(A[0],B[0])+.25;x<Math.min(A[2],B[2]);x+=.5)for(let y=Math.max(A[1],B[1])+.25;y<Math.min(A[3],B[3]);y+=.5)if(inside([x,y],a)&&inside([x,y],b))n++;return n*.25};
const shown=(id,y)=>{const r=model.resolveObject(id,y);return !!r?.geometry&&['standing','occupied','construction'].includes(r.state)};

test('15 museum-map houses are merged into the later house, 16 end at their successor, 18 pairs are deferred',()=>{
 assert.equal(review.merges.length,15);assert.equal(review.replacements.length,16);assert.equal(Object.values(review.deferred).flat().length,18);
 assert.ok(catalog.sources.some(s=>s.id===review.source.id));
 for(const d of review.merges){assert.ok(!catalog.objects.some(o=>o.id===d.donor),d.donor);assert.equal(model.resolveObject(d.donor,1950).object.id,d.keep)}
 for(const d of review.replacements)assert.equal(model.objects.get(d.museum).museumDuplicateReview.decision,'replacement');
 for(const v of Object.values(review.deferred))for(const p of v)if(catalog.objects.some(o=>o.id===p.museum))assert.ok(!model.objects.get(p.museum).museumDuplicateReview,p.museum);
});

test('a merged house is one object from 1920 with its own outline, the museum evidence and alias, and its later history',()=>{
 for(const d of review.merges){const o=model.objects.get(d.keep);
  assert.equal(o.states[0].from,1920);assert.ok(o.aliases.includes(d.donor));assert.ok(o.evidence.some(e=>e.sourceId==='city-1920'),d.keep);
  assert.equal(o.reconstruction.firstObserved,1920);assert.equal(o.museumDuplicateReview.donorId,d.donor);assert.equal(o.museumDuplicateReview.constructionYear,null);
  const early=model.resolveObject(d.keep,1925),later=model.resolveObject(d.keep,Math.max(d.keepFrom,1925));
  assert.equal(early.geometry.id,later.geometry.id);
  if(d.keepFrom>1920){assert.deepEqual([o.states[0].to,o.states[1].from],[d.keepFrom,d.keepFrom]);assert.equal(o.geometryPeriods[0].previousFrom,d.keepFrom);assert.equal(o.reconstruction.previous.from,d.keepFrom)}}
});

test('a replaced museum house ends where its successor is first evidenced and never overlaps it on the map',()=>{
 for(const d of review.replacements){const o=model.objects.get(d.museum);
  assert.deepEqual(o.states.map(s=>[s.state,s.from,s.to]),[['standing',1920,d.endYear],['demolished',d.endYear,null]]);
  assert.ok(shown(d.museum,d.endYear-1));assert.ok(!shown(d.museum,d.endYear));
  for(const s of d.successors){assert.ok(o.relationships.some(r=>r.type==='replaced-by'&&r.objectId===s));assert.ok(model.objects.get(s).relationships.some(r=>r.type==='replaces'&&r.objectId===d.museum));
   for(const y of [d.endYear,2026])assert.ok(!(shown(d.museum,y)&&shown(s,y)),`${d.museum} ${s} ${y}`)}
  assert.match(d.basis,/inte ett rivningsår/)}
});

const area=r=>Math.abs(r.reduce((a,p,i)=>{const q=r[(i+1)%r.length];return a+p[0]*q[1]-q[0]*p[1]},0))/2;
// The same threshold as the town-wide check that found the pairs: at least 4 m² and 15 % of the smaller outline.
// Museum house 74 touches the merged Storagatan house way/274182776 with about 30 m² (8 %), an edge overlap below it.
test('no merged house overlaps a museum house any more, apart from deferred pairs',()=>{
 for(const d of review.merges){const keep=ring(d.keep);
  for(const y of [1920,1950,1985,2026]){const ids=catalog.objects.filter(o=>o.id.startsWith('building:museum:')&&shown(o.id,y)).map(o=>o.id);
   for(const id of ids)if(Math.abs(ring(id)[0][0]-keep[0][0])<80&&Math.abs(ring(id)[0][1]-keep[0][1])<80&&review.merges.some(m=>m.keep===d.keep))
    {const ov=overlapArea(ring(id),keep);assert.ok(ov<4||ov/Math.min(area(ring(id)),area(keep))<0.15||Object.values(review.deferred).flat().some(p=>p.museum===id),`${id} overlaps ${d.keep} in ${y}`)}}}
});
