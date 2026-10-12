const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const status={textContent:''},box={document:{querySelector:()=>status}};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/historical-overlay.js','utf8')+'\nthis.Overlay=HistoricalOverlay;',box);const Overlay=box.Overlay;
test('city-plan transform maps interpreted controls and preserves map orientation',()=>{
 const project=(lon,lat)=>[lon*1000,-lat*2000],m=Overlay.affine(Overlay.cityAnchors,project);
 for(const a of Overlay.cityAnchors){const [x,y]=a.pixel,[u,v]=project(...a.geo);assert.ok(Math.abs(m[0]*x+m[2]*y+m[4]-u)<1e-8);assert.ok(Math.abs(m[1]*x+m[3]*y+m[5]-v)<1e-8)}
 assert.ok(m[0]*m[3]-m[1]*m[2]>0,'The map is not mirrored');
});
test('1860 comparison stays explicitly a plan when viewing today and has independent loading state',()=>{
 const o=new Overlay(()=>{}),calls=[];o.enabled=true;o.mode='1860';o.ready=false;o.cityReady=true;o.cityImage={};
 const ctx=new Proxy({}, {get:(_,key)=>(...args)=>calls.push([key,...args]),set:()=>true});
 o.draw(ctx,{year:2026,width:800,height:600,panX:0,panY:0,scale:1,meta:{world:100000,width:800,height:600,x0:0,y0:0}});
 assert.match(status.textContent,/planerade hus/);assert.match(status.textContent,/2026/);assert.ok(calls.some(c=>c[0]==='drawImage'));
 o.enabled=false;calls.length=0;o.draw(ctx,{});assert.equal(calls.length,0);
});
test('museum map preserves decade dating and source when compared with today',()=>{
 const o=new Overlay(()=>{}),calls=[];o.enabled=true;o.mode='1920';o.museumReady=true;o.museumImage={};
 const ctx=new Proxy({}, {get:(_,key)=>(...args)=>calls.push([key,...args]),set:()=>true});
 o.draw(ctx,{year:2026,width:800,height:600,panX:0,panY:0,scale:1,meta:{world:100000,width:800,height:600,x0:0,y0:0}});
 assert.match(status.textContent,/1920-talet/);assert.match(status.textContent,/inte en uppmätning från exakt 1920/);assert.match(status.textContent,/vitriner/);assert.match(status.textContent,/2026/);assert.match(status.textContent,/Nybyggarne/);assert.ok(calls.some(c=>c[0]==='drawImage'&&c[1]===o.museumImage));
 const matrix=Overlay.affine(Overlay.museum.anchors,(lon,lat)=>[lon,-lat]);assert.ok(matrix.every(Number.isFinite));assert.ok(matrix[0]*matrix[3]-matrix[1]*matrix[2]>0);
});
test('failed remote museum image keeps source guidance and does not replace the 1860 image',async()=>{
 const localBox={document:{querySelector:()=>status},Image:class{async decode(){throw Error('offline')}}};vm.createContext(localBox);vm.runInContext(fs.readFileSync('dist/historical-overlay.js','utf8')+'\nthis.Overlay=HistoricalOverlay;',localBox);
 const o=new localBox.Overlay(()=>{});o.enabled=true;o.mode='1920';o.cityReady=true;o.cityImage={id:'1860'};await o.loadMuseumMap();assert.equal(o.museumFailed,true);assert.equal(o.museumLoading,false);assert.equal(o.cityImage.id,'1860');
 o.draw({},{});assert.match(status.textContent,/kunde inte laddas/);assert.match(status.textContent,/originalets sida/);
});
