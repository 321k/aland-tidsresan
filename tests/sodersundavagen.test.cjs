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
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
const meets=(a,b)=>ends(a).some(p=>b.paths.some(q=>q.some(x=>d(p,x)<1)))||ends(b).some(p=>a.paths.some(q=>q.some(x=>d(p,x)<1)));
const near=(a,b)=>ends(a).some(p=>b.paths.some(q=>q.some((x,i)=>i&&segd(p,q[i-1],x)<1)));
const segd=(p,a,b)=>{const ax=(b[0]-a[0])*55600,ay=(b[1]-a[1])*111200,px=(p[0]-a[0])*55600,py=(p[1]-a[1])*111200,t=Math.max(0,Math.min(1,(px*ax+py*ay)/(ax*ax+ay*ay||1)));return Math.hypot(px-t*ax,py-t*ay)};
const MA='road:rural:hammarland-way-1422779920',SV='road:rural:hammarland-way-86548779',OLD='road:jomala:gamla-sodersundavagen:jomala-kyrkby',GB='road:qgis:jomala:godbyvagen-batch5';

test('1929–1994 Södersundavägen over Ulvsby round the loop to Jomala church is one line',()=>{
 for(const year of [1929,1950,1975,1990]){
  const g=id=>model.resolveObject(id,year).geometry;
  for(const id of [SV,OLD,GB])assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year);
  const w=g(SV).paths[0].at(-1);assert.ok(d(w,model.resolveObject(SV,1985).geometry.paths[0].at(-1))<0.1,'the west end is the rural review\'s, east of the 1995 bypass at Mattas');
  assert.ok(meets(g(SV),g(OLD)),'Södersundavägen meets the loop in '+year);
  assert.ok(near(g(OLD),g(GB)),'the loop ends on Godbyvägen at the church in '+year);
 }
 assert.equal(model.resolveObject(OLD,1928).state,'open','the Jomala sheet is from 1928');
 assert.equal(model.resolveObject(SV,1928).geometry,null);
});

test('from 1995 today\'s straight; the loop keeps Drittel-Mattes Gränd and S:t Olofs vägen',()=>{
 assert.equal(model.resolveObject(SV,1995).geometry.id,model.resolveObject(SV,2026).geometry.id.replace(/.*/,model.resolveObject(SV,1995).geometry.id));
 assert.equal(model.resolveObject(SV,1995).geometry.paths.length,1);
 const g95=model.resolveObject(OLD,1995).geometry;assert.equal(g95.paths.length,2);
 assert.equal(model.resolveObject(OLD,2026).state,'open');
 assert.equal(model.objects.get(OLD).mainRoadReview.mainRoadUntil,1995);
});
