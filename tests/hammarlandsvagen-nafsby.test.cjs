const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/hammarlandsvagen-nafsby.json'),north=read('data/hammarlandsvagen-main-road.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog),at=(id,y)=>model.resolveObject(id,y);
const k=[55500,111320],dist=(a,b)=>Math.hypot((a[0]-b[0])*k[0],(a[1]-b[1])*k[1]);
const seg=(p,a,b)=>{const v=[0,1].map(i=>(b[i]-a[i])*k[i]),w=[0,1].map(i=>(p[i]-a[i])*k[i]),l=v[0]**2+v[1]**2,t=l?Math.max(0,Math.min(1,(w[0]*v[0]+w[1]*v[1])/l)):0;return Math.hypot(w[0]-t*v[0],w[1]-t*v[1])};
const near=(p,lines)=>Math.min(...lines.flatMap(line=>line.slice(1).map((q,i)=>seg(p,line[i],q))));
const len=p=>p.slice(1).reduce((s,q,i)=>s+dist(p[i],q),0);
const P='road:rural:hammarland-',VAST=P+'hammarlandsvagen-vastmyra',OLD=review.oldRoad.id;
const drawn=y=>[...model.objects.values()].filter(o=>o.kind==='roadSegment').flatMap(o=>{const r=at(o.id,y);return r.state==='open'&&r.geometry?r.geometry.paths:[]});

test('the old road through Näfsby is drawn from 1929 on the smaller roads it survives as',()=>{
 for(const e of review.early){
  assert.equal(at(e.objectId,1928).geometry,null,e.objectId);
  const r=at(e.objectId,1929);assert.equal(r.state,'open');assert.equal(r.geometryPeriod.to,e.until);
  const want=e.ranges.map(([a,b])=>b-a);r.geometry.paths.map(len).forEach((d,i)=>assert.ok(Math.abs(d-want[i])<1+want[i]*0.003,e.objectId));
  // the early geometry is the object's own coordinates: it lies on the geometry it was cut from
  const from=catalog.geometries.find(g=>g.id===e.geometryId).paths;
  for(const p of r.geometry.paths.flat())assert.ok(near(p,from)<0.05,e.objectId);
  const o=model.objects.get(e.objectId);assert.equal(o.hammarlandsvagenMainRoad.review,review.source.id);
  assert.equal(o.hammarlandsvagenMainRoad.previousFirstYear,e.gapUntil||e.until);
 }
});

test('Lillåkersgränd is old road only for its northern 85 m, and the old school road without its younger branch',()=>{
 const l=at(P+'way-545279820',1950);assert.equal(l.geometryPeriod.coverage,'partial');assert.ok(Math.abs(len(l.geometry.paths[0])-85)<1);
 assert.ok(len(at(P+'way-545279820',1970).geometry.paths[0])>360,'whole street from 1968');
 const s=at(P+'vastmyra-old-school-approach',1950);assert.equal(s.geometry.paths.length,1);assert.equal(s.geometryPeriod.coverage,'partial');
 assert.equal(at(P+'vastmyra-old-school-approach',1970).geometry.paths.length,2,'the branch to the bypass is drawn from 1968');
});

test('the parallel stretch is unknown 1968–1985: the base maps draw only a thin line there',()=>{
 const id=P+'way-1419026567';
 assert.equal(at(id,1950).state,'open');assert.equal(at(id,1970).state,'unknown');assert.equal(at(id,1970).geometry,null);assert.equal(at(id,1990).state,'open');
 // way 1419026568: its southern arm (on the same stretch) is drawn before 1968 and again from 1985, not in between
 const arm=P+'way-1419026568';
 assert.ok(len(at(arm,1950).geometry.paths[0])>150);assert.ok(len(at(arm,1970).geometry.paths[0])<90);assert.ok(len(at(arm,1990).geometry.paths[0])>150);
});

test('the vanished pieces are one old-road object: open 1929–1968, then unknown',()=>{
 const o=model.objects.get(OLD);assert.ok(o);assert.equal(o.routeId,'road:Gamla Hammarlandsvägen');
 assert.equal(at(OLD,1929).geometry.paths.length,2);assert.equal(at(OLD,1970).state,'unknown');assert.equal(at(OLD,1970).geometry,null);
 const total=at(OLD,1950).geometry.paths.map(len).reduce((a,b)=>a+b);assert.ok(total>130&&total<150,`${total} m`);
});

test('in 1950 the main road through Näfsby is one connected line from Mattas to Korsbroström',()=>{
 const ids=[VAST,OLD,...review.early.map(e=>e.objectId)],lines=ids.flatMap(id=>at(id,1950).geometry.paths);
 const ends=lines.flatMap(l=>[l[0],l.at(-1)]),loose=ends.filter(p=>lines.filter(l=>near(p,[l])<2).length<2);
 // Västmyra's 1929 cuts end south at Mattas (with Björkgård's cut) and north at Postad–Korsängen; nothing else is loose
 const others=['road:rural:hammarland-way-345143750',P+'hammarlandsvagen-postad-korsangen'].flatMap(id=>at(id,1950).geometry.paths);
 assert.ok(loose.every(p=>near(p,others)<2),`${loose.length} loose ends`);
 // the north review now keeps today's road as the old road up to 14.42 km, where the old road turned into the village
 assert.equal(north.boundaries['nafsby-south'],14420);
});

test('the 1968 picture is unchanged: the vanished pieces and the parallel stretch are not drawn',()=>{
 const y1970=drawn(1970);
 for(const p of review.oldRoad.paths.flatMap(path=>path.slice(2,-2)))assert.ok(near(p,y1970)>3,'old line drawn in 1970');
 assert.equal(at(P+'way-1419026567',1975).geometry,null);
});
