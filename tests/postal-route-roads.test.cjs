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

test('every leg between two post stations follows roads mapped by its year, ferries and boat lines',()=>{
 const legs=J(w.POSTAL_ROUTE_ROADS);assert.deepEqual(legs.map(l=>l.from+'-'+l.to+':'+l.years),data.legs.map(l=>l.from+'-'+l.to+':'+l.years));
 const onRoads=(part,label)=>{
  assert.ok(Number.isInteger(part.year)&&part.year<=1985,label+' is dated');
  // the roads mapped by the part's year: every geometry an object had in a period beginning by then (old ferry roads too)
  const lines=part.objects.flatMap(o=>model.objects.get(o.id).geometryPeriods.filter(g=>g.from<=part.year).flatMap(g=>model.geometries.get(g.geometryId).paths));
  for(const q of part.path.slice(1,-1))assert.ok(lines.some(l=>l.some((x,i)=>i&&segd(q,l[i-1],x)<1)),`${label}: ${q} lies on a road mapped by ${part.year}`);
  for(const f of part.ferries)assert.ok(data.crossings.some(c=>c.id===f));
 };
 for(const leg of legs){
  const a=S[leg.from],b=S[leg.to],label=leg.from+'-'+leg.to+' '+leg.years;
  const parts=leg.by==='road'?[{...leg,by:'road'}]:leg.parts;
  const p=parts.flatMap(x=>x.path);
  assert.ok(m(p[0],[a.lon,a.lat])<1&&m(p.at(-1),[b.lon,b.lat])<1,label+' runs from station to station');
  for(const [x,y] of parts.slice(1).map((y,i)=>[parts[i],y]))assert.ok(m(x.path.at(-1),y.path[0])<1,label+': parts meet');
  for(const part of parts)if(part.by==='road'){assert.ok(m(part.path[0],part.path[1])<=150&&m(part.path.at(-2),part.path.at(-1))<=150);onRoads(part,label)}
  if(leg.by==='road')assert.ok(leg.years[1]<=1911&&leg.years[0]>=1638);
 }
});

test('the Åland stops are the post stations of the year, in order, between the sea crossings',()=>{
 for(const year of [1650,1700,1800]){
  const stops=J(w.postalRouteForYear(year)),names=stops.map(s=>s.name),i=names.indexOf('Storby');
  const want=data.stations.filter(s=>year>=(s.from??1638)&&year<=(s.to??1911));
  assert.deepEqual(names.slice(i,i+want.length),want.map(s=>s.name));assert.deepEqual(stops.slice(i,i+want.length).map(s=>s.station),want.map(s=>s.id));
 }
});
