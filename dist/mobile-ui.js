/* One map workspace on every screen: menu dialog and nonmodal story card. */
(()=>{
 const $=s=>document.querySelector(s),menu=$('#explorePanel'),popup=$('#storyPopup'),open=$('#openExplore'),reopen=$('#reopenStory');
 let lastEra=null,lastYear=null;
 function closeMenu(){if(menu.open)menu.close();open.setAttribute('aria-expanded','false')}
 function hideStory(restoreFocus=false){
  const inside=popup.contains(document.activeElement);popup.hidden=true;reopen.setAttribute('aria-expanded','false');
  if(restoreFocus&&inside)reopen.focus({preventScroll:true});
 }
 function refreshStory(){
  const story=$('#story'),heading=story.querySelector('h2'),more=story.querySelector('details');
  if(heading){heading.id='storyHeading';popup.setAttribute('aria-labelledby','storyHeading')}
  if(more)for(const extra of story.querySelectorAll(':scope > .question, :scope > .wikipedia-link'))more.append(extra);
 }
 function showStory(focus=false){
  refreshStory();
  closeMenu();popup.hidden=false;reopen.setAttribute('aria-expanded','true');popup.scrollTop=0;
  if(focus)$('#closeStory').focus({preventScroll:true});
 }
 function timeChanged(state){
  $('#storyDate').textContent=state.date;$('#stopTitle').textContent=state.title;
  const newStop=state.era!==lastEra||(state.atStop&&state.year!==lastYear);
  lastEra=state.era;lastYear=state.year;
  if(state.playing)hideStory();else if(newStop)showStory();
 }
 open.onclick=()=>{pause();hideStory();menu.showModal();open.setAttribute('aria-expanded','true');$('#closeExplore').focus({preventScroll:true})};
 $('#closeExplore').onclick=closeMenu;
 menu.addEventListener('close',()=>{open.setAttribute('aria-expanded','false');if(document.activeElement===document.body||menu.contains(document.activeElement))open.focus({preventScroll:true})});
 menu.addEventListener('click',e=>{if(e.target===menu){const b=menu.getBoundingClientRect();if(e.clientX<b.left||e.clientX>b.right||e.clientY<b.top||e.clientY>b.bottom)closeMenu()}});
 $('#closeStory').onclick=()=>hideStory(true);reopen.onclick=()=>{pause();showStory(true)};
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!document.querySelector('dialog[open]')&&!popup.hidden){hideStory(true);e.preventDefault()}});
 // Close the menu before opening an archive/source dialog or visiting a place.
 for(const id of ['openArchive','about'])$('#'+id).addEventListener('click',closeMenu,{capture:true});
 for(const id of ['archive','info'])$('#'+id).addEventListener('close',()=>{if(popup.hidden)open.focus({preventScroll:true})});
 for(const id of ['focusMariehamn','focusStone','focusPostal','focusFortress','zoomIn','zoomOut','reset'])$('#'+id).addEventListener('click',()=>{closeMenu();if(['zoomIn','zoomOut','reset'].includes(id))hideStory()});
 $('#modernPlace').addEventListener('change',closeMenu);
 $('#jumpYear').addEventListener('change',()=>{closeMenu();showStory()});
 $('#jumpYear').addEventListener('keydown',e=>{if(e.key==='Enter'){closeMenu();showStory()}});
 $('#mapBackground').addEventListener('change',()=>{closeMenu();hideStory()});
 $('#time').addEventListener('change',()=>{if(!playing)showStory()});
 window.MapUI={showStory,refreshStory,showMap:()=>{closeMenu();hideStory()},timeChanged,playbackStarted:()=>{closeMenu();hideStory()},playbackStopped:()=>showStory()};
 // app.js renders the initial story before this controller loads.
 timeChanged({era,year,date:date(year),title:eras[era].title,atStop:true,playing});
})();
