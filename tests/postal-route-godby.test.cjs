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
const EM='road:emkarbyvagen',GB='road:atlas1894:godbyvagen',VK1='road:qgis:saltvik:von-knorringsvagen-1-batch4',VK2='road:qgis:saltvik:von-knorringsvagen-2-batch4';
const PG='road:jomala:postgardsvagen',GJ='road:jomala:godbyvagen:golby-junction',BJ='road:jomala:godbyvagen:bjorkang',KO='road:finstrom:godby-korsningen',SF='road:finstrom:sundsvagen:godby-farjsundet';

test('from 1968 the postal road runs from Emkarbyvägen through Gölby and Godby to the Färjsundet bridge',()=>{
 for(const year of [1968,1975,1990,2026]){
  const g=id=>model.resolveObject(id,year).geometry;
  for(const id of [PG,GJ,BJ,KO,SF])assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year);
  assert.ok(near(g(PG),g(EM))&&near(g(PG),g(GB)),'Postgårdsvägen joins Emkarbyvägen and Godbyvägen in '+year);
  assert.ok(near(g(KO),g(GB))&&near(g(KO),g(VK2)),'the Godby junction joins Godbyvägen and von Knorringsvägen in '+year);
  assert.ok(near(g(SF),g(VK1)),'Sundsvägen leaves von Knorringsvägen in '+year);
 }
 for(const id of [PG,GJ,BJ,KO,SF])assert.equal(model.resolveObject(id,1967).geometry,null,id);
});

test('Emkarbyvägen draws its eastern part from 1968: round the old bend to Bergens until 1977, then on the 1978 line',()=>{
 const g68=model.resolveObject(EM,1970).geometry,g78=model.resolveObject(EM,1980).geometry,g67=model.resolveObject(EM,1967).geometry;
 assert.equal(g68.paths.length,g67.paths.length+1);assert.equal(g78.paths.length,g67.paths.length+1);
 const end68=g68.paths.at(-1).at(-1),end78=g78.paths.at(-1).at(-1);
 assert.ok(segd(end68,...model.resolveObject(PG,1970).geometry.paths[0].slice(0,2))<1,'in 1968–1977 it ends at Postgårdsvägen');
 assert.ok(g78.paths.at(-1).length>g68.paths.at(-1).length-40);
 const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);assert.ok(d(end78,model.resolveObject(EM,2026).geometry.paths[0].at(-1))<0.1,'from 1978 it ends where today\'s road ends');
});
