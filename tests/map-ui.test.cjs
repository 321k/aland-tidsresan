const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
function workspace(){
 const elements=new Map(),keys={};let document;
 class Element{
  constructor(id){this.id=id;this.hidden=id==='storyPopup';this.open=false;this.attrs={};this.listeners={}}
  setAttribute(k,v){this.attrs[k]=v}
  addEventListener(k,fn){(this.listeners[k]??=[]).push(fn)}
  emit(k,event={}){for(const fn of this.listeners[k]||[])fn(event)}
  contains(el){return el===this||el?.parent===this}
  focus(){document.activeElement=this}
  showModal(){this.open=true}
  close(){this.open=false;this.emit('close')}
  querySelector(){return null}
  querySelectorAll(){return []}
 }
 const el=id=>{if(!elements.has(id))elements.set(id,new Element(id));return elements.get(id)};
 document={body:el('body'),activeElement:el('body'),querySelector:selector=>selector==='dialog[open]'?[...elements.values()].find(e=>e.open):el(selector.slice(1)),addEventListener:(type,fn)=>keys[type]=fn};
 el('closeStory').parent=el('storyPopup');el('closeExplore').parent=el('explorePanel');
 const box={window:{},document,era:0,year:-8000,eras:[{title:'De första öarna'}],date:y=>String(y),playing:false};
 box.pause=()=>{box.playing=false};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/mobile-ui.js','utf8'),box);
 return{ui:box.window.MapUI,el,keys,document,box};
}
test('story can be dismissed without reopening on every time update in the same stop',()=>{
 const {ui,el,keys,document}=workspace();assert.equal(el('storyPopup').hidden,false);
 el('closeStory').focus();el('closeStory').onclick();assert.equal(el('storyPopup').hidden,true);assert.equal(document.activeElement.id,'reopenStory');
 ui.timeChanged({era:0,year:-8000,date:'8000 f.Kr.',title:'Öar',atStop:true,playing:false});assert.equal(el('storyPopup').hidden,true);
 ui.timeChanged({era:1,year:-4000,date:'4000 f.Kr.',title:'Boplatser',atStop:true,playing:false});assert.equal(el('storyPopup').hidden,false);
 keys.keydown({key:'Escape',preventDefault(){}});assert.equal(el('storyPopup').hidden,true);
 el('reopenStory').onclick();assert.equal(el('storyPopup').hidden,false);
});
test('playback hides the popup until playback stops, including after continuous mode',()=>{
 const {ui,el}=workspace();ui.playbackStarted();assert.equal(el('storyPopup').hidden,true);
 ui.timeChanged({era:1,year:-4000,date:'4000 f.Kr.',title:'Boplatser',atStop:true,playing:true});assert.equal(el('storyPopup').hidden,true);
 ui.playbackStopped();assert.equal(el('storyPopup').hidden,false);assert.equal(el('storyDate').textContent,'4000 f.Kr.');
});
test('menu and popup never compete; opening archive closes menu first',()=>{
 const {ui,el}=workspace();el('openExplore').onclick();assert.equal(el('explorePanel').open,true);assert.equal(el('storyPopup').hidden,true);
 assert.equal(el('openExplore').attrs['aria-expanded'],'true');
 el('openArchive').emit('click');assert.equal(el('explorePanel').open,false);assert.equal(el('openExplore').attrs['aria-expanded'],'false');
 el('openExplore').onclick();ui.showStory(true);assert.equal(el('explorePanel').open,false);assert.equal(el('storyPopup').hidden,false);
});
test('secondary controls are retained in one menu and story lives over the map',()=>{
 const html=fs.readFileSync('dist/index.html','utf8'),menu=html.slice(html.indexOf('<dialog id="explorePanel"'),html.indexOf('</dialog>',html.indexOf('<dialog id="explorePanel"'))),main=html.slice(html.indexOf('<main>'),html.indexOf('</main>'));
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length);
 for(const id of ['openArchive','about','jumpYear','autostop','mapBackground','layerModern','placeSearch','routeChoice','roadYear','mapLegend','detailStatus','zoomIn','reset'])assert.ok(menu.includes(`id="${id}"`),id);
 assert.ok(main.includes('id="storyPopup"'));assert.ok(main.includes('id="story"'));assert.ok(!main.includes('id="explorePanel"'));assert.ok(!html.includes('<aside'));
});
test('changing time clears a selected place and opens the stop story instead',()=>{
 const source=fs.readFileSync('dist/app.js','utf8'),notified=[],s={selected:'jomala',selectedFeature:{id:'a-road'},explorer:{selected:'jomala'},MAX_TIME:100,LAST:1,pos:0,era:0,year:1280,playing:false,eras:[{y:1280,title:'Kyrkor'},{y:1388,title:'Slott'}],window:{MapUI:{timeChanged:x=>notified.push(x)}},$:()=>({setAttribute(){}}),date:y=>String(y),updateUI(){assert.equal(s.selected,null);assert.equal(s.selectedFeature,null)},draw(){}};
 vm.createContext(s);vm.runInContext(source.slice(source.indexOf('function yearAtPosition('),source.indexOf('function project(')),s);
 s.setTime(100);assert.equal(s.explorer.selected,null);assert.equal(notified[0].title,'Slott');assert.equal(notified[0].atStop,true);
});
