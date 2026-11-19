import json,sys,numpy as np
from shapely.geometry import LineString,Polygon
from pyproj import Transformer
G=Transformer.from_crs(3874,4326,always_xy=True).transform
S=sys.argv[1]
ctrl=json.load(open(S+'/ctrl.json'))
tr=json.load(open('data/mariehamn-city-traces.json'));plan=next(x for x in tr['sets'] if x['id']=='plan-1860')
PX={r['name']:r['pixels'] for r in plan['roads']}
EWo=['Norragatan i planen','Norra esplanadens gata','Storagatans planerade stråk','Södragatans planerade stråk','Södra kvarterens tvärgata','Planens södra gränsgata']
NSo=['Västra strandens planerade gata','Västra kvarterens gata','Planerad gata väster om esplanaden','Västra esplanadens gata','Östra esplanadens gata','Planerad gata öster om esplanaden','Torggatans planerade stråk','Östra strandens gata']
def ext(c,d):
    c=np.array(c,float);a=c[0]+(c[0]-c[1])/np.linalg.norm(c[0]-c[1])*d;b=c[-1]+(c[-1]-c[-2])/np.linalg.norm(c[-1]-c[-2])*d;return LineString([a,*c,b])
known={(EWo.index(a),NSo.index(b)):np.array(q) for a,b,p,q in ctrl}
CP=np.array([p for _,_,p,_ in ctrl]);CQ=np.array([q for _,_,_,q in ctrl])
def local(p,k=8):
    d=np.hypot(*(CP-p).T);i=np.argsort(d)[:k];w=1/(d[i]+30)**2
    M=np.linalg.lstsq(np.c_[CP[i],np.ones(len(i))]*np.sqrt(w)[:,None],CQ[i]*np.sqrt(w)[:,None],rcond=None)[0];return np.r_[p,1]@M
Pn={};Qn={};filled=[]
for i,a in enumerate(EWo):
    for j,b in enumerate(NSo):
        x=ext(PX[a],400).intersection(ext(PX[b],400));p=np.array([x.x,x.y]);Pn[(i,j)]=p
        if (i,j) in known: Qn[(i,j)]=known[(i,j)]
        else: Qn[(i,j)]=local(p);filled.append((a,b))
def bil(D,i,j,u,v): return (1-u)*(1-v)*D[(i,j)]+u*(1-v)*D[(i,j+1)]+(1-u)*v*D[(i+1,j)]+u*v*D[(i+1,j+1)]
def inv(i,j,p):
    u=v=.5
    for _ in range(50):
        f=bil(Pn,i,j,u,v)-p;h=1e-4
        J=np.c_[(bil(Pn,i,j,u+h,v)-bil(Pn,i,j,u,v))/h,(bil(Pn,i,j,u,v+h)-bil(Pn,i,j,u,v))/h];du,dv=np.linalg.solve(J,f);u-=du;v-=dv
    return u,v
def cell(p):
    # choose the row/column band in plan space, clamped to the grid
    i=0
    while i<len(EWo)-2 and ext(PX[EWo[i+1]],400).distance(LineString([p,p+[0,-1e4]]))==0: i+=1
    j=0
    while j<len(NSo)-2 and ext(PX[NSo[j+1]],400).distance(LineString([p,p+[-1e4,0]]))==0: j+=1
    return i,j
B=json.load(open(S+'/buildings_px.json'));res=[]
for b in B:
    c=np.mean(b['px'],axis=0);i,j=cell(c)
    pts=[];ext_=0
    for p in b['px']:
        u,v=inv(i,j,np.array(p));ext_=max(ext_,max(0,-u,u-1)+max(0,-v,v-1));pts.append(bil(Qn,i,j,u,v))
    poly=Polygon(pts);res.append(dict(b,cell=[EWo[i],EWo[i+1],NSo[j],NSo[j+1]],extrapolation=round(ext_,2),area=round(poly.area),lonlat=[[round(v,7) for v in G(*q)] for q in pts]))
    print(b['key'].ljust(18),(i,j),'extrap',round(ext_,2),'area',round(poly.area))
print('filled',filled)
json.dump(res,open(S+'/placed.json','w'),ensure_ascii=False,indent=1)
