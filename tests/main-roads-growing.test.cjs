const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),review=read('data/main-roads-growing.json');
const len=p=>p.slice(1).reduce((s,q,i)=>s+Math.hypot((q[0]-p[i][0])*55600,(q[1]-p[i][1])*111200),0);
const drawn=(id,y)=>model.resolveObject(id,y).geometry.paths.reduce((s,p)=>s+len(p),0);
const sum=rs=>rs.reduce((s,[a,b])=>s+b-a,0);

test('growing roads of the Hammarland review are drawn on the neighbouring sheets from their first edition',()=>{
 assert.deepEqual(review.objects.map(o=>o.objectId).sort(),['road:rural:hammarland-bovikvagen-east','road:rural:hammarland-skarpnatovagen-south','road:rural:hammarland-way-350331479','road:rural:hammarland-way-557084450','road:rural:hammarland-way-71082200']);
 let added=0;
 for(const t of review.objects){
  const o=model.objects.get(t.objectId);
  assert.equal(o.mainRoadReview.review,'review:main-roads-growing');assert.equal(model.resolveObject(t.objectId,1967).geometry,null);
  for(const p of t.periods){
   const r=model.resolveObject(t.objectId,p.from);assert.equal(r.state,'open');
   if(p.ranges.length){assert.ok(r.geometry.id.startsWith('geometry:main-roads-growing:'),t.objectId);
    const base=model.geometries.get(p.baseGeometryId).paths.reduce((s,q)=>s+len(q),0);
    assert.ok(Math.abs(drawn(t.objectId,p.from)-base-sum(p.ranges))<sum(p.ranges)*0.01+3,`${t.objectId} ${p.from}`);}
  }
  added+=sum(t.periods[0].ranges);
  assert.ok(o.evidence.some(e=>e.reviewId==='review:main-roads-growing'&&e.describes.from===t.stages[0].year&&/^nls:10(12|21)/.test(e.sourceId)));
  // the full geometry from its OSM year is unchanged
  const last=o.geometryPeriods.at(-1);assert.ok(!last.geometryId.startsWith('geometry:main-roads-growing:'));
 }
 assert.ok(added>10600&&added<10800,String(added));
 // Skarpnåtövägen södra: the 1984 edition draws more of it
 const s='road:rural:hammarland-skarpnatovagen-south';assert.ok(drawn(s,1984)>drawn(s,1983)+1500);
});
