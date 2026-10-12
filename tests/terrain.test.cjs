const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../dist');
function renderer(){
 const context=vm.createContext({Worker:class{postMessage(){}},Map,Promise,Error,Date,Math,Float32Array,Path2D:class{},setTimeout,clearTimeout});
 vm.runInContext(fs.readFileSync(path.join(root,'terrain.js'),'utf8')+';this.Renderer=TerrainRenderer',context);
 const r=new context.Renderer(()=>{}, {textContent:''});
 r.meta={world:262144,x0:145052,y0:75137,width:1602,height:1463};
 return r;
}
const view={width:1280,height:720,fit:.7,zoom:1,panX:0,panY:0,level:3.4,ice:false};
test('zoom loads finer source data while preserving the geographic center',()=>{
 const r=renderer(),overview=r.specification(view),detail=r.specification({...view,zoom:32});
 assert.equal(overview.z,10);assert.equal(detail.z,14);
 const worldX=r.meta.x0+r.meta.width/2,worldY=r.meta.y0+r.meta.height/2;
 assert.ok(detail.x0*256/detail.ratio<worldX&&detail.x1*256/detail.ratio>worldX);
 assert.ok(detail.y0*256/detail.ratio<worldY&&detail.y1*256/detail.ratio>worldY);
 assert.ok((detail.x1-detail.x0+1)*(detail.y1-detail.y0+1)<100);
});
test('a slow contour response cannot restore the previous historical shoreline',async()=>{
 const r=renderer();let finish;
 r.geometry=()=>new Promise(resolve=>finish=resolve);r.generation=1;
 const task=r.refresh(r.specification(view),1);
 r.generation=2;finish([]);await task;
 assert.equal(r.layers.base,undefined);assert.equal(r.busy,false);
});
test('the contour worker preserves island holes and removes submerged land',()=>{
 const messages=[],context=vm.createContext({postMessage:data=>messages.push(data)});
 context.importScripts=(...names)=>names.forEach(name=>vm.runInContext(fs.readFileSync(path.join(root,name),'utf8'),context));
 vm.runInContext(fs.readFileSync(path.join(root,'terrain-worker.js'),'utf8'),context);
 const values=new Float32Array(49).fill(0);
 for(let y=1;y<6;y++)for(let x=1;x<6;x++)values[y*7+x]=10;
 values[3*7+3]=0;
 context.onmessage({data:{type:'init',grid:{width:7,height:7,values}}});
 context.onmessage({data:{id:1,level:1}});
 assert.equal(messages[0].contours[0].coordinates.length,1);
 assert.equal(messages[0].contours[0].coordinates[0].length,2);
 context.onmessage({data:{id:2,level:11}});
 assert.equal(messages[1].contours[0].coordinates.length,0);
});
