const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const catalog=read('dist/assets/temporal-objects.json.gz'),model=new box.Model(catalog),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const segd=(p,a,b)=>{const ax=(b[0]-a[0])*55600,ay=(b[1]-a[1])*111200,px=(p[0]-a[0])*55600,py=(p[1]-a[1])*111200,t=Math.max(0,Math.min(1,(px*ax+py*ay)/(ax*ax+ay*ay||1)));return Math.hypot(px-t*ax,py-t*ay)};
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
const near=(a,b)=>ends(a).some(p=>b.paths.some(q=>q.some((x,i)=>i&&segd(p,q[i-1],x)<1)));
const NS='road:qgis:gottby:norra-svibyvagen-100km5',KB='road:qgis:mariehamn:kasbergsvagen-200km2',SV='road:qgis:mariehamn:svibyvagen-1-200km2',NM='road:mariehamn:major-followup:norra-mockelovagen';
const JN='road:jomala:kasbergsvagen:norra-svibyvagen',EW='road:jomala:sviby:vagen-mot-svibyvagen',SH='road:jomala:norra-mockelovagen:norra-delen';

test('from 1929 Norra Svibyvägen joins Kasbergsvägen and runs on along the shore as Norra Möckelövägen',()=>{
 for(const year of [1929,1950,1975,2026]){
  const g=id=>model.resolveObject(id,year).geometry;
  for(const id of [NS,JN,KB,SH])assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year);
  assert.equal(model.resolveObject(NM,year).state,'open',NM+' '+year); /* a Mariehamn street object, drawn by the town layers */
  assert.ok(near(g(JN),g(NS))&&near(g(JN),g(KB)),'the junction piece joins both roads in '+year);
  assert.ok(near(g(SH),g(NM)),'the shore piece joins Norra Möckelövägen in '+year);
 }
 assert.equal(model.resolveObject(JN,1928).state,'open','the Kungsö sheet is from 1928');
 assert.equal(model.resolveObject(NM,1928).geometry,null);
});

test('from 1942 the road east to Svibyvägen replaces the 1942 photo stub',()=>{
 assert.equal(model.resolveObject(EW,1941).geometry,null);
 for(const year of [1942,1953,1975,2026]){
  const g=id=>model.resolveObject(id,year).geometry;
  assert.ok(near(g(EW),g(NS))&&near(g(EW),g(SV))&&near(g(SH),g(EW)),'the road joins Norra Svibyvägen, Svibyvägen and the shore piece in '+year);
 }
 for(const s of catalog.cityStages.filter(s=>['city-reconstruction-1942','city-reconstruction-1952'].includes(s.id))){
  assert.ok(!s.features.some(f=>f.id.endsWith(':approach-gap:0')&&f.traceId==='city-1942-trace-0'),'no stub in '+s.id);
  assert.ok(s.features.some(f=>f.objectId===EW),'the road is in '+s.id);
 }
 assert.equal(model.objects.get(EW).evidence.find(e=>e.observationType==='aerial').observedAt,'1942-07-25');
});
