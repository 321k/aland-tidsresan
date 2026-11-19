const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const MV='road:qgis:eckero:marsundsvagen-100km4',M='road:marsund:eckero-hammarland',K='road:rural:hammarland-hammarlandsvagen-kattby-west';
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const len=p=>p.slice(1).reduce((n,q,i)=>n+d(q,p[i]),0);

test('Marsundsvägen to the ferry pier is drawn from 1929, the rest of it still from 1994',()=>{
 assert.equal(model.resolveObject(MV,1928).geometry,null);
 const early=model.resolveObject(MV,1950),whole=model.resolveObject(MV,1994).geometry;
 assert.equal(early.state,'open');assert.equal(early.geometryPeriod.from,1929);assert.equal(early.geometryPeriod.to,1994);assert.ok(grid.ownsRoadObject(MV,v(1950)));
 assert.equal(early.geometry.paths.length,1);assert.ok(Math.abs(len(early.geometry.paths[0])-1040)<5);
 // the cut starts where the whole road starts (Frebbenby) and keeps its coordinates
 assert.ok(d(early.geometry.paths[0][0],whole.paths[0][0])<0.05);
 for(const q of early.geometry.paths[0].slice(1,-1))assert.ok(whole.paths[0].some(s=>d(s,q)<0.05));
 for(const y of [1959,1968,1985])assert.equal(model.resolveObject(MV,y).geometryPeriod.from,1929);
 assert.equal(model.resolveObject(MV,2026).geometry.id,whole.id);
});

test('in 1929–1958 the road runs from Kattby west through Frebbenby to Marsundsvägen, with the 27 m junction link',()=>{
 const k=model.resolveObject(K,1950).geometry,m=model.resolveObject(M,1950).geometry,mv=model.resolveObject(MV,1950).geometry;
 const ends=g=>g.paths.flatMap(p=>[p[0],p.at(-1)]);
 assert.ok(ends(k).some(a=>ends(m).some(b=>d(a,b)<1)),'Kattby west meets the Frebbenby stretch');
 const gap=Math.min(...ends(m).map(b=>d(b,mv.paths[0][0])));assert.ok(gap>25&&gap<28,gap);
 const fr=m.paths.slice(0,3);assert.ok(Math.abs(fr.reduce((n,p)=>n+len(p),0)-472)<3);
});
