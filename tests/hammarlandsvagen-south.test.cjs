const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/hammarlandsvagen-south.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog),at=(id,y)=>model.resolveObject(id,y);
const k=[55500,111320],dist=(a,b)=>Math.hypot((a[0]-b[0])*k[0],(a[1]-b[1])*k[1]);
const seg=(p,a,b)=>{const v=[0,1].map(i=>(b[i]-a[i])*k[i]),w=[0,1].map(i=>(p[i]-a[i])*k[i]),l=v[0]**2+v[1]**2,t=l?Math.max(0,Math.min(1,(w[0]*v[0]+w[1]*v[1])/l)):0;return Math.hypot(w[0]-t*v[0],w[1]-t*v[1])};
const near=(p,lines)=>Math.min(...lines.flatMap(line=>line.slice(1).map((q,i)=>seg(p,line[i],q))));
const len=p=>p.slice(1).reduce((s,q,i)=>s+dist(p[i],q),0);

test('the older roads are drawn from the first parish map that prints them, until their previous first year',()=>{
 for(const e of review.early){
  assert.equal(at(e.objectId,e.firstYear-1).geometry,null,e.objectId);
  const r=at(e.objectId,e.firstYear);assert.equal(r.state,'open');assert.equal(r.geometryPeriod.to,e.until);
  const want=e.ranges.map(([a,b])=>b-a);r.geometry.paths.map(len).forEach((d,i)=>assert.ok(Math.abs(d-want[i])<1+want[i]*0.003,e.objectId));
  for(const p of r.geometry.paths.flat())assert.ok(near(p,at(e.objectId,e.until).geometry.paths)<0.05,e.objectId);
  const o=model.objects.get(e.objectId);assert.equal(o.hammarlandsvagenMainRoad.review,review.source.id);assert.equal(o.hammarlandsvagenMainRoad.previousFirstYear,e.until);
  assert.ok(o.evidence.filter(x=>x.reviewId===review.source.id).every(x=>x.constructionYear===null&&x.outcome==='present'));
 }
 assert.deepEqual([...new Set(review.early.map(e=>e.firstYear))].sort(),[1928,1929]);
});

test('the east route Söderby–Västansunda–Mattas is connected in 1929 except the known gap at Burs',()=>{
 const ids=review.early.filter(e=>e.firstYear===1929).map(e=>e.objectId),lines=ids.flatMap(id=>at(id,1929).geometry.paths);
 const ends=lines.flatMap(l=>[l[0],l.at(-1)]);
 // Every end meets another piece, except the route's two ends and the Burs gap: the Mattas piece's own first
 // geometry (1968) covers only part of its way, so the early period does too (as in 1968–1994).
 const loose=ends.filter(p=>lines.filter(l=>near(p,[l])<1).length<2);
 assert.equal(loose.length,4,`${loose.length} loose ends`);
 const gaps=loose.flatMap((p,i)=>loose.slice(i+1).map(q=>dist(p,q))).filter(d=>d<200);
 assert.equal(gaps.length,1);assert.ok(gaps[0]>100&&gaps[0]<160,`Burs gap ${gaps[0]} m`);
 assert.equal(at('road:rural:hammarland-way-1422779920',1990).geometry.paths.map(len).map(Math.round)[0],Math.round(len(at('road:rural:hammarland-way-1422779920',1929).geometry.paths[0])));
 const main=at('road:rural:hammarland-way-345142933',1929).geometry.paths;
 assert.ok(loose.some(p=>near(p,main)<5),'starts at Söderby on the 1929 main road');
});

test('Natbacken: only 4.1–5.5 km of Hammarlandsvägen del 1 is drawn before 1978, Utängsvägen whole from 1928',()=>{
 const d1=review.early.find(e=>e.objectId.endsWith('hammarlandsvagen-1-100km5'));
 assert.equal(at(d1.objectId,1950).geometryPeriod.coverage,'partial');assert.deepEqual(d1.referenceRange,[4108,5504]);
 assert.equal(at('road:qgis:gottby:utangsvagen-100km5',1928).geometryPeriod.coverage,'full');
 assert.equal(at('road:rural:hammarland-way-155327037',1950).geometry,null,'Ödanbölevägen is a later addition on the 1929 sheet');
});
