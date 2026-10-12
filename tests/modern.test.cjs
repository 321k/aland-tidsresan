const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const box={URL};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/explorer.js','utf8')+'\nthis.ExplorerLayers=ExplorerLayers;',box);
test('modern spatial index matches a full geometry scan, including grid boundaries',()=>{
 const layer=new box.ExplorerLayers(()=>{},()=>{});
 layer.modern=[{id:'long-road',bounds:[-20,-5,90,40]},{id:'house',bounds:[32,32,33,33]},{id:'remote',bounds:[800,900,810,910]}];layer.indexModern();
 for(const b of [[31,31,34,34],[-100,-100,0,0],[90,40,91,41],[700,800,799,899],[-999,-999,999,999],[10000,10000,10100,10100]]){
  const expected=layer.modern.filter(f=>f.bounds[2]>=b[0]&&f.bounds[0]<=b[2]&&f.bounds[3]>=b[1]&&f.bounds[1]<=b[3]).map(f=>f.id);
  assert.deepEqual(Array.from(layer.modernInView(...b),f=>f.id),expected);
 }
});
test('modern detail hierarchy preserves main roads and reveals houses and paths when zooming',()=>{
 const layer=new box.ExplorerLayers(()=>{},()=>{}),road=cls=>({kind:'road',class:cls}),house={kind:'building'};
 assert.equal(layer.modernVisible(road('primary'),200),true);
 assert.equal(layer.modernVisible(road('service'),30),false);
 assert.equal(layer.modernVisible(road('service'),10),true);
 assert.equal(layer.modernVisible(road('footway'),10),false);
 assert.equal(layer.modernVisible(road('footway'),2),true);
 assert.equal(layer.modernVisible(house,20),false);
 assert.equal(layer.modernVisible(house,5),true);
});

test('Åland extract contains buildings and roads near mainland and archipelago settlements',()=>{
 const data=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync('dist/assets/modern.json.gz')));
 for(const name of ['Storby','Godby','Jomala','Hammarland','Geta','Saltvik','Lemland','Lumparland','Vårdö','Degerby','Sottunga','Kumlinge','Brändö','Karlby']){
  const place=data.places.find(p=>p.name===name&&(name!=='Brändö'||p.lon>21));assert.ok(place,name);
  const near=data.features.filter(f=>f.paths.some(path=>path.some(([lon,lat])=>Math.abs(lon-place.lon)<.04&&Math.abs(lat-place.lat)<.02)));
  assert.ok(near.filter(f=>f.kind==='building').length>10, name+' needs mapped buildings');
  assert.ok(near.filter(f=>f.kind==='road').length>5,name+' needs a road network');
 }
});
test('coast rendering skips distant islands when zoomed in',()=>{
 const layer=new box.ExplorerLayers(()=>{},()=>{}),filled=[];
 layer.coastBounds=[0,0,1000,1000];layer.coastPaths=[{path:'near',bounds:[490,490,510,510]},{path:'far',bounds:[0,0,10,10]}];
 const ctx=new Proxy({fill:path=>filled.push(path)},{get:(o,k)=>k in o?o[k]:()=>{},set:(o,k,v)=>(o[k]=v,true)});
 layer.drawCoast(ctx,{scale:1,width:100,height:100,panX:0,panY:0,meta:{width:1000,height:1000}});
 assert.deepEqual(filled,['near']);
});
test('compressed map data works with raw gzip and server-decoded responses',async()=>{
 const context={URL,Response,Blob,DecompressionStream,TextDecoder};vm.createContext(context);vm.runInContext(fs.readFileSync('dist/explorer.js','utf8'),context);
 const json=JSON.stringify({features:[{id:'way/42'}]});
 for(const body of [json,require('node:zlib').gzipSync(json)]){
  const actual=await context.readCompressedJSON(new Response(body));assert.equal(actual.features[0].id,'way/42');
 }
 await assert.rejects(context.readCompressedJSON(new Response('not found',{status:404})));
});
test('resizing the map keeps the selected geographic centre',()=>{
 let size={width:1200,height:700};const s={canvas:{getBoundingClientRect:()=>size},window:{devicePixelRatio:2},ctx:{setTransform(){}},draw(){},W:1200,H:700,fit:.6,zoom:28,panX:730,panY:-920,meta:{width:1602,height:1463}};
 const centre=()=>[s.meta.width/2-s.panX/(s.fit*s.zoom),s.meta.height/2-s.panY/(s.fit*s.zoom)],before=centre();
 vm.createContext(s);const source=fs.readFileSync('dist/app.js','utf8');vm.runInContext(source.slice(source.indexOf('function resize()'),source.indexOf('function zoomAt(')),s);
 for(size of [{width:865,height:647},{width:390,height:440},{width:1600,height:900}]){s.resize();assert.ok(centre().every((x,i)=>Math.abs(x-before[i])<1e-9));assert.equal(s.canvas.width,size.width*2);}
});
