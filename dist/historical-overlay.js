'use strict';
class HistoricalOverlay {
 constructor(change){this.change=change;this.enabled=false;this.opacity=.65;}
 async load(){try{const r=await fetch('assets/historical-overlays.json?v=70c0074cf968');if(!r.ok)throw Error();const data=await r.json();this.data=data.readyOverlays[0];this.image=new Image();this.image.src='assets/aland-1894-mercator.webp';await this.image.decode();this.ready=true;this.change()}catch{this.failed=true;this.change()}}
 draw(ctx,v){if(!this.enabled)return;const status=document.querySelector('#overlayStatus');if(!this.ready){status.textContent=this.failed?'Kartan kunde inte laddas. Originalet finns i kartarkivet.':'Laddar 1894 års karta…';return}
  status.textContent='Karta 1894 · ungefärlig inpassning, kontroller ger cirka 0,5–0,6 km medelfel, lokalt större. För överblick, inte enskilda hus. '+(v.year!==1894?'Jämförelse med '+(v.year<0?Math.abs(v.year).toLocaleString('sv-SE')+' f.Kr.':v.year)+'.':'');
  const b=this.data.boundsWgs84||this.data.bounds||[19.31,59.90,21.26,60.58];
  const project=(lon,lat)=>[(lon+180)/360*v.meta.world-v.meta.x0,(1-Math.asinh(Math.tan(lat*Math.PI/180))/Math.PI)/2*v.meta.world-v.meta.y0];
  const nw=project(b[0],b[3]),se=project(b[2],b[1]),s=v.scale,x=(nw[0]-v.meta.width/2)*s+v.width/2+v.panX,y=(nw[1]-v.meta.height/2)*s+v.height/2+v.panY;
  ctx.save();ctx.globalAlpha=this.opacity;ctx.drawImage(this.image,x,y,(se[0]-nw[0])*s,(se[1]-nw[1])*s);ctx.restore();
 }
}
