const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const review=read('data/plan-north-street.json'),catalog=read('dist/assets/temporal-objects.json.gz');
const stage=id=>catalog.cityStages.find(s=>s.id===id),key=f=>f.id.split(':').slice(1).join(':');
// Local metres around Mariehamn; accurate to well under a metre over a kilometre.
const M=([x,y])=>[x*55600,y*111320];
const segDist=(p,a,b)=>{const[dx,dy]=[b[0]-a[0],b[1]-a[1]],t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy||1)));return Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)};
const lineDist=(p,path)=>Math.min(...path.slice(1).map((q,i)=>segDist(M(p),M(path[i]),M(q))));

test('the review is registered as a source and the step applies only to its three stages',()=>{
 assert.ok(catalog.sources.some(s=>s.id===review.source.id));
 assert.equal(fs.readFileSync('dist/assets/plan-north-street.json','utf8'),fs.readFileSync('data/plan-north-street.json','utf8'));
 assert.deepEqual(review.stages,['city-reconstruction-1860','city-reconstruction-1861','city-reconstruction-1871']);
 for(const s of catalog.cityStages.filter(s=>!review.stages.includes(s.id)))
  assert.ok(!s.features.some(f=>f.alignment?.reviewId===review.source.id),s.id);
});

for(const id of review.stages)test(`${id}: Norra planerade tvärgatan runs 47 m north of and parallel to Norragatan`,()=>{
 const s=stage(id),F=new Map(s.features.map(f=>[key(f),f])),street=F.get(review.featureId);
 assert.equal(street.paths[0].length,2,'one straight segment');assert.equal(street.traceId,review.traceId);
 assert.ok(street.sourcePaths[0].length>2,'the original trace is kept');assert.equal(street.alignment.reviewId,review.source.id);
 const ng=s.features.filter(f=>f.kind==='street'&&(f.name||'').includes('Norragatan')).flatMap(f=>f.paths);
 const [a,b]=street.paths[0].map(M),len=Math.hypot(b[0]-a[0],b[1]-a[1]);assert.ok(len>950&&len<1050,`${len}`);
 // Every Norragatan vertex lies 45–49 m south of the street (the reconstruction itself wanders ±1.6 m about a straight line).
 for(const p of ng.flat()){const d=lineDist(p,street.paths[0]);assert.ok(d>45&&d<49,`${p} ${d}`);
  const c=(b[0]-a[0])*(M(p)[1]-a[1])-(b[1]-a[1])*(M(p)[0]-a[0]);assert.ok(c*(b[0]>a[0]?1:-1)<0,'Norragatan is south of it')}
 for(const x of review.attached){const f=F.get(x.featureId),p=f.paths[0];
  assert.ok(Math.min(lineDist(p[0],street.paths[0]),lineDist(p.at(-1),street.paths[0]))<0.05,x.featureId);
  assert.deepEqual(f.paths[0].length,f.sourcePaths[0].length,x.featureId);assert.equal(f.alignment.reviewId,review.source.id)}
 const strand=s.features.find(f=>f.objectId===review.eastEndObjectId);
 assert.ok(lineDist(street.paths[0].at(-1),strand.paths[0])<0.05||lineDist(street.paths[0][0],strand.paths[0])<0.05,'ends on Strandgatan');
 const block=F.get(review.block.featureId);assert.equal(block.alignment.reviewId,review.source.id);assert.ok(block.sourcePaths);
 const ring=block.paths[0].map(M),area=Math.abs(ring.reduce((s,p,i)=>s+p[0]*ring[(i+1)%ring.length][1]-ring[(i+1)%ring.length][0]*p[1],0))/2;
 assert.ok(area>review.block.minArea&&area<review.block.maxArea,`${area}`);
});
