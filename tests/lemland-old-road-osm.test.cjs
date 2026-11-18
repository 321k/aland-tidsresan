const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/lemland-old-road-osm.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog),at=(id,y)=>model.resolveObject(id,y),geometries=new Map(catalog.geometries.map(g=>[g.id,g]));
const k=[55600,111320],seg=(p,a,b)=>{const v=[0,1].map(i=>(b[i]-a[i])*k[i]),w=[0,1].map(i=>(p[i]-a[i])*k[i]),l=v[0]**2+v[1]**2,t=l?Math.max(0,Math.min(1,(w[0]*v[0]+w[1]*v[1])/l)):0;return Math.hypot(w[0]-t*v[0],w[1]-t*v[1])};
const near=(p,lines)=>Math.min(...lines.flatMap(line=>line.slice(1).map((q,i)=>seg(p,line[i],q))));
const slice=(line,[a,b])=>{const pt=t=>{const i=Math.min(Math.floor(t),line.length-2),f=t-i;return line[i].map((v,j)=>v+(line[i+1][j]-v)*f)};return [pt(a),...line.filter((_,i)=>a<i&&i<b),pt(b)]};
const densify=line=>line.slice(1).flatMap((q,i)=>{const p=line[i],n=Math.max(1,Math.ceil(Math.hypot((q[0]-p[0])*k[0],(q[1]-p[1])*k[1])/5));return [...Array(n).keys()].map(j=>p.map((v,m)=>v+(q[m]-v)*j/n))}).concat([line.at(-1)]);
const snapshots={'osm-2014':read('dist/assets/roads-2014.json.gz'),'osm-2021':read('dist/assets/roads-2021.json.gz'),'osm-2025':read('dist/assets/roads-2025.json.gz'),'osm-2026':read('dist/assets/modern.json.gz')};
const feature=(d,id)=>snapshots[d].features.find(f=>f.id===id);

test('the surviving old road is open to today, drawn only where it survives; the rest is not claimed after 1985',()=>{
 for(const s of review.objects){
  const o=model.objects.get(s.id),last=s.phases.at(-1);
  assert.equal(o.name,s.name);assert.equal(at(s.id,1916).geometry,null);
  for(const y of [1917,1960,1994,1995,2014,2025])assert.equal(at(s.id,y).state,'open',`${s.id} ${y}`);
  assert.equal(at(s.id,1994).geometryPeriod.coverage,'full');
  const r=at(s.id,2014);assert.equal(r.geometryPeriod.coverage,'partial');assert.equal(r.geometryPeriod.from,last.from);
  assert.ok(o.evidence.every(e=>e.constructionYear==null));assert.equal(o.lemlandOldRoadOsm.constructionYear,null);
 }
 const t=review.unchanged[0].id;assert.equal(at(t,1984).state,'open');assert.equal(at(t,1985).state,'unknown');assert.equal(at(t,2026).geometry,null);
});

test('the road does not move when the source changes: the surviving line is the same line it had before 1995',()=>{
 for(const s of review.objects){
  const before=at(s.id,1994).geometry.paths,after=at(s.id,1995).geometry.paths;
  for(const p of after.flat())assert.ok(near(p,before)<0.05,s.id);
 }
});

test('each phase keeps to its 1929 trace; the raw trace is kept unchanged as evidence',()=>{
 for(const s of review.objects){
  const o=model.objects.get(s.id),raw=geometries.get(s.traceGeometryId);
  assert.ok(raw.sourceIds.includes('nls:9c76c492-0456-43c6-9478-b2aa0034b26c'));
  assert.equal(o.evidence.find(e=>e.id===`${s.id}:osm-review`).originalGeometryId,s.traceGeometryId);
  for(const ph of s.phases.filter(p=>p.traceCheck)){
   const line=at(s.id,ph.from).geometry.paths,d=densify(raw.paths[0]).map(p=>near(p,line)).sort((a,b)=>a-b);
   assert.ok(d.at(-1)<=review.limits.traceMeters,`${s.id} ${ph.from}`);assert.ok(d[Math.floor(d.length*0.9)]<=review.limits.traceP90Meters,`${s.id} ${ph.from}`);
  }
 }
});

test('Övre-Börs: the 1929/1948 corner at Fridelund, the eased curve from 1968',()=>{
 const id='road:lemland:gamla-lemlandsvagen:ovre-bors-ostergard',raw=geometries.get(review.objects[0].traceGeometryId).paths;
 const knuts=feature('osm-2026','way/119232836').paths[0],corner=slice(knuts,[9,13]);
 const lines=y=>at(id,y).geometry.paths,off=(y)=>Math.max(...densify(corner).map(p=>near(p,lines(y))));
 assert.ok(off(1948)>25,'1948 does not follow the curve');assert.ok(off(1968)<0.05,'1968 follows Knutsbodavägen');
 assert.ok(Math.max(...densify(lines(1948)[0]).map(p=>near(p,raw)))<review.limits.traceMeters);
 assert.ok(model.objects.get(id).evidence.some(e=>e.id===`${id}:realigned-1968`));
});

test('the old-road objects own their OpenStreetMap ranges in every snapshot, and no copy is left beside them',()=>{
 let count=0;
 for(const s of review.objects){
  const o=model.objects.get(s.id),survivor=at(s.id,2026).geometry.paths;
  assert.ok(o.sourceLinks.length>0);
  for(const l of o.sourceLinks){
   count++;
   assert.ok(model.roadPartsForSource(l.datasetId,l.featureId).some(p=>p.objectId===s.id&&p.sourceVertexRange[0]===l.sourceVertexRange[0]),l.featureId);
   const f=feature(l.datasetId,l.featureId);assert.equal(f.paths[0].length,l.sourceVertexCount);
   for(const p of densify(slice(f.paths[0],l.sourceVertexRange)))assert.ok(near(p,survivor)<=review.limits.linkMeters,`${l.featureId} off the line`);
  }
  // What stays unowned of these features must not run along the old road (it would be drawn twice).
  const byFeature=new Map();for(const l of o.sourceLinks){const key=l.datasetId+' '+l.featureId;byFeature.set(key,[...(byFeature.get(key)||[]),l.sourceVertexRange])}
  for(const [key,ranges] of byFeature){
   const [d,id]=key.split(' '),line=feature(d,id).paths[0];let at0=0,run=0;
   for(const [a,b] of [...ranges.sort((x,y)=>x[0]-y[0]),[line.length-1,line.length-1]]){
    if(a>at0+1e-8){const pts=densify(slice(line,[at0,a])),inside=pts.filter(p=>near(p,survivor)<10).length*5;run=Math.max(run,inside)}
    at0=Math.max(at0,b);
   }
   assert.ok(run<=30,`${key}: ${run} m left beside the old road`);
  }
 }
 assert.equal(count,42);
 assert.deepEqual(review.objects.map(s=>model.objects.get(s.id).lemlandOldRoadOsm.snapshotYears),[[2014,2021,2025,2026],[2021,2025,2026],[2014,2021,2025,2026]]);
});

test('in 1929 the old road still joins its neighbours: today\'s road, Långskata and the other old pieces',()=>{
 const [ob,jo,ms]=review.objects.map(s=>at(s.id,1929).geometry.paths[0]);
 const road=id=>at(id,1929).geometry.paths;
 assert.ok(near(ob[0],road('road:lemland:lemlandsvagen:solstrand-knutsboda'))<0.5);
 assert.ok(near(ob.at(-1),[jo])<0.5);assert.ok(near(jo.at(-1),road('road:lemland:lemlandsvagen:johans-lindebo'))<0.5);
 assert.ok(near(ms[0],road('road:qgis:mariehamn:langskata-2-100km3'))<0.5);
});
