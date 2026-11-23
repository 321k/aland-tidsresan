const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
class Path{moveTo(){}lineTo(){}closePath(){}rect(){}}
const box={Path2D:Path,document:{getElementById:()=>null}};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(read('dist/assets/temporal-objects.json.gz'));
const len=p=>p.slice(1).reduce((s,q,i)=>s+Math.hypot((q[0]-p[i][0])*55600,(q[1]-p[i][1])*111200),0);
const P='road:qgis:saltvik:',VH=P+'sundsvagen-varsundet-haraldsby';

test('from 1929 the road runs from Godby to the Färjsundet landing and from the far landing through Haraldsby to Sundsvägen',()=>{
 for(const id of ['road:finstrom:sundsvagen:godby-farjsundet',VH,P+'haraldsbyvagen-sodra-anslutningen',P+'haraldsbyvagen',P+'gamla-sundsvagen-vaster',P+'gamla-sundsvagen-oster']){
  assert.equal(model.resolveObject(id,1928).geometry,null,id);assert.equal(model.resolveObject(id,1929).state,'open',id);
  assert.ok(model.objects.get(id).evidence.some(e=>e.sourceId==='nls:map-38157483'&&e.outcome==='present'),id);
 }
 // only the stretch from the landing to Vårsundet is the old road; the causeway over Östervik is later
 const early=len(model.resolveObject(VH,1929).geometry.paths[0]),later=len(model.resolveObject(VH,1968).geometry.paths[0]);
 assert.ok(early>540&&early<580&&later>1600);
 assert.ok(len(model.resolveObject(P+'haraldsbyvagen',1929).geometry.paths[0])<len(model.resolveObject(P+'haraldsbyvagen',1968).geometry.paths[0])-500);
});

test('the postal route crosses Färjsundet by ferry before the bridge and runs through Haraldsby village',()=>{
 const w={};vm.createContext(w);w.window=w;vm.runInContext(fs.readFileSync('dist/postal-route-roads.js','utf8'),w);
 const legs=JSON.parse(JSON.stringify(w.POSTAL_ROUTE_ROADS)),eh=legs.find(l=>l.from==='emkarby'),hs=legs.find(l=>l.from==='haraldsby');
 assert.equal(eh.year,1929);assert.deepEqual(eh.ferries,['farjsundet']);
 assert.ok(['road:qgis:saltvik:haraldsbyvagen','road:qgis:saltvik:gamla-sundsvagen-vaster','road:qgis:saltvik:gamla-sundsvagen-oster'].every(id=>hs.objects.some(o=>o.id===id)));
 assert.ok(!hs.objects.some(o=>o.id==='road:qgis:saltvik:sundsvagen-haraldsby-vagskal'),'not over the causeway');
});
