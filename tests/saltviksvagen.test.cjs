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
const D1='road:qgis:saltvik:saltviksvagen-1-batch4',TS='road:qgis:tjudo:saltviksvagen-100km1',DG='road:qgis:tjudo:daglosavagen-100km1',AND='road:tjudo:gamla-saltviksvagen:andelsby',
 D2='road:qgis:saltvik:saltviksvagen-2-batch4',ANT='road:qgis:saltvik:saltviksvagen-antbole-nygard',KN='road:qgis:saltvik:saltviksvagen-kavelbro-norr',
 KAV='road:qgis:saltvik:kavelbrovagen',BY='road:qgis:saltvik:saltviksvagen-kavelbro-forbifart',KK='road:qgis:saltvik:saltviksvagen-kvarnbo-kavelbro';

test('1929–1967 Saltviksvägen runs from Laby round the Andelsby curve and along the shore over Kavelbro to Kvarnbo',()=>{
 for(const year of [1929,1950,1967]){
  const g=id=>model.resolveObject(id,year).geometry;
  for(const id of [TS,DG,AND,D2,ANT,KN,KAV,KK])assert.ok(grid.ownsRoadObject(id,v(year)),id+' '+year);
  assert.equal(model.resolveObject(BY,year).geometry,null,'the Kavelbro bypass is younger');
  assert.equal(g(TS).paths.length,2,'today\'s diagonal at Andelsby is younger');
  for(const [a,b] of [[TS,DG],[DG,AND],[AND,TS],[TS,D2],[D2,ANT],[ANT,KN],[KN,KAV],[KAV,KK]])assert.ok(meets(g(a),g(b)),a+' meets '+b+' in '+year);
  assert.ok(!meets(g(D1),g(TS)),'the link at Västergård lies on the sheet seam and is not drawn');
 }
 assert.equal(model.resolveObject(ANT,1928).geometry,null);
 assert.ok(model.resolveObject(TS,1927).geometry,'the Tjudö sheet is from 1927');
});

test('from 1968 the diagonal at Andelsby; the old curve is drawn until 1984 and Dåglösavägen whole',()=>{
 assert.equal(model.resolveObject(TS,1968).geometry.paths.length,1);
 assert.equal(model.resolveObject(AND,1975).state,'open');assert.equal(model.resolveObject(AND,1984).state,'unknown');
 assert.equal(model.resolveObject(DG,1968).geometry.id,model.resolveObject(DG,2026).geometry.id);
 assert.equal(model.resolveObject(KAV,1980).state,'open','Kavelbrovägen stays as it is mapped today');
 assert.equal(model.objects.get(AND).hammarlandsvagenMainRoad.constructionYear,null);
});
