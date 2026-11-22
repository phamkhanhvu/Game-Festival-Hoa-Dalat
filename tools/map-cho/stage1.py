# Bước 1: xoá công trình cũ trong khu, tính địa hình mới (điều hoà giữa các cao độ thiết kế), dời các lớp mặt đường/vỉa hè theo địa hình
import numpy as np, sys, pickle, collections
sys.path.insert(0,'/home/claude/work'); sys.path.insert(0,'/home/claude/work/build')
from design import *
from rast import raster
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve
m=np.load('/home/claude/work/market_dec.npz'); P,N,UV,C,I=[m[k].copy() for k in ('P','N','UV','C','I')]
tl=np.load('/home/claude/work/tri_comp.npy')
import os
if os.path.exists('told2.npy'): Told=np.load('told2.npy')
else:
    T_=P[I[tl==98]]; s_=(T_[:,:,0].max(1)>X0-3)&(T_[:,:,0].min(1)<X0+NX*ST+3)&(T_[:,:,2].max(1)>Z0-3)&(T_[:,:,2].min(1)<Z0+NZ*ST+3)
    Told=raster(T_[s_],X0,Z0,ST,NX,NZ); np.save('told2.npy',Told)
tri=P[I]; X,Z=grid_xz(); U,V=w2l(X,Z)
zone=poly_mask(ZONE_E); zdel=poly_mask(ZONE_DEL)
# ---- phân loại thành phần ----
comps=collections.defaultdict(list)
for i,l in enumerate(tl): comps[l].append(i)
TERR=98
info={}
for l,idx in comps.items():
    idx=np.array(idx); pts=tri[idx].reshape(-1,3); mn=pts.min(0); mx=pts.max(0)
    if mx[0]<X0+1 or mn[0]>X0+(NX-1)*ST-1 or mx[2]<Z0+1 or mn[2]>Z0+(NZ-1)*ST-1: continue
    inside=(pts[:,0]>X0)&(pts[:,0]<X0+(NX-1)*ST)&(pts[:,2]>Z0)&(pts[:,2]<Z0+(NZ-1)*ST)
    rel=(pts[inside,1]-samp(Told,pts[inside,0],pts[inside,2])) if inside.any() else np.array([9.0])
    info[l]=dict(n=len(idx),mn=mn,mx=mx,ctr=(mn+mx)/2,relmax=float(rel.max()),relmin=float(rel.min()),ground=bool(rel.max()<0.6 and l!=TERR))
def in_poly_pt(x,z,mask):
    i=int(round((x-X0)/ST)); j=int(round((z-Z0)/ST)); return 0<=i<NX and 0<=j<NZ and mask[j,i]
# ---- danh sách xoá ----
west_bld=[785,780,767,731,718,677,633,783,841,840,881]
dele=set([1207])
for l,d in info.items():
    if l==TERR or d['ground']: continue
    if in_poly_pt(d['ctr'][0],d['ctr'][2],zdel): dele.add(l)
# biển hiệu, mái hiên nhỏ gắn trước mặt tiền các nhà phía tây sẽ thay
FRONTS={785:((-66.2,24.9),(-66.2,29.6)),780:((-66.2,29.6),(-66.2,34.3)),767:((-66.2,34.5),(-66.2,39.2)),731:((-71.1,12.3),(-68.1,15.9)),718:((-74.1,8.7),(-71.1,12.3)),
        677:((-77.1,5.1),(-74.1,8.7)),633:((-80.1,1.4),(-77.1,5.1)),783:((-63.7,50.1),(-62.1,54.5)),841:((-62.0,54.7),(-60.4,59.1)),840:((-60.3,59.3),(-58.4,63.6)),881:((-58.4,63.7),(-56.4,67.9))}
def segdist(p,a,b):
    p=np.array(p); a=np.array(a); b=np.array(b); t=np.clip(np.dot(p-a,b-a)/np.dot(b-a,b-a),0,1); return np.linalg.norm(p-(a+t*(b-a)))
for l in west_bld: dele.add(l)
for l,d in info.items():
    if l==TERR or d['ground'] or l in dele or d['n']>12: continue
    if any(segdist((d['ctr'][0],d['ctr'][2]),a_,b_)<1.6 for a_,b_ in FRONTS.values()): dele.add(l)
dele|=set([1176,1201,1025])          # cây cũ trong bồn liễu, biển của ki-ốt đã xoá
dele|=set([1345,1344,1379,1483,1596,1662,1564,1575,1580,1591,1386,1393,1402,1413,1597,1496,1577,1578,1673,1696,1794])   # khu cầu đi bộ vào chợ
keep_force=set([1371,1177,1687,1428,1452])
dele-=keep_force
print('xoá',len(dele),'thành phần;',int(np.isin(tl,list(dele)).sum()),'tam giác')

# lớp mặt đất nằm trong vùng: giữ lại và dời theo địa hình
glayers=[l for l,d in info.items() if d['ground'] and l not in dele]
gl_in=[]
for l in glayers:
    pts=tri[np.array(comps[l])].reshape(-1,3)
    ii=np.clip(np.round((pts[:,0]-X0)/ST).astype(int),0,NX-1); jj=np.clip(np.round((pts[:,2]-Z0)/ST).astype(int),0,NZ-1)
    ok=(pts[:,0]>X0)&(pts[:,0]<X0+(NX-1)*ST)&(pts[:,2]>Z0)&(pts[:,2]<Z0+(NZ-1)*ST)
    if (zone[jj,ii]&ok).any(): gl_in.append(l)
garden=[l for l in gl_in if np.hypot(info[l]['mn'][0]-RB_C[0],info[l]['mn'][2]-RB_C[1])<RB_R+7 and np.hypot(info[l]['mx'][0]-RB_C[0],info[l]['mx'][2]-RB_C[1])<RB_R+7]
gl_in=[l for l in gl_in if l not in garden]
print('bồn hoa bùng binh giữ nguyên:',len(garden),'thành phần')
print('lớp mặt đất chạm vùng:',[(l,info[l]['n'],tuple((C[I[comps[l]]].mean((0,1))[:3]*255).astype(int))) for l in gl_in])
# tam giác lớp mặt đất cũ nằm dưới mảng lát/cỏ mới hoặc dưới công trình mới: bỏ
tc=tri.mean(1); tcu,tcv=w2l(tc[:,0],tc[:,2])
platemask=np.zeros((NZ,NX),bool)
for poly in PLAZA+UPPER+LAWN+[TOPLAND]: platemask|=poly_mask(poly)
ci=np.clip(np.round((tc[:,0]-X0)/ST).astype(int),0,NX-1); cj=np.clip(np.round((tc[:,2]-Z0)/ST).astype(int),0,NZ-1)
cin=(tc[:,0]>X0)&(tc[:,0]<X0+(NX-1)*ST)&(tc[:,2]>Z0)&(tc[:,2]<Z0+(NZ-1)*ST)
t_band=(tcu>=-1.5)&(tcu<=UF)&(np.abs(tcv)<=SW+PW)
t_bld=((tcu>=WA['u0'])&(tcu<=WA['u1'])&(tcv>=WA['v0'])&(tcv<=WA['v1']))|in_wb(tcu,tcv)|((tcu>=ST_R['u0'])&(tcu<=ST_F['u1'])&(tcv>=ST_F['v0'])&(tcv<=ST_F['v1']))
ASPH=(1452,1456)
is_gl=np.isin(tl,gl_in+[1452]); is_asph=np.isin(tl,ASPH)
drop_tri=cin&is_gl&((~is_asph&(platemask[cj,ci]|t_band|t_bld))|(is_asph&(t_band|t_bld)))
drop_tri|=cin&(tl==961)&platemask[cj,ci]      # đoạn lối lát cũ nối lên đỉnh thang
import bridge as BR
_q,_p=BR.w2f(tri[:,:,0],tri[:,:,2])
back=(tl==1551)&(np.abs(_p)<0.35).all(1)&(tri[:,:,1].min(1)>=8.7)&(tri[:,:,1].max(1)<=17.4)&(_q.min(1)>BR.QW-0.3)&(_q.max(1)<BR.QE+0.3)
print('bỏ tường sau chợ cũ (tầng 1, 2, tường mái):',int(back.sum()),'tam giác'); drop_tri|=back
print('bỏ tam giác lớp mặt đất cũ:',drop_tri.sum())
keepmask=np.zeros((NZ,NX),bool)
for l in gl_in:
    if l in ASPH: continue
    sel=(tl==l)&~drop_tri
    if sel.any(): keepmask|=tris_mask(tri[sel])
from scipy.ndimage import binary_dilation
keepd=binary_dilation(keepmask,iterations=3)
free=zone&~keepd
# ---- cao độ thiết kế cố định ----
fixed=~free; D=Told.copy()
def fix(mask,val):
    global fixed,D
    mk=mask&zone&~keepd; D[mk]=np.broadcast_to(val,D.shape)[mk]; fixed|=mk
band=(U>=-1.5)&(U<=UF)&(np.abs(V)<=SW+PW)
fix(band, s_ramp(U)-0.30)
fix((U>=WA['u0']-0.01)&(U<=WA['u1'])&(V>=WA['v0'])&(V<=WA['v1']), U0-0.30)
fix(in_wb(U,V), Q-0.10)
fix((U>=ST_F['u0'])&(U<=ST_F['u1'])&(V>=ST_F['v0'])&(V<=ST_F['v1']), Q-0.10)
fix((U>=18.0)&(U<=35.0)&(V>=-31.0)&(V<=16.0)&~band, Q-PL_OFF)
fix(((X-RB_C[0])**2+(Z-RB_C[1])**2<=RB_R**2)&~fixed, RB_Y)
fix(poly_mask(PLAZA[2])&(X<7.0)&~fixed, Q-PL_OFF)                                   # sân chân thang phẳng
fix((Z>=WALL_Z)&(Z<=WALL_Z+2.2)&(X>=WALL_X0-0.5)&(X<=WALL_X1+0.3)&~fixed, Q-PL_OFF-0.05)   # nền dưới dốc cỏ sau kè đá (dốc cỏ dựng riêng)                 # nền quanh bồn hoa bùng binh            # sân lát trước chân thang và mặt tiền hai công trình
fix((U>=-7.0)&(U<-1.5)&(V>=-29.5)&(V<=SW+PW), U0-UP_OFF)                 # thềm trên đỉnh thang, trước sân thượng
fr=free&~fixed
print('ô tự do',fr.sum(),'ô cố định trong vùng',(fixed&zone).sum())
# ---- giải Laplace cho các ô tự do ----
idx=-np.ones((NZ,NX),int); idx[fr]=np.arange(fr.sum()); n=int(fr.sum())
jj,ii=np.where(fr); rows=[];cols=[];vals=[]; b=np.zeros(n)
for dj,di in ((1,0),(-1,0),(0,1),(0,-1)):
    nj=jj+dj; ni=ii+di; nb=idx[nj,ni]; isf=nb>=0
    rows.append(np.arange(n)[isf]); cols.append(nb[isf]); vals.append(-np.ones(isf.sum()))
    np.add.at(b,np.arange(n)[~isf],D[nj[~isf],ni[~isf]])
rows.append(np.arange(n)); cols.append(np.arange(n)); vals.append(4*np.ones(n))
A=csr_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(n,n))
D[fr]=spsolve(A.tocsc(),b)
print('D range in zone',D[zone].min(),D[zone].max())
np.save('D.npy',D)
# ---- đỉnh địa hình ----
tv=np.unique(I[tl==TERR]); tx=P[tv,0]; tz=P[tv,2]
inb=(tx>X0+0.5)&(tx<X0+(NX-1)*ST-0.5)&(tz>Z0+0.5)&(tz<Z0+(NZ-1)*ST-0.5)
ti=np.clip(np.round((tx-X0)/ST).astype(int),0,NX-1); tj=np.clip(np.round((tz-Z0)/ST).astype(int),0,NZ-1)
chg=inb&zone[tj,ti]&~keepd[tj,ti]
ynew=samp(D,tx,tz)
# hạ địa hình xuống dưới các mặt cứng mới (bậc thang, sàn, mái) trong bán kính một ô lưới địa hình
cover=np.full((NZ,NX),np.inf)
cover=np.where(band&(np.abs(V)<=SW), s_step(U+0.01)-0.02, cover)                                   # mặt bậc
cover=np.where((U>=-7.0)&(U<US)&(V>=-29.5)&(V<=SW+PW), np.minimum(cover,U0), cover)                # thềm trên
cover=np.where((U>=WA['u0'])&(U<=WA['u1'])&(V>=WA['v0'])&(V<=WA['v1']), np.minimum(cover,U0), cover)
cover=np.where(in_wb(U,V), np.minimum(cover,Q+0.02), cover)
cover=np.where((U>=ST_F['u0'])&(U<=ST_F['u1'])&(V>=ST_F['v0'])&(V<=ST_F['v1']), np.minimum(cover,Q+0.02), cover)
cover=np.where((U>=ST_R['u0'])&(U<=ST_R['u1'])&(V>=ST_R['v0'])&(V<=ST_R['v1']), np.minimum(cover,store_roof(U,V)-0.25), cover)
from scipy.ndimage import minimum_filter
cov_nb=minimum_filter(cover,size=int(2*2.6/ST)+1,mode='nearest')
lim=cov_nb[tj,ti]-0.12
ynew=np.where(np.isfinite(lim),np.minimum(ynew,lim),ynew)
P[tv[chg],1]=ynew[chg]
print('đỉnh địa hình đổi cao độ:',chg.sum(),'lệch lớn nhất',np.abs(P[tv[chg],1]-m['P'][tv[chg],1]).max())
# ---- lưới địa hình mới và độ lệch ----
T=P[I[tl==TERR]]
sel=(T[:,:,0].max(1)>X0-3)&(T[:,:,0].min(1)<X0+NX*ST+3)&(T[:,:,2].max(1)>Z0-3)&(T[:,:,2].min(1)<Z0+NZ*ST+3)
Tnew=raster(T[sel],X0,Z0,ST,NX,NZ)
Tnew[np.isnan(Tnew)]=Told[np.isnan(Tnew)]
delta=Tnew-Told; delta[np.abs(delta)<1e-6]=0
print('delta',delta.min(),delta.max())
np.save('Tnew.npy',Tnew)
# ---- dời các lớp mặt đất giữ lại ----
moved=0
for l in gl_in+[1452]:
    vi=np.unique(I[(tl==l)&~drop_tri]); ok=(P[vi,0]>X0+0.3)&(P[vi,0]<X0+(NX-1)*ST-0.3)&(P[vi,2]>Z0+0.3)&(P[vi,2]<Z0+(NZ-1)*ST-0.3)
    vi=vi[ok]
    if l in ASPH:
        i_=np.clip(np.round((P[vi,0]-X0)/ST).astype(int),0,NX-1); j_=np.clip(np.round((P[vi,2]-Z0)/ST).astype(int),0,NZ-1)
        inz=zone[j_,i_]&~keepd[j_,i_]
        newy=samp(Tnew,P[vi,0],P[vi,2])+0.2
        moved+=(np.abs(newy[inz]-P[vi[inz],1])>0.005).sum(); P[vi[inz],1]=newy[inz]
    else:
        dv=samp(delta,P[vi,0],P[vi,2]); P[vi,1]+=dv; moved+=(np.abs(dv)>0.005).sum()
print('đỉnh lớp mặt đất dời:',moved)
# ---- vật còn giữ đứng trên nền cũ trong vùng (đèn, ghế, cây): dời theo độ lệch địa hình tại chân vật ----
nshift=0
for l,d in info.items():
    if l==TERR or d['ground'] or l in dele or l in (1452,): continue
    cx,cz=d['ctr'][0],d['ctr'][2]
    if not in_poly_pt(cx,cz,zone): continue
    if (d['mx'][0]-d['mn'][0])>12 or (d['mx'][2]-d['mn'][2])>12: continue
    dl=float(samp(delta,cx,cz))
    if abs(dl)<0.02 or d['relmin']<-0.6 or np.hypot(cx-RB_C[0],cz-RB_C[1])<RB_R+1.5: continue
    vi=np.unique(I[tl==l]); P[vi,1]+=dl; nshift+=1; print('   dời',l,d['n'],'ctr(%.1f,%.1f)'%(cx,cz),'%.2f'%dl)
print('vật dời theo nền:',nshift)
# ---- màu cỏ cũ trên địa hình trong vùng: trả về màu nền; tính lại pháp tuyến cho mặt đất đã đổi ----
tvz=tv[chg]; g=(C[tvz,1]>C[tvz,0]*1.5)
base=np.array([141,131,116])/255.0
C[tvz[g],:3]=base
pk=poly_mask(POCKET)|poly_mask(POCKET2); pv=tv[inb&pk[tj,ti]]; C[pv,:3]=np.array([0.150,0.330,0.090]); print('đỉnh địa hình phủ màu cỏ:',len(pv))
gsel=np.isin(tl,[TERR,1452]+gl_in)&~drop_tri
Tg=I[gsel]; pt=P[Tg]
box=(pt[:,:,0].max(1)>-62)&(pt[:,:,0].min(1)<58)&(pt[:,:,2].max(1)>-16)&(pt[:,:,2].min(1)<56)
Tg=Tg[box]; pt=P[Tg]
fn=np.cross(pt[:,1]-pt[:,0],pt[:,2]-pt[:,0]); fn[fn[:,1]<0]*=-1
acc=np.zeros_like(P)
for k in range(3): np.add.at(acc,Tg[:,k],fn)
vv=np.unique(Tg); L=np.linalg.norm(acc[vv],axis=1); ok=L>1e-9
N[vv[ok]]=acc[vv[ok]]/L[ok][:,None]
print('tính lại pháp tuyến cho',ok.sum(),'đỉnh; đổi màu cỏ cũ',g.sum())
# ---- bỏ tam giác của các thành phần xoá ----
keep=~np.isin(tl,list(dele))&~drop_tri
I2=I[keep]; tl2=tl[keep]
print('tam giác còn lại',len(I2),'/',len(I))
np.savez('stage1.npz',P=P,N=N,UV=UV,C=C,I=I2,tl=tl2)
pickle.dump(dict(dele=sorted(dele),gl_in=gl_in,info={l:{k:(v.tolist() if hasattr(v,'tolist') else v) for k,v in d.items()} for l,d in info.items()}),open('stage1.pkl','wb'))
np.save('keepd.npy',keepd); np.save('zone.npy',zone); np.save('Told_used.npy',Told); pickle.dump(garden,open('garden.pkl','wb'))
