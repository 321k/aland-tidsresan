const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/hammarlandsvagen-kattby.json'),catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog),at=(id,y)=>model.resolveObject(id,y);
const k=[55500,111320],dist=(a,b)=>Math.hypot((a[0]-b[0])*k[0],(a[1]-b[1])*k[1]);
const seg=(p,a,b)=>{const v=[0,1].map(i=>(b[i]-a[i])*k[i]),w=[0,1].map(i=>(p[i]-a[i])*k[i]),l=v[0]**2+v[1]**2,t=l?Math.max(0,Math.min(1,(w[0]*v[0]+w[1]*v[1])/l)):0;return Math.hypot(w[0]-t*v[0],w[1]-t*v[1])};
const near=(p,lines)=>Math.min(...lines.flatMap(line=>line.slice(1).map((q,i)=>seg(p,line[i],q))));
const K='road:rural:hammarland-hammarlandsvagen-kattby-west',CH='road:rural:hammarland-hammarlandsvagen-church-corridor';

test('Kattby westwards is drawn from the 1929 parish maps, not only from the 1959 bridge assumption',()=>{
 assert.equal(at(K,1928).geometry,null);
 const r=at(K,1929);assert.equal(r.state,'open');assert.equal(r.geometryPeriod.coverage,'full');assert.equal(r.geometryPeriod.to,1959);
 for(const p of r.geometry.paths[0])assert.ok(near(p,at(K,1959).geometry.paths)<0.05,'the same line, not moved');
 for(const p of at(K,1959).geometry.paths[0])assert.ok(near(p,r.geometry.paths)<0.05,'the whole line');
 const o=model.objects.get(K);assert.equal(o.hammarlandsvagenMainRoad.review,review.source.id);assert.equal(o.hammarlandsvagenMainRoad.previousFirstYear,1959);
 // the 1959 assumption stays as it was, after the map-dated period
 assert.equal(o.states[1].from,1959);assert.match(o.states[1].note,/Marsund/);
 const ev=o.evidence.filter(e=>e.reviewId===review.source.id);
 assert.deepEqual(ev.map(e=>e.sourceId).sort(),['nls:9c72a692-bae4-473d-93bb-7bcdee1222e7','nls:9c72eaa7-cd73-4f92-91b0-dc36524bef08','nls:map-37971493','nls:map-39091228']);
 assert.ok(ev.every(e=>e.outcome==='present'&&e.constructionYear===null));
});

test('in 1929–1958 the road runs on from the church corridor without a gap',()=>{
 for(const y of [1929,1950,1958]){
  const a=at(CH,y).geometry.paths.flat(),b=at(K,y).geometry.paths[0];
  assert.ok(Math.min(...a.map(p=>Math.min(dist(p,b[0]),dist(p,b.at(-1)))))<1,`${y}`);
 }
});

test('the Eckerö sheets are cited as their own sources',()=>{
 for(const id of ['nls:map-39091228','nls:map-37971493']){const s=catalog.sources.find(x=>x.id===id);assert.ok(s&&/Eckerö/.test(s.title)&&/funet/.test(s.url),id)}
});
