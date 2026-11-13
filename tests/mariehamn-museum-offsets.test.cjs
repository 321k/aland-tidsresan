const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-museum-offsets.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog);
const shown=(id,y)=>{const r=model.resolveObject(id,y);return !!r?.geometry&&['standing','occupied','construction'].includes(r.state)};

test('every museum house left open by the overlap review is decided: 24 merges, 33 endings, 17 deferred',()=>{
 assert.equal(review.merges.length,24);assert.equal(new Set(review.merges.map(d=>d.keep)).size,22);assert.equal(review.endings.length,33);
 assert.equal(Object.values(review.deferred).flat().length,17);assert.ok(catalog.sources.some(s=>s.id===review.source.id));
 const open=catalog.objects.filter(o=>o.id.startsWith('building:museum:')&&o.states.at(-1).state!=='demolished').map(o=>o.id).sort();
 assert.deepEqual(open,Object.values(review.deferred).flat().sort());
});

test('the reported Storagatan-area duplicates resolve to one house each',()=>{
 for(const [museum,keep] of [['building:museum:136','map-building:nls-symbol-498'],['building:museum:138','building:osm:way-165436732'],['building:museum:139','map-building:nls-symbol-492'],['building:museum:152','map-building:nls-symbol-487']]){
  assert.ok(!catalog.objects.some(o=>o.id===museum),museum);assert.equal(model.resolveObject(museum,1950).object.id,keep);
  assert.ok(model.objects.get(keep).aliases.includes(museum));assert.equal(model.objects.get(keep).states[0].from<=1920,true)}
 // Museum 153 by the 1978 block is empty on the 1985 map and ends by 1983.
 const o=model.objects.get('building:museum:153');assert.ok(shown(o.id,1982));assert.ok(!shown(o.id,1983));
});

test('merged houses keep their own outline and later history; two museum houses may join one longer building',()=>{
 for(const d of review.merges){const o=model.objects.get(d.keep);
  assert.ok(o.aliases.includes(d.donor));assert.equal(o.reconstruction.firstObserved,1920);assert.ok(d.gapMeters<=review.maxGapMeters);
  const r=o.museumOffsetReview.find(r=>r.donorId===d.donor);assert.equal(r.decision,'merge');assert.equal(r.constructionYear,null);
  assert.equal(model.resolveObject(d.keep,1925).geometry.id,model.resolveObject(d.keep,Math.max(d.keepFrom,1925)).geometry.id)}
 for(const keep of ['map-building:nls-symbol-489','map-building:nls-symbol-392'])assert.equal(model.objects.get(keep).museumOffsetReview.length,2);
});

test('an ending rests on an empty footprint on the map and ends at its survey year, not a demolition year',()=>{
 for(const d of review.endings){const o=model.objects.get(d.museum);
  assert.deepEqual(o.states.map(s=>[s.state,s.from,s.to]),[['standing',1920,d.endYear],['demolished',d.endYear,null]]);
  const e=o.evidence.find(e=>e.id===`${d.museum}:map-absent-${d.mapYear}`);assert.equal(e.outcome,'absent');assert.equal(e.sourceId,d.sourceId);
  assert.ok(d.darkShare<=review.maxDarkShare);assert.match(d.basis,/inte ett rivningsår/);assert.ok(shown(d.museum,d.endYear-1));assert.ok(!shown(d.museum,d.endYear))}
});
