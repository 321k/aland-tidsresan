const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
for(const name of ['temporal-objects','city-grid','historical-roads'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.Model=TemporalObjects;this.Grid=CityGrid;this.Roads=HistoricalRoads',box);
const catalogue=read('dist/assets/temporal-objects.json.gz'),objects=new Map(catalogue.objects.map(o=>[o.id,o]));
const model=new box.Model(catalogue),grid=new box.Grid(()=>{});
Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model});
const v=year=>({year,zoom:1,scale:1,meta:{world:40075016.7},cityGrid:grid});
const atlas=read('dist/assets/historical-roads.json').sets.find(s=>s.id==='atlas-1894').features.find(f=>f.id==='atlas-1894-1');
// Atlas vertices 10-13.6 are Kattby-Smedens: the stretch the 1929 Hammarlandsvägen reviews draw.
const retired=year=>atlas.replacementIntervals.filter(r=>grid.ownsRoadObject(r.objectId,v(year))&&model.resolveObject(r.objectId,year)?.geometry?.id===r.geometryId)
 .map(r=>r.sourceVertexRange).sort((a,b)=>a[0]-b[0]);
// Neighbouring intervals meet within about 1e-5 of a vertex index (atlas segments are about 1 km long, so 1e-3 is about 1 m).
const covered=(ranges,from,to)=>{let at=from;for(const [a,b] of ranges){if(a>at+1e-3)break;at=Math.max(at,b);}return at>=to-1e-3;};
const length=year=>{let n=0;for(const l of new box.Roads(()=>{}).reconciledFeature(atlas,v(year),(x,y)=>[x,y]).paths)for(let i=1;i<l.length;i++)n+=Math.hypot((l[i][0]-l[i-1][0])*55.6,(l[i][1]-l[i-1][1])*111.2);return n;};

test('the 1894 atlas line is not drawn beside the 1929 Hammarlandsvägen (Kattby–Smedens)',()=>{
 for(const year of [1929,1944,1950,1958,1965])assert.ok(covered(retired(year),10,13.6),'retired '+year);
 assert.ok(!covered(retired(1928),10,13.6),'before 1929 only older roads (Kattbyvägen, Emkarbyvägen) retire parts of it');
 assert.ok(length(1950)<length(1928)-3,'about 3.5 km fewer drawn in 1929–1958');
 assert.equal(length(1928),length(1900));
});

test('the old Näfsby and Smedens lines and the Näfsby roads retire the atlas line through their 1929 geometry',()=>{
 const P='road:rural:hammarland-';
 for(const id of [P+'way-545279820',P+'way-1419026567',P+'way-1419026568',P+'vastmyra-old-school-approach-east',P+'vastmyra-old-school-approach','road:hammarland:gamla-hammarlandsvagen:smedens','road:hammarland:gamla-hammarlandsvagen:nafsby']){
  const g=model.resolveObject(id,1950).geometry.id;
  assert.ok(atlas.replacementIntervals.some(r=>r.objectId===id&&r.geometryId===g),id);
  assert.equal(objects.get(id).evidence.filter(e=>e.id===id+':regional-context:atlas-1894-1').length,1);
 }
});
