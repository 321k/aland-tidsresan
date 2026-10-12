/* Zoom-aware elevation tiles plus resolution-independent, interpolated outlines. */
class TerrainRenderer {
 constructor(onChange,status){
  this.onChange=onChange;this.status=status;this.cache=new Map();this.layers={};this.jobs=new Map();this.serial=0;this.generation=0;
  this.worker=new Worker('terrain-worker.js');
  this.worker.onmessage=({data})=>{const job=this.jobs.get(data.id);if(!job)return;this.jobs.delete(data.id);data.error?job.reject(Error(data.error)):job.resolve(data.contours)};
  this.worker.onerror=()=>{for(const job of this.jobs.values())job.reject(Error('Kunde inte beräkna kartkonturer'));this.jobs.clear();this.unavailable=true;this.status.textContent='Översiktskarta visas';};
 }
 initialize(meta,values){this.meta=meta;this.worker.postMessage({type:'init',grid:{width:meta.width,height:meta.height,values}})}
 geometry(grid,level){return new Promise((resolve,reject)=>{const id=++this.serial;this.jobs.set(id,{resolve,reject});this.worker.postMessage({id,grid,level})})}
 path(contours){return contours.map(c=>{const path=new Path2D();for(const polygon of c.coordinates)for(const ring of polygon){if(ring.length<4)continue;const first=ring[0],last=ring[ring.length-2];path.moveTo((last[0]+first[0])/2,(last[1]+first[1])/2);for(let i=0;i<ring.length-1;i++){const p=ring[i],n=ring[(i+1)%(ring.length-1)];path.quadraticCurveTo(p[0],p[1],(p[0]+n[0])/2,(p[1]+n[1])/2)}path.closePath()}return path})}
 specification(view){
  const scale=view.fit*view.zoom;
  // Limit the input grid to roughly one elevation sample per CSS pixel;
  // outlines themselves are rasterized at the device's full pixel density.
  const z=Math.max(10,Math.min(14,10+Math.floor(Math.log2(scale))));
  const ratio=2**(z-10),m=this.meta;
  const left=m.width/2+(-view.width/2-view.panX)/scale,top=m.height/2+(-view.height/2-view.panY)/scale;
  const right=left+view.width/scale,bottom=top+view.height/scale;
  const x0=Math.floor((Math.max(0,left)+m.x0)*ratio/256)-1,y0=Math.floor((Math.max(0,top)+m.y0)*ratio/256)-1;
  const x1=Math.floor((Math.min(m.width,right)+m.x0)*ratio/256)+1,y1=Math.floor((Math.min(m.height,bottom)+m.y0)*ratio/256)+1;
  return {z,ratio,x0,y0,x1,y1,level:Math.round(view.level*5)/5,key:[z,x0,y0,x1,y1,Math.round(view.level*5)].join('/')};
 }
 update(view){
  if(!this.meta||this.unavailable)return;this.view=view;
  const spec=this.specification(view);
  if(view.ice){clearTimeout(this.debounce);this.generation++;this.requested=null;this.status.textContent='';return}
  if(spec.key===this.requested)return;
  this.requested=spec.key;const generation=++this.generation;clearTimeout(this.debounce);
  this.debounce=setTimeout(()=>this.refresh(spec,generation),140);
 }
 async tile(z,x,y){
  const key=`${z}/${x}/${y}`;
  if(this.cache.has(key)){const entry=this.cache.get(key);this.cache.delete(key);this.cache.set(key,entry);return entry}
  const promise=(async()=>{
   const response=await fetch(`https://elevation-tiles-prod.s3.amazonaws.com/terrarium/${key}.png`,{signal:AbortSignal.timeout(15000)});
   if(!response.ok)throw Error(`Tile ${response.status}`);
   const bitmap=await createImageBitmap(await response.blob());
   const c=document.createElement('canvas');c.width=c.height=256;const context=c.getContext('2d',{willReadFrequently:true});context.drawImage(bitmap,0,0);bitmap.close();
   const rgba=context.getImageData(0,0,256,256).data,values=new Float32Array(256*256);
   for(let i=0;i<values.length;i++)values[i]=rgba[i*4]*256+rgba[i*4+1]+rgba[i*4+2]/256-32768;
   return values;
  })();
  this.cache.set(key,promise);
  while(this.cache.size>96)this.cache.delete(this.cache.keys().next().value);
  promise.catch(()=>this.cache.delete(key));return promise;
 }
 async refresh(spec,generation){
  if(this.busy){this.pending={spec,generation};return}
  this.busy=true;this.status.textContent=spec.z>10?'Laddar kartdetaljer…':'';
  try{
   if(this.layers.base?.level!==spec.level){
    const contours=await this.geometry(null,spec.level);
    // Never let a response for an old year overwrite the selected year.
    if(generation!==this.generation)return;
    this.layers.base={paths:this.path(contours),level:spec.level,x:0,y:0,unit:1,width:this.meta.width,height:this.meta.height};this.onChange();
   }
   if(spec.z===10){this.status.textContent='';return}
   if(spec.x1<spec.x0||spec.y1<spec.y0){this.status.textContent='';return}
   const width=(spec.x1-spec.x0+1)*256,height=(spec.y1-spec.y0+1)*256;
   // An extreme viewport should keep the overview rather than allocate unbounded memory.
   if(width*height>9000000){this.status.textContent='';return}
   const values=new Float32Array(width*height),coords=[];
   for(let y=spec.y0;y<=spec.y1;y++)for(let x=spec.x0;x<=spec.x1;x++)coords.push({x,y});
   let cursor=0;
   await Promise.all(Array.from({length:6},async()=>{
    while(cursor<coords.length){if(generation!==this.generation)return;const {x,y}=coords[cursor++],v=await this.tile(spec.z,x,y);
     for(let row=0;row<256;row++)values.set(v.subarray(row*256,(row+1)*256),((y-spec.y0)*256+row)*width+(x-spec.x0)*256);
    }
   }));
   if(generation!==this.generation)return;
   const contours=await this.geometry({width,height,values},spec.level);
   if(generation!==this.generation)return;
   this.layers.detail={paths:this.path(contours),key:spec.key,level:spec.level,x:spec.x0*256/spec.ratio-this.meta.x0,y:spec.y0*256/spec.ratio-this.meta.y0,unit:1/spec.ratio,width,height};
   this.status.textContent='';this.onChange();
  }catch(error){
   if(generation===this.generation){this.status.textContent='Detaljer kunde inte laddas · översikt visas';this.requested=null;this.retryAfter=Date.now()+30000}
  }finally{
   this.busy=false;
   if(this.pending){const next=this.pending;this.pending=null;if(next.generation===this.generation)this.refresh(next.spec,next.generation)}
  }
 }
 draw(context,view){
  if(view.ice||!this.meta)return;
  const lev=Math.round(view.level*5)/5,scale=view.fit*view.zoom;
  for(const layer of [this.layers.base,this.layers.detail]){
   if(!layer||layer.level!==lev)continue;
   // Detail can remain visible while the adjacent view loads, but cannot replace
   // an overview after zooming out beyond its source resolution.
   if(layer.key&&this.specification(view).z===10)continue;
   const s=scale*layer.unit,x=view.width/2+view.panX+(layer.x-this.meta.width/2)*scale,y=view.height/2+view.panY+(layer.y-this.meta.height/2)*scale;
   context.save();context.translate(x,y);context.scale(s,s);
   context.beginPath();context.rect(1,1,layer.width-2,layer.height-2);context.clip();
   context.fillStyle='#b8d7da';context.fillRect(0,0,layer.width,layer.height);
   // Water halo, a crisp coastline, and restrained height bands read as a map.
   context.strokeStyle='#a0c2c2';context.lineWidth=5/s;context.lineJoin='round';context.stroke(layer.paths[0]);
   ['#ccd5b2','#c4cfaa','#bdcaa4'].forEach((color,i)=>{context.fillStyle=color;context.fill(layer.paths[i],'evenodd')});
   context.strokeStyle='#8da68e';context.lineWidth=.8/s;context.stroke(layer.paths[0]);
   context.restore();
  }
 }
}
