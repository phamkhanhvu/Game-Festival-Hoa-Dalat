# Lề đường khu Hòa Bình: bỏ các dải lề chạy theo đường và mảng nền sáng tràn ra; mặt đất trong vùng thành mặt đường nhựa,
# lề chỉ còn là một viền hẹp ôm chân công trình (chân nhà + BUF).
import numpy as np, sys, json, shapely
sys.path.insert(0,'/home/claude/work/build')
from shapely.geometry import Polygon, MultiPoint, Point
from shapely.ops import unary_union
from mb import lin, tile_uv, PLAIN
BRICK=(2,2)
ZONE=Polygon([(-104,-132),(-4,-132),(-4,-100),(-13,-96.5),(-24.5,-90),(-22,-86),(-16,-86),(-16,-28),(-104,-28)])
BUF=0.6; OFF=0.30; SEG=3.0
ASPH=np.array([0.106,0.114,0.125]); CREAM=np.array([0.729,0.686,0.604]); CURB=lin('#b8b2a5')
HALL=Polygon([(-53.7,-107.7),(-72.6,-111.7),(-85.0,-53.0),(-66.0,-49.0)])       # thân khối rạp (phần trong không cần lát)
def analyse(P,I,tl,C,UV):
    """UV: toạ độ atlas gốc 4x4. Trả về: sw = tam giác lề cần bỏ, terr_v = đỉnh địa hình đổi sang màu nhựa, bld = đường bao các công trình"""
    tri=P[I]; cen=tri.mean(1); x0,z0,x1,z1=ZONE.bounds
    inbb=(cen[:,0]>x0)&(cen[:,0]<x1)&(cen[:,2]>z0)&(cen[:,2]<z1)
    nrm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); flat=np.abs(nrm[:,1])>0.9*(np.linalg.norm(nrm,axis=1)+1e-12)
    col=C[I[:,0]][:,:3]
    cream=(col[:,0]>0.6)&(col[:,1]>0.55)&(col[:,2]>0.45)&(col[:,0]-col[:,2]>0.08)
    # chỉ gỡ lề thuộc các lớp mặt đất (gần như toàn tam giác nằm); nền, sân của chính công trình (vd. sân và hiên khối rạp) giữ nguyên
    labs=np.unique(tl[inbb]); gl=np.array([l for l in labs if l!=98 and flat[tl==l].mean()>0.85])
    cand=np.where(inbb&flat&cream&np.isin(tl,gl))[0]
    sw=np.zeros(len(I),bool)
    for k in cand:
        if ZONE.contains(Point(cen[k,0],cen[k,2])): sw[k]=True
    # địa hình: đỉnh màu be trong vùng -> màu nhựa (đỉnh cỏ giữ nguyên)
    tv=np.unique(I[tl==98]); p=P[tv]; m=(p[:,0]>x0)&(p[:,0]<x1)&(p[:,2]>z0)&(p[:,2]<z1); tv=tv[m]
    c=C[tv][:,:3]; beige=~((c[:,1]>c[:,0]*1.25)&(c[:,1]>c[:,2]*1.25))
    terr_v=np.array([v for v,b in zip(tv,beige) if b and ZONE.contains(Point(P[v,0],P[v,2]))],int)
    # công trình: thành phần cao, không phải mặt phẳng nằm, không phải cây
    bld=[]; zb=ZONE.buffer(6.0)
    for l in np.unique(tl[inbb]):
        if l==98: continue
        m=tl==l; n=int(m.sum())
        if n<12: continue
        v=P[np.unique(I[m])]; hgt=v[:,1].max()-v[:,1].min()
        if hgt<4.5 or flat[m].mean()>0.85: continue
        cm=C[np.unique(I[m])][:,:3].mean(0)
        if cm[1]>cm[0]*1.25 and cm[1]>cm[2]*1.25: continue                     # cây
        hull=MultiPoint([(float(a),float(b)) for a,b in v[:,[0,2]]]).convex_hull
        if hull.geom_type!='Polygon' or hull.area<14 or not zb.intersects(hull): continue
        if int((m&flat&cream).sum())>=2: continue                              # công trình đã có nền, hiên riêng: không viền thêm
        bld.append(hull)
    return dict(sw=sw,terr_v=terr_v,bld=bld)
def build(walk,solid,gfn,bld):
    """viền lề quanh công trình: mặt lát (walk) cao OFF so với mặt đất và mặt bó vỉa đứng (solid)"""
    zc=ZONE.buffer(-0.05)
    S=unary_union([b.buffer(BUF,join_style=2,mitre_limit=2.0) for b in bld]).intersection(zc)
    inner=unary_union([b.buffer(-0.25) for b in bld])
    ring=shapely.segmentize(S.difference(inner),SEG)
    UPV=np.array([0,1.0,0]); nt=0; cell=2.5
    for g in getattr(ring,'geoms',[ring]):
        if g.geom_type!='Polygon' or g.area<0.05: continue
        for t in shapely.constrained_delaunay_triangles(g).geoms:
            xy=np.array(t.exterior.coords)[:3]
            if abs((xy[1,0]-xy[0,0])*(xy[2,1]-xy[0,1])-(xy[1,1]-xy[0,1])*(xy[2,0]-xy[0,0]))<1e-4: continue
            c=xy.mean(0); cx=np.floor(c[0]/cell)*cell; cz=np.floor(c[1]/cell)*cell
            pts=[(float(x),float(gfn(x,z))+OFF,float(z)) for x,z in xy]
            uv=[tile_uv(BRICK,float(np.clip((x-cx)/cell,0,1)),float(np.clip((z-cz)/cell,0,1))) for x,z in xy]
            walk.tri(pts,uv,CREAM,UPV); nt+=1
    # bó vỉa: mặt đứng dọc mép ngoài của viền lề
    nc=0
    Sd=shapely.segmentize(S,SEG)
    for g in getattr(Sd,'geoms',[Sd]):
        if g.geom_type!='Polygon': continue
        for r in [g.exterior]+list(g.interiors):
            co=np.array(r.coords)
            for a,b in zip(co[:-1],co[1:]):
                mid=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
                if zc.exterior.distance(mid)<0.02: continue                    # mép cắt của vùng, không phải mép lề
                ya=float(gfn(a[0],a[1])); yb=float(gfn(b[0],b[1])); d=b-a; L=np.linalg.norm(d)
                if L<1e-6: continue
                solid.quad([(a[0],ya-0.08,a[1]),(b[0],yb-0.08,b[1]),(b[0],yb+OFF,b[1]),(a[0],ya+OFF,a[1])],PLAIN,CURB,np.array([d[1]/L,0,-d[0]/L])); nc+=2
    open('/home/claude/work/build/curbs.wkt','w').write(S.wkt)
    return nt,nc
