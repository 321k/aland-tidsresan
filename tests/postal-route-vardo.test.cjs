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
const VV='road:qgis:vardo:vardovagen-200km1',DK=[...model.objects.keys()].find(k=>k.startsWith('road:qgis:vardo:drottning-kristinas-gata'));

test('1971–1984 Vårdövägen runs into Vargata and round the bend past the Post farm; the straight is first on the 1985 map',()=>{
 for(const year of [1971,1980]){
  const g=model.resolveObject(VV,year).geometry,k=model.resolveObject(DK,year).geometry.paths[0];
  assert.ok(grid.ownsRoadObject(VV,v(year)));assert.equal(g.paths.length,2,'two pieces in '+year);
  assert.ok(d(g.paths[0].at(-1),k[0])<0.1&&d(g.paths[1][0],k.at(-1))<0.1,'the bend joins both pieces in '+year);
 }
 assert.equal(model.resolveObject(VV,1970).geometry,null);
 assert.equal(model.resolveObject(VV,1985).geometry.paths.length,1);
});
