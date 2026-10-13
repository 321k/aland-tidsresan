'use strict';
class HistoricalRoads {
 constructor(change){this.change=change;this.enabled=true;this.sets=[];this.cache=new Map();this.loading=new Set();this.failed=new Set();this.drawn=[];this.selected=null;this.manifestReady=false}
 static snapshotYear(year){return year>=2026?null:year>=2025?2025:year>=2021?2021:year>=2014?2014:null}
 static sourceIds(year){if(year<1800||year>=2026)return [];const snapshot=this.snapshotYear(year);if(snapshot)return ['osm-'+snapshot];return [year>=1894?'atlas-1894':'alvin-1800',...(year>=1920?['museum-1920']:[]),...(year>=1942?['photo-1942']:[])]}
 async load(){try{const r=await fetch('assets/historical-roads.json?v=eb6056f20a3a');if(!r.ok)throw Error();this.sets=(await r.json()).sets;this.manifestReady=true}catch{this.failed.add('curated')}this.change()}
 async loadSnapshot(year){if(this.cache.has(year)||this.loading.has(year)||this.failed.has(year))return;this.loading.add(year);try{const response=await fetch(HistoricalRoads.snapshotFiles[year]);const data=await readCompressedJSON(response);if(data.year!==year||!Array.isArray(data.features))throw Error();this.cache.set(year,data)}catch{this.failed.add(year)}this.loading.delete(year);this.change()}
 static snapshotFiles={2014:'assets/roads-2014.json.gz?v=74cbe5e3c340',2021:'assets/roads-2021.json.gz?v=a4f6eaa5be29',2025:'assets/roads-2025.json.gz?v=2e3305d14dd6'};
 sources(year){const ids=HistoricalRoads.sourceIds(year),snapshot=HistoricalRoads.snapshotYear(year);return snapshot?(this.cache.has(snapshot)?[this.cache.get(snapshot)]:[]):this.sets.filter(d=>ids.includes(d.id))}
 prepare(dataset,project){if(dataset.prepared)return;dataset.grid=new Map();dataset.bounds=[Infinity,Infinity,-Infinity,-Infinity];
  for(const f of dataset.features){f.recordType='historicalRoad';f.kind='road';f.sourceSet=dataset;const path=new Path2D(),b=[Infinity,Infinity,-Infinity,-Infinity];
   for(const ring of f.paths)for(const [i,p]of ring.entries()){const[x,y]=project(...p);b[0]=Math.min(b[0],x);b[1]=Math.min(b[1],y);b[2]=Math.max(b[2],x);b[3]=Math.max(b[3],y);i?path.lineTo(x,y):path.moveTo(x,y)}
   f.path=path;f.bounds=b;if(f.pathsOutsideCity){f.pathOutsideCity=new Path2D();for(const ring of f.pathsOutsideCity)ring.forEach((p,i)=>{const[x,y]=project(...p);i?f.pathOutsideCity.lineTo(x,y):f.pathOutsideCity.moveTo(x,y)})}const mid=f.paths[0][Math.floor(f.paths[0].length/2)];f.lon=mid[0];f.lat=mid[1];
   for(let x=Math.floor(b[0]/32);x<=Math.floor(b[2]/32);x++)for(let y=Math.floor(b[1]/32);y<=Math.floor(b[3]/32);y++){const key=x+','+y;if(!dataset.grid.has(key))dataset.grid.set(key,[]);dataset.grid.get(key).push(f)}
   dataset.bounds[0]=Math.min(dataset.bounds[0],b[0]);dataset.bounds[1]=Math.min(dataset.bounds[1],b[1]);dataset.bounds[2]=Math.max(dataset.bounds[2],b[2]);dataset.bounds[3]=Math.max(dataset.bounds[3],b[3]);
  }dataset.prepared=true;
 }
 inView(dataset,b){const found=new Set(),d=dataset.bounds;if(!d)return [];
  for(let x=Math.max(Math.floor(d[0]/32),Math.floor(b[0]/32));x<=Math.min(Math.floor(d[2]/32),Math.floor(b[2]/32));x++)for(let y=Math.max(Math.floor(d[1]/32),Math.floor(b[1]/32));y<=Math.min(Math.floor(d[3]/32),Math.floor(b[3]/32));y++)for(const f of dataset.grid.get(x+','+y)||[])if(f.bounds[0]<=b[2]&&f.bounds[2]>=b[0]&&f.bounds[1]<=b[3]&&f.bounds[3]>=b[1])found.add(f);
  return [...found];
 }
 static visibleClass(cls,mpp){if(['motorway','trunk','primary','secondary'].some(c=>cls===c||cls===c+'_link'))return true;if(['tertiary','tertiary_link','unclassified'].includes(cls))return mpp<120;if(['residential','living_street','road'].includes(cls))return mpp<70;if(['service','track'].includes(cls))return mpp<20;return mpp<9}
 status(year){
  if(!this.enabled)return 'Äldre väglagret är avstängt.';
  if(year>=2026)return 'Dagens vägar visas i nutidslagret · OSM 2026.';
  if(year<1800)return 'Inget sammanhängande vägnät är kartlagt här före cirka 1800. Det betyder inte att vägar saknades.';
  const snapshot=HistoricalRoads.snapshotYear(year);
  if(snapshot){if(this.failed.has(snapshot))return 'Vägkartan '+snapshot+' kunde inte laddas. Ladda om sidan för att försöka igen.';if(!this.cache.has(snapshot))return 'Laddar vägkartan från '+snapshot+'…';return 'Vägar: OSM '+snapshot+' · '+this.cache.get(snapshot).features.length.toLocaleString('sv-SE')+' väg- och stigsegment. Kartläggningsår, inte byggår.'}
  if(this.failed.has('curated'))return 'De äldre vägarna kunde inte laddas. Ladda om sidan för att försöka igen.';
  if(!this.manifestReady)return 'Laddar äldre vägkartor…';
  return 'Vägunderlag: '+(year>=1894?'1894':'cirka 1800')+(year>=1920?' · Mariehamn: 1920-talet':'')+(year>=1942?' + infarter 1942':'')+'. Senaste belägg fram till valt år; senare ombyggnader kan saknas.';
 }
 draw(ctx,v,project){this.view=v;this.drawn=[];
  const snapshot=HistoricalRoads.snapshotYear(v.year);if(this.enabled&&snapshot)this.loadSnapshot(snapshot);
  const text=v.cityGrid?.replacesRoads(v.year)&&this.enabled?'Regionala vägar: '+(v.year>=1894?'1894':'cirka 1800')+'. Mariehamn: '+v.cityGrid.stage(v.year).name+'. Källåren anger inte byggår.':this.status(v.year);for(const id of ['roadStatus']){const el=document.getElementById(id);if(el&&el.textContent!==text)el.textContent=text}
  const badge=document.getElementById('roadMapStatus');if(badge){badge.hidden=v.year>=2026||v.year<1800||!this.enabled;const label=v.cityGrid?.replacesRoads(v.year)?'Mariehamn: '+v.cityGrid.stage(v.year).name:snapshot?(this.cache.has(snapshot)?'Vägar: OSM '+snapshot+' · kartläggningsår':text):v.year<1894?'Vägar: cirka 1800 · schematiska lägen':'Vägar: 1894'+(v.year>=1920?' / Mariehamn: 1920-tal':'')+(v.year>=1942?' + infarter 1942':'');if(badge.textContent!==label)badge.textContent=label;}
  if(!this.enabled||v.year>=2026)return;
  const s=v.scale,left=v.meta.width/2+(-v.width/2-v.panX)/s,top=v.meta.height/2+(-v.height/2-v.panY)/s,mpp=Math.cos(60.1*Math.PI/180)*40075016.7/v.meta.world/s;
  const b=[left-10/s,top-10/s,left+v.width/s+10/s,top+v.height/s+10/s];
  for(const dataset of this.sources(v.year)){if(v.cityGrid?.replacesRoads(v.year)&&['museum-1920','photo-1942'].includes(dataset.id))continue;this.prepare(dataset,project);this.drawn.push(...this.inView(dataset,b).filter(f=>HistoricalRoads.visibleClass(f.class,mpp)))}
  ctx.save();ctx.translate(v.width/2+v.panX-v.meta.width/2*s,v.height/2+v.panY-v.meta.height/2*s);ctx.scale(s,s);ctx.lineCap='round';ctx.lineJoin='round';
  for(const f of this.drawn){f.renderPath=(v.year>=1920||v.cityGrid?.replacesRoads(v.year))&&f.pathOutsideCity?f.pathOutsideCity:f.path;const selected=this.selected===f.id,minor=['footway','path','steps','cycleway','track','bridleway'].includes(f.class),approx=f.sourceSet.year<1900,width=selected?4:minor?1.1:['primary','secondary'].includes(f.class)?2.3:1.6;
   ctx.setLineDash([]);ctx.strokeStyle=approx?'#b59b74':'#9eaa96';ctx.lineWidth=(width+1.2)/s;ctx.stroke(f.renderPath);
   ctx.lineWidth=width/s;ctx.strokeStyle=selected?'#a66b2d':approx?'#f1dba3':'#faf7e7';ctx.setLineDash(minor?[3/s,3/s]:[]);ctx.stroke(f.renderPath);
  }ctx.restore();
 }
 hit(x,y,ctx){const v=this.view;if(!v||!this.enabled||v.year>=2026)return null;const wx=(x-v.width/2-v.panX)/v.scale+v.meta.width/2,wy=(y-v.height/2-v.panY)/v.scale+v.meta.height/2,tolerance=7/v.scale;
  ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.lineWidth=tolerance*2;const found=[...this.drawn].reverse().find(f=>wx>=f.bounds[0]-tolerance&&wx<=f.bounds[2]+tolerance&&wy>=f.bounds[1]-tolerance&&wy<=f.bounds[3]+tolerance&&ctx.isPointInStroke(f.renderPath,wx,wy));ctx.restore();return found||null;
 }
 story(f){const d=f.sourceSet;return `<button class="back" id="backFeature">← Till tidsperioden</button><br><span class="storytag">Äldre vägunderlag</span><h2>${htmlEscape(f.name)}</h2><div class="dating"><strong>${htmlEscape(d.name)}</strong><p>${htmlEscape(d.note)}</p></div><p>Vägen visas enligt det senaste tillgängliga underlaget fram till valt år. Källåret anger inte när vägen byggdes. Vi vet inte att sträckningen var oförändrad ända fram till nästa karta.</p>${d.year===1800?'<p class="asidehint">Mycket ungefärlig inpassning: kontrollberäkningen ger omkring 3 km fel när en kyrkpunkt lämnas utanför. Följ förbindelserna mellan orterna, inte det exakta läget.</p>':''}<p><a href="${safeURL(d.source)}" target="_blank" rel="noopener noreferrer">Öppna vägkartans källa ↗</a></p>${f.osmId?`<p><a href="https://www.openstreetmap.org/${f.osmId}/history" target="_blank" rel="noopener noreferrer">Kartobjektets ändringshistorik ↗</a></p>`:''}<div class="question"><strong>Fundera tillsammans</strong>Vilka byar binds ihop av vägen? Var behövde man fortsätta över vatten?</div>`}
}
