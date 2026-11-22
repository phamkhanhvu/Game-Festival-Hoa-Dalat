# Hình khối chi tiết khu cầu thang chợ: bậc thang, lan can, chậu cây, đèn, toà nhà trắng đầu cong, cửa hàng đặc sản, cây bách tán, liễu, dãy khách sạn, tháp viễn thông
import numpy as np, sys
sys.path.insert(0,'/home/claude/work/build')
from mb import MB, lin, tile_uv, WHITE, PLAIN
from design import *
SHUT,BALC,WIDE=(0,0),(1,0),(2,0); SHOPA,SHOPB,BIGGLASS,ROOFT=(0,1),(1,1),(2,1),(3,1); PAVE,BILL,BRICK,NOISE=(0,2),(1,2),(2,2),(3,2); LOUV,STRIPE=(0,3),(1,3)
HWIN,ARCH,GLASS,GBAL=(0,4),(1,4),(2,4),(3,4); MANS,SHOP2,SIGNA,SIGNB=(0,5),(1,5),(2,5),(3,5); SIGNST,ROOFSIGN,LOGO,BILLG=(0,6),(1,6),(2,6),(3,6); ARAU,WILL,CONC,STONE=(0,7),(1,7),(2,7),(3,7)
TOP=(0,0,1,0.5); BOT=(0,0.5,1,1)
UH=np.array([DX,0,DZ]); VH=np.array([VX,0,VZ]); UP=np.array([0,1.0,0])
def wall(mb, a, b, y0, y1, tile=PLAIN, col=WHITE, sub=None, bays=1, ya=None, yb=None):
    """mặt đứng từ a (trái) tới b (phải) nhìn từ ngoài; a,b=(x,z). ya/yb: đỉnh nghiêng (y1 tại a, tại b)"""
    a=np.asarray(a,float); b=np.asarray(b,float); r=b-a; L=np.linalg.norm(r); n=np.array([-r[1],0,r[0]])/L
    for k in range(bays):
        p=a+r*k/bays; q=a+r*(k+1)/bays
        t0=y1 if ya is None else ya+(yb-ya)*k/bays; t1=y1 if ya is None else ya+(yb-ya)*(k+1)/bays
        mb.quad([(p[0],y0,p[1]),(q[0],y0,q[1]),(q[0],t1,q[1]),(p[0],t0,p[1])],tile,col,n,sub)
    return n
def lw(u,v): return np.array(l2w(u,v),float)
# ---------- mảng phủ theo địa hình ----------
def clip_poly(pts, a, b):
    """cắt đa giác 3D (x,y,z) theo nửa mặt phẳng bên trái cạnh a->b trong mặt xz (đa giác xz thuận chiều kim đồng hồ trên màn hình = trong ở bên phải), tự chọn dấu"""
    out=[]; n=len(pts)
    def side(p): return (b[0]-a[0])*(p[2]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    for i in range(n):
        p=pts[i]; q=pts[(i+1)%n]; sp=side(p); sq=side(q)
        if sp>=-1e-9: out.append(p)
        if (sp>1e-9 and sq<-1e-9) or (sp<-1e-9 and sq>1e-9):
            t=sp/(sp-sq); out.append(p+(q-p)*t)
    return out
def drape(mb, terr_tris, poly, off, tile, col, cell=2.5, curb=None, curbcol=None, curb_h=0.45, world_uv=True):
    poly=np.array(poly,float)
    # hướng đa giác: bảo đảm 'trong' cho dấu dương
    area=0.5*np.sum(poly[:,0]*np.roll(poly[:,1],-1)-np.roll(poly[:,0],-1)*poly[:,1])
    if area<0: poly=poly[::-1]
    mn=poly.min(0); mx=poly.max(0); n=len(poly); cnt=0
    orig_idx=list(range(n)) if area>=0 else list(range(n))[::-1]
    for t in terr_tris:
        if t[:,0].max()<mn[0] or t[:,0].min()>mx[0] or t[:,2].max()<mn[1] or t[:,2].min()>mx[1]: continue
        pts=[t[0].copy(),t[1].copy(),t[2].copy()]
        for i in range(n):
            pts=clip_poly(pts,poly[i],poly[(i+1)%n])
            if len(pts)<3: break
        if len(pts)<3: continue
        pts=np.array(pts); c=pts.mean(0); cx=np.floor(c[0]/cell)*cell; cz=np.floor(c[2]/cell)*cell
        P=pts.copy(); P[:,1]+=off
        uvf=lambda p: tile_uv(tile,np.clip((p[0]-cx)/cell,0,1),np.clip((p[2]-cz)/cell,0,1))
        mb.poly(P,tile,col,UP,uvf); cnt+=len(P)-2
        if curb:
            for i in range(n):
                e=i if area>=0 else (n-2-i)%n      # chỉ số cạnh theo thứ tự gốc
                if e not in curb: continue
                a=poly[i]; b=poly[(i+1)%n]; d=b-a; L=np.linalg.norm(d); nrm=np.array([d[1],0,-d[0]])/L
                for k in range(len(P)):
                    p=P[k]; q=P[(k+1)%len(P)]
                    dp=abs((b[0]-a[0])*(p[2]-a[1])-(b[1]-a[1])*(p[0]-a[0]))/L; dq=abs((b[0]-a[0])*(q[2]-a[1])-(b[1]-a[1])*(q[0]-a[0]))/L
                    if dp<1e-5 and dq<1e-5 and np.linalg.norm(p-q)>1e-4:
                        mb.quad([(p[0],p[1]-curb_h,p[2]),(q[0],q[1]-curb_h,q[2]),tuple(q),tuple(p)],PLAIN,curbcol if curbcol is not None else col,nrm)
    return cnt
# ---------- cầu thang ----------
def stairs(mb):
    TC=lin('#dfdacf'); RC=lin('#d2ccc1'); RC2=lin('#a8a297'); NOSE=lin('#f3efe7'); LC=lin('#d6d0c4'); rng=np.random.RandomState(3)
    for k in range(NF):
        us=US+k*PER
        for i in range(NR):
            u0=us+i*TREAD; ytop=U0-(k*NR+i)*RISE; yb=ytop-RISE
            ym=ytop-0.035
            mb.quad([P3(u0,SW,ym),P3(u0,-SW,ym),P3(u0,-SW,ytop),P3(u0,SW,ytop)],CONC,NOSE,UH,sub=(0,0.9,1,0.91))
            mb.quad([P3(u0,SW,yb),P3(u0,-SW,yb),P3(u0,-SW,ym),P3(u0,SW,ym)],CONC,np.stack([RC2,RC2,RC,RC]),UH,sub=(0,0.9,1,0.93))
            last=(i==NR-1)
            u1=u0+TREAD if not last else (us+PER if k<NF-1 else UF)
            t0=rng.uniform(0.02,0.6); th=0.03 if not last or k==NF-1 else 0.2
            mb.quad([P3(u1,SW,yb),P3(u1,-SW,yb),P3(u0,-SW,yb),P3(u0,SW,yb)],CONC,LC if (last and k<NF-1) else TC,UP,sub=(0,t0,1,t0+th))
    # lan can hai bên: mặt trong, mặt trên, mặt ngoài; đỉnh song song mũi bậc, cao 0,95
    PC=lin('#e7e3da'); CAP=lin('#f4f2ec'); H=0.95
    bp=[US-0.6,US]
    for k in range(NF):
        us=US+k*PER; bp.append(us+NR*TREAD)
        if k<NF-1: bp.append(us+PER)
    bp.append(UF+0.5)
    def ptop(u): return float(s_ramp(min(max(u,US),UF)))+H
    def pbot_out(u,s):
        if s<0 and u>=17.5: return Q-0.45          # phía bắc, đoạn dưới: nền sân lát
        return float(s_ramp(min(max(u,US),UF)))-1.3
    for s in (-1,1):
        vi=s*SW; vo=s*(SW+PW); nin=-s*VH; nout=s*VH
        for a,b in zip(bp[:-1],bp[1:]):
            ta,tb=ptop(a),ptop(b); ba=float(s_ramp(min(max(a,US),UF)))-0.5; bb=float(s_ramp(min(max(b,US),UF)))-0.5
            mb.quad([P3(a,vi,ba),P3(b,vi,bb),P3(b,vi,tb),P3(a,vi,ta)],PLAIN,PC,nin)
            mb.quad([P3(a,vo,pbot_out(a,s)),P3(b,vo,pbot_out(b,s)),P3(b,vo,tb),P3(a,vo,ta)],PLAIN,PC,nout)
            mb.quad([P3(a,vi,ta),P3(b,vi,tb),P3(b,vo,tb),P3(a,vo,ta)],PLAIN,CAP,UP)
        # đầu trên và đầu dưới lan can
        for uu,nn in ((bp[0],-UH),(bp[-1],UH)):
            t=ptop(uu); bo=min(float(s_ramp(min(max(uu,US),UF)))-0.5,pbot_out(uu,s))
            mb.quad([P3(uu,vi,bo),P3(uu,vo,bo),P3(uu,vo,t),P3(uu,vi,t)],PLAIN,PC,nn)
    return bp
def urn(mb, x, z, y, s=1.0):
    BODY=lin('#3f4a3a'); RIM=lin('#56634c'); PLANT=lin('#4f8f3e'); PL2=lin('#3f7a33')
    c=(x,z)
    mb.prism(c,0.26*s,0.20*s,y,y+0.14*s,6,BODY,cap=False)
    mb.prism(c,0.20*s,0.44*s,y+0.14*s,y+0.62*s,6,BODY,cap=False)
    mb.prism(c,0.44*s,0.33*s,y+0.62*s,y+0.86*s,6,RIM,cap=False)
    mb.prism(c,0.36*s,0.52*s,y+0.84*s,y+1.12*s,6,PL2,NOISE,cap=False,rot=0.5)
    mb.prism(c,0.52*s,0.0,y+1.12*s,y+1.55*s,6,PLANT,NOISE,cap=False,rot=0.5)
def lamp(mb, x, z, y, h=3.7, globes=4):
    POLE=lin('#262a2e'); GL=np.array([1.0,0.97,0.86]); c=(x,z)
    mb.prism(c,0.13,0.09,y,y+0.5,5,POLE,cap=False)
    mb.prism(c,0.065,0.05,y+0.5,y+h,5,POLE,cap=False)
    def globe(cx,cz,cy,r):
        mb.prism((cx,cz),0.0,r,cy-r,cy,5,GL,cap=False); mb.prism((cx,cz),r,0.0,cy,cy+r,5,GL,cap=False)
    globe(x,z,y+h+0.28,0.27)
    for k in range(globes):
        a=k*2*np.pi/globes+0.4; ax,az=np.cos(a),np.sin(a)
        ex,ez=x+ax*0.62,z+az*0.62
        mb.quad([(x,y+h-0.55,z),(ex,y+h-0.35,ez),(ex,y+h-0.29,ez),(x,y+h-0.49,z)],PLAIN,POLE,np.array([-az,0,ax]))
        globe(ex,ez,y+h-0.12,0.2)
def ball_tree(mb, x, z, y, h=4.2, r=1.5, col='#4c8a3f'):
    c=(x,z); T=lin('#5b4636'); G=lin(col); G2=lin(col,0.82)
    mb.prism(c,0.16,0.11,y,y+h*0.45,5,T,cap=False)
    mb.prism(c,r*0.55,r,y+h*0.40,y+h*0.62,7,G2,NOISE,cap=False)
    mb.prism(c,r,r*0.72,y+h*0.62,y+h*0.84,7,G,NOISE,cap=False)
    mb.prism(c,r*0.72,0.0,y+h*0.84,y+h,7,G,NOISE,cap=False)
# ---------- toà nhà trắng đầu cong ----------
def white_building(mb, deco=None):
    deco=deco or mb
    WH=lin('#f3f2ed'); WH2=lin('#e6e4dd'); FLOOR=lin('#d9d6ce'); yA=WA['roof']; yB=WB['roof']; v0=WA['v0']; v1=WA['v1']-0.03; vc=(WB['v0']+WB['v1'])/2
    u0,u1=WA['u0'],WA['u1']
    # khối cao: sàn sân thượng lát gạch, tường bắc và nam, mặt đông bằng kính nhìn ra sân khấu thấp
    nu,nv=4,6
    for i in range(nu):
        for j in range(nv):
            a,b=u0+(u1-u0)*i/nu,u0+(u1-u0)*(i+1)/nu; c,d=v0+(v1-v0)*j/nv,v0+(v1-v0)*(j+1)/nv
            mb.quad([P3(a,d,yA),P3(b,d,yA),P3(b,c,yA),P3(a,c,yA)],PAVE,lin('#e3ddd0'),UP)
    wall(mb,lw(u1,v0),lw(u0,v0),3.0,yA,PLAIN,WH)                      # bắc
    wall(mb,lw(u0,v1),lw(u1,v1),8.0,yA,PLAIN,WH)                      # nam (trên lan can thang)
    wall(mb,lw(u1,v1),lw(u1,v0),yB,yA-1.0,GLASS,WHITE,bays=8)         # đông: kính
    wall(mb,lw(u1,v1),lw(u1,v0),yA-1.0,yA,PLAIN,WH)                   # đông: băng trắng
    # lan can kính sân thượng (bắc, đông, nam)
    for a,b,n in ((lw(u1,v0),lw(u0,v0),6),(lw(u1,v1),lw(u1,v0),8),(lw(u0,v1),lw(u1,v1),6)): wall(mb,a,b,yA,yA+1.1,GBAL,WHITE,bays=n)
    # biển chữ trên mép đông
    for (va,vb,sub) in ((-16.0,-20.4,BOT),(-21.2,-25.6,TOP)):
        wall(mb,lw(u1-0.25,va),lw(u1-0.25,vb),yA+1.45,yA+3.65,ROOFSIGN,WHITE,sub)
        wall(mb,lw(u1-0.31,vb),lw(u1-0.31,va),yA+1.45,yA+3.65,PLAIN,lin('#d5d8dc'))            # mặt sau biển để trơn
        for vv in (va-0.3,vb+0.3): mb.obox(lw(u1-0.25,vv),UH[[0,2]],VH[[0,2]],0.06,0.06,yA,yA+1.6,lin('#8a8f96'),top=False)
    # dù và bàn cà phê trên sân thượng
    for k,(uu,vv) in enumerate([(2.5,-11),(7.5,-12.5),(3.0,-18),(8.5,-19.5),(3.5,-25.5),(9.0,-26)]):
        x,z=l2w(uu,vv); cu=lin(['#f4efe2','#e8843a','#f4efe2','#d9a23a','#e8843a','#f4efe2'][k])
        deco.prism((x,z),0.03,0.03,yA,yA+2.3,4,lin('#6b6f75'),cap=False); deco.prism((x,z),1.35,0.05,yA+2.0,yA+2.55,8,cu,cap=False)
        deco.prism((x,z),0.5,0.5,yA+0.70,yA+0.76,6,lin('#f1ede4'))
    # khối thấp đầu cong: đường bao đi từ góc tây-nam, qua mũi cong, tới góc tây-bắc
    R=WB['R']; uc=WB['uc']; NS=18
    out=[(WB['u0'],v1),(uc,v1)]+[(uc+R*np.cos(a),vc+(R-0.03)*np.sin(a)) for a in np.linspace(np.pi/2,-np.pi/2,NS+1)[1:-1]]+[(uc,v0),(WB['u0'],v0)]
    W=[lw(u,v) for u,v in out]
    yg=Q+4.2
    for k in range(len(W)-1):
        a,b=W[k],W[k+1]; L=np.linalg.norm(b-a); nb=max(1,int(round(L/2.4)))
        wall(mb,a,b,Q-0.5,yg,GLASS,lin('#ffffff',0.96),bays=nb)
        wall(mb,a,b,yg,yB,PLAIN,WH)
        wall(mb,a,b,yB,yB+1.05,GBAL,WHITE,bays=nb)
    # mái đón mỏng chạy quanh mũi cong
    CW=0.9
    def outw(k):
        a=W[max(k-1,0)]; b=W[min(k+1,len(W)-1)]; r=b-a; r/=np.linalg.norm(r); return np.array([-r[1],r[0]])
    for k in range(1,len(W)-2):
        a,b=W[k],W[k+1]; na,nb_=outw(k),outw(k+1); a2=a+na*CW; b2=b+nb_*CW
        mb.quad([(a[0],yg+0.16,a[1]),(a2[0],yg+0.16,a2[1]),(b2[0],yg+0.16,b2[1]),(b[0],yg+0.16,b[1])],PLAIN,WH,UP)
        mb.quad([(a2[0],yg-0.02,a2[1]),(b2[0],yg-0.02,b2[1]),(b2[0],yg+0.16,b2[1]),(a2[0],yg+0.16,a2[1])],PLAIN,WH2,np.array([na[0],0,na[1]]))
        mb.quad([(a[0],yg-0.02,a[1]),(b[0],yg-0.02,b[1]),(b2[0],yg-0.02,b2[1]),(a2[0],yg-0.02,a2[1])],PLAIN,WH2,-UP)
    # sàn sân thượng thấp (quạt từ tâm)
    ctr=lw(uc-2.0,vc)
    for k in range(len(W)-1):
        a,b=W[k],W[k+1]; mb.tri([(ctr[0],yB,ctr[1]),(a[0],yB,a[1]),(b[0],yB,b[1])],[tile_uv(PLAIN,.5,.5)]*3,FLOOR,UP)
    mb.tri([(ctr[0],yB,ctr[1]),(W[-1][0],yB,W[-1][1]),(W[0][0],yB,W[0][1])],[tile_uv(PLAIN,.5,.5)]*3,FLOOR,UP)
    # bể nước nông viền trắng
    pc=lw(16.9,-11.8); mb.obox(pc,UH[[0,2]],VH[[0,2]],2.6,1.9,yB,yB+0.45,WH,topcol=WH)
    mb.obox(pc,UH[[0,2]],VH[[0,2]],2.25,1.55,yB+0.3,yB+0.47,lin('#7fd3ea'),topcol=lin('#7fd3ea'))
    # vài chậu cây trên sân thượng thấp
    for uu,vv in ((24.0,-12.5),(26.5,-18.25),(24.0,-24.0)):
        x,z=l2w(uu,vv); urn(deco,x,z,yB,1.25)
    return W
# ---------- cửa hàng đặc sản ----------
def store(mb, ground_fn):
    MR=lin('#6a2a2c'); MR2=lin('#55201f'); CR=lin('#eadfcd'); v0=ST_F['v0']+0.03; v1=ST_F['v1']; u0=ST_F['u0']; u1=ST_F['u1']; top=ST_F['top']; ysh=Q+3.3
    # khối trước
    wall(mb,lw(u1,v1),lw(u1,v0),Q-0.4,ysh,SHOP2,WHITE,bays=3)
    L=v1-v0
    for k,(sub,tile) in enumerate(((BOT,SIGNST),(TOP,SIGNST),(BOT,SIGNST))):
        wall(mb,lw(u1,v1-L*k/3),lw(u1,v1-L*(k+1)/3),ysh,top,tile,WHITE,sub)
    wall(mb,lw(u0,v1),lw(u1,v1),Q-0.6,ysh,PLAIN,CR); wall(mb,lw(u0,v1),lw(u1,v1),ysh,top,PLAIN,MR)          # nam
    wall(mb,lw(u1,v0),lw(u0,v0),Q+0.5,top,PLAIN,MR)                                                           # bắc (trên lan can)
    wall(mb,lw(u0,v0),lw(u0,v1),5.0,top,PLAIN,MR2)                                                            # tây (trên mái ngói)
    mb.quad([P3(u0,v1,top-0.3),P3(u1,v1,top-0.3),P3(u1,v0,top-0.3),P3(u0,v0,top-0.3)],PLAIN,lin('#55524e'),UP)
    # mái đón trước cửa
    c0,c1=u1,u1+1.1
    mb.quad([P3(c0,v1,ysh+0.14),P3(c1,v1,ysh+0.14),P3(c1,v0,ysh+0.14),P3(c0,v0,ysh+0.14)],PLAIN,MR2,UP)
    mb.quad([P3(c1,v1,ysh-0.04),P3(c1,v0,ysh-0.04),P3(c1,v0,ysh+0.14),P3(c1,v1,ysh+0.14)],PLAIN,MR,UH)
    mb.quad([P3(c0,v1,ysh-0.04),P3(c1,v1,ysh-0.04),P3(c1,v0,ysh-0.04),P3(c0,v0,ysh-0.04)],PLAIN,MR2,-UP)
    # khối sau: mái ngói dốc về phía nam và về phía chân thang
    r0,r1=ST_R['u0'],ST_R['u1']; TILEC=lin('#b4553d')
    nu,nv=4,3
    for i in range(nu):
        for j in range(nv):
            a,b=r0+(r1-r0)*i/nu,r0+(r1-r0)*(i+1)/nu; c,d=v0+(v1+0.4-v0)*j/nv,v0+(v1+0.4-v0)*(j+1)/nv
            mb.quad([P3(a,d,store_roof(a,d)),P3(b,d,store_roof(b,d)),P3(b,c,store_roof(b,c)),P3(a,c,store_roof(a,c))],ROOFT,TILEC,UP)
    for i in range(nu):                                                                                       # tường nam khối sau
        a,b=r0+(r1-r0)*i/nu,r0+(r1-r0)*(i+1)/nu
        pa,pb=lw(a,v1),lw(b,v1); ga=ground_fn(pa[0],pa[1])-0.6; gb=ground_fn(pb[0],pb[1])-0.6
        mb.quad([(pa[0],ga,pa[1]),(pb[0],gb,pb[1]),(pb[0],float(store_roof(b,v1))-0.05,pb[1]),(pa[0],float(store_roof(a,v1))-0.05,pa[1])],PLAIN,CR,VH)
    pa,pb=lw(r0,v0),lw(r0,v1)                                                                                  # tường tây
    mb.quad([(pa[0],6.0,pa[1]),(pb[0],6.0,pb[1]),(pb[0],float(store_roof(r0,v1)),pb[1]),(pa[0],float(store_roof(r0,v0)),pa[1])],PLAIN,CR,-UH)
# ---------- cây ----------
def araucaria(mb, x, z, y, h=30.0):
    c=(x,z); T=lin('#5c4937'); G=[lin('#ffffff',0.95),lin('#e6f2e2',0.85),lin('#ffffff',0.78)]
    mb.prism(c,0.48,0.10,y-0.5,y+h-1.0,6,T,cap=False)
    n=13; yb=y+5.5
    for k in range(n):
        f=k/(n-1); R=3.7*(1-f)**0.85+0.75; yy=yb+(h-8.5)*f
        mb.prism(c,R,R*0.18,yy-0.25*R*0.3,yy+0.95,7,G[k%3],ARAU,cap=False,rot=k*0.45)
        mb.prism(c,R*0.55,R,yy-0.75,yy-0.25*R*0.3,7,G[(k+1)%3]*0.8,ARAU,cap=False,rot=k*0.45)
    mb.prism(c,0.8,0.0,y+h-2.6,y+h,6,G[0],ARAU,cap=False)
def willow(mb, x, z, y, s=1.0, rot=0.0):
    """liễu rủ: thân nghiêng nhẹ, vòm lá, các dải lá rủ nhọn đầu dài ngắn khác nhau (hở giữa các dải để thấy thân)"""
    c=(x,z); T=lin('#5a4a38'); A=lin('#ffffff',0.95); B=lin('#f2ffe0',0.80); rng=np.random.RandomState(int(abs(x*7+z*13))%1000)
    mb.prism(c,0.30*s,0.18*s,y,y+3.4*s,5,T,cap=False)
    mb.prism(c,2.5*s,0.0,y+5.3*s,y+6.4*s,8,A,WILL,cap=False,rot=rot)
    mb.prism(c,3.1*s,2.5*s,y+4.1*s,y+5.3*s,8,A,WILL,cap=False,rot=rot)
    NP=11
    for k in range(NP):
        a0=rot+k*2*np.pi/NP; w=2*np.pi/NP*0.86; a1=a0+w; am=(a0+a1)/2
        R=3.1*s; L=rng.uniform(1.9,3.1)*s; yt=y+4.1*s; yb=yt-L; rb=R*rng.uniform(0.9,1.02)
        p0=(x+R*np.cos(a0),yt,z+R*np.sin(a0)); p1=(x+R*np.cos(a1),yt,z+R*np.sin(a1))
        q0=(x+rb*np.cos(a0+w*0.12),yb+0.5*s,z+rb*np.sin(a0+w*0.12)); q1=(x+rb*np.cos(a1-w*0.12),yb+0.5*s,z+rb*np.sin(a1-w*0.12))
        tip=(x+rb*np.cos(am),yb,z+rb*np.sin(am)); nh=np.array([np.cos(am),0,np.sin(am)]); col=B if k%2 else A*0.9
        mb.quad([q0,q1,p1,p0],WILL,col,nh,sub=(0,0,1,0.8))
        mb.tri([q0,tip,q1],[tile_uv(WILL,0,0.8),tile_uv(WILL,0.5,1),tile_uv(WILL,1,0.8)],col,nh)
# ---------- nhà phố / khách sạn ----------
def shophouse(mb, a, b, depth, yg, floors, wallc, roof='flat', roofc='#8d8a84', parapet=0.7, signs=(), tanks=0, awning=None, side_k=0.9, mans=None, billboard=None):
    a=np.asarray(a,float); b=np.asarray(b,float); r=b-a; L=np.linalg.norm(r); r/=L; n=np.array([-r[1],r[0]]); back=-n
    WC=lin(wallc); SC=lin(wallc,side_k); y=yg
    for f in floors:
        h=f['h']; tiles=f['tiles']; nb=len(tiles)
        for k,t in enumerate(tiles):
            p=a+r*L*k/nb; q=a+r*L*(k+1)/nb
            tile,sub,col=(t+(None,None))[:3] if isinstance(t[0],tuple) else (t,None,None)
            wall(mb,p,q,y,y+h,tile,WC if col is None else col,sub)
        y+=h
    top=y; a2=a+back*depth; b2=b+back*depth
    ytop=top+(parapet if roof=='flat' else 0)
    wall(mb,b,b2,yg-1.6,ytop,PLAIN,SC); wall(mb,a2,a,yg-1.6,ytop,PLAIN,SC); wall(mb,b2,a2,yg-1.6,ytop,PLAIN,SC)
    wall(mb,a,b,yg-1.6,yg,PLAIN,SC)
    if roof=='flat':
        if parapet: wall(mb,a,b,top,ytop,PLAIN,WC)
        mb.quad([(a[0],top+0.05,a[1]),(b[0],top+0.05,b[1]),(b2[0],top+0.05,b2[1]),(a2[0],top+0.05,a2[1])],PLAIN,lin(roofc),UP)
    elif roof=='gable':
        rh=2.2; m1=(a+a2)/2; m2=(b+b2)/2; RC=lin(roofc); e=n*0.35
        mb.quad([(a[0]+e[0],top-0.1,a[1]+e[1]),(b[0]+e[0],top-0.1,b[1]+e[1]),(m2[0],top+rh,m2[1]),(m1[0],top+rh,m1[1])],ROOFT,RC,UP)
        mb.quad([(b2[0],top-0.1,b2[1]),(a2[0],top-0.1,a2[1]),(m1[0],top+rh,m1[1]),(m2[0],top+rh,m2[1])],ROOFT,RC,UP)
        for p,q,m,nn in ((a2,a,m1,-r),(b,b2,m2,r)):
            mb.tri([(p[0],top,p[1]),(q[0],top,q[1]),(m[0],top+rh,m[1])],[tile_uv(PLAIN,.5,.5)]*3,SC,np.array([nn[0],0,nn[1]]))
    if mans:
        mh,ms=mans; a3=a+back*ms; b3=b+back*ms; nb=2
        for k in range(nb):
            p=a+r*L*k/nb; q=a+r*L*(k+1)/nb; p3=a3+r*L*k/nb; q3=a3+r*L*(k+1)/nb
            mb.quad([(p[0],top,p[1]),(q[0],top,q[1]),(q3[0],top+mh,q3[1]),(p3[0],top+mh,p3[1])],MANS,WHITE,np.array([n[0],0.3,n[1]]))
        SL=lin('#5d636b')
        mb.quad([(a3[0],top+mh,a3[1]),(b3[0],top+mh,b3[1]),(b2[0],top+mh,b2[1]),(a2[0],top+mh,a2[1])],PLAIN,SL,UP)
        wall(mb,b,b2,top,top+mh,PLAIN,SL); wall(mb,a2,a,top,top+mh,PLAIN,SL); wall(mb,b2,a2,top,top+mh,PLAIN,SL)
        ytop=top+mh
    for (f0,f1,y0,y1,tile,sub,off) in signs:
        p=a+r*L*f0+n*off; q=a+r*L*f1+n*off; wall(mb,p,q,yg+y0,yg+y1,tile,WHITE,sub)
    if billboard:
        bw,bh,tile,sub=billboard; mid=(a+b)/2+back*1.2; p=mid-r*bw/2; q=mid+r*bw/2
        wall(mb,p,q,ytop+0.9,ytop+0.9+bh,tile,WHITE,sub)
        wall(mb,q+back*0.07,p+back*0.07,ytop+0.9,ytop+0.9+bh,PLAIN,lin('#cfd2d6'))
        for e in (p+r*0.4,q-r*0.4): mb.prism((e[0],e[1]),0.07,0.07,ytop,ytop+0.9,4,lin('#6f747a'),cap=False)
        ytop+=0.9+bh
    for k in range(tanks):
        c=a+r*L*(0.3+0.4*k)+back*(depth*0.6); mb.prism((c[0],c[1]),0.55,0.55,top+0.6,top+1.9,7,lin('#c9ced3'),capcol=lin('#e3e6ea'))
        mb.prism((c[0],c[1]),0.08,0.08,top,top+0.6,4,lin('#7b8087'),cap=False)
    if awning:
        col,dz=awning; p=a+n*0.02; q=b+n*0.02; p2=a+n*dz; q2=b+n*dz; yy=yg+floors[0]['h']
        mb.quad([(p2[0],yy-0.75,p2[1]),(q2[0],yy-0.75,q2[1]),(q[0],yy-0.1,q[1]),(p[0],yy-0.1,p[1])],PLAIN,lin(col),np.array([n[0],0.5,n[1]]))
    return ytop
def hotels(mb, gfn):
    def fl(h,*tiles): return dict(h=h,tiles=list(tiles))
    G=lambda a,b: float(gfn((a[0]+b[0])/2,(a[1]+b[1])/2))+0.18
    DK=lin('#aab6c2')
    # dãy phía nam lối sang đường (từ nam lên bắc)
    a,b=(-56.4,67.9),(-60.3,59.3)
    shophouse(mb,a,b,10.0,G(a,b),[fl(3.9,SHOPA,SHOPB,SHOPA)]+[fl(3.2,BALC,BALC,BALC)]*5,'#f2f0ea',parapet=0.9,tanks=2,signs=[(0.33,0.67,3.95,5.5,SIGNA,BOT,0.14)])
    a,b=(-60.4,59.1),(-62.0,54.7)
    shophouse(mb,a,b,9.8,G(a,b),[fl(3.8,SHOPB)]+[fl(3.2,HWIN,HWIN)]*4,'#efe8da',parapet=0.6,tanks=1,awning=('#c8402f',1.1))
    a,b=(-62.1,54.5),(-63.7,50.1)
    shophouse(mb,a,b,13.6,G(a,b),[fl(3.8,SHOPA)]+[fl(3.1,ARCH,ARCH)]*6,'#f7f6f2',parapet=0,mans=(2.8,0.9),billboard=(4.3,2.15,SIGNA,TOP),signs=[(0.1,0.9,3.2,4.3,SIGNB,BOT,0.16)])
    # dãy đối diện đỉnh thang (từ nam lên bắc)
    a,b=(-66.2,39.2),(-66.2,34.5)
    shophouse(mb,a,b,11.7,G(a,b),[fl(3.8,SHOPA)]+[fl(3.2,HWIN,HWIN)]*3,'#c7dbe8',parapet=0.7,awning=('#2f6fb0',1.0))
    a,b=(-66.2,34.3),(-66.2,29.6)
    shophouse(mb,a,b,10.5,G(a,b),[fl(3.8,SHOPB)]+[fl(3.2,WIDE)]*3,'#dc8a50',parapet=0.9,signs=[(0.22,0.78,7.3,9.9,LOGO,None,0.18)])
    a,b=(-66.2,29.6),(-66.2,24.9)
    shophouse(mb,a,b,10.0,G(a,b),[fl(3.8,SHOPA)]+[fl(3.2,SHUT)]*3,'#f0e2a8',roof='gable',roofc='#b4513a',awning=('#e0a62e',1.0))
    # dãy chéo quay ra ngã tư Khu Hòa Bình
    a,b=(-68.1,15.9),(-74.1,8.7)
    GD=(GLASS,None,lin('#8f9aa6'))
    shophouse(mb,a,b,11.5,G(a,b),[fl(4.0,GD,GD,GD,GD)]+[fl(3.3,BALC,BIGGLASS,BIGGLASS,BALC)]*4,'#b99670',parapet=1.0,roofc='#7d776e',tanks=1)
    a,b=(-74.1,8.7),(-77.1,5.1)
    shophouse(mb,a,b,10.4,G(a,b),[fl(3.8,SHOPB)]+[fl(3.2,WIDE)]*3,'#467377',parapet=0.8)
    a,b=(-77.1,5.1),(-80.1,1.4)
    GB=(GLASS,None,lin('#c9d4de'))
    shophouse(mb,a,b,12.8,G(a,b),[fl(4.0,GB,GB),fl(1.7,(PLAIN,None,lin('#24509a')))]+[fl(3.2,GB,GB)]*4,'#c2c6ca',parapet=0.8,roofc='#878c92',
              signs=[(0.14,0.86,4.03,5.67,SIGNB,TOP,0.12)],billboard=(4.2,4.2,BILLG,None))
def tower(mb, x, z, y, h=40.0, mast=7.0):
    RED=lin('#d0382c'); WHT=lin('#f1f1ef'); NS=8; hs=h/NS; w0,w1=2.3,0.55
    def hw(yy): return w0+(w1-w0)*(yy/h)
    C4=[(-1,-1),(1,-1),(1,1),(-1,1)]
    for s in range(NS):
        ya,yb=s*hs,(s+1)*hs; wa,wb=hw(ya),hw(yb); col=RED if s%2==0 else WHT
        for k in range(4):
            cx,cz=C4[k]; nx,nz=C4[(k+1)%4]
            A=np.array([x+cx*wa,y+ya,z+cz*wa]); B=np.array([x+cx*wb,y+yb,z+cz*wb]); A2=np.array([x+nx*wa,y+ya,z+nz*wa]); B2=np.array([x+nx*wb,y+yb,z+nz*wb])
            fn=np.array([(cx+nx)/2,0.05,(cz+nz)/2]); e=(A2-A)/np.linalg.norm(A2-A)
            t=0.2
            mb.quad([A,A+e*t,B+e*t,B],PLAIN,col,fn); mb.quad([A2-e*t,A2,B2,B2-e*t],PLAIN,col,fn)        # hai thanh đứng của mặt
            mb.quad([B,B2,B2-np.array([0,0.16,0]),B-np.array([0,0.16,0])],PLAIN,col,fn)                 # thanh ngang
            up=np.array([0,0.13,0])
            mb.quad([A,A+up,B2+up,B2],PLAIN,col,fn); mb.quad([A2,A2+up,B+up,B],PLAIN,col,fn)            # hai thanh chéo
    mb.prism((x,z),0.12,0.06,y+h,y+h+mast,4,RED,cap=False)
    PAN=lin('#eceff1')
    for k,(dy,ang) in enumerate(((h-2.5,0.3),(h-2.5,2.4),(h-2.5,4.5),(h-6.5,1.2),(h-6.5,3.6))):
        cx=x+np.cos(ang)*(hw(dy)+0.35); cz=z+np.sin(ang)*(hw(dy)+0.35)
        mb.obox((cx,cz),(np.cos(ang),np.sin(ang)),(-np.sin(ang),np.cos(ang)),0.12,0.28,y+dy,y+dy+2.0,PAN)
    for dy,ang in ((h-11.0,0.9),(h-14.0,4.0)):
        cx=x+np.cos(ang)*(hw(dy)+0.5); cz=z+np.sin(ang)*(hw(dy)+0.5)
        mb.prism((cx,cz),0.0,0.8,y+dy-0.25,y+dy,7,PAN,cap=False); mb.prism((cx,cz),0.8,0.0,y+dy,y+dy+0.25,7,PAN,cap=False)
    mb.obox((x,z),(1,0),(0,1),2.6,2.6,y-0.6,y+0.25,lin('#b7b2a8'))
