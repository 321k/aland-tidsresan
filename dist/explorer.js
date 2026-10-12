'use strict';
const htmlEscape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const categoryLabels={settlement:'Boplats',grave:'Grav / röse',foundation:'Husgrund',road:'Historisk väg',maritime:'Sjöfartsspår',fortification:'Befästning',other:'Övrig lämning',building:'Historisk byggnad'};
const safeURL=value=>{try{const u=new URL(value);return ['http:','https:'].includes(u.protocol)?u.href:'#'}catch{return '#'}};
class ExplorerLayers {
 constructor(change,select){this.change=change;this.select=select;this.heritage=[];this.historic=[];this.boundaries=[];this.modern=[];this.drawn=[];this.hits=[];this.flags={heritage:true,modern:true,postal:true,undated:false,uncertain:true,traces:true,historic:true,boundaries:true};this.category='all';this.ready=false;this.viewList=[];this.selected=null;this.query='';this.sourceDate='2026-10-12';this.coast=null;}
 async load(){
  const results=await Promise.allSettled([fetch('assets/heritage.json?v=23e800887684').then(r=>{if(!r.ok)throw Error();return r.json()}),fetch('assets/modern.json?v=9a9b4f03571c').then(r=>{if(!r.ok)throw Error();return r.json()}),fetch('assets/coast.json?v=5a3a6ed878b6').then(r=>{if(!r.ok)throw Error();return r.json()}),fetch('assets/historic-buildings.json?v=35881d45dd18').then(r=>{if(!r.ok)throw Error();return r.json()}),fetch('assets/heritage-boundaries.geojson?v=94bddcf5764a').then(r=>{if(!r.ok)throw Error();return r.json()})]);
  if(results[0].status==='fulfilled')this.heritage=results[0].value.features;else document.querySelector('#registerStatus').textContent='Fornminnesregistret kunde inte laddas. Prova att ladda om sidan.';
  if(results[1].status==='fulfilled'){this.modern=results[1].value.features;this.sourceDate=results[1].value.snapshot.slice(0,10)}else document.querySelector('#modernStatus').textContent='Byggnader och vägar kunde inte laddas. Prova att ladda om sidan.';
  if(results[2].status==='fulfilled')this.coast=results[2].value;
  if(results[3].status==='fulfilled')this.historic=results[3].value.features.map(f=>({...f,recordType:'building',category:'building',code:f.address,childText:f.text,periods:[]}));else document.querySelector('#historicStatus').textContent='Historiska byggnader kunde inte laddas.';
  if(results[4].status==='fulfilled')this.boundaries=results[4].value.features;else document.querySelector('#registerStatus').textContent='Områdesgränserna kunde inte laddas.';this.ready=true;this.change();
 }
 prepare(project){if(this.prepared||!this.ready)return;this.prepared=true;this.project=project;
  for(const feature of this.modern){const p=new Path2D(),bounds=[Infinity,Infinity,-Infinity,-Infinity];
   for(const ring of feature.paths){ring.forEach((point,i)=>{const [x,y]=project(...point);bounds[0]=Math.min(bounds[0],x);bounds[1]=Math.min(bounds[1],y);bounds[2]=Math.max(bounds[2],x);bounds[3]=Math.max(bounds[3],y);i?p.lineTo(x,y):p.moveTo(x,y)});if(feature.kind==='building')p.closePath()}
   feature.path=p;feature.bounds=bounds;
  }
  for(const feature of [...this.heritage,...this.historic])feature.point=project(feature.lon,feature.lat);
  const byCode=new Map(this.heritage.map(f=>[f.code,f]));
  for(const f of this.boundaries){const parent=byCode.get(f.properties.code);if(!parent)continue;const path=parent.boundaryPath??new Path2D();const polys=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;for(const polygon of polys)for(const ring of polygon){ring.forEach((p,i)=>{const[x,y]=project(...p);i?path.lineTo(x,y):path.moveTo(x,y)});path.closePath()}parent.boundaryPath=path;}

  if(this.coast){this.coastPath=new Path2D();const polygons=this.coast.geometry.type==='Polygon'?[this.coast.geometry.coordinates]:this.coast.geometry.coordinates;for(const polygon of polygons)for(const ring of polygon){ring.forEach((point,i)=>{const[x,y]=project(...point);i?this.coastPath.lineTo(x,y):this.coastPath.moveTo(x,y)});this.coastPath.closePath()}const b=this.coast.bbox,a=project(b[0],b[3]),z=project(b[2],b[1]);this.coastBounds=[a[0],a[1],z[0]-a[0],z[1]-a[1]]}
 
 }
 available(feature,year){const state=EvidenceTime.state(feature,year);return state!=='future'&&(state!=='undated'||this.flags.undated)&&(state!=='possible'||this.flags.uncertain)&&(state!=='trace'||this.flags.traces)}
 screen(point,view){return[(point[0]-view.meta.width/2)*view.scale+view.width/2+view.panX,(point[1]-view.meta.height/2)*view.scale+view.height/2+view.panY]}
 matches(feature){return !this.query||[feature.name,feature.code,feature.village,feature.description,...(feature.periodLabels||[])].join(' ').toLocaleLowerCase('sv').includes(this.query)}
 render(ctx,view){if(!this.prepared)return;this.hits=[];this.drawn=[];this.viewList=[];this.view=view;
  if(view.year>=2026)this.drawCoast(ctx,view);
  view.overlay?.draw(ctx,view);
  if(view.year>=2026&&this.flags.modern)this.drawModern(ctx,view);
  if(view.year>=1700&&this.flags.postal)this.drawPostal(ctx,view);
  if(this.flags.heritage||this.flags.historic)this.drawHeritage(ctx,view);
  this.updateList(view);
 }
 drawCoast(ctx,v){if(!this.coastPath)return;const s=v.scale;ctx.save();ctx.translate(v.width/2+v.panX-v.meta.width/2*s,v.height/2+v.panY-v.meta.height/2*s);ctx.scale(s,s);ctx.beginPath();ctx.rect(...this.coastBounds);ctx.clip();ctx.fillStyle='#b8d7da';ctx.fillRect(...this.coastBounds);ctx.fillStyle='#c5ceab';ctx.fill(this.coastPath,'evenodd');ctx.lineWidth=.8/s;ctx.strokeStyle='#8dac9c';ctx.stroke(this.coastPath);ctx.restore()}
 drawModern(ctx,v){
  const s=v.scale,left=v.meta.width/2+(-v.width/2-v.panX)/s,top=v.meta.height/2+(-v.height/2-v.panY)/s,right=left+v.width/s,bottom=top+v.height/s;
  const features=this.modern.filter(f=>f.bounds[2]>=left&&f.bounds[0]<=right&&f.bounds[3]>=top&&f.bounds[1]<=bottom);
  this.drawn=features;
  ctx.save();ctx.translate(v.width/2+v.panX-v.meta.width/2*s,v.height/2+v.panY-v.meta.height/2*s);ctx.scale(s,s);ctx.lineCap='round';ctx.lineJoin='round';
  const mpp=Math.cos(60.1*Math.PI/180)*40075016.7/v.meta.world/s;
  const roads=features.filter(f=>f.kind==='road');
  const roadWidth=f=>['trunk','primary','secondary'].includes(f.class)?Math.max(2.8,8/mpp):['tertiary','residential','unclassified','living_street'].includes(f.class)?Math.max(1.5,5/mpp):Math.max(.7,2/mpp);
  for(const f of roads){ctx.lineWidth=(roadWidth(f)+1.2)/s;ctx.strokeStyle='#9eaa96';ctx.stroke(f.path)}
  for(const f of roads){ctx.lineWidth=roadWidth(f)/s;ctx.strokeStyle=['footway','path','steps','cycleway'].includes(f.class)?'#e3d5b5':'#faf7e7';ctx.stroke(f.path)}
  if(mpp<18)for(const f of features.filter(f=>f.kind==='building')){ctx.fillStyle=this.selected===f.id?'#b67747':'#a9917d';ctx.strokeStyle=this.selected===f.id?'#624125':'#706a5c';ctx.lineWidth=.7/s;ctx.fill(f.path,'evenodd');ctx.stroke(f.path)}
  ctx.restore();
  if(mpp<5){const used=new Set(),occupied=[];ctx.font='11px -apple-system,sans-serif';ctx.textAlign='center';
   for(const f of roads){if(f.name==='Väg eller stig'||used.has(f.name)||f.class==='service')continue;const b=f.bounds,[x,y]=this.screen([(b[0]+b[2])/2,(b[1]+b[3])/2],v),w=ctx.measureText(f.name).width;if(x<50||y<30||x>v.width-50||y>v.height-30||occupied.some(p=>Math.abs(p[0]-x)<(p[2]+w)/2+14&&Math.abs(p[1]-y)<25))continue;used.add(f.name);occupied.push([x,y,w]);ctx.lineWidth=3;ctx.strokeStyle='#faf7e8';ctx.strokeText(f.name,x,y);ctx.fillStyle='#4d594d';ctx.fillText(f.name,x,y)}
  }
 }
 drawHeritage(ctx,v){const buckets=new Map(),size=v.zoom<8?34:20;
  const features=[...(this.flags.heritage?this.heritage:[]),...(this.flags.historic?this.historic:[])];
  for(const f of features){if(!this.available(f,v.year)||!this.matches(f)||(this.category!=='all'&&f.category!==this.category))continue;const [x,y]=this.screen(f.point,v);if(x<-30||x>v.width+30||y<-30||y>v.height+30)continue;this.viewList.push(f);const key=`${Math.floor(x/size)},${Math.floor(y/size)}`;if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push({f,x,y});
   if(f.boundaryPath&&v.zoom>=8&&(this.flags.boundaries||this.selected===f.id)){ctx.save();const s=v.scale;ctx.translate(v.width/2+v.panX-v.meta.width/2*s,v.height/2+v.panY-v.meta.height/2*s);ctx.scale(s,s);ctx.fillStyle='#a4644420';ctx.strokeStyle=this.selected===f.id?'#b16c27':'#925f49';ctx.lineWidth=1/s;ctx.setLineDash([4/s,3/s]);ctx.fill(f.boundaryPath,'evenodd');ctx.stroke(f.boundaryPath);ctx.restore()}
  }
  for(const entries of buckets.values()){const x=entries.reduce((s,e)=>s+e.x,0)/entries.length,y=entries.reduce((s,e)=>s+e.y,0)/entries.length,f=entries[0].f,state=EvidenceTime.state(f,v.year),cluster=entries.length>1;ctx.save();
   const color=entries.some(e=>e.f.id===this.selected)?'#ae681e':state==='trace'?'#797d70':f.category==='building'?'#886b51':'#854f44';
   ctx.strokeStyle=color;ctx.fillStyle=state==='possible'||state==='undated'?'#faf7e8':color;ctx.lineWidth=1.8;if(state==='undated')ctx.setLineDash([2,2]);
   ctx.beginPath();if(cluster)ctx.arc(x,y,12,0,Math.PI*2);else if(f.category==='building'||f.category==='foundation')ctx.rect(x-7,y-5,14,10);else if(f.category==='grave'){ctx.moveTo(x,y-7);ctx.lineTo(x+7,y+5);ctx.lineTo(x-7,y+5);ctx.closePath()}else if(f.category==='road'){ctx.moveTo(x-7,y+5);ctx.lineTo(x+7,y-5)}else ctx.arc(x,y,5.5,0,Math.PI*2);ctx.fill();ctx.stroke();
   if(cluster){ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='bold 10px sans-serif';ctx.fillStyle=state==='possible'?'#5d5144':'#fff';ctx.fillText(entries.length,x,y)}else if(f.category==='building'){ctx.beginPath();ctx.moveTo(x-7,y);ctx.lineTo(x+7,y);ctx.strokeStyle=state==='possible'?color:'#eee5d5';ctx.stroke();if(state==='trace'){ctx.beginPath();ctx.moveTo(x-9,y-7);ctx.lineTo(x+9,y+7);ctx.strokeStyle=color;ctx.stroke()}}
   if(!cluster&&(this.selected===f.id||(f.category==='building'&&v.zoom>=32))){ctx.font='11px -apple-system,sans-serif';ctx.textAlign='center';ctx.lineWidth=3;ctx.strokeStyle='#faf7e8';ctx.strokeText(f.name,x,y+21);ctx.fillStyle='#435445';ctx.fillText(f.name,x,y+21)}ctx.restore();this.hits.push({x,y,r:cluster?16:12,entries:entries.map(e=>e.f)});
  }
 }

 drawPostal(ctx,v){const stops=window.POSTAL_ROUTE||[];if(!stops.length)return;ctx.save();ctx.strokeStyle='#b4783f';ctx.lineWidth=3;ctx.setLineDash([8,6]);ctx.beginPath();stops.forEach((p,i)=>{const [x,y]=this.screen(this.project(p.lon,p.lat),v);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke();ctx.setLineDash([]);ctx.font='11px sans-serif';ctx.textAlign='center';for(const p of stops){const[x,y]=this.screen(this.project(p.lon,p.lat),v);ctx.fillStyle='#fff2d8';ctx.strokeStyle='#aa7437';ctx.beginPath();ctx.arc(x,y,4,0,7);ctx.fill();ctx.stroke();if(v.zoom>1.8){ctx.lineWidth=3;ctx.strokeStyle='#faf7e8';ctx.strokeText(p.name,x,y-9);ctx.fillStyle='#7c562b';ctx.fillText(p.name,x,y-9)}}ctx.restore()}
 hit(x,y,ctx){const h=this.hits.filter(h=>Math.hypot(x-h.x,y-h.y)<h.r).sort((a,b)=>Math.hypot(x-a.x,y-a.y)-Math.hypot(x-b.x,y-b.y))[0];if(h)return h.entries.length>1?{cluster:h.entries}:h.entries[0];
  const v=this.view;if(!v||v.year<2026||!this.flags.modern)return null;const wx=(x-v.width/2-v.panX)/v.scale+v.meta.width/2,wy=(y-v.height/2-v.panY)/v.scale+v.meta.height/2;
  ctx.save();ctx.setTransform(1,0,0,1,0,0);const candidates=this.drawn.filter(f=>wx>=f.bounds[0]-5/v.scale&&wx<=f.bounds[2]+5/v.scale&&wy>=f.bounds[1]-5/v.scale&&wy<=f.bounds[3]+5/v.scale);let found=candidates.find(f=>f.kind==='building'&&ctx.isPointInPath(f.path,wx,wy,'evenodd'));
  if(!found){ctx.lineWidth=10/v.scale;found=candidates.find(f=>f.kind==='road'&&ctx.isPointInStroke(f.path,wx,wy))}ctx.restore();return found;
 }
 updateList(v){
  const status=document.querySelector('#modernStatus');const buildings=this.modern.filter(f=>f.kind==='building').length;
  if(this.modern.length)status.textContent=v.year>=2026?`${buildings.toLocaleString('sv-SE')} byggnadskonturer · ${(this.modern.length-buildings).toLocaleString('sv-SE')} väg- och stigsegment. Mariehamn med omnejd, OSM ${this.sourceDate}.`:'Nutida byggnader och vägar visas vid 2026. Äldre år kan jämföras med flygfoton i kartarkivet.';
  document.querySelector('#postalStatus').textContent=v.year>=1700?'1700-talets postförbindelse · schematisk sträckning, inte uppmätt väg. '+(v.year>1799?'Visas som historisk referens.':''):'Postlagret bygger på en 1700-talskarta och visas från 1700.';
  if(this.historic.length)document.querySelector('#historicStatus').textContent=this.historic.length+' källbelagda byggnader och byggnadsplatser · lägen är punkter, inte historiska konturer.';
  const list=document.querySelector('#registerPlaces');const key=this.viewList.map(f=>f.id).join('|')+this.query+v.year;if(key===this.listKey)return;this.listKey=key;
  document.querySelector('#registerCount').textContent=this.viewList.length+' i kartvyn';
  list.replaceChildren();const ordered=[...this.viewList].sort((a,b)=>(b.recordType==='building')-(a.recordType==='building'));for(const f of ordered.slice(0,35)){const b=document.createElement('button');b.className='register-place';b.innerHTML=`<span>${htmlEscape(f.name||'Namnlös lämning')}</span><small>${htmlEscape(categoryLabels[f.category]||'Plats')} · ${htmlEscape(f.dateLabel||f.periodLabels?.join(' / ')||'Odaterad')}</small>`;b.onclick=()=>this.select(f,true);list.append(b)}
  if(this.viewList.length>35){const p=document.createElement('p');p.className='asidehint';p.textContent='Zooma in, välj platstyp eller sök för att avgränsa fler platser.';list.append(p)}
 }
 search(text){this.query=text.trim().toLocaleLowerCase('sv');this.listKey=null;const found=[...this.heritage,...this.historic].filter(f=>this.matches(f));this.change();return found}
 story(f){
  const state=EvidenceTime.state(f,this.view?.year??2026);
  const datingBadge=`<span class="evidence-badge ${state}">${htmlEscape(EvidenceTime.label(state))}</span>`;
  if(f.recordType==='building'){
   const y=this.view?.year??2026,fmt=y=>y<0?Math.abs(y)+' f.Kr.':y;
   return `<button class="back" id="backFeature">← Till tidsperioden</button><br><span class="storytag">${state==='trace'?'Historisk byggnadsplats':'Historisk byggnad'}</span><h2>${htmlEscape(f.name)}</h2><p class="register-id">${htmlEscape(f.address)}</p>${datingBadge}<p>${htmlEscape(f.text)}</p>${state==='trace'?'<p>Huset finns inte längre kvar. Symbolen visar platsen där det stod.</p>':''}<div class="dating"><strong>${htmlEscape(f.dateLabel)}</strong><p>${htmlEscape(f.accuracyNote||'Byggår enligt den angivna källan.')}</p></div><h3>Husets historia</h3><ol class="building-phases">${f.phases.map(p=>`<li class="${p.from>y?'later-phase':''}"><strong>${p.from==null?'År saknas':fmt(p.from)}${p.to?'–'+fmt(p.to):''}</strong><span>${htmlEscape(p.label)}</span>${p.from>y?'<small>Efter valt år</small>':''}</li>`).join('')}</ol>${f.relatedEvents?.length?`<details><summary>Andra händelser kring huset</summary>${f.relatedEvents.map(e=>`<p>${htmlEscape(e.year||e.from||'')} ${htmlEscape(e.label||e.text||'')}</p>`).join('')}</details>`:''}<p class="asidehint">${htmlEscape(f.precision)} Symbolen är schematisk och visar inte husets exakta form eller storlek.</p>${f.wiki?`<p class="wikipedia-link"><a href="${safeURL(f.wiki)}" target="_blank" rel="noopener noreferrer">Läs mer på Wikipedia ↗</a></p>`:''}<details><summary>Källor till byggnadens historia</summary><ul>${f.sources.map(s=>`<li><a href="${safeURL(s.url)}" target="_blank" rel="noopener noreferrer">${htmlEscape(s.title)} ↗</a></li>`).join('')}</ul></details>`;
  }

  if(f.kind){const actual='Nutida kartkontur. Kartpostens datum kan avse verksamheten och används inte som byggår. För källbelagd byggnadshistoria, välj det historiska byggnadslagret.';
   return `<button class="back" id="backFeature">← Till tidsperioden</button><br><span class="storytag">Nutida ${f.kind==='building'?'byggnad':'väg eller stig'}</span><h2>${htmlEscape(f.name)}</h2><p>${f.kind==='building'?'Här ser du byggnadens kartlagda kontur ovanifrån.':'Den här linjen följer ett kartlagt väg- eller stigsegment.'}</p><p>${actual}</p>${f.wiki?`<p class="wikipedia-link"><a href="${safeURL(/^https?:/.test(f.wiki)?f.wiki:'https://'+(f.wiki.includes(':')?f.wiki.split(':')[0]:'sv')+'.wikipedia.org/wiki/'+encodeURIComponent(f.wiki.includes(':')?f.wiki.slice(f.wiki.indexOf(':')+1):f.wiki))}" target="_blank" rel="noopener noreferrer">Läs mer på Wikipedia ↗</a></p>`:''}<p class="asidehint">OpenStreetMap, hämtat ${this.sourceDate}. En nutida kartbild; den daterar inte bebyggelsen bakåt i tiden.</p><a href="https://www.openstreetmap.org/${f.id}" target="_blank" rel="noopener noreferrer">Se kartobjekt och uppgifter i OpenStreetMap ↗</a>`;
  }
  return `<button class="back" id="backFeature">← Till tidsperioden</button><br><span class="storytag">${htmlEscape(categoryLabels[f.category]||'Registrerad fornlämning')}</span><h2>${htmlEscape(f.name||'Namnlös lämning')}</h2>${datingBadge}<p class="register-id">${htmlEscape(f.code)} · ${htmlEscape(f.village||'Åland')}</p>${f.childText?`<p>${htmlEscape(f.childText)}</p><details><summary>Läs registerbeskrivningen</summary><p>${htmlEscape(f.description)}</p></details>`:`<p>${htmlEscape(f.description||'Det finns ingen beskrivning i registerposten.')}</p>`}${f.wiki?`<p class="wikipedia-link"><a href="${safeURL(f.wiki)}" target="_blank" rel="noopener noreferrer">Läs mer på Wikipedia ↗</a></p>`:''}<div class="dating"><strong>Datering</strong><p>${htmlEscape(f.dateLabel||(f.periodLabels||[]).join(' · ')||'Odaterad i underlaget')}</p><small>${htmlEscape(f.datingNote||'Periodgränserna är ungefärliga. Markeringen visar en registrerad plats, inte en rekonstruerad byggnad.')}</small></div><p class="asidehint">${htmlEscape(f.status||'')} · Koordinat från fornlämningsregistret. Äldre belägg betyder inte att platsen var i oavbrutet bruk. Streckad områdesgräns är registrets avgränsning, inte en byggnads kontur.</p><a href="${safeURL(f.sourceUrl||'https://kartor.regeringen.ax/arcgis/rest/services/Kulturarv/Fornminnen/MapServer')}" target="_blank" rel="noopener noreferrer">${f.sourceUrl?.includes('doi.org')?'Forskning · dateringskälla':'Ålands landskapsregering · registerkälla'} ↗</a><p class="asidehint">CC BY 4.0 · registertext</p>`;
 }
}
