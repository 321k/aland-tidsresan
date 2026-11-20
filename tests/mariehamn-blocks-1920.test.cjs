const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),zlib=require('node:zlib');
const read=p=>JSON.parse(p.endsWith('.gz')?zlib.gunzipSync(fs.readFileSync(p)):fs.readFileSync(p));
const catalog=read('dist/assets/temporal-objects.json.gz'),review=read('data/mariehamn-blocks-1920.json');
const stage=id=>catalog.cityStages.find(s=>s.id===id);
const area=ring=>Math.abs(ring.reduce((s,p,i)=>{const q=ring[(i+1)%ring.length];return s+(p[0]*55600)*(q[1]*111320)-(q[0]*55600)*(p[1]*111320)},0))/2;
const fill=f=>area(f.paths[0])-f.paths.slice(1).reduce((s,r)=>s+area(r),0);
const inside=(p,ring)=>{let c=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const [xi,yi]=ring[i],[xj,yj]=ring[j];if((yi>p[1])!==(yj>p[1])&&p[0]<(xj-xi)*(p[1]-yi)/(yj-yi)+xi)c=!c}return c};

test('blocks drawn in 1871 and 1942 stay block fill through the 1920s stages',()=>{
 assert.deepEqual(review.stageIds,['city-reconstruction-1920','city-reconstruction-1927']);
 for(const id of review.stageIds){
  const s=stage(id),carried=s.features.filter(f=>f.carriedBlock);
  assert.equal(carried.length,s.counts.carriedBlocks);assert.ok(carried.length>=10,id);
  for(const f of carried){assert.equal(f.kind,'block');assert.equal(f.objectId,undefined);assert.equal(f.carriedBlock,'city-reconstruction-1871');assert.ok(fill(f)>=review.minPieceSquareMeters-1,f.id)}
  const total=carried.reduce((n,f)=>n+fill(f),0),want=review.expectedSquareMeters[id];
  assert.ok(Math.abs(total-want)<0.1*want,`${id} ${Math.round(total)} m²`);
  // The linked example: the block between Ålandsvägen and Mariegatan has fill again in the 1920s.
  const centre=[19.9416,60.0959];assert.ok(s.features.some(f=>f.kind==='block'&&inside(centre,f.paths[0])),id+' block 13');
 }
 for(const st of catalog.cityStages.filter(st=>st.from<1920||st.from>1941))assert.ok(!st.features.some(f=>f.carriedBlock),st.id);
});

test('carried pieces never cover a block, park or square of the same stage',()=>{
 for(const id of review.stageIds){
  const s=stage(id),own=s.features.filter(f=>['block','park','square'].includes(f.kind)&&!f.carriedBlock);
  for(const f of s.features.filter(f=>f.carriedBlock))for(const p of f.paths[0])assert.ok(!own.some(b=>inside(p,b.paths[0])),`${f.id} vertex inside ${id}`);
 }
});
