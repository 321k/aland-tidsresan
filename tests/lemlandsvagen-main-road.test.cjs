const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/lemlandsvagen-main-road.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog),at=(id,y)=>model.resolveObject(id,y);
const dist=(a,b)=>Math.hypot((a[0]-b[0])*55600,(a[1]-b[1])*111320);
const seg=(p,a,b)=>{const k=[55600,111320],v=[0,1].map(i=>(b[i]-a[i])*k[i]),w=[0,1].map(i=>(p[i]-a[i])*k[i]),l=v[0]**2+v[1]**2,t=l?Math.max(0,Math.min(1,(w[0]*v[0]+w[1]*v[1])/l)):0;return Math.hypot(w[0]-t*v[0],w[1]-t*v[1])};
const near=(p,line)=>Math.min(...line.slice(1).map((q,i)=>seg(p,line[i],q)));
const sections=[...review.sections,{...review.remainder,id:review.target.objectId}].sort((a,b)=>a.range[0]-b.range[0]);

test('today\'s Lemlandsvägen is eight sections that meet end to end; each starts at the first map that draws it',()=>{
 assert.equal(sections.length,8);
 for(const s of sections){
  assert.equal(at(s.id,s.firstYear-1).geometry,null,s.id);assert.equal(at(s.id,s.firstYear).state,'open',s.id);assert.equal(at(s.id,2026).state,'open',s.id);
  const o=model.objects.get(s.id);
  for(const [y,v] of Object.entries(s.maps)){const e=o.evidence.find(e=>e.id===`${s.id}:early-map-${y}`);assert.equal(e.outcome,v);assert.equal(e.constructionYear,null)}}
 for(const [a,b] of sections.slice(0,-1).map((s,i)=>[s,sections[i+1]]))
  assert.ok(dist(at(a.id,2026).geometry.paths[0].at(-1),at(b.id,2026).geometry.paths[0][0])<0.5,`${a.part}->${b.part}`);
 assert.deepEqual(Object.fromEntries(sections.map(s=>[s.part,s.firstYear])),{A:1968,B:1917,C:1968,D:1917,E:1985,F1:1968,F2:1917,F3:1968});
});

test('the original object keeps its identity, 1985 start and evidence for the Knutsboda–Dragsvik bypass',()=>{
 const o=model.objects.get(review.target.objectId);
 assert.equal(o.states[0].from,1985);assert.equal(o.name,'Lemlandsvägen · Knutsboda–Dragsvik');
 assert.ok(catalog.geometries.some(g=>g.id===review.target.geometryId),'original geometry kept as evidence');
 assert.ok(o.evidence.some(e=>e.observationType==='qgis-reconciled-road'));
 assert.equal(o.lemlandsvagenMainRoad.splitInto.length,7);
});

test('in 1929 the main road is the old road: the old pieces join today\'s unchanged sections',()=>{
 const line=id=>at(id,1929).geometry.paths[0],ids=Object.fromEntries(sections.map(s=>[s.part,s.id]));
 for(const p of ['A','C','E','F1','F3'])assert.equal(at(ids[p],1929).geometry,null,p);
 const old=Object.fromEntries(review.oldRoad.objects.map(o=>[o.id.split(':').pop(),o.id]));
 assert.ok(near(line(old['tomtebo-solstrand'])[0],line(ids.B))<0.5);assert.ok(near(line(old['tomtebo-solstrand']).at(-1),line(ids.D))<0.5);
 assert.ok(near(line(old['ovre-bors-ostergard'])[0],line(ids.D))<0.5);assert.ok(near(line(old.johans).at(-1),line(ids.F2))<0.5);
 assert.ok(near(line(old['mangard-soderby'])[0],line(review.langskata.objectId))<0.5);
 assert.ok(dist(line(old['mangard-soderby']).at(-1),at(ids.F3,2026).geometry.paths[0].at(-1))<0.5,'reaches the end of today\'s road');
});

test('old road pieces stay open until the edition after their last map; after that only what survives is claimed',()=>{
 // The later OpenStreetMap review (docs/lemland-old-road-osm.md) keeps the surviving parts open with partial
 // coverage; Tomtebo–Solstrand has no surviving part and stays 'unknown' (not abandoned).
 for(const o of review.oldRoad.objects){
  assert.equal(at(o.id,1916).geometry,null);assert.equal(at(o.id,1917).state,'open');assert.equal(at(o.id,o.until-1).state,'open');
  assert.equal(at(o.id,o.until-1).geometryPeriod.coverage,'full');
  if(model.objects.get(o.id).lemlandOldRoadOsm){assert.equal(at(o.id,o.until).state,'open');assert.equal(at(o.id,2026).geometryPeriod.coverage,'partial')}
  else{assert.equal(at(o.id,o.until).state,'unknown');assert.equal(at(o.id,2026).geometry,null)}
  assert.ok(o.endSnapMeters.every(m=>m<=25));assert.equal(model.objects.get(o.id).lemlandsvagenMainRoad.constructionYear,null)}
 assert.equal(review.oldRoad.objects.filter(o=>model.objects.get(o.id).lemlandOldRoadOsm).length,3);
 assert.deepEqual(review.oldRoad.objects.map(o=>o.until),[1985,1995,1995,1995]);
});

test('Långskata del 2: only its first 300 m are the old road before 1985',()=>{
 const id=review.langskata.objectId;
 for(const y of [1917,1948,1984]){const r=at(id,y);assert.equal(r.geometryPeriod.coverage,'partial');assert.deepEqual(r.geometryPeriod.canonicalRange,review.langskata.canonicalRange)}
  assert.notEqual(at(id,1985).geometryPeriod.coverage,'partial');assert.equal(at(id,1916).geometry,null);
});
