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
const on=(p,id,year)=>model.resolveObject(id,year).geometry.paths.some(q=>q.some((x,i)=>i&&segd(p,q[i-1],x)<1));
const S='road:sund:sundsvagen:',LAP=S+'lappbole-bladkant',KW=S+'klippan-vast',KE=S+'klippan-ost';
const SALTVIK='road:qgis:saltvik:sundsvagen-lappbole-bladgransen',B='road:qgis:bomarsund:sundsvagen-',DEL1=B+'1-100km5',DEL2=B+'2-100km5',DEL3=B+'3-100km5';

test('Sundsvägen is continuous at the Lappböle sheet edge from 1968 and at Klippan from 1978',()=>{
 // The Klippan pieces are on the 1968 sheet as well (docs/main-roads-mainland.md); they join del 2 from 1978.
 for(const [id,from,a,b,first] of [[LAP,1968,SALTVIK,DEL2,1968],[KW,1978,DEL2,DEL3,1968],[KE,1978,DEL3,DEL1,1968]]){
  assert.equal(model.resolveObject(id,first-1).geometry,null,id+' before '+first);
  assert.equal(model.resolveObject(id,first).state,'open',id+' in '+first);
  for(const year of [from,1990,2026]){
   const p=model.resolveObject(id,year).geometry.paths[0];
   assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year);
   assert.ok(on(p[0],a,year)&&on(p.at(-1),b,year),id+' joins its neighbours in '+year);
  }
 }
 assert.ok(['nls:102110:1968','nls:102110:1993'].every(id=>model.objects.get(LAP).evidence.some(e=>e.sourceId===id)));
 for(const id of [KW,KE])assert.ok(model.objects.get(id).evidence.some(e=>e.sourceId==='nls:101212:1968'&&e.reviewId==='review:main-roads-mainland'),'the 1968 straight is dated by the main-road review');
});
