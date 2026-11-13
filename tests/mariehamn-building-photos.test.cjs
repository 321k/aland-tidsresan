const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/mariehamn-building-photos.json'),catalog=read('dist/assets/temporal-objects.json.gz'),data=read('dist/assets/city-buildings.json'),modern=read('dist/assets/modern.json.gz');
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null},htmlEscape:String,safeURL:String};vm.createContext(box);
for(const name of ['temporal-objects','timeline-model','city-buildings','city-grid'])vm.runInContext(fs.readFileSync('dist/'+name+'.js','utf8'),box);
vm.runInContext('this.City=CityBuildings;this.Model=TemporalObjects;this.Grid=CityGrid;',box);
const model=new box.Model(catalog),photos=new Map(read('data/mariehamn-aerial-review.json').sources.map(s=>[s.year,s]));

test('Östra Ytternäs buildings with no map symbol are dated from the 1991–2015 photos',()=>{
 assert.equal(review.decisions.length,160);assert.deepEqual(review.totals.byFirstYear,{1991:45,1999:17,2007:93,2015:5});
 assert.deepEqual(review.totals.deferred,{'below-size':1,'map-ink':9,'no-photo-evidence':74});
 assert.ok(catalog.sources.some(s=>s.id===review.source.id));
 const maps=read('data/mariehamn-building-maps.json');
 for(const d of review.decisions){assert.ok(maps.deferred.absent.includes(d.objectId),d.objectId);assert.ok(d.areaSquareMeters>=review.minAreaSquareMeters)}
 assert.deepEqual(catalog.objects.filter(o=>o.buildingPhotoReview).map(o=>o.id).sort(),review.decisions.map(d=>d.objectId).sort());
});

test('a photo-dated building starts at its first photo with that photo as evidence, keeps its outline and later history',()=>{
 for(const d of review.decisions){const o=model.objects.get(d.objectId);
  assert.equal(model.resolveObject(d.objectId,d.firstYear-1).geometry,null,d.objectId);
  const first=model.resolveObject(d.objectId,d.firstYear),orig=model.resolveObject(d.objectId,d.originalFrom);
  assert.equal(first.state,'standing');assert.equal(first.geometry.id,d.referenceGeometryId);assert.equal(orig.geometry.id,d.referenceGeometryId);
  assert.deepEqual([o.states[0].from,o.states[0].to,o.states[1].from],[d.firstYear,d.originalFrom,d.originalFrom]);
  assert.equal(o.reconstruction.from,d.firstYear);assert.equal(o.reconstruction.photoDated,true);assert.equal(o.buildingPhotoReview.constructionYear,null);
  for(const x of d.observations){const e=o.evidence.find(e=>e.id===`${d.objectId}:photo-${x.year}`);
   if(x.year<d.firstYear){assert.ok(['absent','not-covered'].includes(x.outcome));assert.equal(e,undefined);continue}
   assert.equal(x.outcome,'present');assert.equal(e.sourceId,photos.get(x.year).id);assert.equal(e.observedAt,photos.get(x.year).capturedAt);
   assert.equal(e.constructionYear,null);assert.ok(o.states[0].evidenceIds.includes(e.id))}
  assert.match(d.basis,/inte byggår/)}
});

test('the city layer draws photo-dated buildings from their first photo year and never before',()=>{
 const layer=new box.City(()=>{});Object.assign(layer,data,{objects:model});
 const e={objects:model,ready:true,flags:{historic:true,modern:true,uncertain:true,traces:false},category:'all',query:'',historic:[],modern:modern.features,matches:()=>true,prepared:true,project:(x,y)=>[x*10000,y*10000]};
 const grid=new box.Grid(()=>{});Object.assign(grid,read('dist/assets/mariehamn-city-grid.json'),{objects:model,ready:true});
 for(const year of [1990,1991,1998,1999,2006,2007,2014,2015]){const ids=new Set(layer.records(year,e,grid).map(r=>r.id));layer.cache=null;
  for(const d of review.decisions)assert.equal(ids.has(d.objectId),year>=d.firstYear,`${d.objectId} ${year}`)}
});
