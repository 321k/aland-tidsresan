const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const segd=(p,a,b)=>{const ax=(b[0]-a[0])*55600,ay=(b[1]-a[1])*111200,px=(p[0]-a[0])*55600,py=(p[1]-a[1])*111200,t=Math.max(0,Math.min(1,(px*ax+py*ay)/(ax*ax+ay*ay||1)));return Math.hypot(px-t*ax,py-t*ay)};
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
const near=(a,b)=>ends(a).some(p=>b.paths.some(q=>q.some((x,i)=>i&&segd(p,q[i-1],x)<1)));
const NM='road:mariehamn:major-followup:norra-mockelovagen',MV='road:qgis:gottby:mockelovagen-100km5',ID='road:jomala:mockelovagen:lonnelund';

test('from 1929 the road runs from Norra Möckelövägen along Lönnelund to Möckelö as one line',()=>{
 for(const year of [1929,1953,1975,2026]){
  const g=id=>model.resolveObject(id,year).geometry;
  for(const id of [ID,MV])assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year);
  assert.ok(near(g(ID),g(NM))&&near(g(ID),g(MV)),'the link joins Norra Möckelövägen and Möckelövägen in '+year);
 }
 assert.equal(model.resolveObject(MV,1928).state,'open','the Kungsö sheet is from 1928');
 assert.equal(model.resolveObject(MV,1927).geometry,null);
 assert.equal(model.resolveObject(MV,1950).geometry.id,'geometry:mockelo-road-1928:mockelovagen-100km5');
});
