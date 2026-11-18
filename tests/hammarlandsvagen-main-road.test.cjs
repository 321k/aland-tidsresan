const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/hammarlandsvagen-main-road.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog),at=(id,y)=>model.resolveObject(id,y);
const k=[55600,111320],dist=(a,b)=>Math.hypot((a[0]-b[0])*k[0],(a[1]-b[1])*k[1]);
const seg=(p,a,b)=>{const v=[0,1].map(i=>(b[i]-a[i])*k[i]),w=[0,1].map(i=>(p[i]-a[i])*k[i]),l=v[0]**2+v[1]**2,t=l?Math.max(0,Math.min(1,(w[0]*v[0]+w[1]*v[1])/l)):0;return Math.hypot(w[0]-t*v[0],w[1]-t*v[1])};
const near=(p,lines)=>Math.min(...lines.flatMap(line=>line.slice(1).map((q,i)=>seg(p,line[i],q))));
const len=p=>p.slice(1).reduce((s,q,i)=>s+dist(p[i],q),0);
const early=Object.fromEntries(review.early.map(e=>[e.objectId,e]));

test('the same-road stretches are drawn from 1929, the rest of each object only from its own first map',()=>{
 for(const e of review.early){
  assert.equal(at(e.objectId,1928).geometry,null,e.objectId);
  const r=at(e.objectId,1929);assert.equal(r.state,'open');assert.equal(r.geometryPeriod.to,e.until);
  const drawn=r.geometry.paths.map(len),want=e.ranges.map(([a,b])=>b-a);
  drawn.forEach((d,i)=>assert.ok(Math.abs(d-want[i])<1+want[i]*0.003,`${e.objectId}: ${d} vs ${want[i]}`));   // planar test metric vs EPSG:3874
  assert.equal(r.geometryPeriod.coverage,e.ranges.length===1&&e.ranges[0][0]===0&&Math.abs(e.ranges[0][1]-e.lengthMeters)<0.1?'full':'partial');
  // Same coordinates as the later geometry: the road does not move in 1968.
  const later=at(e.objectId,e.until).geometry.paths;
  for(const p of r.geometry.paths.flat())assert.ok(near(p,later)<0.05,e.objectId);
  const o=model.objects.get(e.objectId);assert.equal(o.hammarlandsvagenMainRoad.previousFirstYear,e.until);
  assert.ok(o.evidence.some(x=>x.id===`${e.objectId}:parish-map-1929`&&x.outcome==='present'&&x.constructionYear===null));
 }
});

test('the bypasses at Drygsböle, Smedens and Näfsby still begin with the 1968 base map',()=>{
 const main=at('road:rural:hammarland-way-345142933',1950).geometry.paths;
 const ref=JSON.parse(fs.readFileSync('docs/reviews/hammarlandsvagen-main-road-2026-11-18/data/reference.json'));
 // A point in the middle of each bypass is not drawn in 1950 by any of today's objects.
 const ids=review.early.map(e=>e.objectId),drawn=ids.flatMap(id=>at(id,1950).geometry.paths);
 const point=d=>{let run=0;const m=ref.wgs84;for(let i=1;i<m.length;i++){const s=dist(m[i-1],m[i]);if(run+s>=d){const f=(d-run)/s;return m[i-1].map((v,j)=>v+(m[i][j]-v)*f)}run+=s}};
 const b=review.boundaries;
 for(const d of [(b['drygsbole-south']+b['drygsbole-north'])/2,(b.bolstad+b['smedens-north'])/2,(b['nafsby-south']+b['nafsby-north'])/2])assert.ok(near(point(d),drawn)>20,`bypass at ${d} is drawn in 1950`);
 for(const d of [10000,12500,14200,16000])assert.ok(near(point(d),drawn)<1,`same road at ${d} is not drawn in 1950`);
 for(const id of ['road:rural:hammarland-way-174570457','road:rural:hammarland-way-345143751','road:rural:hammarland-way-69739600','road:rural:hammarland-way-345143754'])
  assert.equal(model.objects.get(id).states[0].from,1968,id);
 assert.ok(main.length===2);
});

test('the old line at Smedens is its own road, open 1929 until the 1968 map, then not claimed',()=>{
 const od=review.oldRoad,o=model.objects.get(od.id);
 assert.equal(at(od.id,1928).geometry,null);assert.equal(at(od.id,1929).state,'open');assert.equal(at(od.id,1967).state,'open');
 assert.equal(at(od.id,1968).state,'unknown');assert.equal(at(od.id,2026).geometry,null);
 const line=at(od.id,1950).geometry.paths[0],today=['road:rural:hammarland-way-345142933','road:rural:hammarland-way-345143750'].flatMap(id=>at(id,1968).geometry.paths);
 assert.ok(near(line[0],today)<1&&near(line.at(-1),today)<1,'ends on today\'s road');
 const mid=line[Math.floor(line.length/2)];assert.ok(near(mid,today)>20,'runs apart from today\'s road');
 assert.ok(Math.abs(len(line)-od.lengthMeters)<1+od.lengthMeters*0.003);assert.equal(o.hammarlandsvagenMainRoad.constructionYear,null);
 assert.deepEqual(o.evidence.filter(e=>e.observationType==='printed-map-review').map(e=>[e.describes.from,e.outcome]),[[1929,'present'],[1944,'present'],[1968,'absent']]);
});

test('in 1950 the same-road stretches meet each other and the Smedens line end to end',()=>{
 const p=id=>at(id,1950).geometry.paths,m=p('road:rural:hammarland-way-345142933'),sm=p(review.oldRoad.id)[0];
 assert.ok(dist(m[1].at(-1),sm[0])<1||dist(m[1][0],sm[0])<1,'Bolstad piece meets the Smedens line');
 const b750=p('road:rural:hammarland-way-345143750')[0],v=p('road:rural:hammarland-hammarlandsvagen-vastmyra')[0];
 assert.ok(Math.min(dist(b750[0],sm.at(-1)),dist(b750.at(-1),sm.at(-1)))<1,'Smedens line meets the Björkgård piece');
 assert.ok(Math.min(...[b750[0],b750.at(-1)].flatMap(a=>[v[0],v.at(-1)].map(c=>dist(a,c))))<1,'Björkgård piece runs on into Västmyra');
 const pk=p('road:rural:hammarland-hammarlandsvagen-postad-korsangen')[0],ch=p('road:rural:hammarland-hammarlandsvagen-church-corridor')[0];
 assert.ok(Math.min(...[pk[0],pk.at(-1)].flatMap(a=>[ch[0],ch.at(-1)].map(c=>dist(a,c))))<1);
});
