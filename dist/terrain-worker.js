/* Contours are computed off the UI thread so panning and playback stay responsive. */
importScripts('vendor/d3-array.min.js','vendor/d3-contour.min.js');
let base;
onmessage=({data})=>{
 try{
  if(data.type==='init'){base=data.grid;return}
  const grid=data.grid||base;
  const thresholds=[data.level+.02,data.level+14,data.level+45];
  const contours=d3.contours().size([grid.width,grid.height]).smooth(true).thresholds(thresholds)(grid.values);
  postMessage({id:data.id,contours});
 }catch(error){postMessage({id:data.id,error:String(error)})}
};
