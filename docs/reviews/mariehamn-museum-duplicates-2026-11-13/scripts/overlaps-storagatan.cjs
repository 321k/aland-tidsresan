const fs=require('fs'),zlib=require('zlib'),vm=require('vm');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const catalog=read('dist/assets/temporal-objects.json.gz'),box={};vm.createContext(box);
vm.runInContext(fs.readFileSync('dist/temporal-objects.js','utf8')+';this.Model=TemporalObjects',box);
const model=new box.Model(catalog);
const geom=new Map(catalog.geometries.map(g=>[g.id,g]));
const X=x=>x*55600,Y=y=>y*111320;
const roadPts=catalog.objects.filter(o=>o.kind==='roadSegment'&&/Storagatan/.test(o.name||'')).flatMap(o=>geom.get(o.geometryPeriods.at(-1).geometryId).paths.flat()).map(([x,y])=>[X(x),Y(y)]);
// densify road
const segs=[];for(const o of catalog.objects.filter(o=>o.kind==='roadSegment'&&/Storagatan/.test(o.name||'')))for(const p of geom.get(o.geometryPeriods.at(-1).geometryId).paths)for(let i=1;i<p.length;i++)segs.push([[X(p[i-1][0]),Y(p[i-1][1])],[X(p[i][0]),Y(p[i][1])]]);
const dseg=(p,[a,b])=>{const dx=b[0]-a[0],dy=b[1]-a[1],l=dx*dx+dy*dy;let t=l?((p[0]-a[0])*dx+(p[1]-a[1])*dy)/l:0;t=Math.max(0,Math.min(1,t));return Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)};
const near=r=>r.some(p=>segs.some(s=>dseg(p,s)<60));
const area=r=>Math.abs(r.reduce((a,p,i)=>{const q=r[(i+1)%r.length];return a+p[0]*q[1]-q[0]*p[1]},0))/2;
// polygon clipping (Sutherland–Hodgman works for convex clip; use sampling instead)
const inside=(p,r)=>{let c=false;for(let i=0,j=r.length-1;i<r.length;j=i++){const [xi,yi]=r[i],[xj,yj]=r[j];if((yi>p[1])!==(yj>p[1])&&p[0]<(xj-xi)*(p[1]-yi)/(yj-yi)+xi)c=!c}return c};
const bb=r=>[Math.min(...r.map(p=>p[0])),Math.min(...r.map(p=>p[1])),Math.max(...r.map(p=>p[0])),Math.max(...r.map(p=>p[1]))];
const overlap=(a,b)=>{const A=bb(a),B=bb(b);const x0=Math.max(A[0],B[0]),y0=Math.max(A[1],B[1]),x1=Math.min(A[2],B[2]),y1=Math.min(A[3],B[3]);if(x0>=x1||y0>=y1)return 0;let n=0;const s=0.5;for(let x=x0+s/2;x<x1;x+=s)for(let y=y0+s/2;y<y1;y+=s)if(inside([x,y],a)&&inside([x,y],b))n++;return n*s*s};
const cands=catalog.objects.filter(o=>['building','buildingGroup'].includes(o.kind));
const years=[1900,1920,1940,1950,1960,1968,1975,1983,1985,1990,1995,2000,2010,2014,2018,2021,2026];
const pairs=new Map();
for(const y of years){const shown=[];
 for(const o of cands){let r;try{r=model.resolveObject(o.id,y)}catch(e){continue}
  if(!r||!r.geometry||!['standing','occupied','underConstruction','ruin'].includes(r.state))continue;
  const ring=r.geometry.paths[0].map(([x,yy])=>[X(x),Y(yy)]);if(ring.length<4||!near(ring))continue;shown.push([o,ring])}
 for(let i=0;i<shown.length;i++)for(let j=i+1;j<shown.length;j++){const [a,ra]=shown[i],[b,rb]=shown[j];const ov=overlap(ra,rb);if(ov<4)continue;
  const frac=ov/Math.min(area(ra),area(rb));if(frac<0.15)continue;const k=[a.id,b.id].sort().join(' | ');
  const e=pairs.get(k)||{years:[],frac:0,ov:0};e.years.push(y);e.frac=Math.max(e.frac,frac);e.ov=Math.max(e.ov,ov);pairs.set(k,e)}}
const tag=id=>{const o=model.objects.get(id);return ['printedMapSymbol','symbolMap1968','buildingMapReview','historicalReview','neighborhoodReviews','externalModern','replacementReview','aerialReview'].filter(k=>o[k]).join(',')||'-'};
const out=[...pairs].map(([k,e])=>({pair:k,years:e.years,overlapM2:Math.round(e.ov),fraction:+e.frac.toFixed(2),tags:k.split(' | ').map(tag),names:k.split(' | ').map(id=>model.objects.get(id).name)}));
out.sort((a,b)=>a.years[0]-b.years[0]);fs.writeFileSync(process.argv[2],JSON.stringify(out,null,1));
console.log(out.length,'overlapping pairs');for(const p of out)console.log(p.years[0]+'–'+p.years.at(-1),p.overlapM2+'m²',p.fraction,p.pair,p.tags.join(' / '));
