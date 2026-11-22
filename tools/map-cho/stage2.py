# Bước 2: dựng hình khối mới lên địa hình đã chỉnh, ghép với mô hình cũ, ghi market.glb
import numpy as np, sys
sys.path.insert(0,'/home/claude/work/build')
from design import *
from mb import MB, lin, write_glb, WHITE, PLAIN
import geom
from geom import *
d=np.load('stage1.npz'); P,N,UV,C,I,tl=[d[k] for k in ('P','N','UV','C','I','tl')]
UV=UV.copy(); UV[:,1]*=0.5; UV[:,0]*=0.5; C=C[:,:3].copy()
Tnew=np.load('Tnew.npy')
gfn=lambda x,z: samp(Tnew,x,z)
T=P[I[tl==98]]
sel=(T[:,:,0].max(1)>-62)&(T[:,:,0].min(1)<20)&(T[:,:,2].max(1)>-8)&(T[:,:,2].min(1)<78)
T=T[sel]
walk=MB(); solid=MB(); deco=MB()
PAVC=np.array([0.80,0.76,0.68]); LAWNC=np.array([0.150,0.330,0.090]); CURB=lin('#b8b2a5')
n=0
for k,poly in enumerate(PLAZA): n+=drape(walk,T,poly,PL_OFF,PAVE,PAVC,curb={0:{0,1},1:set(),2:{1,2,3,4,5}}[k],curbcol=CURB)
for poly in UPPER: n+=drape(walk,T,poly,UP_OFF,PAVE,PAVC)
# thềm phẳng đỉnh thang (U0) và mép thềm phía nam
tp=np.array(TOPLAND); cell=2.5; flat=[]
for gx in np.arange(np.floor(tp[:,0].min()/cell)*cell,tp[:,0].max(),cell):
    for gz in np.arange(np.floor(tp[:,1].min()/cell)*cell,tp[:,1].max(),cell):
        y=U0-UP_OFF; flat.append([(gx,y,gz),(gx+cell,y,gz),(gx+cell,y,gz+cell)]); flat.append([(gx,y,gz),(gx+cell,y,gz+cell),(gx,y,gz+cell)])
n+=drape(walk,np.array(flat),TOPLAND,UP_OFF,PAVE,PAVC)
a_,b_=TOPLAND[1],TOPLAND[2]; solid.quad([(a_[0],U0-1.6,a_[1]),(b_[0],U0-1.6,b_[1]),(b_[0],U0,b_[1]),(a_[0],U0,a_[1])],PLAIN,lin('#e7e3da'),geom.VH)
# kè đá chân dốc cỏ phía nam sân, và mặt dốc cỏ sau kè nối lên nền cũ cạnh khách sạn trắng
Told=np.load('Told_used.npy')
NSEG=8; xs=np.linspace(WALL_X0,WALL_X1,NSEG+1); ST_C=lin('#f2ede2'); CAPC=lin('#d6d0c4')
for k in range(NSEG):
    xa,xb=xs[k],xs[k+1]; ta,tb=float(wall_top(xa)),float(wall_top(xb))
    solid.quad([(xb,Q-0.6,WALL_Z),(xa,Q-0.6,WALL_Z),(xa,ta,WALL_Z),(xb,tb,WALL_Z)],geom.STONE,ST_C,np.array([0,0,-1.0]),sub=(0,0.0,1,0.62))
    solid.quad([(xa,ta,WALL_Z),(xb,tb,WALL_Z),(xb,tb,WALL_Z+0.4),(xa,ta,WALL_Z+0.4)],PLAIN,CAPC,geom.UP)
solid.quad([(WALL_X1,Q-0.6,WALL_Z),(WALL_X1,Q-0.6,WALL_Z+0.4),(WALL_X1,float(wall_top(WALL_X1)),WALL_Z+0.4),(WALL_X1,float(wall_top(WALL_X1)),WALL_Z)],PLAIN,CAPC,np.array([1.0,0,0]))
xo=np.linspace(-2.5,12.5,NSEG+1)
for k in range(NSEG):
    ia,ib=xs[k],xs[k+1]; oa,ob=xo[k],xo[k+1]
    pa=(ia,float(wall_top(ia))-0.02,WALL_Z+0.4); pb=(ib,float(wall_top(ib))-0.02,WALL_Z+0.4)
    qa=(oa,float(samp(Told,oa,45.0))+0.06,45.0); qb=(ob,float(samp(Told,ob,45.0))+0.06,45.0)
    solid.quad([pa,pb,qb,qa],NOISE,LAWNC,geom.UP)
for poly in LAWN+ALLEY+[NBANK,NBANK2]: n+=drape(walk,T,poly,LAWN_OFF,NOISE,LAWNC)
n+=drape(walk,T,WILLOW_BED,0.30,NOISE,LAWNC,curb={0,1,2},curbcol=lin('#a8a195'),curb_h=0.5)
# chân tường khách sạn trắng ở mũi bắc (nền sân thấp hơn chân tường cũ)
PLC=lin('#d6d1c6')
wall(solid,(-6.5,44.8),(-2.0,43.0),3.3,6.2,PLAIN,PLC); wall(solid,(-2.0,43.0),(0.2,47.4),3.3,6.2,PLAIN,PLC)
print('mảng phủ:',n,'tam giác (+ bó vỉa) =',walk.ntri)
bp=stairs(solid); n0=solid.ntri; print('bậc thang + lan can:',n0)
# chậu cây trên chiếu nghỉ và trên lan can; đèn ở hai đầu lan can và chiếu nghỉ giữa
for k in range(NF-1):
    uu=US+k*PER+NR*TREAD+0.9; yy=U0-(k+1)*NR*RISE
    x,z=l2w(uu,0.0); urn(deco,x,z,yy,1.15)
    for s in (-1,1):
        x,z=l2w(uu,s*(SW+PW/2))
        if k==2: lamp(deco,x,z,yy+0.95,3.4)
        else: urn(deco,x,z,yy+0.95,0.9)
for uu,yy in ((US-0.3,U0),(UF+0.2,Q)):
    for s in (-1,1):
        x,z=l2w(uu,s*(SW+PW/2)); lamp(deco,x,z,yy+0.95,3.6)
print('chậu, đèn:',deco.ntri); n0=solid.ntri
W=white_building(solid,deco); print('toà trắng:',solid.ntri-n0); n0=solid.ntri
store(solid,gfn); print('cửa hàng:',solid.ntri-n0); n0=solid.ntri
araucaria(deco,PINE[0],PINE[1],float(gfn(*PINE))+LAWN_OFF,30.0)
for k,(x,z) in enumerate(WILLOWS): willow(deco,x,z,float(gfn(x,z))+0.30,[1.0,1.1,0.95,1.05,1.0,0.9][k],k*0.7)
# sân trên: cây bóng mát, đèn, biển chỉ dẫn
for x,z,h in ((-49.0,4.5,4.6),(-48.0,11.5,4.2),(-46.2,18.5,4.4)): ball_tree(deco,x,z,float(gfn(x,z))+UP_OFF,h,1.6)
for x,z in ((-51.5,8.0),(-44.0,22.5)): lamp(deco,x,z,float(gfn(x,z))+UP_OFF,3.8)
sx,sz=l2w(0.6,5.6); sy=float(gfn(sx,sz))+UP_OFF
deco.prism((sx,sz),0.05,0.05,sy,sy+2.3,4,lin('#4a4f55'),cap=False)
wall(deco,lw(0.75,6.3),lw(0.75,4.9),sy+1.5,sy+2.4,BILL,lin('#2a5fa8'))
hotels(solid,gfn); print('dãy khách sạn:',solid.ntri-n0); n0=solid.ntri
TW=(-83.0,42.0); tower(deco,TW[0],TW[1],float(gfn(*TW))); print('cây, chậu, đèn, tháp:',deco.ntri)
# ---- cầu đi bộ vào tầng trên chợ, cầu thang lên sân thượng ----
import bridge as BR, json
from rast import raster as _raster
sys.path.insert(0,'/home/claude/work')
_T=P[I[tl==98]]; _s=(_T[:,:,0].max(1)>-63)&(_T[:,:,0].min(1)<75)&(_T[:,:,2].max(1)>-128)&(_T[:,:,2].min(1)<-3)
_GX,_GZ=-60.0,-125.0; _GNX,_GNZ=267,243; _G=_raster(_T[_s],_GX,_GZ,0.5,_GNX,_GNZ)
def gfnB(x,z):
    fx=min(max((float(x)-_GX)/0.5,0),_GNX-2.0); fz=min(max((float(z)-_GZ)/0.5,0),_GNZ-2.0); i=int(fx); j=int(fz); a=fx-i; b=fz-j
    return (_G[j,i]*(1-a)+_G[j,i+1]*a)*(1-b)+(_G[j+1,i]*(1-a)+_G[j+1,i+1]*a)*b
n0=solid.ntri; n1=deco.ntri
decks=BR.build(solid,deco,gfnB,walk); n_br=solid.ntri; BR.low_buildings(solid,gfnB)
json.dump(dict(decks=decks,path=BR.deck_path(gfnB),props=[[round(x,2),round(z,2),round(0.6*sc,2),round(y,2)] for (x,z,y,sc) in BR.pots()],tri=[n0,n_br]),open('decks.json','w')); print('cầu đi bộ, cửa chợ, cầu thang, sân thượng:',solid.ntri-n0,'+',deco.ntri-n1,'tam giác;',len(decks),'mảng đi được tầng trên')
# ---- khu đầu cầu phía Khu Hòa Bình ----
import plaza as PZ
n0=solid.ntri; n1=deco.ntri; _tp=_T[(_T[:,:,0].max(1)>-45)&(_T[:,:,0].min(1)<-8)&(_T[:,:,2].max(1)>-116)&(_T[:,:,2].min(1)<-84)]
_r=PZ.build(walk,solid,deco,gfnB,_tp); print('khu đầu cầu Khu Hòa Bình:',solid.ntri-n0,'+',deco.ntri-n1,'tam giác; sân nhựa',_r['walk_tris'])
# toà nhà lớn phía nam (khách sạn trắng trong ảnh): sơn lại màu trắng
v1371=np.unique(I[tl==1371]); c=C[v1371]; wallv=(c.max(1)>0.3)&(np.abs(c[:,0]-c[:,1])<0.12)
C[v1371[wallv]]=lin('#f3f1eb')
print('sơn trắng toà 1371:',wallv.sum(),'đỉnh')
# ---- ghép ----
Pw,Nw,UVw,Cw=walk.arrays(); Ps,Ns,UVs,Cs=solid.arrays(); Pd,Nd,UVd,Cd=deco.arrays()
P2=np.concatenate([P,Pw,Ps,Pd]); N2=np.concatenate([N,Nw,Ns,Nd]); UV2=np.concatenate([UV,UVw,UVs,UVd]); C2=np.concatenate([C,Cw,Cs,Cd])
In=np.arange(len(Pw)+len(Ps)+len(Pd)).reshape(-1,3)+len(P)
I2=np.concatenate([I,In])
jpeg=open('atlas2.jpg','rb').read()
out=sys.argv[1] if len(sys.argv)>1 else '/home/claude/work/srv/test.glb'
print('glb',write_glb(out,P2,N2,UV2,C2,I2,jpeg), 'tam giác mới',len(In),'tổng',len(I2))
np.savez('stage2_new.npz',Pw=Pw,Ps=Ps,Pd=Pd,P=P,I=I,tl=tl,TW=np.array(TW))
