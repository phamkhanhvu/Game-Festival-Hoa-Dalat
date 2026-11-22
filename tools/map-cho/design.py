# Thông số thiết kế khu cầu thang chợ Đà Lạt (toạ độ thế giới: x đông, z nam, y cao)
import numpy as np
from PIL import Image, ImageDraw
X0,Z0,ST=-120.0,-15.0,0.25; NX,NZ=721,421            # lưới mịn dùng khi tính địa hình
TH=np.radians(-5.0); DX,DZ=np.cos(TH),np.sin(TH); VX,VZ=-np.sin(TH),np.cos(TH)   # trục u: hướng đi xuống cầu thang; v: sang nam
T0=np.array([-37.0,31.0])                             # tâm đỉnh cầu thang
U0=14.10; Q=4.20                                      # cao độ đỉnh và chân cầu thang
NF,NR,TREAD,LAND=6,10,0.32,1.8; US=2.0; PER=NR*TREAD+LAND; RISE=(U0-Q)/(NF*NR); UF=US+(NF-1)*PER+NR*TREAD   # UF: chân thang
SW=6.5; PW=0.5                                        # nửa bề rộng thang, bề dày lan can
def l2w(u,v):
    u=np.asarray(u,float); v=np.asarray(v,float); return T0[0]+u*DX+v*VX, T0[1]+u*DZ+v*VZ
def w2l(x,z):
    x=np.asarray(x,float)-T0[0]; z=np.asarray(z,float)-T0[1]; return x*DX+z*DZ, x*VX+z*VZ
def P3(u,v,y):
    x,z=l2w(u,v); return (float(x),float(y),float(z))
def s_step(u):
    """cao độ mặt bậc tại u (hằng từng bậc)"""
    u=np.asarray(u,float); k=np.clip(np.floor((u-US)/PER),0,NF-1); du=u-US-k*PER
    i=np.clip(np.floor(du/TREAD)+1,0,NR); i=np.where(u<US,0,i)
    return U0-(k*NR+i)*RISE
def s_ramp(u):
    """dốc trơn đi qua mũi bậc (dùng cho lưới đi lại)"""
    u=np.asarray(u,float); k=np.clip(np.floor((u-US)/PER),0,NF-1); du=np.clip(u-US-k*PER,0,NR*TREAD)
    y=U0-(k*NR+du/TREAD)*RISE
    return np.where(u<US,U0,np.where(u>UF,Q,y))
# công trình mới, theo toạ độ (u,v)
WA=dict(u0=-2.5,u1=12.5,v0=-29.5,v1=-7.0,roof=U0)             # toà trắng, khối cao (sân thượng ngang đỉnh thang)
WB=dict(u0=12.5,uc=18.75,R=11.25,v0=-29.5,v1=-7.0,roof=Q+5.2) # khối thấp đầu cong bán nguyệt về phía bùng binh
ST_F=dict(u0=23.0,u1=UF,v0=7.0,v1=14.5,top=Q+4.6)             # cửa hàng đặc sản: khối trước
ST_R=dict(u0=13.0,u1=23.0,v0=7.0,v1=14.5)                     # khối sau mái ngói dốc
def in_wb(u,v):
    u=np.asarray(u,float); v=np.asarray(v,float); vc=(WB['v0']+WB['v1'])/2
    rect=(u>=WB['u0'])&(u<=WB['uc'])&(v>=WB['v0'])&(v<=WB['v1'])
    return rect|(((u-WB['uc'])**2+(v-vc)**2<=WB['R']**2)&(u>WB['uc']))
def store_roof(u,v):
    a=float(s_ramp(13.0))+0.5; b=float(s_ramp(23.0))+0.5
    return a+(b-a)*(np.asarray(u,float)-13.0)/10.0-1.4*(np.asarray(v,float)-7.0)/7.5
# vùng chỉnh địa hình (đa giác x,z)
ZONE_DEL=[(-55.5,-1.0),(-12.4,-1.0),(-12.4,-6.0),(2.0,-6.0),(2.0,14.0),(13.8,17.0),(13.8,40.0),(12.0,44.0),(1.5,44.5),(-2.0,41.5),(-11.6,45.3),(-13.3,43.4),(-18.6,45.5),(-19.8,47.0),(-21.0,50.0),(-28.0,50.0),(-37.0,38.0),(-44.5,30.0),(-53.0,14.0),(-55.5,5.0)]   # vùng xoá công trình cũ
ZONE_E=[(-55.5,-1.0),(-12.4,-1.0),(-12.4,-6.0),(0.0,-6.0),(4.0,-12.0),(44.0,-12.0),(50.0,-6.0),(52.5,4.0),(52.5,18.0),(48.0,27.0),(39.0,32.5),(28.0,33.5),(20.0,36.0),(13.8,40.0),(12.0,44.0),(1.5,44.5),(-2.6,42.9),(-11.6,45.3),(-13.3,43.4),(-18.6,45.5),(-19.8,47.0),(-21.0,50.0),(-28.0,50.0),(-37.0,38.0),(-44.5,30.0),(-53.0,14.0),(-55.5,5.0)]
def grid_xz():
    xs=X0+np.arange(NX)*ST; zs=Z0+np.arange(NZ)*ST; return np.meshgrid(xs,zs)
def poly_mask(poly, nx=NX, nz=NZ, x0=X0, z0=Z0, st=ST):
    im=Image.new('L',(nx,nz),0); ImageDraw.Draw(im).polygon([((x-x0)/st,(z-z0)/st) for x,z in poly],fill=1,outline=1)
    return np.asarray(im).astype(bool)
def tris_mask(tris, nx=NX, nz=NZ, x0=X0, z0=Z0, st=ST):
    im=Image.new('L',(nx,nz),0); d=ImageDraw.Draw(im)
    for t in tris: d.polygon([((p[0]-x0)/st,(p[2]-z0)/st) for p in t],fill=1,outline=1)
    return np.asarray(im).astype(bool)
def samp(G,x,z):
    """nội suy song tuyến tính trên lưới mịn"""
    fx=np.clip((np.asarray(x,float)-X0)/ST,0,NX-1.001); fz=np.clip((np.asarray(z,float)-Z0)/ST,0,NZ-1.001)
    i=np.floor(fx).astype(int); j=np.floor(fz).astype(int); a=fx-i; b=fz-j
    return (G[j,i]*(1-a)+G[j,i+1]*a)*(1-b)+(G[j+1,i]*(1-a)+G[j+1,i+1]*a)*b

# ---- các mảng phủ theo địa hình (đa giác lồi, toạ độ x,z) ----
def LW(u,v):
    x,z=l2w(u,v); return (float(x),float(z))
PL_OFF=0.37; UP_OFF=0.30; LAWN_OFF=0.07
WALL_Z=41.6; WALL_X0,WALL_X1=-5.8,13.5
def wall_top(x):
    x=np.asarray(x,float); return np.where(x<=3.0,Q+1.15,Q+1.15-(x-3.0)/(WALL_X1-3.0)*1.30)
PLAZA=[ [LW(18,-27.8),LW(35,-27.8),LW(35,-9.5),LW(18,-9.5)],                                       # trước toà trắng
        [LW(18,-9.5),LW(29.5,-9.5),LW(29.5,-7.0),LW(18,-7.0)],                                     # khe giữa toà trắng và lan can thang
        [LW(29.5,-9.5),LW(35,-9.5),(5.6,22.2),(8.7,26.3),(11.7,30.9),(13.5,34.2),(13.5,WALL_Z),(-5.76,WALL_Z)] ]   # sân chân thang
UPPER=[ [(-51.0,-0.9),(-42.33,-0.9),LW(-2.5,-29.5),LW(-2.5,-7.0),(-47.05,24.24),(-50.8,18.0),(-53.0,14.0),(-54.3,10.0),(-55.0,6.2),(-53.6,2.0)] ]
TOPLAND=[LW(2.0,-7.0),LW(2.0,7.0),LW(-2.2,7.0),LW(-4.55,2.61),LW(-9.2,-7.0)]      # thềm phẳng trên đỉnh thang (cao độ U0)
LAWN=[ [(-38.75,37.9),LW(13,7.0),LW(13,14.5),(-22.33,49.6),(-30.2,49.6),(-33.0,46.0),(-35.9,42.0)] ]
NBANK=[(-12.3,-5.9),(-3.2,-5.9),(-4.94,0.22),(-12.3,0.86)]; NBANK2=[(-21.9,1.70),(-12.3,0.86),(-12.3,-0.95),(-22.0,-0.95)]      # dốc cỏ giữa toà trắng và khối nhà phía bắc
POCKET=[(-1.2,43.0),(13.9,40.3),(14.6,52.0),(3.4,52.0)]
POCKET2=[(-22.0,43.0),(0.5,40.5),(0.5,47.5),(-22.0,50.5)]   # dải đất sát mặt bắc khách sạn trắng      # khoảng đất cạnh khách sạn trắng: phủ màu cỏ
WILLOW_BED=[(-51.7,46.4),(-31.8,73.4),(-39.9,73.4)]
WILLOWS=[(-50.2,50.5),(-47.3,55.5),(-44.3,60.5),(-41.2,65.5),(-37.6,70.5),(-41.6,71.0)]
PINE=LW(7.0,13.5)
RB_C=(31.5,11.5); RB_R=15.9; RB_Y=3.15       # bùng binh: hạ nền quanh bồn hoa cho bồn hoa lộ trọn vòng
_A,_B,_C,_D=LW(UF,14.5),(-2.0,41.5),(-11.6,45.3),(-13.2,43.55); _E,_F,_G,_H,_I=(-13.4,43.5),(-18.6,45.5),(-21.0,50.0),(-22.33,49.6),LW(13,14.5)
ALLEY=[[_A,_B,_C],[_A,_C,_D],[_E,_F,_I],[_F,_H,_I],[_F,_G,_H]]
def convex_ok(poly):
    p=np.array(poly); n=len(p); s=[]
    for i in range(n):
        a=p[(i+1)%n]-p[i]; b=p[(i+2)%n]-p[(i+1)%n]; s.append(a[0]*b[1]-a[1]*b[0])
    s=np.array(s); return bool((s>=-1e-6).all() or (s<=1e-6).all())
