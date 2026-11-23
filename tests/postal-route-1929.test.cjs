const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz'));
const d=(p,q)=>Math.hypot((p[0]-q[0])*55600,(p[1]-q[1])*111200);
const EARLY={'road:jomala:postgardsvagen':1928,'road:jomala:godbyvagen:golby-junction':1928,'road:jomala:godbyvagen:bjorkang':1928,'road:finstrom:godby-korsningen':1929,'road:qgis:saltvik:von-knorringsvagen-1-batch4':1929,'road:rural:hammarland-way-459195076':1929};

test('the road from Emkarby through Gölby to Godby is on the parish maps 1928 and 1929, on its own later line',()=>{
 for(const [id,year] of Object.entries(EARLY)){
  assert.equal(model.resolveObject(id,year-1).geometry,null,id+' before '+year);
  const early=model.resolveObject(id,year).geometry.paths,later=model.resolveObject(id,1968).geometry.paths;
  assert.ok(early.length===later.length&&early.every((p,i)=>p.length===later[i].length&&p.every((q,j)=>d(q,later[i][j])<.1)),id+' keeps its own geometry');
  assert.ok(model.objects.get(id).evidence.some(e=>e.describes.from===year&&e.outcome==='present'));
 }
 // Emkarbyvägen reaches Bergens, where Postgårdsvägen begins, on the 1928 map
 const em=model.resolveObject('road:emkarbyvagen',1929).geometry.paths,pg=model.resolveObject('road:jomala:postgardsvagen',1929).geometry.paths[0];
 assert.equal(em.length,2);assert.ok(d(em[1].at(-1),pg[0])<1);
 for(const y of [1893,1900,1927])assert.equal(model.resolveObject('road:emkarbyvagen',y).geometry.paths.length,1,'before 1928 Emkarbyvägen still ends at Tingsbacka ('+y+')');
});

test('the postal route from Frebbenby to Emkarby runs on the 1929 roads',()=>{
 const w={};vm.createContext(w);w.window=w;vm.runInContext(fs.readFileSync('dist/postal-route-roads.js','utf8'),w);
 const leg=JSON.parse(JSON.stringify(w.POSTAL_ROUTE_ROADS)).find(l=>l.from==='frebbenby');
 assert.equal(leg.year,1929);assert.ok(leg.joinsMeters.every(m=>m<=40));
});
