# Khu đầu cầu phía Khu Hòa Bình (lối vào cầu đi bộ sang chợ), dựng theo 7 ảnh góc nhìn quanh số 31 Khu Hòa Bình:
# nhà xám cũ ba tầng có hàng quán dưới mái hiên (bên trái lối lên cầu), ki-ốt bên phải, đảo cây bách có hàng rào cắt tỉa,
# cột đèn, cột điện, sân nhựa trước cầu, tường tấm bê tông và băng lam của khối rạp Hòa Bình.
# Biển hiệu là chữ chung (TIỆM ẢNH, CÀ PHÊ, KI-ỐT SỐ 1, BÃI ĐẬU XE), không dùng tên cửa hàng thật.
import numpy as np, sys, json
sys.path.insert(0,'/home/claude/work/build')
from mb import MB, lin, tile_uv, WHITE, PLAIN
from geom import wall, drape, SHOPA, SHOPB, SHOP2, NOISE, STRIPE, SIGNST, ROOFSIGN, ARAU, UP, TOP, BOT
SIGNC,OLDWIN,GREYW,FINS=(4,0),(5,0),(6,0),(7,0); VENT,PANEL,FLOWER=(4,1),(5,1),(6,1); SIGND=(4,2)
# ---- nhà xám ba tầng (thay hai nhà phố 1357, 1404) ----
G0=np.array([-19.2,-109.9]); GU=np.array([6.5,11.0]); GU=GU/np.linalg.norm(GU); GV=np.array([GU[1],-GU[0]])
GLEN=12.8; GDEP=9.4
def GW(u,v): return G0+GU*u+GV*v
# ---- ki-ốt bên phải lối lên cầu ----
KC=np.array([-28.4,-89.2]); KU=np.array([0.9707,-0.2402]); KV=np.array([-KU[1],KU[0]]); KL=7.6; KD=3.4; KH=2.9
def KW(u,v): return KC+KU*u+KV*v
# ---- đảo cây ở góc tây bắc bãi xe (sau ki-ốt): bồn nâng, hàng rào cắt tỉa, cụm bách ----
IBX0,IBX1,IBZ0,IBZ1=-37.4,-32.0,-86.4,-80.6; IBH=0.3
TREES=[(-35.7,-84.6,9.5,1.3),(-34.2,-85.0,11.0,1.45),(-33.0,-84.1,10.0,1.35),(-34.9,-82.7,11.6,1.5),(-33.4,-82.3,8.6,1.2)]   # (x, z, cao, bán kính)
GLAMPS=[(-38.0,-87.1),(-31.3,-80.0)]; UPOLE=(-34.9,-88.3)
# ---- sân nhựa trước cầu ----
FS=[(-29.8,-104.1),(-18.9,-96.9),(-24.6,-90.4),(-32.4,-88.4),(-36.1,-88.3)]
FN=[(-28.2,-104.7),(-16.2,-96.5),(-13.0,-99.4),(-19.6,-110.6)]
ASPH=np.array([0.106,0.114,0.125])
# ---- khối rạp Hòa Bình: bốn góc thân nhà ----
CNE=np.array([-53.7,-107.7]); CNW=np.array([-72.6,-111.7]); CSW=np.array([-85.0,-53.0]); CSE=np.array([-66.0,-49.0])
PARKSIGN=(-38.5,-83.4)
def P3(p,y): return (float(p[0]),float(y),float(p[1]))
def parasols():
    """dù che của hàng rong trước nhà xám: (x, z, bán kính, màu)"""
    out=[]
    for (u,v,r,col) in ((5.0,-4.4,1.25,'#f2f0ea'),(6.5,-5.3,1.15,'#cdb89a'),(3.3,-5.9,1.2,'#b9a9c9'),(GLEN+2.3,-1.4,1.6,'#c8392f')):
        p=GW(u,v); out.append((float(p[0]),float(p[1]),r,col))
    return out
def parasol(mb,x,z,y,r,col):
    c=(x,z); mb.prism(c,0.035,0.03,y,y+2.25,4,lin('#d8d8d4'),cap=False)
    mb.prism(c,r,0.06,y+1.95,y+2.4,8,lin(col),cap=False); mb.prism(c,0.34,0.3,y,y+0.36,6,lin('#b5673f'),cap=True,capcol=lin('#caa05a'))
def cypress(mb,x,z,y,h,r):
    c=(x,z); G1=lin('#ffffff',0.62); G2=lin('#e6f2e2',0.74)
    mb.prism(c,0.2,0.16,y,y+1.1,5,lin('#4a3a2c'),cap=False)
    mb.prism(c,r*1.15,r*0.8,y+0.7,y+h*0.38,7,G1,ARAU,cap=False,rot=0.3)
    mb.prism(c,r*0.95,r*0.5,y+h*0.3,y+h*0.72,7,G2,ARAU,cap=False,rot=0.9)
    mb.prism(c,r*0.62,0.0,y+h*0.62,y+h,7,G1,ARAU,cap=False,rot=0.1)
def green_lamp(mb,x,z,y,h=4.3):
    G=lin('#2f6b4a'); c=(x,z); GL=np.array([1.0,0.97,0.86])
    mb.prism(c,0.16,0.1,y,y+0.6,6,G,cap=False); mb.prism(c,0.07,0.055,y+0.6,y+h,5,G,cap=False)
    for k,(yy,r) in enumerate(((h-1.25,0.52),(h-0.75,0.42),(h-0.28,0.32))):
        mb.prism(c,r,0.08,y+yy,y+yy+0.3,6,G,cap=False); mb.prism(c,0.13,0.13,y+yy-0.2,y+yy,5,GL,cap=False)
def globe_post(mb,x,z,y,h=2.7,r=0.24):
    W=lin('#f4f3ee'); GL=np.array([1.0,0.98,0.92]); c=(x,z)
    mb.prism(c,0.09,0.06,y,y+0.35,5,W,cap=False); mb.prism(c,0.045,0.04,y+0.35,y+h,5,W,cap=False)
    mb.prism(c,0.05,r,y+h,y+h+r,6,GL,cap=False); mb.prism(c,r,0.03,y+h+r,y+h+2*r,6,GL,cap=False)
def build(walk,solid,deco,gfn,terr):
    """gfn(x,z): cao độ mặt đất; terr: tam giác địa hình quanh khu này. Trả về dict vật cản cho lưới đi lại."""
    NU=np.array([GU[0],0,GU[1]]); NV=np.array([GV[0],0,GV[1]])
    rects=[]; discs=[]
    # ================= sân nhựa trước cầu =================
    n=drape(walk,terr,FS,0.10,PLAIN,ASPH)+drape(walk,terr,FN,0.10,PLAIN,ASPH)
    # ================= nhà xám ba tầng =================
    gy=float(gfn(*GW(GLEN/2,-1.0))); yb=gy-2.6
    y1=gy+3.3; y2=gy+3.52; y3=gy+4.1; y4=gy+7.6; y5=gy+11.1; y6=gy+11.45; y7=gy+11.95
    DK=lin('#ffffff',0.62)
    def face(a,b,nb,shops,canopy=True):
        """một mặt đứng từ a (trái) tới b (phải): tầng trệt hàng quán, băng ô thoáng, hai tầng cửa sổ"""
        a=np.asarray(a,float); b=np.asarray(b,float)
        wall(solid,a,b,yb,gy,PLAIN,lin('#8f8d87'))
        for k,tl_ in enumerate(shops):
            p=a+(b-a)*k/len(shops); q=a+(b-a)*(k+1)/len(shops); wall(solid,p,q,gy,y1,tl_,DK)
        wall(solid,a,b,y1,y3,VENT,WHITE,bays=max(2,int(round(np.linalg.norm(b-a)/2.2))))
        for (ya,ybb) in ((y3,y4),(y4,y5)): wall(solid,a,b,ya,ybb,OLDWIN,WHITE,bays=nb)
        wall(solid,a,b,y5,y7,GREYW,lin('#ffffff',0.92),sub=(0,0,1,0.25),bays=nb)
    Wa,Wb=GW(0,0),GW(GLEN,0)                      # mặt tây (ra sân trước cầu): trái là đầu bắc
    Sa,Sb=GW(GLEN,0),GW(GLEN,GDEP)                # mặt nam (về phía cầu)
    Na,Nb=GW(0,GDEP),GW(0,0)                      # mặt bắc (đường Nguyễn Chí Thanh)
    Ea,Eb=GW(GLEN,GDEP),GW(0,GDEP)                # mặt đông (giáp nhà bên)
    face(Wa,Wb,3,(SHOPB,SHOP2,SHOPA)); face(Sa,Sb,2,(SHOP2,SHOPB)); face(Na,Nb,2,(SHOPA,SHOPB))
    wall(solid,Ea,Eb,yb,y7,GREYW,lin('#ffffff',0.9),bays=3)
    # mảng lam đứng giữa mặt tây (nổi ra 12 cm), viền trên dưới
    b0=GLEN/3+0.45; b1=2*GLEN/3-0.45; o=-0.12
    wall(solid,GW(b0,o),GW(b1,o),y3+0.35,y5-0.3,FINS,WHITE)
    wall(solid,GW(b0,0),GW(b0,o),y3+0.35,y5-0.3,PLAIN,lin('#a9a9a3')); wall(solid,GW(b1,o),GW(b1,0),y3+0.35,y5-0.3,PLAIN,lin('#a9a9a3'))
    # mái đua và mái bằng
    c=GW(GLEN/2,GDEP/2); solid.obox(c,GU,GV,GLEN/2+0.35,GDEP/2+0.35,y5,y6,lin('#bdbdb7'),top=True,bottom=True)
    solid.quad([P3(GW(0,0),y7-0.35),P3(GW(GLEN,0),y7-0.35),P3(GW(GLEN,GDEP),y7-0.35),P3(GW(0,GDEP),y7-0.35)],PLAIN,lin('#8c8a84'),UP)
    for (a,b) in ((Wb,Wa),(Sb,Sa),(Nb,Na),(Eb,Ea)):       # mặt trong tường chắn mái
        wall(solid,a,b,y7-0.35,y7,PLAIN,lin('#a3a39d'))
    # buồng thang trên mái (thấy ở góc trái ảnh)
    solid.obox(GW(2.4,GDEP-2.6),GU,GV,1.8,1.9,y7-0.35,y7+2.1,lin('#b4b4ae'),top=True)
    # mái hiên tầng trệt: mặt tây và mặt nam, cột mảnh đỡ mép ngoài
    CAN=lin('#5b5a56'); CW=1.7
    solid.obox(GW(GLEN/2+CW/2-0.1,-CW/2),GU,GV,GLEN/2+CW/2+0.1,CW/2,y1,y2,CAN,top=True,bottom=True)
    solid.obox(GW(GLEN+CW/2,GDEP/2),GU,GV,CW/2,GDEP/2,y1,y2,CAN,top=True,bottom=True)
    for u in (0.15,GLEN/3,2*GLEN/3,GLEN+CW-0.15):
        p=GW(u,-CW+0.12); deco.prism((p[0],p[1]),0.06,0.06,gy,y1,4,lin('#6e6d68'),cap=False); discs.append((float(p[0]),float(p[1]),0.22))
    p=GW(GLEN+CW-0.15,GDEP-0.2); deco.prism((p[0],p[1]),0.06,0.06,gy,y1,4,lin('#6e6d68'),cap=False); discs.append((float(p[0]),float(p[1]),0.22))
    # biển: TIỆM ẢNH (trên mái hiên, gian phải), GIẢI KHÁT · CÀ PHÊ (mép mái hiên, gian trái), hộp đèn CÀ PHÊ ở góc về phía cầu
    wall(solid,GW(7.7,-0.16),GW(11.9,-0.16),y2+0.05,y2+1.3,SIGNC,WHITE,sub=(0,0,1,76/256.0))
    wall(solid,GW(1.0,-CW-0.03),GW(4.2,-CW-0.03),y1-0.5,y1+0.14,SIGNC,WHITE,sub=(0,78/256.0,1,126/256.0))
    bx=GW(GLEN+0.75,-0.95); hb=0.62
    for (a,b) in ((bx-GU*hb-GV*hb,bx+GU*hb-GV*hb),(bx+GU*hb-GV*hb,bx+GU*hb+GV*hb),(bx+GU*hb+GV*hb,bx-GU*hb+GV*hb),(bx-GU*hb+GV*hb,bx-GU*hb-GV*hb)):
        wall(solid,a,b,y2,y2+1.15,ROOFSIGN,WHITE,sub=BOT)
    solid.quad([P3(bx-GU*hb-GV*hb,y2+1.15),P3(bx+GU*hb-GV*hb,y2+1.15),P3(bx+GU*hb+GV*hb,y2+1.15),P3(bx-GU*hb+GV*hb,y2+1.15)],PLAIN,lin('#e6e4de'),UP)
    rects.append(dict(c=[float(v) for v in GW(GLEN/2,GDEP/2)],u=[float(GU[0]),float(GU[1])],hu=GLEN/2+0.25,hv=GDEP/2+0.25))
    ngb=solid.ntri
    # dù hàng rong
    for (x,z,r,col) in parasols():
        parasol(deco,x,z,float(gfn(x,z))+0.1,r,col); discs.append((x,z,0.4))
    # ================= ki-ốt =================
    ky=float(gfn(*KC))+0.02; CH=lin('#3a3a3e'); CH2=lin('#2b2b2f')
    f0,f1=KW(KL/2,-KD/2),KW(-KL/2,-KD/2)          # mặt trước: trái là đầu đông (phía cầu)
    wall(solid,f0,f1,ky-0.6,ky+1.0,PLAIN,CH2)
    wall(solid,f0,f1,ky+1.0,ky+2.3,SHOP2,lin('#ffffff',0.8),bays=3)
    wall(solid,f0,f1,ky+2.3,ky+KH,PLAIN,CH)
    wall(solid,KW(1.7,-KD/2-0.03),KW(-1.7,-KD/2-0.03),ky+2.34,ky+KH-0.04,SIGNST,WHITE,sub=TOP)
    wall(solid,KW(-KL/2,-KD/2),KW(-KL/2,KD/2),ky-0.6,ky+KH,PLAIN,CH); wall(solid,KW(-KL/2,KD/2),KW(KL/2,KD/2),ky-0.6,ky+KH,PLAIN,CH2); wall(solid,KW(KL/2,KD/2),KW(KL/2,-KD/2),ky-0.6,ky+KH,PLAIN,CH)
    solid.quad([P3(KW(KL/2,-KD/2),ky+KH),P3(KW(-KL/2,-KD/2),ky+KH),P3(KW(-KL/2,KD/2),ky+KH),P3(KW(KL/2,KD/2),ky+KH)],PLAIN,lin('#55555a'),UP)
    # mái che trước quầy
    a0,a1=KW(KL/2+0.2,-KD/2),KW(-KL/2-0.2,-KD/2); b0_,b1_=KW(KL/2+0.2,-KD/2-1.25),KW(-KL/2-0.2,-KD/2-1.25)
    solid.quad([(b0_[0],ky+2.02,b0_[1]),(b1_[0],ky+2.02,b1_[1]),(a1[0],ky+2.32,a1[1]),(a0[0],ky+2.32,a0[1])],PLAIN,lin('#26303c'),UP)
    # biển trên mái: CÀ PHÊ (trái) và KI-ỐT SỐ 1 (phải); mặt sau che kín
    for (ua,ub,sub) in ((KL/2,0.0,(0,130/256.0,1,190/256.0)),(0.0,-KL/2,(0,194/256.0,1,254/256.0))):
        wall(solid,KW(ua,-KD/2+0.02),KW(ub,-KD/2+0.02),ky+KH,ky+KH+0.95,SIGNC,WHITE,sub=sub)
    wall(solid,KW(-KL/2,-KD/2+0.1),KW(KL/2,-KD/2+0.1),ky+KH,ky+KH+0.95,PLAIN,CH2)
    rects.append(dict(c=[float(KC[0]),float(KC[1])],u=[float(KU[0]),float(KU[1])],hu=KL/2+0.25,hv=KD/2+0.25))
    # ================= đảo cây =================
    cx,cz=(IBX0+IBX1)/2,(IBZ0+IBZ1)/2; hx,hz=(IBX1-IBX0)/2,(IBZ1-IBZ0)/2; EX=np.array([1.0,0.0]); EZ=np.array([0.0,1.0])
    gs_=[float(gfn(x,z)) for x in (IBX0,IBX1) for z in (IBZ0,IBZ1)]; iy=max(gs_)+IBH
    solid.obox((cx,cz),EX,EZ,hx,hz,min(gs_)-0.4,iy,lin('#b8b2a5'),top=True,topcol=np.array([0.150,0.330,0.090]),tile=PLAIN)
    HG=lin('#a6bf45')
    solid.obox((cx,IBZ0+0.55),EX,EZ,hx-0.15,0.42,iy-0.05,iy+0.85,HG,NOISE,top=True)          # hàng rào mép bắc (phía lối lên cầu)
    solid.obox((IBX0+0.55,cz+0.45),EX,EZ,0.42,hz-0.6,iy-0.05,iy+0.85,HG,NOISE,top=True)     # hàng rào mép tây
    rects.append(dict(c=[cx,cz],u=[1.0,0.0],hu=hx+0.2,hv=hz+0.2))
    for (x,z,h,r) in TREES: cypress(deco,x,z,iy,h,r)
    for (x,z) in GLAMPS:
        green_lamp(deco,x,z,float(gfn(x,z))+0.05); discs.append((x,z,0.3))
    # cột điện bê tông giữa ki-ốt và đảo cây, hai tay đèn
    c=UPOLE; p=np.array(c); py=float(gfn(*c)); PC=lin('#9a9a94'); ph=9.6; AX=np.array([0.38,-0.925]); AV=np.array([0.925,0.38])
    deco.prism(c,0.19,0.12,py,py+ph,6,PC,cap=False)
    for sg in (-1,1):
        e=p+AV*sg*1.7; deco.quad([(c[0],py+ph-0.5,c[1]),(e[0],py+ph+0.25,e[1]),(e[0],py+ph+0.33,e[1]),(c[0],py+ph-0.42,c[1])],PLAIN,PC,np.array([AX[0],0,AX[1]]))
        deco.obox((e[0],e[1]),AV,AX,0.38,0.14,py+ph+0.2,py+ph+0.32,lin('#d9d9d4'),top=True,bottom=True)
    deco.obox(c,AV,AX,0.9,0.05,py+ph-1.6,py+ph-1.5,lin('#6a6a66'),top=True,bottom=True)
    discs.append((c[0],c[1],0.4))
    # biển BÃI ĐẬU XE ở mép bãi xe
    sx,sz=PARKSIGN; sy=float(gfn(sx,sz)); deco.prism((sx,sz),0.05,0.05,sy,sy+2.5,4,lin('#8a8f96'),cap=False)
    d=np.array([-33.0-sx,-108.0-sz]); d/=np.linalg.norm(d); r=np.array([d[1],-d[0]])
    wall(deco,(sx-r[0]*0.85,sz-r[1]*0.85),(sx+r[0]*0.85,sz+r[1]*0.85),sy+1.9,sy+2.5,SIGND,WHITE,sub=(0,0,1,84/256.0))
    wall(deco,(sx+r[0]*0.85-d[0]*0.04,sz+r[1]*0.85-d[1]*0.04),(sx-r[0]*0.85-d[0]*0.04,sz-r[1]*0.85-d[1]*0.04),sy+1.9,sy+2.5,PLAIN,lin('#1c54aa'))
    discs.append((sx,sz,0.25))
    # ================= khối rạp: băng lam và tường tấm bê tông che mái =================
    cc=(CNE+CNW+CSW+CSE)/4
    def out(p): v=p-cc; return p+v/np.linalg.norm(v)*0.35
    ne,nw,sw,se=out(CNE),out(CNW),out(CSW),out(CSE); ya,ybm,yt=19.72,21.6,26.5; BE=lin('#e0d3b6')
    for (a,b) in ((se,ne),(ne,nw),(nw,sw),(sw,se)):
        L=float(np.linalg.norm(b-a))
        wall(solid,a,b,ya,ybm,STRIPE,BE,bays=max(1,int(round(L/3.2)))); wall(solid,a,b,ybm,yt,PANEL,WHITE,bays=max(1,int(round(L/5.0))))
        wall(solid,a,b,ya-0.14,ya,PLAIN,lin('#b9ad92'))
    solid.quad([(ne[0],yt-0.25,ne[1]),(nw[0],yt-0.25,nw[1]),(sw[0],yt-0.25,sw[1]),(se[0],yt-0.25,se[1])],PLAIN,lin('#8f8a7e'),UP)
    for (a,b) in ((ne,se),(nw,ne),(sw,nw),(se,sw)): wall(solid,a,b,yt-0.25,yt,PLAIN,lin('#b9ad92'))
    json.dump(dict(rects=rects,discs=[[round(float(v),2) for v in d_] for d_ in discs],asphalt=[FS,FN]),open('/home/claude/work/build/plaza.json','w'))
    return dict(walk_tris=n)
