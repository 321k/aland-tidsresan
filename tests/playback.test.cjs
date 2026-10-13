const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
function shore(){
 const requests=new Map(),changes=[],ctx={URL,console,Promise,readCompressedJSON:r=>r.json(),fetch:url=>new Promise((resolve,reject)=>requests.set(url,{resolve,reject}))};vm.createContext(ctx);
 vm.runInContext(fs.readFileSync('dist/timeline-model.js','utf8')+fs.readFileSync('dist/shorelines.js','utf8')+';this.Model=ShorelineModel',ctx);
 const status={textContent:''},model=new ctx.Model(()=>changes.push(model.target),status);model.manifest={years:[-4000,-3000,-2000,-1000,0,1000,1900]};model.paths=x=>x;
 return {model,status,requests,changes,finish:async(year)=>{requests.get(`assets/shorelines/${year}.json.gz`).resolve({json:async()=>({land:year})});await model.pending.get(year)}};
}
const view={year:-4000,width:500,height:500,scale:1,panX:0,panY:0,meta:{width:500,height:500}};
test('slow shoreline loading preserves the visible land and honestly labels its year',async()=>{
 const {model,status,finish}=shore(),filled=[],canvas=new Proxy({fill:p=>filled.push(p)},{get:(o,k)=>o[k]||(()=>{}),set:()=>true});
 model.cache.set(-4000,{land:-4000});model.draw(canvas,view);model.draw(canvas,{...view,year:-3000});
 assert.deepEqual(filled.filter(Number.isFinite),[-4000,-4000]);assert.match(status.textContent,/Visar tills vidare modell/);
 await finish(-3000);model.draw(canvas,{...view,year:-3000});assert.equal(filled.filter(Number.isFinite).at(-1),-3000);assert.doesNotMatch(status.textContent,/tills vidare/);
});
test('playback prefetches ahead, deduplicates downloads and only advances when ready',async()=>{
 const {model,requests,finish}=shore();assert.equal(model.prepare(-4000),false);model.prepare(-4000);assert.equal(requests.size,3);
 await finish(-4000);assert.equal(model.prepare(-4000),true);assert.equal(model.prepare(-3000),false);
 await finish(-3000);assert.equal(model.prepare(-3000),true);
});
test('out-of-order responses never replace the requested shoreline',async()=>{
 const {model,finish,changes}=shore();model.update(-4000);model.update(-3000);await finish(-3000);model.update(-3000);await finish(-4000);
 assert.equal(model.displayed.year,-3000);assert.deepEqual(changes,[-3000]);
});
test('failed loads retain the previous coast and do not trap playback forever',async()=>{
 const {model,requests,status}=shore();model.cache.set(-4000,{land:-4000});model.update(-4000);model.update(-3000);
 requests.get('assets/shorelines/-3000.json.gz').reject(Error('offline'));await model.pending.get(-3000);model.update(-3000);
 assert.equal(model.displayed.year,-4000);assert.match(status.textContent,/kunde inte laddas/);assert.equal(model.prepare(-3000),true);
});
test('returning to the ice age clears the later shoreline fallback',()=>{
 const {model}=shore();model.cache.set(-4000,{land:-4000});model.update(-4000);model.update(-12000);assert.equal(model.displayed,null);
});
function playback(){
 const elements=new Map(),s={window:{},playing:true,pos:0,year:-4000,LAST:1,MAX_TIME:100,lastTick:0,eras:[{y:-4000},{y:-3000}],timer:null,ready:false,frames:[],updates:[],shorelines:{prepare:()=>s.ready},$:id=>{if(!elements.has(id))elements.set(id,{checked:false,setAttribute(){}});return elements.get(id)},requestAnimationFrame:f=>{s.frames.push(f);return s.frames.length},cancelAnimationFrame(){},setTime:p=>{s.pos=p;s.year=s.yearAtPosition(p);s.updates.push(p)}};
 vm.createContext(s);const source=fs.readFileSync('dist/app.js','utf8');vm.runInContext(source.slice(source.indexOf('function yearAtPosition('),source.indexOf('function setTime('))+source.slice(source.indexOf('function pause()'),source.indexOf("$('#play').onclick=")),s);return s;
}
test('buffering freezes time and resumes without catching up or skipping a stop',()=>{
 const s=playback();s.playbackFrame(100);s.playbackFrame(5000);assert.equal(s.pos,0);assert.equal(s.updates.length,0);
 s.ready=true;s.playbackFrame(5100);assert.ok(s.pos>0&&s.pos<2);
 s.pos=99;s.$('#autostop').checked=true;s.playbackFrame(5200);assert.equal(s.pos,100);assert.equal(s.playing,false);
});
test('pausing during buffering prevents a queued frame from advancing',()=>{
 const s=playback();s.playbackFrame(100);s.pause();s.ready=true;s.playbackFrame(200);assert.equal(s.pos,0);assert.equal(s.updates.length,0);
});

test('coverage gaps leave the sea background visible by default at historical and modern years',()=>{
 const {model}=shore(),filled=[],backgrounds=[];
 const canvas=new Proxy({fill:p=>filled.push(p),fillRect:()=>backgrounds.push(canvas.fillStyle)},{get:(o,k)=>o[k]??(()=>{})});
 for(const year of [-4000,1900,2025,2026]){
  filled.length=0;const sourceYear=year>=1900?1900:year;
  model.cache.set(sourceYear,{land:'islands',ice:'ice',noData:'coverage gaps'});
  model.draw(canvas,{...view,year});
  assert.deepEqual(filled,['islands','ice']);
  assert.equal(backgrounds.at(-1),'#b8d7da');
 }
});
test('coverage gaps remain available as an optional inspection layer',()=>{
 const {model}=shore(),filled=[];
 const canvas=new Proxy({fill:p=>filled.push(p)},{get:(o,k)=>o[k]??(()=>{})});
 model.cache.set(-4000,{land:'islands',ice:'ice',noData:'coverage gaps'});
 model.showCoverageGaps=true;model.draw(canvas,view);
 assert.deepEqual(filled,['islands','ice','coverage gaps']);
 filled.length=0;model.showCoverageGaps=false;model.draw(canvas,view);
 assert.deepEqual(filled,['islands','ice']);
});
