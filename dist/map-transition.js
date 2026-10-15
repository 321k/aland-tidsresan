'use strict';
// A compositor-only fade between years. Map geometry and hit targets stay exact.
// Mouse movement, camera changes and asynchronous data loads never start a fade.
class MapTransition {
 constructor(canvas,overlay){this.canvas=canvas;this.overlay=overlay;this.buffer=document.createElement('canvas');this.motion=window.matchMedia('(prefers-reduced-motion: reduce)');this.motion.addEventListener('change',()=>this.cancel())}
 capture(enabled){
  if(!enabled||this.motion.matches||!this.canvas.width||!this.canvas.height){this.cancel();return false}
  const c=this.canvas,b=this.buffer,o=this.overlay;b.width=c.width;b.height=c.height;
  const ctx=b.getContext('2d');ctx.drawImage(c,0,0);
  // Rapid scrubbing starts from the visible blend, not an older target frame.
  if(this.animation&&!o.hidden){ctx.globalAlpha=Number(getComputedStyle(o).opacity);ctx.drawImage(o,0,0);ctx.globalAlpha=1}
  this.cancel();o.width=c.width;o.height=c.height;o.getContext('2d').drawImage(b,0,0);o.hidden=false;return true;
 }
 play(){if(this.overlay.hidden)return;const animation=this.overlay.animate([{opacity:1},{opacity:0}],{duration:240,easing:'ease-out',fill:'forwards'});this.animation=animation;animation.finished.then(()=>{if(this.animation===animation)this.cancel()}).catch(()=>{})}
 cancel(){this.animation?.cancel();this.animation=null;this.overlay.hidden=true}
}
