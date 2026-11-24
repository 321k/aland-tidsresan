const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),review=read('data/main-roads-new.json');
const len=p=>p.slice(1).reduce((s,q,i)=>s+Math.hypot((q[0]-p[i][0])*55600,(q[1]-p[i][1])*111200),0);

test('main roads no object had are drawn from the first base-map edition that draws them in red',()=>{
 const want={'kumlinge:kungshamnsvagen':1971,'saltvik:odkarbyvagen-haga':1968,'lumparland:bistorpvagen':1968,'sund:sonrodavagen':1968,'jomala:klockargrand':1968,
  'brando:langang-farjfastet':1969,'svartsmara:bovikvagen':1968,'kokar:pavals':1971,'sund:bjorbyvagen-trygghem':1968,'sund:eliasvagen':1968};
 assert.deepEqual(review.newRoads.map(r=>r.id.replace('road:main-roads-new:','')).sort(),Object.keys(want).sort());
 let total=0;
 for(const r of review.newRoads){
  const id=r.id,y=want[id.replace('road:main-roads-new:','')],o=model.objects.get(id);
  assert.equal(model.resolveObject(id,y-1).geometry,null,id);assert.equal(model.resolveObject(id,y).state,'open',id);
  const drawn=model.resolveObject(id,y).geometry.paths.reduce((s,p)=>s+len(p),0);total+=drawn;
  assert.ok(Math.abs(drawn-r.lengthMeters)<r.lengthMeters*0.01+2,id);
  assert.ok(o.evidence.some(e=>e.describes.from===y&&e.outcome==='present'&&/^nls:10\d\d\d\d:/.test(e.sourceId)),id);
  assert.ok(o.sourceLinks.some(l=>l.datasetId==='osm-2026'),id);assert.equal(o.mainRoadReview.newFromOsm,true,id);
 }
 assert.ok(total>9900&&total<10100,`${Math.round(total)} m`);
});

test('each OSM way of the new roads is owned by one object only',()=>{
 const owners={};
 for(const o of model.objects.values())for(const l of o.sourceLinks||[])if(l.datasetId==='osm-2026'){(owners[l.featureId]??=[]).push(o.id);}
 for(const r of review.newRoads)for(const l of r.sourceLinks.filter(l=>l.datasetId==='osm-2026'))assert.deepEqual(owners[l.featureId],[r.id],l.featureId);
});
