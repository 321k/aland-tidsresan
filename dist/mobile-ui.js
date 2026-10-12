/* Keep the map and time controls in view on phones; reuse the desktop content. */
(()=>{
 const media=matchMedia('(max-width:800px), (max-width:950px) and (max-height:500px)'),panel=document.querySelector('#explorePanel'),content=panel.querySelector('.panel-content'),open=document.querySelector('#openExplore'),close=document.querySelector('#closeExplore'),legend=document.querySelector('#toggleLegend');
 function setOpen(value,target){
  if(!media.matches)return;
  document.body.classList.toggle('explore-open',value);panel.inert=!value;open.setAttribute('aria-expanded',String(value));
  if(value){
   if(typeof pause==='function')pause();
   content.scrollTop=target==='story'?document.querySelector('#story').offsetTop-16:0;
   close.focus({preventScroll:true});
  }else open.focus({preventScroll:true});
 }
 function sync(){
  const active=document.activeElement;
  document.body.classList.remove('explore-open','mobile-legend-open');
  panel.inert=media.matches;open.setAttribute('aria-expanded','false');legend.setAttribute('aria-expanded','false');
  if(media.matches&&panel.contains(active))open.focus({preventScroll:true});
  else if(!media.matches&&active?.closest('.mobile-map-actions,.mobile-panel-head'))document.querySelector('#map').focus({preventScroll:true});
 }
 open.onclick=()=>setOpen(true,'explore');close.onclick=()=>setOpen(false);
 document.querySelector('#panelStory').onclick=()=>{content.scrollTop=document.querySelector('#story').offsetTop-16};
 document.querySelector('#panelExplore').onclick=()=>{content.scrollTop=0};
 legend.onclick=()=>{const visible=document.body.classList.toggle('mobile-legend-open');legend.setAttribute('aria-expanded',String(visible))};
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!document.querySelector('dialog[open]')&&document.body.classList.contains('explore-open')){setOpen(false);e.preventDefault()}});
 // Starting playback returns to the map, where changes can be watched.
 document.querySelector('#play').addEventListener('click',()=>{if(media.matches&&document.body.classList.contains('explore-open'))setOpen(false)});
 window.MobileMapUI={isMobile:()=>media.matches,showStory:()=>setOpen(true,'story'),showMap:()=>setOpen(false)};
 media.addEventListener('change',sync);sync();
})();
