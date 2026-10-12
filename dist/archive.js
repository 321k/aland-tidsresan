'use strict';
window.POSTAL_ROUTE=[
 {name:'Eckerö',lon:19.54361,lat:60.22017},{name:'Marsund',lon:19.67,lat:60.23},
 {name:'Boda',lon:19.8,lat:60.19},{name:'Färjsundet',lon:20.01326,lat:60.23909},
 {name:'Kastelholm',lon:20.08056,lat:60.23306},{name:'Bomarsund',lon:20.242,lat:60.212},
 {name:'Vårdö',lon:20.36667,lat:60.23333},{name:'Kumlinge',lon:20.78333,lat:60.26667}
];
(()=>{
 const dialog=document.querySelector('#archive'),content=document.querySelector('#archiveContent');
 const photos=[[1942,'25 juli'],[1952,'11 juli'],[1962,'5 juni'],[1975,'9 maj'],[1982,'12 maj'],[1991,'6 maj'],[1999,'10 juni'],[2007,'4 juni'],[2015,'20 maj'],[2021,'6 juni']];
 function url(year,embed=true){return `https://karta.mariehamn.ax/IMS/${embed?'sv/embed':''}?layers=${year===2021?'Flygfoto%202021':'Baskarta'}&lon=Flygfoto%20${year}&cp=6664855,20496370&z=2${embed?'&ui=z!o!b':''}`}
 function photo(year){const date=photos.find(p=>p[0]===year)[1];return `<section class="photo"><h3>${year} <small>${date}</small></h3><iframe title="Mariehamns stads flygfoto ${year}" src="${url(year)}" loading="eager" allowfullscreen></iframe><a href="${url(year,false)}" target="_blank" rel="noopener noreferrer">Öppna ${year} i stadens karta ↗</a></section>`}
 function render(tab){document.querySelectorAll('[data-archive]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.archive===tab)));
  if(tab==='compare'){content.innerHTML=`<p class="archiveintro">Samma startområde, två ögonblick i tiden. Flytta och zooma i varje bild för sig. Utanför 1942-bildens täckning syns stadens nutida baskarta. Leta efter hus, gator och förändrade stränder.</p><div class="photocompare">${photo(1942)}${photo(2021)}</div><p class="archivecredit">© Mariehamns stad · officiella kartvyer. Om bilderna inte visas, använd länkarna till stadens karta.</p>`;return}
  if(tab==='photo'){content.innerHTML=`<div class="photochooser"><label for="photoYear">Välj flygfoto</label><select id="photoYear">${photos.map(([y])=>`<option value="${y}">${y}</option>`).join('')}</select><span>Tio årgångar ur stadens bildarkiv</span></div><div id="singlePhoto">${photo(1942)}</div><p class="archivecredit">© Mariehamns stad · officiell kartvy. Flygfotot visar den valda fotograferingsdagen.</p>`;document.querySelector('#photoYear').onchange=e=>document.querySelector('#singlePhoto').innerHTML=photo(Number(e.target.value));return}
  const postal=tab==='postal';
  const src=postal?'assets/postvag-1700.webp':'assets/aland-1894.jpg',title=postal?'Postvägen över Åland · 1700-talet':'Karta över Åland · 1894';
  content.innerHTML=`<div class="scanheading"><h3>${title}</h3><label>Förstora <input id="scanZoom" type="range" min="100" max="400" step="25" value="100" aria-label="Förstora historisk karta"><output id="scanPercent">100 %</output></label></div><p class="archiveintro">${postal?'Följ postförarnas väg på C. J. Carlssons karta. På vår tidskarta visas en förenklad del av förbindelsen mellan Eckerö och Kumlinge. Originalet visar en längre sträcka och fler hållpunkter.':'Leta efter välbekanta namn och jämför hur öarna avbildades 1894.'} Förstora bilden och rulla åt sidorna för att läsa detaljer. Originalet är inte inpassat i vår moderna karta.</p><div class="scanviewport" tabindex="0" aria-label="Historisk karta, rulla för att utforska"><img id="archiveScan" src="${src}" alt="${title}"></div><p class="archivecredit">${postal?'C. J. Carlsson / Postmuseum, POST.044851 · DigitaltMuseum · Public Domain / CC0. Katalogen anger 1700-talet, med osäkerhet om närmare datering. <a href="https://digitaltmuseum.se/011024626117/karta" target="_blank" rel="noreferrer">Se originalets uppgifter ↗</a>':'British Library / Wikimedia Commons · Finland in the Nineteenth Century (1894) · Public Domain. <a href="https://commons.wikimedia.org/wiki/File:(1894)_MAP_OF_THE_%C3%85LAND_ISLANDS.jpg" target="_blank" rel="noreferrer">Se originalets uppgifter ↗</a>'}</p>`;
  document.querySelector('#scanZoom').oninput=e=>{document.querySelector('#archiveScan').style.width=e.target.value+'%';document.querySelector('#scanPercent').value=e.target.value+' %'};
 }
 document.querySelector('#openArchive').onclick=()=>{if(typeof pause==='function')pause();render('compare');dialog.showModal()};
 document.querySelector('#closeArchive').onclick=()=>dialog.close();
 document.querySelectorAll('[data-archive]').forEach(b=>b.onclick=()=>render(b.dataset.archive));
})();
