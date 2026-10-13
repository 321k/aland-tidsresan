'use strict';
class ShorelineModel {
 constructor(change,status){this.change=change;this.status=status;this.cache=new Map();this.pending=new Map();this.year=null;this.failed=new Set();this.displayed=null;this.showCoverageGaps=false;}
 async load(){try{const r=await fetch('assets/shorelines/manifest.json?v=1425d2c2bbec');if(!r.ok)throw Error();this.manifest=await r.json();this.change()}catch{this.unavailable=true;this.status.textContent='Strandlinjemodellen kunde inte laddas.'}}
 paths(data){const result={};for(const[k,polygons]of Object.entries(data.classes)){const path=new Path2D();for(const polygon of polygons)for(const ring of polygon){ring.forEach(([x,y],i)=>i?path.lineTo(x,y):path.moveTo(x,y));path.closePath()}result[k]=path}return result}
 request(target){
  if(this.cache.has(target)||this.failed.has(target))return Promise.resolve();
  if(this.pending.has(target))return this.pending.get(target);
  const task=fetch(`assets/shorelines/${target}.json.gz`).then(readCompressedJSON).then(data=>{
   this.cache.set(target,this.paths(data));
   // Keep the visible and requested shorelines even if prefetches finish out of order.
   for(const key of this.cache.keys()){if(this.cache.size<=8)break;if(key!==this.target&&key!==this.displayed?.year)this.cache.delete(key)}
  }).catch(()=>this.failed.add(target)).finally(()=>{this.pending.delete(target);if(this.target===target)this.change()});
  this.pending.set(target,task);return task;
 }
 prepare(year){
  if(!this.manifest)return !!this.unavailable;
  const years=this.manifest.years,index=year<years[0]?0:years.indexOf(EvidenceTime.modelYear(year,years));
  for(const target of years.slice(index,index+3))this.request(target);
  return year<years[0]||this.cache.has(years[index])||this.failed.has(years[index]);
 }
 update(year){this.year=year;if(year<(this.manifest?.years[0]??-9750)){this.status.textContent='Före modellens början · istäcket är schematiskt';this.target=null;this.displayed=null;return}if(!this.manifest)return;
  const target=EvidenceTime.modelYear(year,this.manifest.years);this.target=target;
  if(this.cache.has(target))this.displayed={year:target,paths:this.cache.get(target)};
  const label=y=>y<0?Math.abs(y).toLocaleString('sv-SE')+' f.Kr.':y===0?'omkring vår tideräknings början':y+' e.Kr.';
  const note=year===target?'Strandlinjemodell '+label(target):'Valt år '+label(year)+' · strandlinjemodell '+label(target);
  const previous=this.displayed?' Visar tills vidare modell '+label(this.displayed.year)+'.':'';
  this.status.textContent=this.cache.has(target)?note+(year===2026?' · Ålands kust: OSM 2026':year>1900?' · senare strandbyggnation ingår inte':''):this.failed.has(target)?'Strandlinjen kunde inte laddas för modellåret.'+previous:'Laddar strandlinjemodell '+label(target)+'…'+previous;
  this.request(target);
 }
 draw(ctx,v){this.update(v.year);if(v.year<(this.manifest?.years[0]??-9750)){ctx.fillStyle='#e3eeec';ctx.fillRect(0,0,v.width,v.height);return}
  const paths=this.displayed?.paths;ctx.fillStyle='#b8d7da';ctx.fillRect(0,0,v.width,v.height);if(!paths)return;
  ctx.save();const s=v.scale;ctx.translate(v.width/2+v.panX-v.meta.width/2*s,v.height/2+v.panY-v.meta.height/2*s);ctx.scale(s,s);
  ctx.fillStyle='#c8d2ae';ctx.fill(paths.land,'evenodd');ctx.strokeStyle='#8ca89b';ctx.lineWidth=.65/s;ctx.stroke(paths.land);
  ctx.fillStyle='#e9f0ef';ctx.fill(paths.ice,'evenodd');ctx.strokeStyle='#cadbdc';ctx.stroke(paths.ice);
  // Missing model coverage is not land. Keep the sea background unless the
  // reader explicitly asks to inspect the coverage mask.
  if(this.showCoverageGaps){ctx.fillStyle='#e0e5dc';ctx.fill(paths.noData,'evenodd')}ctx.restore();
 }
}
