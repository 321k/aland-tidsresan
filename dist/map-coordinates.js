'use strict';
// ETRS-GK20FIN (EPSG:3874), GRS80 Transverse Mercator, central meridian 20°.
function mariehamnGrid(lon,lat){
 const a=6378137,f=1/298.257222101,e2=f*(2-f),ep2=e2/(1-e2),phi=lat*Math.PI/180,dl=(lon-20)*Math.PI/180;
 const n=a/Math.sqrt(1-e2*Math.sin(phi)**2),t=Math.tan(phi)**2,c=ep2*Math.cos(phi)**2,A=Math.cos(phi)*dl;
 const M=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*phi-(3*e2/8+3*e2**2/32+45*e2**3/1024)*Math.sin(2*phi)+(15*e2**2/256+45*e2**3/1024)*Math.sin(4*phi)-35*e2**3/3072*Math.sin(6*phi));
 return [M+n*Math.tan(phi)*(A*A/2+(5-t+9*c+4*c*c)*A**4/24+(61-58*t+t*t+600*c-330*ep2)*A**6/720),20500000+n*(A+(1-t+c)*A**3/6+(5-18*t+t*t+72*c-58*ep2)*A**5/120)];
}
