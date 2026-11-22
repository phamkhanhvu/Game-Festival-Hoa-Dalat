# Bước 3: cập nhật lưới đi lại (h), lưới vật cao nhất (top), loại nền (k), cao độ tuyến xe, điểm check-in và bản đồ nhỏ trong world_cho.js
import numpy as np, sys, pickle, json, base64, io
sys.path.insert(0,'/home/claude/work'); sys.path.insert(0,'/home/claude/work/build')
from design import *
from rast import raster
import worldio
from PIL import Image, ImageDraw
import bridge as BR
SRC='/home/claude/phamkhanhvu/game-festival-hoa-dalat/world_cho.js' if len(sys.argv)<2 else sys.argv[1]
OUT=sys.argv[2] if len(sys.argv)>2 else '/home/claude/work/srv/world_cho_test.js'
j,h,top,k,pre,post=worldio.load('/home/claude/work/world_cho_orig.js')
gx0,gz0,gs,gnx,gnz=j['x0'],j['z0'],j['step'],j['nx'],j['nz']; h0=h.copy()
# vùng tính lại
RX0,RX1,RZ0,RZ1=-130.0,200.0,-165.0,265.0      # cả bản đồ (lề đường làm lại toàn bản đồ)
i0=int(round((RX0-gx0)/gs)); i1=int(round((RX1-gx0)/gs)); j0=int(round((RZ0-gz0)/gs)); j1=int(round((RZ1-gz0)/gs)); rnx=i1-i0+1; rnz=j1-j0+1
Xg,Zg=np.meshgrid(gx0+np.arange(i0,i1+1)*gs, gz0+np.arange(j0,j1+1)*gs); Ug,Vg=w2l(Xg,Zg)
def pmask(poly): return poly_mask(poly,rnx,rnz,RX0,RZ0,gs)
def tmask(tris): return tris_mask(tris,rnx,rnz,RX0,RZ0,gs)
def R(tris,mode='max'): return raster(tris,RX0,RZ0,gs,rnx,rnz,mode=mode)
s2=np.load('stage2_new.npz'); P,I,tl=s2['P'],s2['I'],s2['tl']; Pw=s2['Pw'].reshape(-1,3,3); Ps=s2['Ps'].reshape(-1,3,3); TW=s2['TW']
st=pickle.load(open('stage1.pkl','rb')); info=st['info']; dele=st['dele']; garden=pickle.load(open('garden.pkl','rb'))
tri=P[I]
inreg=(tri[:,:,0].max(1)>RX0)&(tri[:,:,0].min(1)<RX1)&(tri[:,:,2].max(1)>RZ0)&(tri[:,:,2].min(1)<RZ1)
gset=set([98,1452])|set(l for l,d in info.items() if d['ground'])
is_g=np.isin(tl,list(gset))
Hk=R(tri[inreg&is_g]); Hw=R(Pw)
hn=np.fmax(Hk,Hw)
# ---- lề đã gỡ (curbs.py): ô dưới lề cũ lấy cao độ mặt còn lại (địa hình, đường, vạch, sân) ----
CD=np.load('curb_del.npy'); swm=tmask(CD) if len(CD) else np.zeros(Hk.shape,bool)
Ht=R(tri[inreg&(tl==98)]); _n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); _flat=np.abs(_n[:,1])>0.9*(np.linalg.norm(_n,axis=1)+1e-12)
_c=tri.mean(1); _ci=np.clip(np.round((_c[:,0]-RX0)/gs).astype(int),0,rnx-1); _cj=np.clip(np.round((_c[:,2]-RZ0)/gs).astype(int),0,rnz-1)
_near=(_c[:,1]-np.nan_to_num(Ht[_cj,_ci],nan=-1e9))<0.7
Hflat=R(tri[inreg&_flat&_near&(tl!=98)])
hn=np.where(swm,np.fmax(hn,Hflat),hn)
zone=pmask(ZONE_E); zdel=pmask(ZONE_DEL)
hold=h[j0:j1+1,i0:i1+1].astype(float); oldvalid=hold>-32000
# mặt đi lại định sẵn: bậc thang (dốc trơn), sân thượng khối cao
band=(Ug>=US)&(Ug<=UF)&(np.abs(Vg)<SW)
hn=np.where(band,np.maximum(s_ramp(Ug)-0.08,Q),hn)
wa=(Ug>=WA['u0'])&(Ug<=WA['u1'])&(Vg>=WA['v0'])&(Vg<=WA['v1'])
hn=np.where(wa,U0,hn)
# ô đi được
m0=np.load('/home/claude/work/market_dec.npz'); P0,I0=m0['P'],m0['I']; tl0=np.load('/home/claude/work/tri_comp.npy'); tri0=P0[I0]
kept_obj=inreg&~is_g
Mobj=tmask(tri[kept_obj])
valid=oldvalid.copy()
valid[zdel]=~(~oldvalid[zdel]&Mobj[zdel])
tree_del=tmask(tri0[np.isin(tl0,[1176,1201])]); valid|=tree_del
# vật cản mới
blk=np.zeros_like(valid)
vc=(WB['v0']+WB['v1'])/2
blk|=((Ug>=WB['u0']-0.2)&(Ug<=WB['uc'])&(Vg>=WB['v0']-0.2)&(Vg<=WB['v1']+0.2))|(((Ug-WB['uc'])**2+(Vg-vc)**2<=(WB['R']+0.25)**2)&(Ug>WB['uc']))
edge=wa&((Vg<WA['v0']+0.45)|(Vg>WA['v1']-0.45)|(Ug>WA['u1']-0.45)); blk|=edge
blk|=(Ug>=ST_R['u0']-0.2)&(Ug<=ST_F['u1']+0.15)&(Vg>=ST_F['v0'])&(Vg<=ST_F['v1']+0.45)
blk|=(Ug>=US-0.75)&(Ug<=UF+0.65)&(np.abs(Vg)>=SW-0.05)&(np.abs(Vg)<=SW+PW+0.08)
for kf in range(NF-1):
    uu=US+kf*PER+NR*TREAD+0.9; blk|=((Ug-uu)**2+Vg**2<0.6**2)
blk|=(Zg>=WALL_Z-0.15)&(Zg<=45.3)&(Xg>=WALL_X0-0.3)&(Xg<=WALL_X1+0.3)&zone
def disc(x,z,r): return (Xg-x)**2+(Zg-z)**2<r*r
blk|=disc(PINE[0],PINE[1],0.75)
for x,z in WILLOWS: blk|=disc(x,z,0.5)
for x,z in ((-49.0,4.5),(-48.0,11.5),(-46.2,18.5)): blk|=disc(x,z,0.4)
for x,z in ((-51.5,8.0),(-44.0,22.5)): blk|=disc(x,z,0.35)
sx,sz=l2w(0.6,5.6); blk|=disc(float(sx),float(sz),0.3)
blk|=(np.abs(Xg-TW[0])<=2.9)&(np.abs(Zg-TW[1])<=2.9)
# ---- cầu đi bộ vào chợ: mặt cầu là tầng trên (WORLD.decks), lưới h chỉ giữ mặt đất bên dưới ----
Sg,Tg=BR.w2b(Xg,Zg); Qf,Pf=BR.w2f(Xg,Zg); dky=BR.deck_y(Sg); WB_=BR.HW+BR.PT
front=Pf>0.4
# mố cầu và đoạn gầm thấp hơn 2 m: không đi được bên dưới
low=(Sg>=1.5)&(Sg<=30)&(np.abs(Tg)<=WB_+0.15)&((dky-BR.SLAB-np.nan_to_num(hn,nan=-99))<2.0)
blk|=low
# lan can hai bên đoạn mặt cầu sát mặt đất
blk|=(Sg>=-1.15)&(Sg<=17.0)&(np.abs(Tg)>=BR.HW-0.25)&(np.abs(Tg)<=WB_+0.3)
for sp in BR.PIERS:
    c=BR.BW(sp,0.0); blk|=disc(float(c[0]),float(c[1]),0.95)
for (x,z) in BR.columns(): blk|=disc(float(x),float(z),0.5)
# ---- khu đầu cầu Khu Hòa Bình: nhà xám, ki-ốt, đảo cây, cột, dù ----
import plaza as PZ
PL=json.load(open('/home/claude/work/build/plaza.json'))
for r_ in PL['rects']:
    dx=Xg-r_['c'][0]; dz=Zg-r_['c'][1]; uu=dx*r_['u'][0]+dz*r_['u'][1]; vv=-dx*r_['u'][1]+dz*r_['u'][0]
    blk|=(np.abs(uu)<=r_['hu'])&(np.abs(vv)<=r_['hv'])
for (x,z,r_) in PL['discs']: blk|=disc(x,z,r_)
valid&=~blk
valid&=~np.isnan(hn)
# chỉ ghi các ô thuộc vùng chỉnh hoặc nằm dưới mảng/vật mới
wb=pmask(WILLOW_BED)
chg=zone|wb|blk|tree_del|~np.isnan(Hw)|swm
newh=np.where(valid,np.round(hn*100),-32768)
hsub=h[j0:j1+1,i0:i1+1]; before=hsub.copy()
hsub[chg]=newh[chg].astype(np.int16)
print('ô h đổi:',(hsub!=before).sum(),'| ô đi được trước/sau trong vùng:',(before[chg]>-32000).sum(),(hsub[chg]>-32000).sum())
# top: vật cao nhất trong ô
Tk=R(tri[inreg])
# khối mới: riêng phần cầu đi bộ chỉ tính mặt đứng chợ, mái và nhà sân thượng (mặt cầu, thang là tầng trên, camera xử lý riêng)
DK=json.load(open('/home/claude/work/build/decks.json')); b0,b1=DK['tri']
Ts=np.fmax(R(np.concatenate([Ps[:b0],Ps[b1:]])),Hw); Tbr=R(Ps[b0:b1]); Ts=np.fmax(Ts,np.where(Pf<=0.6,Tbr,np.nan))
tn=np.fmax(Tk,Ts)
deltri=np.isin(tl0,dele)&(tri0[:,:,0].max(1)>RX0)&(tri0[:,:,0].min(1)<RX1)&(tri0[:,:,2].max(1)>RZ0)&(tri0[:,:,2].min(1)<RZ1)
chg_top=zone|tmask(tri0[deltri])|~np.isnan(Ts)|~np.isnan(Tbr)|blk
tsub=top[j0:j1+1,i0:i1+1]; tb=tsub.copy()
tv=np.where(np.isnan(tn),tsub,np.round(np.clip(tn,-300,320)*100)).astype(np.int16)
tsub[chg_top]=tv[chg_top]
# mố cầu (đoạn cầu sát đất): top là mặt cầu, mép là đỉnh lan can
inb=(Sg>=-1.0)&(Sg<=17.0)&(np.abs(Tg)<=WB_+0.2)
dtop=dky+np.where(np.abs(Tg)>=BR.HW-0.2,BR.PH,0.0)
tsub[inb]=np.round(dtop[inb]*100).astype(np.int16)
# trụ cầu: cột cao tới đáy bản mặt cầu
for sp in BR.PIERS:
    c=BR.BW(sp,0.0); pm=disc(float(c[0]),float(c[1]),0.9); tsub[pm]=int(round((float(BR.deck_y(sp))-BR.SLAB)*100))
# nhà sân thượng: tính cả lan can kính trên mái (tấm đứng mỏng, raster không bắt được)
pv=BR.PAV; pavm=(Qf>=pv['q0']-0.3)&(Qf<=pv['q1']+0.3)&(Pf>=pv['p0']-0.3)&(Pf<=pv['p1']+0.3)
tsub[pavm]=int(round((BR.RT+pv['h']+0.9)*100))
# tháp viễn thông: coi như cột cao tại chân tháp
print('ô top đổi:',(tsub!=tb).sum())
# k: cỏ
ksub=k[j0:j1+1,i0:i1+1]
lawn=np.zeros_like(valid)
for poly in LAWN+ALLEY+[WILLOW_BED,POCKET,NBANK,NBANK2]: lawn|=pmask(poly)
ksub[zone]=0; ksub[lawn&valid]=1
# ---- tuyến xe, check-in, quầy: cập nhật cao độ ----
def hat(x,z):
    fi=(x-gx0)/gs; fj=(z-gz0)/gs; i=int(np.floor(fi)); jj=int(np.floor(fj)); a=fi-i; b=fj-jj
    q=[h[jj,i],h[jj,i+1],h[jj+1,i],h[jj+1,i+1]]
    if min(q)<-32000: 
        q=[v for v in q if v>-32000]
        return (sum(q)/len(q)/100.0) if q else None
    return ((q[0]*(1-a)+q[1]*a)*(1-b)+(q[2]*(1-a)+q[3]*a)*b)/100.0
zfull=poly_mask(ZONE_E,gnx,gnz,gx0,gz0,gs)
def inzone(x,z): 
    i=int(round((x-gx0)/gs)); jj=int(round((z-gz0)/gs)); return zfull[jj,i]
nr=0
for r in j['routes']:
    for p in r['pts']:
        if inzone(p[0],p[1]):
            y=hat(p[0],p[1])
            if y is not None and abs(y-p[2])>0.01: p[2]=round(y,2); nr+=1
print('điểm tuyến xe đổi cao độ:',nr)
for c in j['checkins']:
    if inzone(c['x'],c['z']):
        y=hat(c['x'],c['z']); print('check-in',c['id'],c['y'],'->',y)
        if y is not None: c['y']=round(y,2)
for c in j['checkins']:
    if c['id']=='cauthang': c['desc']='Bậc thang lớn sáu nhịp nối đường Lê Đại Hành trên cao xuống sân trước chợ, bên cây bách tán cao và toà nhà trắng đầu cong có sân thượng.'
for nm,sv in j['stalls'].items():
    if inzone(sv['x'],sv['z']): print('quầy trong vùng:',nm,sv,hat(sv['x'],sv['z']))
# các vật đặt sẵn trong thế giới (gian, quầy, ki-ốt, điểm check-in, cổng...) và tuyến xe: nâng hạ theo mặt đất mới
def hat0(x,z):
    fi=(x-gx0)/gs; fj=(z-gz0)/gs; i=int(np.floor(fi)); jj=int(np.floor(fj)); a=fi-i; b=fj-jj
    q=[h0[jj,i],h0[jj,i+1],h0[jj+1,i],h0[jj+1,i+1]]
    if min(q)<-32000: return None
    return ((q[0]*(1-a)+q[1]*a)*(1-b)+(q[2]*(1-a)+q[3]*a)*b)/100.0
nbump=[0]
def bump(o,ki='y'):
    if not isinstance(o,dict) or ki not in o or 'x' not in o: return
    if not (gx0+1<o['x']<gx0+(gnx-2)*gs and gz0+1<o['z']<gz0+(gnz-2)*gs) or inzone(o['x'],o['z']): return
    a=hat0(o['x'],o['z']); b=hat(o['x'],o['z'])
    if a is None or b is None or abs(b-a)<=0.01: return
    o[ki]=round(o[ki]+(b-a),2); nbump[0]+=1
for key in ('booths','kiosks','checkins','audience'):
    for o in j.get(key,[]): bump(o)
for o in j['stalls'].values(): bump(o)
for key in ('stage','gate','man','balloon','portal','spawn','explore'): bump(j.get(key))
for r in j['routes']:
    for p in r['pts']:
        if inzone(p[0],p[1]): continue
        a=hat0(p[0],p[1]); b=hat(p[0],p[1])
        if a is not None and b is not None and abs(b-a)>0.01: p[2]=round(p[2]+(b-a),2); nbump[0]+=1
print('vật và điểm tuyến xe nâng hạ theo mặt đất mới:',nbump[0])
# ---- bản đồ nhỏ (1 px = 1 m) ----
b=base64.b64decode(j['map'].split(',')[1]); mm=np.asarray(Image.open(io.BytesIO(b)).convert('RGB')).copy()
BL=np.array([120,112,104]); AS=np.array([120,122,128]); GR=np.array([126,168,98])
mch=np.zeros((gnz,gnx),bool); mch[j0:j1+1,i0:i1+1]=chg|chg_top
for pz in range(mm.shape[0]):
    for px in range(mm.shape[1]):
        gi=px*2; gj=pz*2
        if gi>=gnx or gj>=gnz or not mch[gj,gi]: continue
        hv=h[gj,gi]
        if tuple(mm[pz,px])==tuple(AS) and hv>-32000 and not (i0<=gi<=i1 and j0<=gj<=j1 and zone[gj-j0,gi-i0] and not np.isnan(Hw[gj-j0,gi-i0])): continue
        if hv<=-32000: mm[pz,px]=BL
        elif k[gj,gi]==1: mm[pz,px]=GR
        else:
            v=int(round(186+2.13*hv/100.0)); mm[pz,px]=(v,v-6,v-16)
# mặt đất đã hoá nhựa (giữa đường và nhà) là màu đường trên bản đồ nhỏ; trừ viền lề, sân lát giữ lại, cỏ, nước
_A=np.load('curb_asph.npy')[:mm.shape[0],:mm.shape[1]]; _KF=np.load('curb_keepflat.npy'); _kf=tmask(_KF) if len(_KF) else np.zeros(Hk.shape,bool)
_sl=(slice(0,2*mm.shape[0],2),slice(0,2*mm.shape[1],2))
_m=_A&(h[_sl]>-32000)&(k[_sl]!=1)&(k[_sl]!=2)&(k[_sl]!=3)&np.isnan(Hw)[_sl]&~_kf[_sl]
mm[_m]=AS
# sân nhựa trước cầu: màu đường trên bản đồ nhỏ
im=Image.fromarray(mm); dr=ImageDraw.Draw(im)
for poly in PL['asphalt']: dr.polygon([((x-gx0)/(2*gs),(z-gz0)/(2*gs)) for x,z in poly],fill=tuple(int(v) for v in AS))
mm=np.asarray(im).copy()
for pz in range(mm.shape[0]):
    for px in range(mm.shape[1]):
        gi=px*2; gj=pz*2
        if gi<gnx and gj<gnz and i0<=gi<=i1 and j0<=gj<=j1 and blk[gj-j0,gi-i0] and h[gj,gi]<=-32000: mm[pz,px]=BL
# tầng trên: cầu đi bộ, cầu thang, sân thượng
j['decks']=DK['decks']; j['deckPath']=DK['path']; j['deckProps']=DK['props']
im=Image.fromarray(mm); dr=ImageDraw.Draw(im)
for d_ in DK['decks']:
    pp=np.array(d_['p']); cx,cz=pp.mean(0); y=d_['a']+d_['b']*cx+d_['c']*cz; v=int(round(186+2.13*y))
    dr.polygon([((x-gx0)/(2*gs),(z-gz0)/(2*gs)) for x,z in d_['p']],fill=(v,v-6,v-16))
mm=np.asarray(im).copy()
buf=io.BytesIO(); Image.fromarray(mm).save(buf,format='PNG',optimize=True)
j['map']='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
Image.fromarray(mm).save('minimap_new.png')
worldio.save(OUT,j,h,top,k,pre,post)
# ---- kiểm tra đi tới được như trong game ----
ok=(h!=-32768)&(k!=2)&(k!=3)
sp=j['spawn']; s0=(int(round((sp['z']-gz0)/gs)),int(round((sp['x']-gx0)/gs)))
from collections import deque
reach=np.zeros_like(ok); reach[s0]=True; dq=deque([s0])
while dq:
    a,b_=dq.popleft(); hc=int(h[a,b_])
    for da,db in ((0,1),(0,-1),(1,0),(-1,0)):
        c,d=a+da,b_+db
        if 0<=c<gnz and 0<=d<gnx and ok[c,d] and not reach[c,d] and abs(int(h[c,d])-hc)<=52: reach[c,d]=True; dq.append((c,d))
def rc(x,z): return bool(reach[int(round((z-gz0)/gs)),int(round((x-gx0)/gs))])
pts={'điểm xuất phát':(j['spawn']['x'],j['spawn']['z']),'cổng chợ đêm':(j['gate']['x'],j['gate']['z']),'trước nhà xám':PZ.GW(6,-3.2),'trước ki-ốt':PZ.KW(0,-3.6),'bãi xe':(-27.0,-80.0),'ngã ba':(-33.5,-108.5),'đầu cầu':BR.BW(-2.5,0),'dốc lên cầu':BR.BW(0.5,0),'gầm cầu s=24':BR.BW(24,0),'đường dưới cầu':BR.BW(52.4,2),'sân chợ dưới thang':BR.FW(9,6),'đỉnh thang':l2w(0.5,0),'giữa thang':l2w(16,2),'chân thang':l2w(UF+1,0),'sân chân thang':(2,32),'sân thượng':l2w(5,-18),'sân trên':(-47,10),'cỏ nam thang':(-30,42),'trước cửa hàng':l2w(UF+1.5,10),'trước toà trắng':l2w(32,-18),'bùng binh tây':(18,12),'bùng binh':(31.5,25),'bồn liễu':(-44.5,61),'vỉa hè LĐH':(-41,33)}
for nm,(x,z) in pts.items(): print(' tới được %-16s'%nm, rc(float(x),float(z)), 'h=%.2f'%(h[int(round((float(z)-gz0)/gs)),int(round((float(x)-gx0)/gs))]/100.0))
for c in j['checkins']: print(' check-in',c['id'],rc(c['x'],c['z']))
for nm,sv in j['stalls'].items(): print(' quầy',nm,rc(sv['x'],sv['z']+2.9))
print(' gian:',sum(rc(b_['x'],b_['z']+(3 if b_.get('face',1)>0 else -3)) for b_ in j['booths']),'/',len(j['booths']), '| tổng ô tới được',int(reach.sum()))
np.save('reach_new.npy',reach)
