const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const segd=(p,a,b)=>{const ax=(b[0]-a[0])*55600,ay=(b[1]-a[1])*111200,px=(p[0]-a[0])*55600,py=(p[1]-a[1])*111200,t=Math.max(0,Math.min(1,(px*ax+py*ay)/(ax*ax+ay*ay||1)));return Math.hypot(px-t*ax,py-t*ay)};
const EK='road:eckero:eckerovagen:storby-hamn',SM='road:eckero:sandmovagen:posthuset',MS='road:marsund:eckero-hammarland';

test('from 1968 the road leads from the Storby post and customs house to the Marsund connection at Labbas',()=>{
 for(const year of [1968,1990,2026]){
  const ek=model.resolveObject(EK,year).geometry.paths[0],sm=model.resolveObject(SM,year).geometry.paths[0],ms=model.resolveObject(MS,year).geometry.paths;
  for(const id of [EK,SM])assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year);
  assert.ok(d(sm[0],ek[0])<1,'Sandmovägen leaves Eckerövägen at the junction in '+year);
  assert.ok(ms.some(q=>q.some((x,i)=>i&&segd(ek.at(-1),q[i-1],x)<1)),'Eckerövägen joins the Marsund connection in '+year);
 }
 assert.equal(model.resolveObject(EK,1967).geometry,null);
 assert.ok(['nls:101215:1968','nls:101215:1994'].every(id=>model.objects.get(EK).evidence.some(e=>e.sourceId===id)));
});
