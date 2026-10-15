const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
function setup(){
 const calls=[],ctx={drawImage:(...args)=>calls.push(args),globalAlpha:1},canvas={width:800,height:600,getContext:()=>ctx};
 const animations=[],overlay={...canvas,hidden:true,animate(frames,options){let finish;const a={frames,options,cancelled:false,cancel(){this.cancelled=true},finished:new Promise(resolve=>finish=resolve),finish:()=>finish()};animations.push(a);return a}};
 const motion={matches:false,addEventListener(type,fn){this.change=fn}},box={document:{createElement:()=>({...canvas})},window:{matchMedia:()=>motion},getComputedStyle:()=>({opacity:'.5'})};
 vm.createContext(box);vm.runInContext(fs.readFileSync('dist/map-transition.js','utf8')+';this.Transition=MapTransition',box);
 return {transition:new box.Transition(canvas,overlay),overlay,animations,motion,calls};
}
test('year fade finishes cleanly and never draws the live map on animation frames',async()=>{
 const{transition,overlay,animations,calls}=setup();assert.equal(transition.capture(true),true);transition.play();assert.equal(overlay.hidden,false);assert.equal(animations[0].options.duration,240);assert.equal(calls.length,2);
 animations[0].finish();await Promise.resolve();assert.equal(overlay.hidden,true);assert.equal(calls.length,2);
});
test('rapid scrubbing captures the visible blend and stale completion cannot hide the new fade',async()=>{
 const{transition,overlay,animations,calls}=setup();transition.capture(true);transition.play();transition.capture(true);transition.play();
 assert.equal(animations[0].cancelled,true);assert.equal(calls.length,5);animations[0].finish();await Promise.resolve();assert.equal(overlay.hidden,false);
 transition.cancel();assert.equal(overlay.hidden,true);assert.equal(animations[1].cancelled,true);
});
test('reduced motion and camera redraws have no transition overlay',()=>{
 const{transition,overlay,motion,animations}=setup();motion.matches=true;assert.equal(transition.capture(true),false);transition.play();assert.equal(animations.length,0);
 motion.matches=false;transition.capture(true);transition.play();motion.matches=true;motion.change();assert.equal(overlay.hidden,true);
 assert.equal(transition.capture(false),false);
});
