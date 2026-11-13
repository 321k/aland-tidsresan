const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-symbols-1968.json'),catalog=read('dist/assets/temporal-objects.json.gz'),data=read('dist/assets/city-buildings.json'),modern=read('dist/assets/modern.json.gz');
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null},htmlEscape:String,safeURL:String};vm.createContext(box);
for(const name of ['temporal-objects','timeline-model','city-buildings','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.City=CityBuildings;this.Model=TemporalObjects;this.Grid=CityGrid;',box);
const model=new box.Model(catalog);

test('125 printed-map symbol houses in the centre are shown from the 1968 edition; hatched blocks date nothing',()=>{
 assert.equal(review.decisions.length,125);assert.equal(review.hatched.length,86);assert.equal(Object.keys(review.visualRejections).length,33);
 assert.ok(catalog.sources.some(s=>s.id===review.source.id));assert.ok(catalog.sources.some(s=>s.id===review.sheet1968));
 assert.deepEqual(catalog.objects.filter(o=>o.symbolMap1968).map(o=>o.id).sort(),review.decisions.map(d=>d.objectId).sort());
 for(const id of [...review.hatched,...Object.keys(review.visualRejections)]){const o=model.objects.get(id);assert.ok(o.printedMapSymbol&&!o.symbolMap1968,id);assert.ok(o.states[0].from>1968,id)}
 for(const r of Object.values(review.visualRejections))assert.match(r.reason,/^(ambiguous-overlap|hatched-block|outline-empty|lettering):/);
});

test('a dated symbol house starts in 1968 with the map as evidence, keeps its outline and its later history',()=>{
 for(const d of review.decisions){const o=model.objects.get(d.objectId);
  assert.ok(o.printedMapSymbol);assert.equal(model.resolveObject(d.objectId,1967).geometry,null,d.objectId);
  const early=model.resolveObject(d.objectId,1968),later=model.resolveObject(d.objectId,d.originalFrom);
  assert.ok(['occupied','standing'].includes(early.state));assert.equal(early.geometry.id,later.geometry.id);
  assert.deepEqual([o.states[0].from,o.states[0].to,o.states[1].from],[1968,d.originalFrom,d.originalFrom]);
  assert.equal(o.geometryPeriods[0].from,1968);assert.equal(o.geometryPeriods[0].previousFrom,d.originalFrom);
  assert.equal(o.reconstruction.from,1968);assert.equal(o.reconstruction.previous.from,d.originalFrom);assert.ok(!o.sourceYears.includes(1968));
  const e=o.evidence.find(e=>e.id===d.objectId+':map-101208-1968');assert.equal(e.constructionYear,null);assert.equal(e.sourceId,review.sheet1968);
  assert.deepEqual(e.sourcePixels.pixel,d.pixel);assert.ok(e.deviationMeters<=review.rules.maxRawSymbolDistanceMeters);assert.deepEqual(o.states[0].evidenceIds,[e.id]);
  assert.equal(o.symbolMap1968.constructionYear,null)}
});

test('the city layer draws the symbol houses from 1968 and never before',()=>{
 const layer=new box.City(()=>{});Object.assign(layer,data,{objects:model});
 const e={objects:model,ready:true,flags:{historic:true,modern:true,uncertain:true,traces:false},category:'all',query:'',historic:[],modern:modern.features,matches:()=>true,prepared:true,project:(x,y)=>[x*10000,y*10000]};
 const grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model,ready:true});
 for(const year of [1967,1968,1975]){const ids=new Set(layer.records(year,e,grid).map(r=>r.id));layer.cache=null;
  for(const d of review.decisions)assert.equal(ids.has(d.objectId),year>=1968,`${d.objectId} ${year}`)}
});
