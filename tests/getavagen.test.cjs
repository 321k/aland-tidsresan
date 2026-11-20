const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const GE='road:qgis:saltvik:getavagen-godby-norra-bladgransen',KY='road:qgis:saltvik:kyrkvagen-batch4',BA='road:qgis:saltvik:bartsgardavagen',
 KR='road:qgis:saltvik:kroklundsvagen',SA='road:qgis:saltvik:saltviksvagen-1-batch4',GA='road:qgis:saltvik:gamla-getavagen';
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
const meets=(a,b)=>ends(a).some(p=>b.paths.some(q=>q.some(x=>d(p,x)<1)))||ends(b).some(p=>a.paths.some(q=>q.some(x=>d(p,x)<1)));

test('1929–1967 the old main road runs from Godby village over Bartsgårda, Ödkarby and Sålis to Avanåker',()=>{
 for(const year of [1929,1944,1967]){
  const g=id=>model.resolveObject(id,year).geometry;
  for(const id of [GE,KY,BA,KR,SA,GA]){assert.equal(model.resolveObject(id,year).state,'open',id);assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year)}
  assert.equal(g(GE).paths.length,2,'today\'s road leaves out the Godby diagonal and the Bartsgårda straight');
  for(const [a,b] of [[KY,GE],[GE,BA],[BA,KR],[KR,SA],[SA,GE],[GA,GE]])assert.ok(meets(g(a),g(b)),a+' meets '+b+' in '+year);
 }
 for(const id of [GE,KY,BA,KR,GA])assert.equal(model.resolveObject(id,1928).geometry,null,id);
});

test('from 1968 today\'s Getavägen is whole; the old roads stay as they are mapped today',()=>{
 assert.equal(model.resolveObject(GE,1968).geometry.paths.length,1);
 for(const id of [KY,BA,KR,GA])assert.equal(model.resolveObject(id,1968).geometry.id,model.resolveObject(id,2026).geometry.id);
 assert.equal(model.resolveObject(SA,1975).geometry.paths.length,1,'Saltviksvägen keeps its dated western stretch until 1993');
 assert.equal(model.objects.get(GE).mainRoadReview.constructionYear,null);
});
