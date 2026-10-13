'use strict';
class CityGrid {
 constructor(change){this.change=change;this.enabled=true;this.sets=[];this.drawn=[];this.selected=null}
 static yearFor(year){return year<1860?null:year<1920?1860:year<1942?1920:year<2014?1942:year<2021?2014:year<2025?2021:year<2026?2025:2026}
 async load(){try{const r=await fetch('assets/mariehamn-city-grid.json?v=748fc7aa96fc');if(!r.ok)throw Error();const data=await r.json();this.sets=data.sets;this.coverage=data.coverage;this.ready=true}catch{this.failed=true}this.change()}
 stage(year){return this.enabled?this.sets.find(d=>d.year===CityGrid.yearFor(year)):null}
 replacesRoads(year){return !!this.stage(year)&&year<2014}
 status(year){const d=this.stage(year);return !this.enabled?'Mariehamns stadsnät är avstängt.':year<1860?'Stadsnätet börjar med planen från 1860.':!d?this.failed?'Stadsnätet kunde inte laddas.':'Laddar Mariehamns stadsnät…':`${d.name} · ${d.counts.blocks} kvarter${d.counts.buildings?' · '+d.counts.buildings+' hussymboler':''}. ${d.kind==='plan'?'Streckat = planerat, inte byggt.':d.year===1920?'Museets årtiondesbild, inte exakt år 1920.':'Källår, inte byggår.'}`}
 prepare(d,project){if(d.prepared)return;
  for(const f of d.features){f.recordType='cityGrid';f.sourceSet=d;f.path=new Path2D();f.bounds=[Infinity,Infinity,-Infinity,-Infinity];
   for(const ring of f.paths){ring.forEach((p,i)=>{const[x,y]=project(...p);f.bounds[0]=Math.min(f.bounds[0],x);f.bounds[1]=Math.min(f.bounds[1],y);f.bounds[2]=Math.max(f.bounds[2],x);f.bounds[3]=Math.max(f.bounds[3],y);i?f.path.lineTo(x,y):f.path.moveTo(x,y)});if(f.kind!=='street')f.path.closePath()}
   f.lon=f.paths[0].reduce((s,p)=>s+p[0],0)/f.paths[0].length;f.lat=f.paths[0].reduce((s,p)=>s+p[1],0)/f.paths[0].length;
  }d.prepared=true;
 }
 draw(ctx,v,project){this.view=v;this.drawn=[];for(const id of ['cityGridStatus','cityStageNote']){const status=document.getElementById(id);if(status&&status.textContent!==this.status(v.year))status.textContent=this.status(v.year)}
  const d=this.stage(v.year);if(!d||v.zoom<8||v.fortressDetail)return;this.prepare(d,project);
  const s=v.scale,left=v.meta.width/2+(-v.width/2-v.panX)/s,top=v.meta.height/2+(-v.height/2-v.panY)/s,b=[left,top,left+v.width/s,top+v.height/s];
  this.drawn=d.features.filter(f=>f.bounds[0]<=b[2]&&f.bounds[2]>=b[0]&&f.bounds[1]<=b[3]&&f.bounds[3]>=b[1]&&(f.kind!=='building'||v.zoom>=16));
  const mpp=Math.cos(60.1*Math.PI/180)*40075016.7/v.meta.world/s,planned=d.kind==='plan';
  ctx.save();ctx.translate(v.width/2+v.panX-v.meta.width/2*s,v.height/2+v.panY-v.meta.height/2*s);ctx.scale(s,s);ctx.lineJoin='round';ctx.lineCap='round';
  for(const f of this.drawn){const selected=f.id===this.selected;ctx.setLineDash([]);
   if(f.kind==='street'){
    const width=Math.max(1.5,Math.min(18,f.width/mpp));ctx.lineWidth=(width+1.3)/s;ctx.strokeStyle=planned?'#a48b6688':'#929e8b';if(planned)ctx.setLineDash([6/s,5/s]);ctx.stroke(f.path);
    ctx.lineWidth=(planned?1.4:width)/s;ctx.strokeStyle=selected?'#ba773c':planned?'#a9773f':'#fff9e8';ctx.stroke(f.path);
   }else{
    ctx.fillStyle=selected?'#e5c793':f.kind==='park'?(planned?'#b5c79b88':'#aebe93'):f.kind==='square'?'#eee1c5':f.kind==='building'?'#b07d60':planned?'#ecdebd55':'#e8e1cb';
    ctx.strokeStyle=f.kind==='building'?'#785d4b':planned?'#ac966f':'#c5bda5';ctx.lineWidth=(selected?2:f.kind==='building'?.7:.55)/s;
    ctx.fill(f.path,'evenodd');if(planned)ctx.setLineDash([4/s,4/s]);ctx.stroke(f.path);
   }
  }ctx.restore();
  // Label only clear, named streets and parks, with screen-space collision checks.
  if(v.zoom>=22){const occupied=[];ctx.save();ctx.font='11px -apple-system,sans-serif';ctx.textAlign='center';ctx.lineWidth=3;
   for(const f of this.drawn.filter(f=>f.kind==='park'||f.kind==='street'&&/^(Torggatan|Norragatan|Storagatan|Södragatan|Strandgatan|Östra Esplanadgatan|Västra Esplanadgatan)/.test(f.name))){const p=project(f.lon,f.lat),x=(p[0]-v.meta.width/2)*s+v.width/2+v.panX,y=(p[1]-v.meta.height/2)*s+v.height/2+v.panY,label=f.name.replace(' · 1942',''),w=ctx.measureText(label).width;if(x<w/2+8||x>v.width-w/2-8||y<18||y>v.height-18||occupied.some(o=>Math.abs(o.x-x)<(o.w+w)/2+12&&Math.abs(o.y-y)<22))continue;occupied.push({x,y,w});ctx.strokeStyle='#faf7ed';ctx.strokeText(label,x,y);ctx.fillStyle='#566650';ctx.fillText(label,x,y)}ctx.restore();}
 }
 hit(x,y,ctx){const v=this.view;if(!v||!this.enabled||!this.drawn.length)return null;const wx=(x-v.width/2-v.panX)/v.scale+v.meta.width/2,wy=(y-v.height/2-v.panY)/v.scale+v.meta.height/2,t=5/v.scale;
  ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.lineWidth=t*2;
  const near=this.drawn.filter(f=>wx>=f.bounds[0]-t&&wx<=f.bounds[2]+t&&wy>=f.bounds[1]-t&&wy<=f.bounds[3]+t);
  const found=near.find(f=>f.kind==='building'&&ctx.isPointInPath(f.path,wx,wy,'evenodd'))||near.find(f=>f.kind==='street'&&ctx.isPointInStroke(f.path,wx,wy))||near.find(f=>f.kind!=='street'&&ctx.isPointInPath(f.path,wx,wy,'evenodd'));ctx.restore();return found||null;
 }
 story(f){const d=f.sourceSet,kind={street:'Gata',block:'Kvarter',park:'Esplanad / park',square:'Torg',building:'Hus på museikartan'}[f.kind]||'Stadsnät';
  const source=d.kind==='plan'?'assets/mariehamn-plan-1860.png':safeURL(d.source);
  const intro=d.kind==='plan'?'Här planerade man den nya staden. De streckade linjerna visar en idé om hur gatorna skulle gå.':f.kind==='building'?'På museikartan finns ett litet hus här. Många gårdar hade både bostadshus och små uthus.':f.kind==='block'?'Gatorna bildar ett kvarter. Jämför med nästa karta och se hur staden förändras.':f.kind==='park'?'Mellan gatorna finns gröna stråk. Kan ni följa esplanaden genom staden?':'Följ gatan genom staden. Finns den kvar på nästa karta?';
  return `<button class="back" id="backFeature">← Till tidsperioden</button><br><span class="storytag">${kind}${d.kind==='plan'?' · planerat':''}</span><h2>${htmlEscape(f.name)}</h2><p>${intro}</p><p class="asidehint">${htmlEscape(d.name)}</p><div class="city-stage-buttons" aria-label="Jämför Mariehamns stadsnät">${this.sets.map(s=>`<button data-city-grid-year="${s.year}" aria-pressed="${s.year===d.year}">${s.year===1920?'1920-tal':s.year===2026?'Idag':s.year}</button>`).join('')}</div><details><summary>Kartans källa och tolkning</summary><p>${htmlEscape(d.note)}</p>${f.kind==='building'?'<p>En förenklad kontur av en synlig hussymbol. Adress, byggår och rivningsår har inte fastställts för just denna symbol. Att symbolen försvinner vid nästa kartunderlag betyder inte att huset revs då.</p>':''}${f.kind==='block'?'<p>Ytan visar ett område omgivet av gator. Den är inte en fastighetsgräns och betyder inte att hela kvarteret var bebyggt.</p>':''}<p><a href="${source}" target="_blank" rel="noopener noreferrer">Öppna originalunderlaget ↗</a></p></details>`;
 }
}
