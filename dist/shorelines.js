'use strict';
class ShorelineModel {
 constructor(change,status){this.change=change;this.status=status;this.cache=new Map();this.pending=new Map();this.year=null;this.failed=new Set();}
 async load(){try{const r=await fetch('assets/shorelines/manifest.json?v=1425d2c2bbec');if(!r.ok)throw Error();this.manifest=await r.json();this.change()}catch{this.unavailable=true;this.status.textContent='Strandlinjemodellen kunde inte laddas.'}}
 paths(data){const result={};for(const[k,polygons]of Object.entries(data.classes)){const path=new Path2D();for(const polygon of polygons)for(const ring of polygon){ring.forEach(([x,y],i)=>i?path.lineTo(x,y):path.moveTo(x,y));path.closePath()}result[k]=path}return result}
 update(year){this.year=year;if(year<(this.manifest?.years[0]??-9750)){this.status.textContent='Före modellens början · istäcket är schematiskt';this.target=null;return}if(!this.manifest)return;
  const target=EvidenceTime.modelYear(year,this.manifest.years);this.target=target;
  const label=y=>y<0?Math.abs(y).toLocaleString('sv-SE')+' f.Kr.':y===0?'omkring vår tideräknings början':y+' e.Kr.';
  const note=year===target?'Strandlinjemodell '+label(target):'Valt år '+label(year)+' · strandlinjemodell '+label(target);
  this.status.textContent=this.cache.has(target)?note+(year===2026?' · Mariehamns kust: OSM 2026':year>1900?' · senare strandbyggnation ingår inte':''):this.failed.has(target)?'Strandlinjen kunde inte laddas för modellåret.':'Laddar strandlinjemodell '+label(target)+'…';
  if(this.cache.has(target)||this.pending.has(target)||this.failed.has(target))return;
  const task=fetch(`assets/shorelines/${target}.json.gz`).then(async r=>{if(!r.ok)throw Error();const bytes=new Uint8Array(await r.arrayBuffer());if(bytes[0]===31&&bytes[1]===139)return new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).json();return JSON.parse(new TextDecoder().decode(bytes))}).then(data=>{this.cache.set(target,this.paths(data));while(this.cache.size>8)this.cache.delete(this.cache.keys().next().value)}).catch(()=>this.failed.add(target)).finally(()=>{this.pending.delete(target);if(this.target===target)this.change()});this.pending.set(target,task);
 }
 draw(ctx,v){this.update(v.year);if(v.year<(this.manifest?.years[0]??-9750)){ctx.fillStyle='#e3eeec';ctx.fillRect(0,0,v.width,v.height);return}
  const paths=this.cache.get(this.target);ctx.fillStyle='#b8d7da';ctx.fillRect(0,0,v.width,v.height);if(!paths)return;
  ctx.save();const s=v.scale;ctx.translate(v.width/2+v.panX-v.meta.width/2*s,v.height/2+v.panY-v.meta.height/2*s);ctx.scale(s,s);
  ctx.fillStyle='#c8d2ae';ctx.fill(paths.land,'evenodd');ctx.strokeStyle='#8ca89b';ctx.lineWidth=.65/s;ctx.stroke(paths.land);
  ctx.fillStyle='#e9f0ef';ctx.fill(paths.ice,'evenodd');ctx.strokeStyle='#cadbdc';ctx.stroke(paths.ice);
  ctx.fillStyle='#e0e5dc';ctx.fill(paths.noData,'evenodd');ctx.restore();
 }
}
