const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid','historical-roads'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid;this.Roads=HistoricalRoads',box);
const catalogue=read('dist/assets/temporal-objects.json.gz'),model=new box.Model(catalogue),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const oid='road:marsund:eckero-hammarland',review=read('data/hammarlandsvagen-marsund.json');
const near=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200)<0.05;

test('Frebbenby, Marby, mid-Överby and Överby–Kyrkoby are drawn from 1929 with the connection’s own coordinates',()=>{
 assert.equal(model.resolveObject(oid,1928).geometry,null);
 const early=model.resolveObject(oid,1950),later=model.resolveObject(oid,1985).geometry;
 assert.equal(early.geometryPeriod.from,1929);assert.equal(early.geometryPeriod.to,1959);assert.ok(grid.ownsRoadObject(oid,v(1950)));
 // Each cut lies on the 1959 line: its ends are on that line's path.
 const e=review.early[0];assert.equal(early.geometry.paths.length,e.pathRanges.length);
 early.geometry.paths.forEach((p,k)=>{const src=later.paths[e.pathRanges[k][0]];
  for(const q of p)assert.ok(src.some(s=>near(s,q))||p.indexOf(q)===0||p.indexOf(q)===p.length-1);});
 // Four stretches, about 470 m, 340 m, 130 m and 1 140 m: the cuts on paths 18/17/16, 4/3 and 3/2 continue across the
 // path boundaries (path 17, 36 m, is cut whole).
 const len=p=>p.slice(1).reduce((n,q,i)=>n+Math.hypot((q[0]-p[i][0])*55600,(q[1]-p[i][1])*111200),0);
 const total=early.geometry.paths.reduce((n,p)=>n+len(p),0);assert.ok(Math.abs(total-2082)<10,total);
 for(const [a,b] of [[0,1],[1,2],[3,4],[6,7]])assert.ok(near(early.geometry.paths[a].at(-1),early.geometry.paths[b][0]),a);
 assert.deepEqual(early.geometryPeriod.canonicalRanges.length,4);
 // The bridge is open from 1959; the whole line (19 paths) from 1985, when the Överby bypass is first drawn.
 assert.equal(model.resolveObject(oid,1959).state,'open');assert.equal(later.paths.length,19);
});

test('the 1894 atlas line is hidden where the 1929 stretches replace it, and only from 1929',()=>{
 const atlas=read('dist/assets/historical-roads.json').sets.find(s=>s.id==='atlas-1894').features.find(f=>f.id==='atlas-1894-1');
 const gid=model.resolveObject(oid,1950).geometry.id,mine=atlas.replacementIntervals.filter(r=>r.geometryId===gid);
 assert.ok(mine.length>=2);
 const roads=new box.Roads(()=>{}),count=y=>roads.reconciledFeature(atlas,v(y),(x,y)=>[x,y]).paths.length;
 assert.ok(count(1950)>count(1928),'the atlas line is split where the stretches replace it');
});
