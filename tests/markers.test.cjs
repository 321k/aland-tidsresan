const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const box={URL};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/timeline-model.js','utf8')+fs.readFileSync('dist/explorer.js','utf8')+';this.Layers=ExplorerLayers',box);
const ctx=new Proxy({},{get:()=>()=>{},set:()=>true});
function layer(points){const l=new box.Layers(()=>{},()=>{});l.heritage=points.map(([x,y],i)=>({id:String(i),name:'Grav '+i,category:'grave',point:[x,y],periods:[{from:100,to:1000}]}));return l;}
const view={width:1000,height:800,meta:{width:1000,height:800},zoom:16,scale:1,year:800,panX:0,panY:0};
function frame(l,v){l.hits=[];l.viewList=[];l.drawHeritage(ctx,v);return JSON.parse(JSON.stringify(l.hits.map(h=>({ids:h.entries.map(f=>f.id),x:h.x,y:h.y}))));}
test('panning translates markers without turning triangles into clusters and back',()=>{
 const l=layer([[219.8,200],[220.2,200],[232,200],[279,240]]),before=frame(l,view);
 for(const dx of [.1,1,5,19,20,33,-33,200]){const after=frame(l,{...view,panX:dx,panY:7});assert.deepEqual(after.map(h=>h.ids),before.map(h=>h.ids));for(let i=0;i<after.length;i++){assert.ok(Math.abs(after[i].x-before[i].x-dx)<1e-8);assert.ok(Math.abs(after[i].y-before[i].y-7)<1e-8);}}
});
test('a visible cluster keeps its members when one point crosses the viewport edge',()=>{
 const l=layer([[0,200],[30,200],[32,200],[33,200]]),v={...view,zoom:4};const before=frame(l,v),after=frame(l,{...v,panX:-31});assert.equal(before.length,1);assert.deepEqual(after.map(h=>h.ids),before.map(h=>h.ids));assert.equal(after[0].x,before[0].x-31);
});
test('zooming and filtering still change which places are grouped',()=>{
 const l=layer([[501,400],[508,400]]);assert.equal(frame(l,view)[0].ids.length,2);assert.equal(frame(l,{...view,scale:4}).length,2);l.query='Grav 0'.toLowerCase();assert.deepEqual(frame(l,view).map(h=>h.ids),[['0']]);assert.equal(frame(l,{...view,year:0}).length,0);
});
// Exercise the actual registered pointer handlers without requiring a live browser.
function gestures(){const events={},win={},s={mapTransition:{cancel(){}},pointers:new Map(),gesture:null,dragged:false,panX:0,panY:0,zoom:1,W:400,H:600,draws:0,draw(){s.draws++},canvas:{addEventListener:(name,fn)=>events[name]=fn,setPointerCapture(){},getBoundingClientRect(){return {left:0,top:0}}},window:{addEventListener:(name,fn)=>win[name]=fn}};vm.createContext(s);const source=fs.readFileSync('dist/app.js','utf8');vm.runInContext(source.slice(source.indexOf('function zoomAt('),source.indexOf('function selectBuilding(')),s);vm.runInContext(source.slice(source.indexOf('function cancelMapGesture()'),source.indexOf("canvas.addEventListener('keydown'")),s);return{s,events,win};}
const mouse=(extra={})=>({pointerType:'mouse',pointerId:1,button:0,buttons:1,clientX:100,clientY:100,...extra});
test('hover and small click movements do not move or redraw the map',()=>{const{s,events}=gestures();events.pointermove(mouse({buttons:0,clientX:120}));assert.equal(s.draws,0);events.pointerdown(mouse());events.pointermove(mouse({clientX:102}));assert.equal(s.panX,0);assert.equal(s.draws,0);events.pointermove(mouse({clientX:110}));assert.equal(s.panX,10);assert.equal(s.draws,1);});
test('a missed mouse release cannot leave the map dragging on hover',()=>{const{s,events}=gestures();events.pointerdown(mouse());events.pointermove(mouse({clientX:115}));events.pointermove(mouse({buttons:0,clientX:160}));events.pointermove(mouse({buttons:0,clientX:180}));assert.equal(s.panX,15);assert.equal(s.draws,1);assert.equal(s.pointers.size,0);});
test('capture loss, cancellation and window blur end an interrupted drag',()=>{for(const end of ['lostpointercapture','pointercancel','blur']){const{s,events,win}=gestures();events.pointerdown(mouse());(end==='blur'?win.blur:events[end])(mouse());events.pointermove(mouse({clientX:150}));assert.equal(s.draws,0);assert.equal(s.pointers.size,0);}});

test('expired markers, clusters, boundaries and list entries disappear together',()=>{
 const l=layer([[501,400],[508,400]]);l.prepared=true;l.flags.modern=false;l.drawCoast=l.drawPostal=l.updateList=()=>{};
 let boundaries=0;const canvas=new Proxy({fill:()=>boundaries++},{get:(o,k)=>o[k]||(()=>{}),set:()=>true});
 l.heritage.forEach(f=>f.boundaryPath={});
 l.render(canvas,{...view,year:1000});assert.equal(l.hits.length,1);assert.equal(l.viewList.length,2);assert.ok(boundaries>0);
 boundaries=0;l.render(canvas,{...view,year:2026});assert.equal(l.hits.length,0);assert.equal(l.viewList.length,0);assert.equal(boundaries,0);assert.equal(l.hit(501,400,canvas),null);
 l.flags.traces=true;l.render(canvas,{...view,year:2026});assert.equal(l.hits.length,1);assert.equal(l.viewList.length,2);
});

const touch=(id,x,y)=>({pointerType:'touch',pointerId:id,button:0,buttons:1,clientX:x,clientY:y});
test('two-finger pan and pinch retain the map point under the moving midpoint',()=>{
 const{s,events}=gestures();events.pointerdown(touch(1,100,200));events.pointerdown(touch(2,200,200));
 const worldX=(150-s.W/2-s.panX)/s.zoom,worldY=(200-s.H/2-s.panY)/s.zoom;
 events.pointermove(touch(1,80,240));events.pointermove(touch(2,240,240));
 assert.ok(Math.abs(s.zoom-1.6)<1e-10);
 assert.ok(Math.abs(worldX*s.zoom+s.W/2+s.panX-160)<1e-10);
 assert.ok(Math.abs(worldY*s.zoom+s.H/2+s.panY-240)<1e-10);
 const before=s.panX;events.pointerup(touch(2,240,240));events.pointermove(touch(1,100,240));
 assert.equal(s.panX,before+20);assert.equal(s.dragged,true);
});
test('cancelling a pinch leaves no phantom touch or later hover redraw',()=>{
 const{s,events}=gestures();events.pointerdown(touch(1,100,200));events.pointerdown(touch(2,200,200));events.pointermove(touch(2,250,200));
 events.pointercancel(touch(2,250,200));const draws=s.draws;events.pointermove(touch(1,120,210));
 assert.equal(s.draws,draws);assert.equal(s.pointers.size,0);assert.equal(s.gesture,null);
});
