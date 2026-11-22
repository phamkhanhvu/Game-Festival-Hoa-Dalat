# Cầu đi bộ từ Khu Hòa Bình sang tầng trên chợ, cửa vào chợ phía cầu, cầu thang trắng hai nhịp lên sân thượng, nhà sân thượng
# Toạ độ cầu (s dọc cầu từ đầu Khu Hòa Bình, t ngang: dương là bên trái khi nhìn về chợ); toạ độ mặt đứng chợ (q dọc tường: dương về bên trái, p ra ngoài)
import numpy as np, sys
sys.path.insert(0,'/home/claude/work/build')
from mb import MB, lin, tile_uv, WHITE, PLAIN
from geom import wall, urn, PAVE, LOUV, SHUT, SHOP2, ARCH, GBAL, ROOFT, NOISE, STRIPE, UP
SIGNT=(2,3)
A=np.array([-19.0,-91.0]); W0=np.array([11.64,-40.39]); W1=np.array([47.0,-61.0])
FLEN=float(np.linalg.norm(W1-W0)); E=(W1-W0)/FLEN; NO=np.array([E[1],-E[0]])
_d0=np.array([0.62587737,0.77992148])
_M=np.array([[_d0[0],-E[0]],[_d0[1],-E[1]]]); _r=np.linalg.solve(_M,W0-A)
BLEN=float(_r[0]); O=A+_d0*BLEN; D=_d0; LB=np.array([D[1],-D[0]])
QW=-float(_r[1]); QE=FLEN+QW                      # mép tây và mép đông của mặt đứng
HW=3.5; PT=0.25; PH=1.05; SLAB=0.45
D1=12.8; RT=16.8; YA=15.7; SF0,SF1=2.0,42.0; F1=8.76; APR=-3.6
def deck_y(s):
    s=np.asarray(s,float); return np.where(s<=SF0,YA,np.where(s>=SF1,D1,YA+(D1-YA)*(s-SF0)/(SF1-SF0)))
def BW(s,t): return A+D*s+LB*t
def FW(q,p): return O+E*q+NO*p
def w2b(x,z): r=np.stack([np.asarray(x,float)-A[0],np.asarray(z,float)-A[1]],-1); return r@D, r@LB
def w2f(x,z): r=np.stack([np.asarray(x,float)-O[0],np.asarray(z,float)-O[1]],-1); return r@E, r@NO
CA=float(-D@NO); SA=float(LB@NO)                 # cos, sin góc lệch giữa trục cầu và pháp tuyến tường
def s_end(t,p=0.0): return BLEN-(p-t*SA)/CA      # s tại đó điểm (s,t) cách tường p
def B3(s,t,y): w=BW(s,t); return (float(w[0]),float(y),float(w[1]))
def F3(q,p,y): w=FW(q,p); return (float(w[0]),float(y),float(w[1]))
# cầu thang lên sân thượng (toạ độ mặt đứng)
PF=dict(q0=3.0,q1=6.0,p0=0.0,p1=4.3)              # chiếu chân thang, ngang mặt cầu
SQ0,SQ1=6.0,11.6; LANE_L=(2.3,4.3); LANE_U=(0.15,2.15); YM=(D1+RT)/2; NRS=12
ML=dict(q0=11.6,q1=13.6,p0=0.15,p1=4.3)
TLD=dict(q0=4.0,q1=6.0)
PAV=dict(q0=-4.0,q1=26.0,p0=-11.3,p1=-5.3,h=4.2)   # nhà trên sân thượng
def lantern(mb,x,z,y,h=3.3):
    POLE=lin('#23262a'); c=(x,z)
    mb.prism(c,0.12,0.08,y,y+0.45,5,POLE,cap=False); mb.prism(c,0.055,0.045,y+0.45,y+h,5,POLE,cap=False)
    mb.prism(c,0.11,0.19,y+h,y+h+0.36,4,np.array([1.0,0.95,0.80]),cap=False,rot=0.785); mb.prism(c,0.23,0.04,y+h+0.36,y+h+0.52,4,POLE,cap=False,rot=0.785)
def palm_pot(mb,x,z,y,s=1.0):
    TER=lin('#b5673f'); c=(x,z); G=lin('#4f8f3e'); G2=lin('#3e7a34')
    mb.prism(c,0.42*s,0.62*s,y,y+0.5*s,7,TER,cap=True,capcol=lin('#5a4634'))
    mb.prism(c,0.09*s,0.07*s,y+0.5*s,y+1.9*s,5,lin('#7a6a55'),cap=False)
    for k in range(6):
        a=k*np.pi/3+0.3; dx,dz=np.cos(a),np.sin(a); t=np.array([x,y+1.9*s,z]); tip=np.array([x+dx*1.25*s,y+1.55*s,z+dz*1.25*s]); mid=np.array([x+dx*0.6*s,y+2.2*s,z+dz*0.6*s]); w=np.array([-dz,0,dx])*0.22*s
        mb.tri([t,mid+w,mid-w],[tile_uv(NOISE,.5,.5)]*3,G,UP); mb.tri([mid+w,tip,mid-w],[tile_uv(NOISE,.5,.5)]*3,G2,UP)
def build(solid, deco, gfn, walk=None):
    """gfn(x,z): cao độ mặt đất. Trả về danh sách mảng đi được tầng trên (đa giác lồi + mặt phẳng)."""
    WHT=lin('#eeece6'); CAPW=lin('#f6f5f0'); PV=lin('#c9958a'); PVC=lin('#dcaea3'); OR=lin('#c8743a'); BAND=lin('#fbfaf5'); DARK=lin('#3a3632'); CREAM=np.array([235,231,218])/255.0
    patches=[]
    def patch(pts,y_fn,seg):
        pts=[(float(x),float(z)) for x,z in pts]
        P3=np.array([[x,z,1.0] for x,z in pts[:3]]); Y=np.array([float(y_fn(x,z)) for x,z in pts[:3]]); b,c,a=np.linalg.solve(P3,Y)
        patches.append(dict(p=[[round(x,2),round(z,2)] for x,z in pts],a=round(float(a),4),b=round(float(b),5),c=round(float(c),5),s=list(seg)))   # s: các đoạn của chuỗi mốc deck_path đi qua mảng này
    # ---------- mặt cầu ----------
    lanes=[(-HW,-1.2,PV),(-1.2,1.2,PVC),(1.2,HW,PV)]; NSG=24; ss=np.linspace(-1.0,BLEN,NSG+1)
    for (t0,t1,col) in lanes:
        for k in range(NSG):
            a0,a1=ss[k],ss[k+1]
            e0=min(a1,s_end(t0)) if k<NSG-1 else s_end(t0); e1=min(a1,s_end(t1)) if k<NSG-1 else s_end(t1)
            (walk if (walk is not None and k==0) else solid).quad([B3(a0,t0,deck_y(a0)),B3(a0,t1,deck_y(a0)),B3(e1,t1,deck_y(e1)),B3(e0,t0,deck_y(e0))],PAVE,col,UP)
        # dốc nối từ mặt đường Khu Hòa Bình lên mặt cầu
        ya=[float(gfn(*BW(APR,t)))+0.05 for t in (t0,t1)]
        (walk if walk is not None else solid).quad([B3(APR,t0,ya[0]),B3(APR,t1,ya[1]),B3(-1.0,t1,YA),B3(-1.0,t0,YA)],PAVE,col,UP)
    for sgn in (-1,1):
        t=sgn*HW; nrm=sgn*np.array([LB[0],0,LB[1]]); g0=float(gfn(*BW(APR,t))); g1=float(gfn(*BW(-1.0,t)))
        solid.quad([B3(APR,t,g0-0.3),B3(-1.0,t,g1-0.4),B3(-1.0,t,YA),B3(APR,t,g0+0.05)],PLAIN,WHT,nrm)
    # mép và đáy bản mặt cầu
    brk=[-1.0,SF0,SF1]
    for sgn in (-1,1):
        t=sgn*(HW+PT); nrm=sgn*np.array([LB[0],0,LB[1]]); se=s_end(sgn*HW) if sgn<0 else s_end(HW,PF['p1'])
        pts=brk+[se]
        for a0,a1 in zip(pts[:-1],pts[1:]):
            # mặt trong, mặt trên, mặt ngoài lan can (mặt ngoài kéo xuống đáy bản; đoạn mố kéo xuống đất)
            ti=sgn*HW; y0,y1=float(deck_y(a0)),float(deck_y(a1))
            solid.quad([B3(a0,ti,y0-0.05),B3(a1,ti,y1-0.05),B3(a1,ti,y1+PH),B3(a0,ti,y0+PH)],PLAIN,WHT,-nrm)
            solid.quad([B3(a0,ti,y0+PH),B3(a1,ti,y1+PH),B3(a1,t,y1+PH),B3(a0,t,y0+PH)],PLAIN,CAPW,UP)
            g0=min(y0-SLAB,float(gfn(*BW(a0,t)))-0.4) if a0<14 else y0-SLAB; g1=min(y1-SLAB,float(gfn(*BW(a1,t)))-0.4) if a1<14 else y1-SLAB
            solid.quad([B3(a0,t,g0),B3(a1,t,g1),B3(a1,t,y1+PH),B3(a0,t,y0+PH)],PLAIN,WHT,nrm)
        solid.quad([B3(se,sgn*HW,D1-SLAB),B3(se,t,D1-SLAB),B3(se,t,D1+PH),B3(se,sgn*HW,D1+PH)],PLAIN,WHT,np.array([D[0],0,D[1]]))
    # mố đầu cầu: tường hai bên xuống đất cho đoạn cầu thấp
    for sgn in (-1,1):
        t=sgn*(HW+PT); nrm=sgn*np.array([LB[0],0,LB[1]])
        for a0,a1 in ((SF0,8.0),(8.0,14.0)):
            y0,y1=float(deck_y(a0)),float(deck_y(a1)); g0=float(gfn(*BW(a0,t)))-0.4; g1=float(gfn(*BW(a1,t)))-0.4
            solid.quad([B3(a0,t,g0),B3(a1,t,g1),B3(a1,t,y1-SLAB+0.02),B3(a0,t,y0-SLAB+0.02)],PLAIN,WHT,nrm)
    for a0,a1 in ((SF0,SF1),(SF1,BLEN)):
        solid.quad([B3(a0,-HW-PT,deck_y(a0)-SLAB),B3(a1,-HW-PT,deck_y(a1)-SLAB),B3(a1,HW+PT,deck_y(a1)-SLAB),B3(a0,HW+PT,deck_y(a0)-SLAB)],PLAIN,lin('#d6d3cc'),-UP)
    # trụ cầu (đúng chỗ các trụ cũ) và xà mũ
    for sp in (20.4,37.9,49.6):
        c=BW(sp,0.0); gy=float(gfn(c[0],c[1])); yy=float(deck_y(sp))-SLAB
        solid.obox(c,D,LB,0.45,0.6,gy-0.6,yy-0.5,WHT,top=False); solid.obox(c,D,LB,0.55,HW+0.1,yy-0.5,yy,WHT,top=False,bottom=True)
    # đèn cột trên lan can, chậu cọ trước cửa
    for sp in (11.0,21.0,31.0,41.0,51.0):
        for sgn in (-1,1):
            c=BW(sp,sgn*(HW+PT/2)); lantern(deco,c[0],c[1],float(deck_y(sp))+PH)
    for (x,z,y,sc) in pots(): palm_pot(deco,x,z,y,sc)
    # mảng đi được: mặt cầu
    HI=HW-0.3
    patch([BW(-1.0,-HI),BW(-1.0,HI),BW(SF0,HI),BW(SF0,-HI)],lambda x,z:YA,(0,1))
    patch([BW(SF0,-HI),BW(SF0,HI),BW(SF1,HI),BW(SF1,-HI)],lambda x,z:deck_y(w2b(x,z)[0]),(1,1))
    patch([BW(SF1,-HI),BW(SF1,HI),BW(s_end(HI,0.35),HI),BW(s_end(-HI,0.35),-HI)],lambda x,z:D1,(1,2))
    # ---------- mặt đứng chợ phía cầu ----------
    def fw(q0,q1,y0,y1,tile=PLAIN,col=WHITE,sub=None,bays=1,p=0.0):
        wall(solid,FW(q1,p),FW(q0,p),y0,y1,tile,col,sub,bays)        # nhìn từ ngoài: trái là q lớn
    nb=10
    fw(QW,QE,F1,11.5,SHUT,CREAM,bays=nb)                                 # tầng 1: cửa chớp
    fw(QW,QE,11.5,12.62,PLAIN,DARK)                                     # băng bông gió zíc zắc
    per=1.4; zq=np.arange(QW,QE-1e-6,per); ZW=lin('#f3f1ea'); th=0.26
    for q0 in zq:
        qm=min(q0+per/2,QE); q1=min(q0+per,QE)
        for (a,b,ya,yb) in ((q0,qm,11.62,12.5-th),(qm,q1,12.5-th,11.62)):
            solid.quad([F3(a,0.03,ya),F3(b,0.03,yb),F3(b,0.03,yb+th),F3(a,0.03,ya+th)],PLAIN,ZW,np.array([NO[0],0,NO[1]]))
    fw(QW,QE,12.62,D1,PLAIN,BAND)
    DQ=2.6; PQ=3.3
    for (a,b) in ((QW,-PQ),(PQ,QE)):
        L=b-a; n2=max(1,int(round(L/3.4)))
        fw(a,b,D1,13.8,PLAIN,OR); fw(a,b,13.8,16.0,LOUV,WHITE,bays=n2)
    for (a,b) in ((-PQ,-DQ),(DQ,PQ)): fw(a,b,D1,16.0,PLAIN,OR)
    fw(-DQ,DQ,15.75,16.0,PLAIN,OR)
    fw(QW,QE,16.0,16.12,PLAIN,lin('#b5362c'))
    fw(QW,QE,16.12,RT,PLAIN,BAND)
    for (a,b) in ((QW,TLD['q0']),(TLD['q1'],QE)):
        fw(a,b,RT,RT+1.1,PLAIN,BAND)
        wall(solid,FW(a,-0.3),FW(b,-0.3),RT,RT+1.1,PLAIN,BAND)                                  # mặt trong tường mái
        solid.quad([F3(a,0.0,RT+1.1),F3(b,0.0,RT+1.1),F3(b,-0.3,RT+1.1),F3(a,-0.3,RT+1.1)],PLAIN,CAPW,UP)
    fw(-3.25,3.25,RT-0.55,RT+0.95,SIGNT,WHITE,sub=(0.035,0.15,0.965,0.34),p=0.04)             # chữ CHỢ ĐÀ LẠT
    # cửa vào: hốc lõm, quầy hàng bên trong, mái bạt sọc xanh trắng
    RC=1.8
    wall(solid,FW(DQ,0),FW(DQ,-RC),D1,15.75,PLAIN,lin('#8a5a36')); wall(solid,FW(-DQ,-RC),FW(-DQ,0),D1,15.75,PLAIN,lin('#8a5a36'))
    wall(solid,FW(DQ,-RC),FW(-DQ,-RC),D1,15.75,SHOP2,lin('#ffffff',0.55),bays=2)
    solid.quad([F3(-DQ,0,D1+0.01),F3(DQ,0,D1+0.01),F3(DQ,-RC,D1+0.01),F3(-DQ,-RC,D1+0.01)],PAVE,PV,UP)
    solid.quad([F3(-DQ,0,15.75),F3(DQ,0,15.75),F3(DQ,-RC,15.75),F3(-DQ,-RC,15.75)],PLAIN,lin('#d9d5cc'),-UP)
    NSTR=12; AQ=3.4; BL=lin('#2f66c4'); WH=lin('#f4f4f2'); AW=2.3
    for k in range(NSTR):
        a=-AQ+2*AQ*k/NSTR; b=-AQ+2*AQ*(k+1)/NSTR; col=BL if k%2==0 else WH
        solid.quad([F3(a,AW,15.25),F3(b,AW,15.25),F3(b,0.05,16.0),F3(a,0.05,16.0)],PLAIN,col,np.array([NO[0],0.5,NO[1]]))
        solid.quad([F3(a,AW,14.95),F3(b,AW,14.95),F3(b,AW,15.25),F3(a,AW,15.25)],PLAIN,col,np.array([NO[0],0,NO[1]]))
    for q in (-AQ+0.1,AQ-0.1): deco.prism(tuple(FW(q,AW-0.1)),0.04,0.04,D1,15.0,4,lin('#d9d9d6'),cap=False)
    # ---------- cầu thang trắng hai nhịp ----------
    NQ=np.array([E[0],0,E[1]]); NP=np.array([NO[0],0,NO[1]]); ST_T=lin('#e9e6de'); ST_R=lin('#c9c5bb'); BAL=lin('#f2f0ea'); BH=1.0; BT=0.15
    rise=(YM-D1)/NRS; tread=(SQ1-SQ0)/NRS
    # chiếu chân thang (ngang mặt cầu) nối mép trái cầu
    qd=PF['q0']
    solid.quad([F3(qd-0.6,PF['p0'],D1),F3(PF['q1'],PF['p0'],D1),F3(PF['q1'],PF['p1'],D1),F3(qd-0.6,PF['p1'],D1)],PAVE,PV,UP)
    solid.quad([F3(qd-0.6,PF['p0'],D1-0.3),F3(PF['q1'],PF['p0'],D1-0.3),F3(PF['q1'],PF['p1'],D1-0.3),F3(qd-0.6,PF['p1'],D1-0.3)],PLAIN,lin('#d6d3cc'),-UP)
    fwp=lambda q0,q1,p,y0,y1,col=BAL,ya=None,yb=None: wall(solid,FW(q1,p),FW(q0,p),y0,y1,PLAIN,col,ya=ya,yb=yb)
    def bal_q(q0,q1,p,yb0,yb1,yt0,yt1):
        """lan can đặc dọc theo q tại p; đáy và đỉnh nghiêng"""
        for pp,nn in ((p-BT/2,-NP),(p+BT/2,NP)):
            solid.quad([F3(q0,pp,yb0),F3(q1,pp,yb1),F3(q1,pp,yt1),F3(q0,pp,yt0)],PLAIN,BAL,nn)
        solid.quad([F3(q0,p-BT/2,yt0),F3(q1,p-BT/2,yt1),F3(q1,p+BT/2,yt1),F3(q0,p+BT/2,yt0)],PLAIN,CAPW,UP)
    def bal_p(q,p0,p1,yb,yt):
        for qq,nn in ((q-BT/2,-NQ),(q+BT/2,NQ)):
            solid.quad([F3(qq,p0,yb),F3(qq,p1,yb),F3(qq,p1,yt),F3(qq,p0,yt)],PLAIN,BAL,nn)
        solid.quad([F3(q-BT/2,p0,yt),F3(q-BT/2,p1,yt),F3(q+BT/2,p1,yt),F3(q+BT/2,p0,yt)],PLAIN,CAPW,UP)
    def flight(q_lo,q_hi,lane,y_lo,up_dir):
        """bậc đi lên theo chiều q tăng (up_dir=+1) hoặc giảm (-1)"""
        p0,p1=lane
        for i in range(NRS):
            qa=q_lo+up_dir*tread*i; qb=qa+up_dir*tread; ya=y_lo+rise*i
            solid.quad([F3(qa,p0,ya),F3(qa,p1,ya),F3(qa,p1,ya+rise),F3(qa,p0,ya+rise)],PLAIN,ST_R,-up_dir*NQ)
            solid.quad([F3(qa,p0,ya+rise),F3(qa,p1,ya+rise),F3(qb,p1,ya+rise),F3(qb,p0,ya+rise)],PLAIN,ST_T,UP)
        qe=q_lo+up_dir*tread*NRS
        solid.quad([F3(q_lo,p0,y_lo-0.3),F3(q_lo,p1,y_lo-0.3),F3(qe,p1,y_lo+rise*NRS-0.3),F3(qe,p0,y_lo+rise*NRS-0.3)],PLAIN,lin('#d6d3cc'),-UP)
    flight(SQ0,SQ1,LANE_L,D1,+1); flight(SQ1,SQ0,LANE_U,YM,-1)
    # chiếu nghỉ giữa và chiếu trên
    for (d_,y) in ((ML,YM),):
        solid.quad([F3(d_['q0'],d_['p0'],y),F3(d_['q1'],d_['p0'],y),F3(d_['q1'],d_['p1'],y),F3(d_['q0'],d_['p1'],y)],PLAIN,ST_T,UP)
        solid.quad([F3(d_['q0'],d_['p0'],y-0.3),F3(d_['q1'],d_['p0'],y-0.3),F3(d_['q1'],d_['p1'],y-0.3),F3(d_['q0'],d_['p1'],y-0.3)],PLAIN,lin('#d6d3cc'),-UP)
        fwp(d_['q0'],d_['q1'],d_['p1'],y-0.3,y); 
    solid.quad([F3(TLD['q0'],LANE_U[0],RT),F3(TLD['q1'],LANE_U[0],RT),F3(TLD['q1'],LANE_U[1],RT),F3(TLD['q0'],LANE_U[1],RT)],PLAIN,ST_T,UP)
    solid.quad([F3(TLD['q0'],-0.3,RT),F3(TLD['q1'],-0.3,RT),F3(TLD['q1'],LANE_U[0],RT),F3(TLD['q0'],LANE_U[0],RT)],PLAIN,ST_T,UP)
    solid.quad([F3(TLD['q0'],LANE_U[0],RT-0.3),F3(TLD['q1'],LANE_U[0],RT-0.3),F3(TLD['q1'],LANE_U[1],RT-0.3),F3(TLD['q0'],LANE_U[1],RT-0.3)],PLAIN,lin('#d6d3cc'),-UP)
    # lan can: nhịp dưới (mép ngoài), vách giữa hai nhịp, chiếu nghỉ, nhịp trên phía chiếu trên, chiếu chân thang
    bal_q(SQ0,SQ1,LANE_L[1],D1-0.3,YM-0.3,D1+BH,YM+BH)
    bal_q(SQ0,SQ1,(LANE_L[0]+LANE_U[1])/2,D1-0.3,YM-0.3,RT+BH,YM+BH)
    bal_q(ML['q0'],ML['q1'],ML['p1'],YM-0.3,YM-0.3,YM+BH,YM+BH)
    bal_p(ML['q1'],ML['p0'],ML['p1'],YM-0.3,YM+BH)
    bal_q(TLD['q0'],TLD['q1'],LANE_U[1],RT-0.3,RT-0.3,RT+BH,RT+BH)
    bal_p(TLD['q0'],-0.0,LANE_U[1],RT-0.3,RT+BH)
    bal_q(PF['q0']-0.6,PF['q1'],PF['p1'],D1-0.3,D1-0.3,D1+BH,D1+BH)
    # cột đỡ
    for (q,p,yt) in ((ML['q1']-0.25,0.5,YM-0.3),(ML['q1']-0.25,ML['p1']-0.3,YM-0.3),(PF['q1']-0.2,PF['p1']-0.25,D1-0.3),(SQ0+0.1,LANE_U[1]+0.08,RT-0.3)):
        c=FW(q,p); gy=float(gfn(c[0],c[1])); solid.obox(c,E,NO,0.2,0.2,gy-0.5,yt,WHT,top=False)
    # mảng đi được: chiếu chân thang, hai nhịp, chiếu nghỉ, chiếu trên
    I_=0.25
    patch([FW(PF['q0']-0.9,0.35),FW(PF['q1']-I_,0.35),FW(PF['q1']-I_,PF['p1']-I_),FW(PF['q0']-0.9,PF['p1']-I_)],lambda x,z:D1,(2,3))
    patch([FW(SQ0-I_,LANE_L[0]+I_),FW(SQ1,LANE_L[0]+I_),FW(SQ1,LANE_L[1]-I_),FW(SQ0-I_,LANE_L[1]-I_)],lambda x,z:D1+np.clip((w2f(x,z)[0]-SQ0)/(SQ1-SQ0),0,1)*(YM-D1),(4,4))
    patch([FW(ML['q0'],ML['p0']+I_),FW(ML['q1']-I_,ML['p0']+I_),FW(ML['q1']-I_,ML['p1']-I_),FW(ML['q0'],ML['p1']-I_)],lambda x,z:YM,(5,7))
    patch([FW(SQ0,LANE_U[0]+I_),FW(SQ1,LANE_U[0]+I_),FW(SQ1,LANE_U[1]-I_),FW(SQ0,LANE_U[1]-I_)],lambda x,z:RT+np.clip((w2f(x,z)[0]-SQ0)/(SQ1-SQ0),0,1)*(YM-RT),(8,8))
    patch([FW(TLD['q0']+I_,-0.9),FW(TLD['q1'],-0.9),FW(TLD['q1'],LANE_U[1]-I_),FW(TLD['q0']+I_,LANE_U[1]-I_)],lambda x,z:RT,(9,10))
    # ---------- sân thượng: nền lát, nhà sân thượng ----------
    RFC=lin('#e2ddd1')
    pf=PAV['p1']+0.2; sl=1.0/2.95                                   # mép đông của mái lùi dần vào theo chiều sâu
    roofp=[[(QW+0.45,-0.35),(QE-0.6,-0.35),(QE-0.6+sl*(pf+0.35),pf),(QW+0.45,pf)],
           [(QW+0.45,pf),(PAV['q0']-0.35,pf),(PAV['q0']-0.35,-11.4),(QW+0.45,-11.4)],
           [(PAV['q1']+0.35,pf),(QE-0.6+sl*(pf+0.35),pf),(QE-4.3,-11.2),(PAV['q1']+0.35,-11.2)]]
    for poly in roofp:
        pts=[F3(q,p,RT+0.03) for q,p in poly]; solid.poly(pts,PLAIN,RFC,UP)
        patch([FW(q,p) for q,p in poly],lambda x,z:RT+0.03,(11,11))
    # nhà sân thượng: trắng, cửa vòm, lan can mái
    q0,q1,p0,p1,h=PAV['q0'],PAV['q1'],PAV['p0'],PAV['p1'],PAV['h']; PW=lin('#f7f6f2')
    nbay=int(round((q1-q0)/2.5))
    wall(solid,FW(q1,p1),FW(q0,p1),RT,RT+h-0.6,ARCH,WHITE,bays=nbay); wall(solid,FW(q1,p1),FW(q0,p1),RT+h-0.6,RT+h,PLAIN,PW)
    wall(solid,FW(q0,p0),FW(q1,p0),RT,RT+h,PLAIN,PW)
    wall(solid,FW(q0,p1),FW(q0,p0),RT,RT+h-0.6,ARCH,WHITE,bays=2); wall(solid,FW(q0,p1),FW(q0,p0),RT+h-0.6,RT+h,PLAIN,PW)
    wall(solid,FW(q1,p0),FW(q1,p1),RT,RT+h-0.6,ARCH,WHITE,bays=2); wall(solid,FW(q1,p0),FW(q1,p1),RT+h-0.6,RT+h,PLAIN,PW)
    solid.quad([F3(q0,p0,RT+h),F3(q1,p0,RT+h),F3(q1,p1,RT+h),F3(q0,p1,RT+h)],PLAIN,lin('#d9d6ce'),UP)
    wall(solid,FW(q1,p1+0.02),FW(q0,p1+0.02),RT+h,RT+h+0.9,GBAL,WHITE,bays=nbay)
    return patches
def low_buildings(solid, gfn):
    """hai dãy nhà thấp hai bên cầu (mái thấp hơn mặt cầu như trong ảnh)"""
    def house(c4, wall_top, ridge, wallc, roofc, hip=True):
        c=np.array(c4,float); ctr=c.mean(0)
        e1=c[1]-c[0]; e2=c[3]-c[0]
        if np.linalg.norm(e1)<np.linalg.norm(e2): c=c[[1,2,3,0]]; e1=c[1]-c[0]; e2=c[3]-c[0]
        g=min(float(gfn(x,z)) for x,z in c)-0.6; WC=lin(wallc); RC=lin(roofc)
        for k in range(4):
            a,b=c[k],c[(k+1)%4]; m=(a+b)/2; out=m-ctr
            p,q=(a,b) if (-(b-a)[1]*out[0]+(b-a)[0]*out[1])>0 else (b,a)
            wall(solid,p,q,g,wall_top,PLAIN,WC)
        ins=0.28 if hip else 0.0
        r0=(c[0]+c[3])/2+(e1)*ins; r1=(c[1]+c[2])/2-(e1)*ins
        ov=0.45; cc=[ctr+(v-ctr)*(1+ov/np.linalg.norm(v-ctr)) for v in c]
        P=lambda v,y:(float(v[0]),y,float(v[1]))
        solid.quad([P(cc[0],wall_top-0.1),P(cc[1],wall_top-0.1),P(r1,ridge),P(r0,ridge)],ROOFT,RC,UP)
        solid.quad([P(cc[2],wall_top-0.1),P(cc[3],wall_top-0.1),P(r0,ridge),P(r1,ridge)],ROOFT,RC,UP)
        for (u,v,r) in ((cc[3],cc[0],r0),(cc[1],cc[2],r1)):
            solid.tri([P(u,wall_top-0.1),P(v,wall_top-0.1),P(r,ridge)],[tile_uv(ROOFT,0,1),tile_uv(ROOFT,1,1),tile_uv(ROOFT,.5,0)],RC*0.92,UP if hip else np.array([0,0.2,0])+np.array([(r-ctr)[0],0,(r-ctr)[1]]))
    house([(4.4,-69.5),(8.1,-72.4),(16.7,-61.6),(13.0,-58.7)],10.9,12.7,'#e8d59a','#8d9197',hip=True)      # nhà vàng mái xám bên trái
    house([(-5.7,-58.3),(-2.0,-61.2),(5.4,-52.7),(1.7,-49.7)],9.9,11.5,'#d9d6cf','#8a8e94',hip=False)       # dãy mái tôn xám bên phải

PIERS=(20.4,37.9,49.6)
def columns():
    """tâm các cột đỡ cầu thang (toạ độ thế giới)"""
    return [tuple(FW(q,p)) for (q,p) in ((ML['q1']-0.25,0.5),(ML['q1']-0.25,ML['p1']-0.3),(PF['q1']-0.2,PF['p1']-0.25),(SQ0+0.1,LANE_U[1]+0.08))]
def deck_path(gfn):
    """chuỗi điểm mốc [x,z,y] cho chạm-để-đi ở tầng trên: từ mặt đường đầu cầu, qua cầu, hai nhịp thang, lên sân thượng"""
    lu=(LANE_U[0]+LANE_U[1])/2; ll=(LANE_L[0]+LANE_L[1])/2; out=[]
    def b(s,t,y=None):
        w=BW(s,t); out.append([round(float(w[0]),2),round(float(w[1]),2),round(float(deck_y(s) if y is None else y),2)])
    def f(q,p,y):
        w=FW(q,p); out.append([round(float(w[0]),2),round(float(w[1]),2),round(float(y),2)])
    w=BW(APR-1.4,0.0); out.append([round(float(w[0]),2),round(float(w[1]),2),round(float(gfn(w[0],w[1])),2)])
    b(0.0,0.0); b(SF1,0.0); f(2.9,2.6,D1); f(5.5,ll,D1); f(SQ1,ll,YM); f(ML['q0']+0.9,ll,YM); f(ML['q0']+0.9,lu,YM); f(SQ1,lu,YM); f(SQ0,lu,RT); f(5.1,lu,RT); f(5.1,-0.6,RT); f(5.1,-1.9,RT+0.03)
    return out

def pots():
    """chậu cọ trên mặt cầu: hai bên cửa chợ và dọc mép cầu; (x, z, cao độ đặt, cỡ)"""
    out=[]
    for (q,p,sc) in ((-3.05,0.75,1.0),(3.05,0.75,1.0)):
        c=FW(q,p); out.append((float(c[0]),float(c[1]),D1,sc))
    for (s_,t,sc) in ((BLEN-11.0,-(HW-0.6),0.85),(BLEN-21.0,HW-0.6,0.85)):
        c=BW(s_,t); out.append((float(c[0]),float(c[1]),float(deck_y(s_)),sc))
    return out
