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
const MA='road:rural:hammarland-way-1422779920',B1='road:rural:hammarland-way-495221553',B2='road:rural:hammarland-way-160987689',SV='road:rural:hammarland-way-86548779',OLD='road:hammarland:gamla-sodersundavagen:mattas';

test('1929–1994 Mattas, the old bend and the link to Södersundavägen are one line',()=>{
 for(const year of [1929,1950,1975,1990]){
  const g=id=>model.resolveObject(id,year).geometry;
  for(const id of [MA,B1,B2,OLD,SV])assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year);
  assert.ok(near(g(B1),g(MA))&&near(g(B1),g(B2)),'the bend joins Mattas in '+year);
  assert.ok(near(g(OLD),g(B2))&&near(g(OLD),g(SV)),'the link joins the bend and Södersundavägen in '+year);
  assert.equal(g(SV).paths[0].at(-1).join(),model.resolveObject(SV,1985).geometry.paths[0].at(-1).join(),'Södersundavägen begins at the junction in '+year);
 }
 assert.equal(model.resolveObject(OLD,1995).state,'unknown');
 assert.equal(model.resolveObject(B2,1928).geometry,null);
});
