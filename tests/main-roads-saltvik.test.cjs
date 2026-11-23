const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),review=read('data/main-roads-saltvik.json');
const len=p=>p.slice(1).reduce((s,q,i)=>s+Math.hypot((q[0]-p[i][0])*55600,(q[1]-p[i][1])*111200),0);

test('the main roads of northern Saltvik and Geta are on the base maps from 1968, on their own later line',()=>{
 for(const e of review.early){
  const id=e.objectId,later=model.resolveObject(id,e.until).geometry,early=model.resolveObject(id,1968);
  assert.equal(model.resolveObject(id,1967).geometry,null,id);assert.equal(early.state,'open',id);
  const want=e.ranges.reduce((s,[a,b])=>s+b-a,0),got=early.geometry.paths.reduce((s,p)=>s+len(p),0);
  assert.ok(Math.abs(got-want)<want*0.01+2,`${id}: ${Math.round(got)} m drawn in 1968, ${Math.round(want)} m reviewed`);
  assert.ok(got<=len(later.paths[0])+2);
  assert.ok(model.objects.get(id).evidence.some(x=>x.describes.from===1968&&x.outcome==='present'&&/^nls:1021/.test(x.sourceId)));
 }
 // the old bends at Bolstaholm and Östergård are not this object's 1968 line
 const sodra=model.resolveObject('road:qgis:geta:sodravagen-2-200km2',1970).geometry;assert.equal(sodra.paths.length,3);
 // Hamnsundsvägen del 3: 290 m from 1968, the whole road from 1978
 assert.ok(len(model.resolveObject('road:qgis:tjudo:hamnsundsvagen-3-100km1',1970).geometry.paths[0])<300);
 assert.ok(len(model.resolveObject('road:qgis:tjudo:hamnsundsvagen-3-100km1',1980).geometry.paths[0])>800);
});
