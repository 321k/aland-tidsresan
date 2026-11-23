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
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
const near=(a,b)=>ends(a).some(p=>b.paths.some(q=>q.some((x,i)=>i&&segd(p,q[i-1],x)<1)));
const UT='road:qgis:gottby:utangsvagen-100km5',NS='road:qgis:gottby:norra-svibyvagen-100km5',KB='road:qgis:mariehamn:kasbergsvagen-200km2',SV='road:qgis:mariehamn:svibyvagen-1-200km2';
const JN='road:jomala:kasbergsvagen:norra-svibyvagen',OLD='road:jomala:gamla-vagen:sviby',CORNER='road:jomala:gamla-kasbergsvagen:tallasen',KG='road:jomala:kasbergsgatan';

test('1929–1977 Utängsvägen through Sviby, Norra Svibyvägen, Kasbergsvägen round the corner, Kasbergsgatan and Svibyvägen are one line',()=>{
 for(const year of [1929,1950,1975]){
  const g=id=>model.resolveObject(id,year).geometry;
  for(const id of [UT,OLD,NS,JN,KB,CORNER,KG,SV])assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year);
  assert.ok(near(g(OLD),g(UT))&&near(g(OLD),g(NS)),'the Sviby road joins Utängsvägen and Norra Svibyvägen in '+year);
  assert.ok(near(g(JN),g(NS))&&near(g(JN),g(KB)),'the junction piece joins Norra Svibyvägen and Kasbergsvägen in '+year);
  assert.ok(near(g(CORNER),g(KB)),'the corner joins Kasbergsvägen in '+year);
  assert.ok(near(g(KG),g(KB))&&near(g(KG),g(SV)),'Kasbergsgatan joins Kasbergsvägen and Svibyvägen in '+year);
  assert.equal(g(KB).paths.length,2,'Kasbergsvägen leaves out the diagonal before 1985');
 }
 assert.equal(model.resolveObject(OLD,1928).state,'open','the Kungsö sheet is from 1928');
 assert.equal(model.resolveObject(KB,1928).geometry,null);
});

test('from 1978 the airport; from 1985 today\'s diagonal at Talläsen',()=>{
 const o78=model.resolveObject(OLD,1978).geometry,o50=model.resolveObject(OLD,1950).geometry;
 assert.ok(o78.paths[0].length<o50.paths[0].length,'only the first part by the fence survives');
 assert.equal(model.resolveObject(CORNER,1985).geometry,null);
 assert.equal(model.resolveObject(KB,1985).geometry.paths.length,1);
 assert.equal(model.resolveObject(KG,2026).state,'open');
});
