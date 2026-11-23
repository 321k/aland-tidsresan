const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz'));
const w={};vm.createContext(w);w.window=w;vm.runInContext(fs.readFileSync('dist/postal-route-roads.js','utf8')+fs.readFileSync('dist/archive.js','utf8').split('(()=>{')[0],w);
const J=x=>JSON.parse(JSON.stringify(x));
const m=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const segd=(p,a,b)=>{const ax=(b[0]-a[0])*55600,ay=(b[1]-a[1])*111200,px=(p[0]-a[0])*55600,py=(p[1]-a[1])*111200,t=Math.max(0,Math.min(1,(px*ax+py*ay)/(ax*ax+ay*ay||1)));return Math.hypot(px-t*ax,py-t*ay)};
const data=read('data/postal-route-stations.json'),S=Object.fromEntries(data.stations.map(s=>[s.id,s]));

test('every land leg between two post stations follows roads mapped by the leg year, and ferries',()=>{
 const legs=J(w.POSTAL_ROUTE_ROADS);assert.deepEqual(legs.map(l=>l.from+'-'+l.to),data.legs.map(l=>l.from+'-'+l.to));
 for(const leg of legs.filter(l=>l.by==='road')){
  assert.ok(Number.isInteger(leg.year)&&leg.year<=1968,leg.from+'-'+leg.to+' is dated by 1968');
  const p=leg.path,a=S[leg.from],b=S[leg.to];
  assert.deepEqual(p[0],[a.lon,a.lat].map(x=>+x.toFixed(6)));assert.deepEqual(p.at(-1),[b.lon,b.lat].map(x=>+x.toFixed(6)));
  assert.ok(m(p[0],p[1])<=150&&m(p.at(-2),p.at(-1))<=150,'stations lie by the road');
  // the roads mapped by the leg year: every geometry an object had in a period beginning by then (old ferry roads too)
  const lines=leg.objects.flatMap(o=>model.objects.get(o.id).geometryPeriods.filter(g=>g.from<=leg.year).flatMap(g=>model.geometries.get(g.geometryId).paths));
  for(const q of p.slice(1,-1))assert.ok(lines.some(l=>l.some((x,i)=>i&&segd(q,l[i-1],x)<1)),`${leg.from}-${leg.to}: ${q} lies on a road mapped by ${leg.year}`);
  for(const f of leg.ferries)assert.ok(data.crossings.some(c=>c.id===f));
 }
 assert.equal(legs.at(-1).by,'boat');assert.equal(legs.at(-1).path,undefined);
});

test('the Åland stops are the post stations, in order, between the sea crossings',()=>{
 const stops=J(w.postalRouteForYear(1700)),names=stops.map(s=>s.name),i=names.indexOf('Storby');
 assert.deepEqual(names.slice(i,i+6),data.stations.map(s=>s.name));
 assert.deepEqual(stops.slice(i,i+6).map(s=>s.station),data.stations.map(s=>s.id));
});
