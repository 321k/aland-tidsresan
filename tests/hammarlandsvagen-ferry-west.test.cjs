const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const MB='road:qgis:eckero:marbyvagen-100km1',M='road:marsund:eckero-hammarland',LINK='road:eckero:gamla-landsvagen:sundkvist',SHORE='road:eckero:gamla-landsvagen:strandvagen';
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const len=p=>p.slice(1).reduce((n,q,i)=>n+d(q,p[i]),0);
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
const meets=(a,b)=>ends(a).some(p=>ends(b).some(q=>d(p,q)<1));

test('in 1929–1955 the road from the narrow sound runs along the shore, past Klemes and Sundkvist to Marby, as one line',()=>{
 for(const year of [1929,1950,1955]){
  const m=model.resolveObject(M,year).geometry,shore=model.resolveObject(SHORE,year).geometry,mb=model.resolveObject(MB,year).geometry,link=model.resolveObject(LINK,year).geometry;
  for(const id of [SHORE,MB,LINK])assert.ok(grid.ownsRoadObject(id,v(year)),id);
  assert.ok(meets(m,shore),'sound–shore');assert.ok(meets(shore,mb),'shore–Marbyvägen');assert.ok(meets(mb,link),'Marbyvägen–link');assert.ok(meets(link,m),'link–Marby');
  assert.ok(Math.abs(len(mb.paths[0])-1800)<5);
 }
});

test('from 1956 the road runs on Marbyvägen to the sound and the shore road is gone; the link at Sundkvist until 1968',()=>{
 const mb=model.resolveObject(MB,1957);assert.equal(mb.geometryPeriod.from,1956);assert.equal(mb.geometryPeriod.to,1968);
 assert.ok(Math.abs(len(mb.geometry.paths[0])-(len(model.resolveObject(MB,1968).geometry.paths[0])-200))<5);
 assert.equal(model.resolveObject(SHORE,1957).state,'unknown');assert.equal(model.resolveObject(SHORE,1957).geometry,null);
 assert.equal(model.resolveObject(LINK,1967).state,'open');assert.equal(model.resolveObject(LINK,1968).state,'unknown');
 assert.equal(model.resolveObject(MB,1928).geometry,null);
 // 1956–1958: Marbyvägen's north end is 30 m from the end of the connection's 1929 stretch at the sound (no road between yet)
 const gap=Math.min(...ends(model.resolveObject(M,1957).geometry).map(p=>Math.min(...ends(mb.geometry).map(q=>d(p,q)))));assert.ok(gap>20&&gap<40,gap);
});
