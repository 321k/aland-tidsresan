'use strict';
// Evidence dates are not continuous occupation dates. Demolition is separate from operation.
const EvidenceTime={
 state(f,year){
  if(f.recordType==='building'){
   if(year<f.start)return 'future';
   if(Number.isFinite(f.end)&&year>=f.end)return 'trace';
   return f.uncertainDate?'possible':'attested';
  }
  const d=f.temporal;
  if(d){
   if(year<d.startEarliest)return 'future';
   if(Number.isFinite(d.endLatest)&&year>d.endLatest)return 'trace';
   if(f.recordType==='marine')return year<d.startLatest||d.confidence!=='documented'?'possible':'attested';
   if(d.dateBasis==='dated_evidence'){
    const spans=(d.phases||[]).filter(p=>Number.isFinite(p.from));
    if(spans.some(p=>year>=p.from&&year<=(p.to??p.from)))return d.confidence==='documented'?'attested':'possible';
    if(year>d.startLatest)return 'trace';
   }
   if(f.periods?.length&&year>Math.max(...f.periods.map(p=>p.to)))return 'trace';
   return 'possible';
  }
  if(!f.periods?.length)return 'undated';
  if(f.periods.some(p=>year>=p.from&&year<=p.to))return 'possible';
  return year<Math.min(...f.periods.map(p=>p.from))?'future':'trace';
 },
 phase(f,year){return(f.phases||f.temporal?.phases||[]).filter(p=>Number.isFinite(p.from)&&year>=p.from&&(p.to==null||year<=p.to)).at(-1)||null},
 label(state){return {attested:'Belagt år / tidsintervall',possible:'Ungefärlig eller osäker datering',trace:'Äldre spår eller belägg',undated:'Datering saknas',future:'Senare än valt år'}[state]},
 firstYear(f){return f.start??f.temporal?.startEarliest??f.earliestYear??(f.periods?.length?Math.min(...f.periods.map(p=>p.from)):null)},
 modelYear(year,years){return years.reduce((best,y)=>Math.abs(y-year)<Math.abs(best-year)?y:best,years[0])}
};
