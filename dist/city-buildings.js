'use strict';
// One renderer for city roofs, source snapshots and documented building places.
class CityBuildings {
 constructor(change){this.change=change;this.sets=[];this.links={};this.coverage=[19.912,60.079,19.962,60.139];this.drawn=[];this.cache=null;this.revision=0}
 async load(){try{const r=await fetch('assets/city-buildings.json?v=9f4b5913dee3');if(!r.ok)throw Error();Object.assign(this,await r.json());this.ready=true;this.revision++}catch{this.failed=true}this.change()}
 contains(lon,lat){const b=this.coverage;return lon>=b[0]&&lon<=b[2]&&lat>=b[1]&&lat<=b[3]}
 owns(f){if(f.kind!=='building')return false;const p=f.paths[0];return this.contains(p.reduce((s,p)=>s+p[0],0)/p.length,p.reduce((s,p)=>s+p[1],0)/p.length)}
 static inside(lon,lat,paths){let yes=false;for(const ring of paths)for(let i=1;i<ring.length;i++){const a=ring[i-1],b=ring[i];if((a[1]>lat)!==(b[1]>lat)&&lon<(b[0]-a[0])*(lat-a[1])/(b[1]-a[1])+a[0])yes=!yes}return yes}
 snapshot(year){return this.sets.filter(s=>s.year<=year).at(-1)}
 geometry(f,project){if(f.cityPath)return;f.cityPath=new Path2D();f.cityBounds=[Infinity,Infinity,-Infinity,-Infinity];for(const ring of f.paths){ring.forEach((p,i)=>{const[x,y]=project(...p),b=f.cityBounds;b[0]=Math.min(b[0],x);b[1]=Math.min(b[1],y);b[2]=Math.max(b[2],x);b[3]=Math.max(b[3],y);i?f.cityPath.lineTo(x,y):f.cityPath.moveTo(x,y)});f.cityPath.closePath()}}
 records(year,explorer,grid,library){
  this.catalogReady=explorer.ready;
  const key=[year,explorer.flags.historic,explorer.flags.modern,explorer.flags.uncertain,explorer.flags.traces,explorer.category,explorer.query,grid.enabled,grid.ready,this.revision,explorer.historic.length,explorer.modern.length].join('|');if(this.cache?.key===key)return this.cache.records;
  let roofs=[],sourceYear=null;
  const stage=grid.stage(year),snapshot=this.snapshot(year);
  if(year>=2026&&explorer.flags.modern){roofs=explorer.modern.filter(f=>this.owns(f));sourceYear=2026}
  else if(year>=2014&&year<2026&&grid.enabled&&snapshot){roofs=snapshot.features;sourceYear=snapshot.year}
  else if(stage?.year===1920){roofs=stage.features.filter(f=>f.kind==='building');sourceYear=1920}
  const records=roofs.map(f=>({id:f.id,shape:f,target:f,sourceYear,schematic:false})),byId=new Map(records.map(r=>[r.id,r]));
  const histories=explorer.flags.historic?explorer.historic.filter(f=>explorer.available(f,year)&&explorer.matches(f)&&(explorer.category==='all'||explorer.category==='building')):[];
  if(library&&year>=library.start&&explorer.flags.historic)histories.push(library);
  for(const h of histories){
   const linked=byId.get(h.osmId||this.links[h.id]);
   // Only a containing roof in the selected source can absorb a place point.
   // A demolished site's modern replacement must never inherit its identity.
   const nearby=!linked&&!h.end?records.find(r=>CityBuildings.inside(h.lon,h.lat,r.shape.paths)):null;
   if(linked||nearby){const r=linked||nearby;r.target=h;r.history=h;continue}
   // A schematic symbol in map space, not a claim about measured dimensions.
   const dx=.000108,dy=.000036;
   const shape={paths:[[[h.lon-dx,h.lat-dy],[h.lon+dx,h.lat-dy],[h.lon+dx,h.lat+dy],[h.lon-dx,h.lat+dy],[h.lon-dx,h.lat-dy]]]};
   records.push({id:h.id,shape,target:h,history:h,schematic:true,trace:EvidenceTime.state(h,year)==='trace'});
  }
  this.cache={key,records,sourceYear};return records;
 }
 draw(ctx,v,explorer,grid,library){this.view=v;this.drawn=[];this.historyInView=[];if(!explorer.prepared)return;
  const records=this.records(v.year,explorer,grid,library);this.currentRecords=records;
  for(const id of ['cityBuildingStatus','cityBuildingNote']){const status=document.getElementById(id);if(status)status.textContent=this.status(v.year,records)}
  if(v.zoom<8||v.fortressDetail)return;
  const s=v.scale,left=v.meta.width/2+(-v.width/2-v.panX)/s,top=v.meta.height/2+(-v.height/2-v.panY)/s;
  ctx.save();ctx.translate(v.width/2+v.panX-v.meta.width/2*s,v.height/2+v.panY-v.meta.height/2*s);ctx.scale(s,s);
  for(const r of records){const f=r.shape;this.geometry(f,explorer.project);const b=f.cityBounds;if(b[2]<left||b[0]>left+v.width/s||b[3]<top||b[1]>top+v.height/s)continue;
   const selected=[r.id,r.target.id,r.history?.osmId].includes(explorer.selected)||r.target.id===this.selected;
   r.renderPath=f.cityPath;r.renderBounds=b;if(r.schematic){const cx=(b[0]+b[2])/2,cy=(b[1]+b[3])/2,hw=Math.max((b[2]-b[0])/2,2.5/s),hh=Math.max((b[3]-b[1])/2,1.7/s);r.renderBounds=[cx-hw,cy-hh,cx+hw,cy+hh];r.renderPath=new Path2D();r.renderPath.rect(cx-hw,cy-hh,hw*2,hh*2)}
   ctx.fillStyle=selected?'#d59e69':r.trace?'#c8c7ba':r.schematic?'#b49270aa':'#ad8a6d';ctx.strokeStyle=selected?'#65442f':r.trace?'#797d70':'#725d49';ctx.lineWidth=(selected?2:.75)/s;ctx.setLineDash(r.schematic?[2/s,2/s]:[]);ctx.fill(r.renderPath,'evenodd');ctx.stroke(r.renderPath);this.drawn.push(r);if(r.history)this.historyInView.push(r.history);
  }ctx.restore();
  // Labels appear on selection, never as a second marker over a roof.
  for(const r of this.drawn.filter(r=>r.target.id===explorer.selected||r.target.id===this.selected)){const b=r.shape.cityBounds,x=((b[0]+b[2])/2-v.meta.width/2)*s+v.width/2+v.panX,y=(b[3]-v.meta.height/2)*s+v.height/2+v.panY+15;ctx.save();ctx.font='12px -apple-system,sans-serif';ctx.textAlign='center';ctx.lineWidth=3;ctx.strokeStyle='#faf7e8';ctx.strokeText(r.target.name,x,y);ctx.fillStyle='#435445';ctx.fillText(r.target.name,x,y);ctx.restore()}
 }
 status(year,records=this.currentRecords||[]){if(!this.catalogReady)return 'Laddar Mariehamns hus…';const known=records.filter(r=>r.history).length,roofs=records.filter(r=>!r.schematic).length;return `${known} ${known===1?'daterad husplats':'daterade husplatser'} · ${roofs.toLocaleString('sv-SE')} kartlagda huskonturer. ${year>=2014?'OSM:s källår är inte byggår.':year>=1942?'Äldre hus utan belagd kontur visas schematiskt.':year>=1920?'Huskonturerna kommer från 1920-talets museikarta.':'Stadsplanen visar planerade kvarter; hus visas från sina belagda år.'}`}
 hit(x,y,ctx){const v=this.view;if(!v||!this.drawn.length)return null;const wx=(x-v.width/2-v.panX)/v.scale+v.meta.width/2,wy=(y-v.height/2-v.panY)/v.scale+v.meta.height/2,t=4/v.scale;
  const candidates=this.drawn.filter(r=>{const b=r.renderBounds;return wx>=b[0]-t&&wx<=b[2]+t&&wy>=b[1]-t&&wy<=b[3]+t});ctx.save();ctx.setTransform(1,0,0,1,0,0);const r=candidates.find(r=>ctx.isPointInPath(r.renderPath,wx,wy,'evenodd'))||candidates.filter(r=>r.schematic).sort((a,b)=>{const distance=r=>Math.hypot(wx-(r.shape.cityBounds[0]+r.shape.cityBounds[2])/2,wy-(r.shape.cityBounds[1]+r.shape.cityBounds[3])/2);return distance(a)-distance(b)})[0];ctx.restore();if(!r)return null;
  if(r.history)return r.history;
  if(r.sourceYear===1920)return r.target;
  return {...r.target,recordType:'cityBuilding',sourceYear:r.sourceYear};
 }
 story(f){return `<button class="back" id="backFeature">← Till tidsperioden</button><br><span class="storytag">Kartlagd byggnad · ${f.sourceYear}</span><h2>${htmlEscape(f.name)}</h2><p>Här ser du husets kontur ovanifrån i kartunderlaget från ${f.sourceYear}. Tryck framåt i tiden och se hur kartbilden förändras.</p><p class="asidehint">Källåret är inte husets byggår. Skillnader mellan kartår kan bero på bättre kartläggning. Ett hus som saknas i en äldre karta kan ändå ha funnits då.</p><a href="https://www.openstreetmap.org/${f.id}" target="_blank" rel="noopener noreferrer">Se kartobjektet i OpenStreetMap ↗</a>`}
}
