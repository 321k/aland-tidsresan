const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),review=read('data/main-roads-archipelago.json');
const len=p=>p.slice(1).reduce((s,q,i)=>s+Math.hypot((q[0]-p[i][0])*55600,(q[1]-p[i][1])*111200),0);
const drawn=(id,y)=>model.resolveObject(id,y).geometry.paths.reduce((s,p)=>s+len(p),0);
const sum=rs=>rs.reduce((s,[a,b])=>s+b-a,0);

test('the archipelago main roads are on the first base maps (1968–1971), on their own later line',()=>{
 assert.equal(review.early.length,16);
 for(const e of review.early){
  const id=e.objectId,y=e.firstYear;
  assert.equal(model.resolveObject(id,y-1).geometry,null,id);assert.equal(model.resolveObject(id,y).state,'open',id);
  const want=sum(e.ranges),got=drawn(id,y);
  assert.ok(Math.abs(got-want)<want*0.01+2,`${id}: ${Math.round(got)} m drawn in ${y}, ${Math.round(want)} m reviewed`);
  assert.ok(got<=len(model.resolveObject(id,e.until).geometry.paths[0])+2);
  assert.ok(model.objects.get(id).evidence.some(x=>x.describes.from===y&&x.outcome==='present'&&/^nls:10(14|23|41)/.test(x.sourceId)),id);
  if(e.laterStage){const s=e.laterStage.firstYear,w=sum(e.laterStage.ranges);
   assert.ok(Math.abs(drawn(id,s)-w)<w*0.01+2,`${id} ${s}`);assert.ok(drawn(id,s)>got+150,id);}
 }
 // Fiskövägen: its matched stretch lies on the 1971 sheet only, so it is not dated by the 1968 Brändö sheet
 assert.equal(model.resolveObject('road:qgis:fisko:fiskovagen-1-200km2',1970).geometry,null);
 // Brändövägen del 1: over Andersör and Nötö only from the 1984 edition
 assert.ok(drawn('road:qgis:ava:brandovagen-1-200km2',1970)<4000);
 assert.ok(drawn('road:qgis:ava:brandovagen-1-200km2',1985)>8000);
});

test('the postal route lands on Brändö on the road the 1984 edition draws',()=>{
 const w={};vm.runInNewContext(fs.readFileSync('dist/postal-route-roads.js','utf8'),{window:w});
 const leg=w.POSTAL_ROUTE_ROADS.find(l=>l.from==='kumlinge'&&l.to==='brando');
 assert.equal(leg.parts.at(-1).year,1984);
});
