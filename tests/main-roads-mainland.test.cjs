const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz')),review=read('data/main-roads-mainland.json');
const len=p=>p.slice(1).reduce((s,q,i)=>s+Math.hypot((q[0]-p[i][0])*55600,(q[1]-p[i][1])*111200),0);
const drawn=(id,y)=>model.resolveObject(id,y).geometry.paths.reduce((s,p)=>s+len(p),0);
const sum=rs=>rs.reduce((s,[a,b])=>s+b-a,0);

test('the main roads of Lemland, Lumparland, Jomala, Eckerö and Sund are on the 1968 base maps, on their own later line',()=>{
 assert.equal(review.early.length,15);
 for(const e of review.early){
  const id=e.objectId;assert.equal(e.firstYear,1968);
  assert.equal(model.resolveObject(id,1967).geometry,null,id);assert.equal(model.resolveObject(id,1968).state,'open',id);
  const want=sum(e.ranges),got=drawn(id,1968);
  assert.ok(Math.abs(got-want)<want*0.01+2,`${id}: ${Math.round(got)} m drawn in 1968, ${Math.round(want)} m reviewed`);
  assert.ok(got<=len(model.resolveObject(id,e.until).geometry.paths[0])+2);
  assert.ok(model.objects.get(id).evidence.some(x=>x.describes.from===1968&&x.outcome==='present'&&/^nls:10(12|21)/.test(x.sourceId)),id);
  if(e.laterStage){const w=sum(e.laterStage.ranges);assert.ok(Math.abs(drawn(id,1978)-w)<w*0.01+2,id);assert.ok(drawn(id,1978)>got+150,id);}
 }
 // Järsövägen and the two Lemlandsvägen objects (dated by earlier reviews) are left out
 assert.equal(model.resolveObject('road:qgis:mariehamn:jarsovagen-100km3',1990).geometry,null);
 for(const id of ['road:qgis:mariehamn:lemlandsvagen-1-100km3','road:qgis:mariehamn:lemlandsvagen-2-100km3'])assert.equal(model.objects.get(id).states[0].from,1985,id);
});

test('the postal route from Haraldsby to Delvik follows Mångstektavägen as the 1978 edition draws it',()=>{
 const w={};vm.runInNewContext(fs.readFileSync('dist/postal-route-roads.js','utf8'),{window:w});
 const leg=w.POSTAL_ROUTE_ROADS.find(l=>l.from==='haraldsby'&&l.to==='delvik');
 assert.equal(leg.year,1978);assert.ok(leg.objects.some(o=>o.name==='Mångstektavägen'));
});
