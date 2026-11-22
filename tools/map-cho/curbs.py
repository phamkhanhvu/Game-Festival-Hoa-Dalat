# Lề đường toàn bản đồ Chợ: bỏ các dải lề chạy theo đường và đảo lát giữa đường; mặt đất nằm giữa đường và nhà thành mặt đường nhựa;
# lề chỉ còn là một viền hẹp ôm chân công trình (chân nhà + BUF). Sân lát rộng, nền và hiên riêng của công trình giữ nguyên.
# Khu cầu thang chợ đã chỉnh tay (design.ZONE_E) không đụng tới.
import numpy as np, sys, shapely
sys.path.insert(0,'/home/claude/work/build')
from collections import Counter
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import unary_union
from scipy import ndimage
from mb import lin, tile_uv, PLAIN
from rast import raster
import design
BRICK=(2,2); BUF=0.6; OFF=0.14; DR=14.0; DB=16.0; THICK=4.5
GX0,GZ0,GS,GNX,GNZ=-130.0,-165.0,0.5,661,861          # lưới 0,5 m trùng lưới đi lại
MNX,MNZ=331,431                                         # lưới 1 m trùng bản đồ nhỏ
ASPH=np.array([0.106,0.114,0.125]); CREAM=np.array([0.729,0.686,0.604]); CURB=lin('#b8b2a5'); BEIGE=np.array([0.55,0.51,0.45])
PROT=Polygon(design.ZONE_E).buffer(0).buffer(1.5)
_G=None
def gfn(x,z):
    fx=min(max((float(x)-GX0)/GS,0),GNX-2.0); fz=min(max((float(z)-GZ0)/GS,0),GNZ-2.0); i=int(fx); j=int(fz); a=fx-i; b=fz-j
    q=np.array([_G[j,i],_G[j,i+1],_G[j+1,i],_G[j+1,i+1]]); w=np.array([(1-a)*(1-b),a*(1-b),(1-a)*b,a*b]); ok=~np.isnan(q)
    return float((q[ok]*w[ok]).sum()/w[ok].sum()) if ok.any() and w[ok].sum()>1e-9 else 0.0
def _thick(tris):
    key=lambda p:(int(round(p[0]*50)),int(round(p[2]*50))); E=Counter()
    for t in tris:
        ks=[key(p) for p in t]
        for a,b in ((0,1),(1,2),(2,0)): E[(ks[a],ks[b]) if ks[a]<ks[b] else (ks[b],ks[a])]+=1
    L=sum(np.hypot((e[0][0]-e[1][0])/50.0,(e[0][1]-e[1][1])/50.0) for e,c in E.items() if c==1)
    a=tris[:,1,[0,2]]-tris[:,0,[0,2]]; b=tris[:,2,[0,2]]-tris[:,0,[0,2]]; A=0.5*np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0]).sum()
    return 2*A/max(L,1e-6)
def _fp(tris):
    """đường bao chân một công trình"""
    if len(tris)<=80: return MultiPoint([(float(a),float(b)) for a,b in tris.reshape(-1,3)[:,[0,2]]]).convex_hull
    ps=[Polygon(t[:,[0,2]]) for t in tris]; ps=[p for p in ps if p.area>1e-3]
    return unary_union(ps).buffer(0.1).buffer(-0.1).simplify(0.1) if ps else None
def analyse(P,I,tl,C,UV):
    """Trả về: sw = tam giác lề/bạt cần bỏ, terr_v = đỉnh địa hình đổi sang màu nhựa, bld = đường bao công trình, keep = đa giác sân lát giữ lại"""
    global _G
    tri=P[I]; cen=tri.mean(1); col=C[I[:,0]][:,:3]
    nrm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); flat=np.abs(nrm[:,1])>0.9*(np.linalg.norm(nrm,axis=1)+1e-12)
    L=int(tl.max())+1; cnt=np.bincount(tl,minlength=L); ff=np.bincount(tl,weights=flat,minlength=L)/np.maximum(cnt,1)
    gl=ff>0.85; gl[98]=False
    _G=raster(tri[tl==98],GX0,GZ0,GS,GNX,GNZ)
    ci=np.clip(np.round((cen[:,0]-GX0)/GS).astype(int),0,GNX-1); cj=np.clip(np.round((cen[:,2]-GZ0)/GS).astype(int),0,GNZ-1)
    near=(cen[:,1]-np.nan_to_num(_G[cj,ci],nan=-1e9))<0.8
    inprot=shapely.contains_xy(PROT,cen[:,0],cen[:,2])
    cream=(col[:,0]>0.6)&(col[:,1]>0.55)&(col[:,2]>0.45)&(col[:,0]-col[:,2]>0.08)
    cand=flat&cream&gl[tl]&near
    sw=np.zeros(len(I),bool); keep=[]
    for l in np.unique(tl[cand]):
        m=cand&(tl==l)
        if _thick(tri[m])<THICK: sw|=m&~inprot                                 # dải lề chạy theo đường, đảo lát: bỏ
        else: keep+= [Polygon(t[:,[0,2]]) for t in tri[m]]                     # sân lát rộng: giữ
    keep=unary_union([p for p in keep if p.area>1e-3]) if keep else Polygon()
    # bạt xanh dương quanh khối rạp Hòa Bình
    ymn=np.full(L,1e9); ymx=np.full(L,-1e9); np.minimum.at(ymn,tl,tri[:,:,1].min(1)); np.maximum.at(ymx,tl,tri[:,:,1].max(1))
    blue=(col[:,2]>0.3)&(col[:,2]>col[:,0]*2.5)&(cen[:,0]>-96)&(cen[:,0]<-46)&(cen[:,2]>-116)&(cen[:,2]<-28)
    aw=blue&(cnt[tl]==2)&(ymn[tl]>18.5)&(ymx[tl]<19.7)
    # đường nhựa và công trình -> vùng mặt đất hoá nhựa (gần đường và gần nhà)
    road=flat&gl[tl]&near&(col.max(1)<0.2)
    cm=np.stack([np.bincount(tl,weights=col[:,k],minlength=L)/np.maximum(cnt,1) for k in range(3)],1)
    isb=(cnt>=12)&((ymx-ymn)>=4.5)&(ff<=0.85)&~((cm[:,1]>cm[:,0]*1.25)&(cm[:,1]>cm[:,2]*1.25)); isb[98]=False
    rm=~np.isnan(raster(tri[road],GX0,GZ0,1.0,MNX,MNZ)); bm=~np.isnan(raster(tri[isb[tl]],GX0,GZ0,1.0,MNX,MNZ))
    X,Z=np.meshgrid(GX0+np.arange(MNX)*1.0,GZ0+np.arange(MNZ)*1.0)
    asph=(ndimage.distance_transform_edt(~rm)<=DR)&(ndimage.distance_transform_edt(~bm)<=DB)&~shapely.contains_xy(PROT,X,Z)
    tv=np.unique(I[tl==98]); p=P[tv]; c=C[tv][:,:3]
    vi=np.clip(np.round(p[:,0]-GX0).astype(int),0,MNX-1); vj=np.clip(np.round(p[:,2]-GZ0).astype(int),0,MNZ-1)
    inl=(p[:,0]>=GX0)&(p[:,0]<=GX0+MNX-1)&(p[:,2]>=GZ0)&(p[:,2]<=GZ0+MNZ-1)        # ngoài lưới bản đồ thì không đổi màu
    terr_v=tv[(np.abs(c-BEIGE).max(1)<0.08)&asph[vj,vi]&inl]
    # đường bao công trình (bỏ công trình đã có nền, hiên riêng và công trình trong khu giữ nguyên)
    own=np.bincount(tl,weights=(flat&cream),minlength=L)
    bld=[]
    for l in np.where(isb)[0]:
        if own[l]>=2: continue
        f=_fp(tri[tl==l])
        if f is None or f.is_empty or f.geom_type not in('Polygon','MultiPolygon') or f.area<14: continue
        bld.append(f)
    kf=flat&gl[tl]&near&~road&~sw&(tl!=98)
    np.save('/home/claude/work/build/curb_del.npy',tri[sw]); np.save('/home/claude/work/build/curb_asph.npy',asph); np.save('/home/claude/work/build/curb_keepflat.npy',tri[kf])
    return dict(sw=sw|aw,nsw=int(sw.sum()),naw=int(aw.sum()),terr_v=terr_v,bld=bld,keep=keep)
def _dens(co):
    """chia nhỏ cạnh chỉ ở chỗ mặt đất cong (lệch quá 6 cm so với đường thẳng nối hai đầu)"""
    out=[]
    def rec(a,b,ya,yb,dep):
        m=(a+b)/2; ym=gfn(m[0],m[1])
        if dep<4 and np.linalg.norm(b-a)>2.5 and abs(ym-(ya+yb)/2)>0.06: rec(a,m,ya,ym,dep+1); out.append(m); rec(m,b,ym,yb,dep+1)
    for a,b in zip(co[:-1],co[1:]):
        out.append(a); rec(a,b,gfn(a[0],a[1]),gfn(b[0],b[1]),0)
    out.append(co[-1]); return out
def build(walk,solid,an,extra=()):
    """viền lề quanh công trình: một dải lát phẳng nằm cao hơn mặt đất OFF (không cần mặt bó vỉa: nhìn từ trên xuống mép dải vẫn sắc nét)"""
    bld=list(an['bld'])+list(extra)
    cut=unary_union([PROT,an['keep'].buffer(0.05)])
    S=unary_union([b.buffer(BUF,join_style=2,mitre_limit=2.0) for b in bld]).difference(cut).simplify(0.2)
    inner=unary_union([b.buffer(-0.25) for b in bld]).simplify(0.2)
    ring=S.difference(inner)
    UPV=np.array([0,1.0,0]); nt=0; cell=2.5
    for g in getattr(ring,'geoms',[ring]):
        if g.geom_type!='Polygon' or g.area<0.05: continue
        g=Polygon(_dens(np.array(g.exterior.coords)),[_dens(np.array(r.coords)) for r in g.interiors])
        if not g.is_valid: g=g.buffer(0)
        for gg in getattr(g,'geoms',[g]):
            if gg.geom_type!='Polygon' or gg.is_empty: continue
            for t in shapely.constrained_delaunay_triangles(gg).geoms:
                xy=np.array(t.exterior.coords)[:3]
                if abs((xy[1,0]-xy[0,0])*(xy[2,1]-xy[0,1])-(xy[1,1]-xy[0,1])*(xy[2,0]-xy[0,0]))<1e-4: continue
                c=xy.mean(0); cx=np.floor(c[0]/cell)*cell; cz=np.floor(c[1]/cell)*cell
                pts=[(float(x),gfn(x,z)+OFF,float(z)) for x,z in xy]
                uv=[tile_uv(BRICK,float(np.clip((x-cx)/cell,0,1)),float(np.clip((z-cz)/cell,0,1))) for x,z in xy]
                walk.tri(pts,uv,CREAM,UPV); nt+=1
    return nt,0
