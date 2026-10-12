'use strict';
class HistoricalOverlay {
 constructor(change){this.change=change;this.enabled=false;this.opacity=.65;this.mode='1894';}
 async load(){try{const r=await fetch('assets/historical-overlays.json?v=70c0074cf968');if(!r.ok)throw Error();const data=await r.json();this.data=data.readyOverlays[0];this.image=new Image();this.image.src='assets/aland-1894-mercator.webp';await this.image.decode();this.ready=true;this.change()}catch{this.failed=true;this.change()}}
 // Three interpreted correspondences, not a surveyed georeference. Coordinates use
 // the 1824 × 1368 reference view; the original image remains unmodified.
 static cityAnchors=[
  {pixel:[1265,697],geo:[19.942466,60.097336],name:'Torggatan / Storagatan'},
  {pixel:[777,657],geo:[19.93527,60.096889],name:'Östra Esplanadgatan / Storagatan'},
  {pixel:[803,452],geo:[19.934845,60.098505],name:'Östra Esplanadgatan / Norragatan'}
 ];
 static museum={
  src:'https://mpf.spfpension.fi/Site/Data/2693/Images/VitrinindelningenS_N.png',
  source:'https://mpf.spfpension.fi/verksamhet/nybyggarne/mariehamn/',
  width:1888,height:1334,
  anchors:[
   {pixel:[1228,637],geo:[19.942466,60.097336],name:'Torggatan / Storagatan'},
   {pixel:[875,637],geo:[19.93527,60.096889],name:'Östra Esplanadgatan / Storagatan'},
   {pixel:[875,471],geo:[19.934845,60.098505],name:'Östra Esplanadgatan / Norragatan'}
  ]
 };
 async loadMuseumMap(){
  if(this.mode!=='1920'||this.museumLoading||this.museumReady)return;
  this.museumLoading=true;this.museumFailed=false;
  try{this.museumImage=new Image();this.museumImage.src=HistoricalOverlay.museum.src;await this.museumImage.decode();this.museumReady=true}catch{this.museumFailed=true}
  this.museumLoading=false;this.change();
 }
 drawMuseumMap(ctx,v){
  const status=document.querySelector('#overlayStatus');
  if(!this.museumReady){status.textContent=this.museumFailed?'Museikartan kunde inte laddas från källan. Öppna originalets sida via Förstora originalet.':'Laddar museikartan över 1920-talets Mariehamn…';return}
  status.textContent='Mariehamn på 1920-talet · museets översiktskarta, inte en uppmätning från exakt 1920. Röda ramar: vitriner. Ungefärlig inpassning mot gatunätet. Källa: Mariehamns Pensionärsförening / Nybyggarne. Vald tid: '+v.year+'.';
  const project=(lon,lat)=>[((lon+180)/360*v.meta.world-v.meta.x0-v.meta.width/2)*v.scale+v.width/2+v.panX,((1-Math.asinh(Math.tan(lat*Math.PI/180))/Math.PI)/2*v.meta.world-v.meta.y0-v.meta.height/2)*v.scale+v.height/2+v.panY];
  ctx.save();ctx.globalAlpha=this.opacity;ctx.transform(...HistoricalOverlay.affine(HistoricalOverlay.museum.anchors,project));ctx.drawImage(this.museumImage,0,0,HistoricalOverlay.museum.width,HistoricalOverlay.museum.height);ctx.restore();
 }
 static affine(anchors,project){
  const [p,q,r]=anchors.map(a=>a.pixel),[a,b,c]=anchors.map(a=>project(...a.geo));
  const ux=q[0]-p[0],uy=q[1]-p[1],vx=r[0]-p[0],vy=r[1]-p[1],det=ux*vy-uy*vx;
  const xx=((b[0]-a[0])*vy-(c[0]-a[0])*uy)/det,xy=(ux*(c[0]-a[0])-vx*(b[0]-a[0]))/det;
  const yx=((b[1]-a[1])*vy-(c[1]-a[1])*uy)/det,yy=(ux*(c[1]-a[1])-vx*(b[1]-a[1]))/det;
  return [xx,yx,xy,yy,a[0]-xx*p[0]-xy*p[1],a[1]-yx*p[0]-yy*p[1]];
 }
 async loadCityPlan(){
  if(this.mode!=='1860'||this.cityLoading||this.cityReady)return;
  this.cityLoading=true;
  try{this.cityImage=new Image();this.cityImage.src='assets/mariehamn-plan-1860.png';await this.cityImage.decode();this.cityReady=true}catch{this.cityFailed=true}
  this.change();
 }
 drawCityPlan(ctx,v){
  const status=document.querySelector('#overlayStatus');
  if(!this.cityReady){status.textContent=this.cityFailed?'Stadsplanen kunde inte laddas. Öppna originalet i kartarkivet.':'Laddar Mariehamns stadsplan…';return}
  status.textContent='Stadsplan 1860 · planerade hus och gator. Ungefärlig inpassning mot gatunätet; inga uppmätta lägesfel. Jämför strukturen, inte enskilda husgränser. Vald tid: '+v.year+'.';
  const project=(lon,lat)=>[((lon+180)/360*v.meta.world-v.meta.x0-v.meta.width/2)*v.scale+v.width/2+v.panX,((1-Math.asinh(Math.tan(lat*Math.PI/180))/Math.PI)/2*v.meta.world-v.meta.y0-v.meta.height/2)*v.scale+v.height/2+v.panY];
  ctx.save();ctx.globalAlpha=this.opacity;ctx.transform(...HistoricalOverlay.affine(HistoricalOverlay.cityAnchors,project));ctx.drawImage(this.cityImage,0,0,1824,1368);ctx.restore();
 }
 draw(ctx,v){if(!this.enabled)return;if(this.mode==='1860'){this.drawCityPlan(ctx,v);return}if(this.mode==='1920'){this.drawMuseumMap(ctx,v);return}const status=document.querySelector('#overlayStatus');if(!this.ready){status.textContent=this.failed?'Kartan kunde inte laddas. Originalet finns i kartarkivet.':'Laddar 1894 års karta…';return}
  status.textContent='Karta 1894 · ungefärlig inpassning, kontroller ger cirka 0,5–0,6 km medelfel, lokalt större. För överblick, inte enskilda hus. '+(v.year!==1894?'Jämförelse med '+(v.year<0?Math.abs(v.year).toLocaleString('sv-SE')+' f.Kr.':v.year)+'.':'');
  const b=this.data.boundsWgs84||this.data.bounds||[19.31,59.90,21.26,60.58];
  const project=(lon,lat)=>[(lon+180)/360*v.meta.world-v.meta.x0,(1-Math.asinh(Math.tan(lat*Math.PI/180))/Math.PI)/2*v.meta.world-v.meta.y0];
  const nw=project(b[0],b[3]),se=project(b[2],b[1]),s=v.scale,x=(nw[0]-v.meta.width/2)*s+v.width/2+v.panX,y=(nw[1]-v.meta.height/2)*s+v.height/2+v.panY;
  ctx.save();ctx.globalAlpha=this.opacity;ctx.drawImage(this.image,x,y,(se[0]-nw[0])*s,(se[1]-nw[1])*s);ctx.restore();
 }
}
