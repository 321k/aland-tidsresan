const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),zlib=require('node:zlib');
const source=fs.readFileSync('dist/app.js','utf8'),data=JSON.parse(zlib.gunzipSync(fs.readFileSync('dist/assets/modern.json.gz')));
const box={};vm.createContext(box);vm.runInContext(source.slice(source.indexOf('const buildings=['),source.indexOf('eras.push('))+';this.stories=buildings;',box);
const modernById=new Map(data.features.map(f=>[f.id,f]));
function modeContext(){const s={explorer:{modernById,flags:{modern:true},prepared:true,modernVisible:(f,mpp)=>mpp<18},meta:{world:262144},fit:1,zoom:28,year:2026};vm.createContext(s);vm.runInContext(source.slice(source.indexOf('function storyMarkerMode('),source.indexOf('function drawStoryPlaces(')),s);return s;}
test('linked stories use existing mapped buildings and an anchor inside their footprint',()=>{
 const inside=(p,ring)=>{let result=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])result=!result}return result};
 for(const id of ['library','kastelholm','vita']){const story=box.stories.find(b=>b.id===id),f=modernById.get(story.osmId);assert.ok(f,id);assert.equal(f.name,story.name);assert.ok(f.paths.reduce((insidePolygon,ring)=>inside([story.lon,story.lat],ring)?!insidePolygon:insidePolygon,false),id+' must lie within its mapped building');}
 assert.ok(!box.stories.some(b=>b.id==='townhall'),'the superseded town hall definition must not return');
});
test('modern footprints replace legacy markers without showing modern geometry in the past',()=>{
 const s=modeContext(),library=box.stories.find(b=>b.id==='library');
 assert.equal(s.storyMarkerMode(library),'footprint');s.year=1989;assert.equal(s.storyMarkerMode(library),'point');s.year=2026;s.explorer.flags.modern=false;assert.equal(s.storyMarkerMode(library),'point');s.explorer.flags.modern=true;s.explorer.prepared=false;assert.equal(s.storyMarkerMode(library),'point');s.explorer.prepared=true;s.zoom=.5;assert.equal(s.storyMarkerMode(library),'point');
 assert.equal(s.storyMarkerMode({id:'unlinked'}),'point');assert.equal(s.storyMarkerMode({recon:true}),'reconstruction');
});
test('the replaced library symbol has no invisible legacy click target',()=>{
 const s=modeContext(),library=box.stories.find(b=>b.id==='library');Object.assign(s,{visible:()=>[library],hits:[],W:100,H:100,screen:()=>[50,50],selected:null,ctx:new Proxy({},{get:()=>()=>{},set:()=>true}),iconFor:()=>{throw Error('Real buildings must not draw illustrations')}});
 vm.runInContext(source.slice(source.indexOf('function drawStoryPlaces('),source.indexOf('function sourceLink(')),s);
 s.drawStoryPlaces();assert.equal(s.hits.length,0);s.year=1989;s.drawStoryPlaces();assert.equal(s.hits.length,1);assert.equal(s.hits[0].size,12);
});
test('clicking a linked footprint opens its historical story',()=>{
 const library=box.stories.find(b=>b.id==='library'),calls=[],s={visible:()=>[library],selectBuilding:(...args)=>calls.push(args)};vm.createContext(s);vm.runInContext(source.slice(source.indexOf('function selectFeature('),source.indexOf("$('#time').max=")),s);s.selectFeature(modernById.get(library.osmId),false);assert.deepEqual(calls,[['library',false]]);
});
