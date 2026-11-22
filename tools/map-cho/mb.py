# Bộ dựng lưới tam giác (vị trí, pháp tuyến phẳng, UV theo ô atlas, màu đỉnh tuyến tính) và ghi GLB lượng tử hoá như tệp gốc
import numpy as np, json, struct
COLS,ROWS=4,8            # atlas mới 1024x2048: 4 cột x 8 hàng ô 256px
INS=2.0/256              # lề trong ô để khỏi lem màu ô bên cạnh
def lin(hexs, k=1.0):
    hexs=hexs.lstrip('#'); c=np.array([int(hexs[i:i+2],16) for i in (0,2,4)])/255.0
    c=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
    return np.clip(c*k,0,1)
WHITE=np.array([1.0,1.0,1.0])
def tile_uv(tile, s, t, sub=None):
    """s,t trong [0,1] (t=0 là mép trên ô). sub=(s0,t0,s1,t1) lấy một phần ô."""
    c,r=tile
    if sub is not None:
        s=sub[0]+(sub[2]-sub[0])*s; t=sub[1]+(sub[3]-sub[1])*t
    s=INS+(1-2*INS)*s; t=INS+(1-2*INS)*t
    return (c+s)/COLS, (r+t)/ROWS
PLAIN=(3,0)
class MB:
    def __init__(self): self.P=[]; self.N=[]; self.UV=[]; self.C=[]; self.ntri=0
    def tri(self, p, uv, col, nhint=None):
        p=np.asarray(p,float); n=np.cross(p[1]-p[0],p[2]-p[0]); L=np.linalg.norm(n)
        if L<1e-10: return
        n/=L; uv=list(uv)
        col=np.asarray(col,float)
        if nhint is not None and np.dot(n,nhint)<0:
            p=p[[0,2,1]]; uv=[uv[0],uv[2],uv[1]]; n=-n
            if col.ndim==2: col=col[[0,2,1]]
        for k in range(3): self.P.append(p[k]); self.N.append(n); self.UV.append(uv[k]); self.C.append(col if col.ndim==1 else col[k])
        self.ntri+=1
    def quad(self, p, tile=PLAIN, col=WHITE, nhint=None, sub=None, st=None):
        """p: 4 điểm theo vòng; UV: p0=(0,1) dưới-trái, p1=(1,1) dưới-phải, p2=(1,0) trên-phải, p3=(0,0) trên-trái (hoặc st tuỳ ý)"""
        st=st or [(0,1),(1,1),(1,0),(0,0)]
        uv=[tile_uv(tile,s,t,sub) for s,t in st]
        p=np.asarray(p,float)
        if nhint is None:
            n=np.cross(p[1]-p[0],p[2]-p[0]); nhint=n
        col=np.asarray(col,float)
        if col.ndim==2: self.tri(p[[0,1,2]],[uv[0],uv[1],uv[2]],col[[0,1,2]],nhint); self.tri(p[[0,2,3]],[uv[0],uv[2],uv[3]],col[[0,2,3]],nhint)
        else: self.tri(p[[0,1,2]],[uv[0],uv[1],uv[2]],col,nhint); self.tri(p[[0,2,3]],[uv[0],uv[2],uv[3]],col,nhint)
    def poly(self, pts, tile=PLAIN, col=WHITE, nhint=None, uvfn=None):
        pts=np.asarray(pts,float)
        uvfn=uvfn or (lambda p: tile_uv(tile,0.5,0.5))
        for k in range(1,len(pts)-1): self.tri(pts[[0,k,k+1]],[uvfn(pts[0]),uvfn(pts[k]),uvfn(pts[k+1])],col,nhint)
    def box(self, lo, hi, col=WHITE, tile=PLAIN, faces='xXzZY', cols=None):
        x0,y0,z0=lo; x1,y1,z1=hi; cols=cols or {}
        F={'x':([(x0,y0,z1),(x0,y0,z0),(x0,y1,z0),(x0,y1,z1)],(-1,0,0)),'X':([(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)],(1,0,0)),
           'z':([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],(0,0,-1)),'Z':([(x1,y0,z1),(x0,y0,z1),(x0,y1,z1),(x1,y1,z1)],(0,0,1)),
           'Y':([(x0,y1,z1),(x1,y1,z1),(x1,y1,z0),(x0,y1,z0)],(0,1,0)),'y':([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],(0,-1,0))}
        for f in faces: self.quad(F[f][0],tile,cols.get(f,col),np.array(F[f][1],float))
    def obox(self, c, ax, az, hx, hz, y0, y1, col=WHITE, tile=PLAIN, top=True, bottom=False, topcol=None):
        """hộp xoay: tâm c=(x,z), trục ngang ax (đơn vị), az, nửa kích thước hx,hz"""
        c=np.asarray(c,float); ax=np.asarray(ax,float); az=np.asarray(az,float)
        def P(sx,sz,y): q=c+ax*hx*sx+az*hz*sz; return (q[0],y,q[1])
        for (a,b,nd) in [((-1,-1),(1,-1),-az),((1,-1),(1,1),ax),((1,1),(-1,1),az),((-1,1),(-1,-1),-ax)]:
            self.quad([P(*a,y0),P(*b,y0),P(*b,y1),P(*a,y1)],tile,col,np.array([nd[0],0,nd[1]]))
        if top: self.quad([P(-1,1,y1),P(1,1,y1),P(1,-1,y1),P(-1,-1,y1)],tile,topcol if topcol is not None else col,np.array([0,1.0,0]))
        if bottom: self.quad([P(-1,-1,y0),P(1,-1,y0),P(1,1,y0),P(-1,1,y0)],tile,col,np.array([0,-1.0,0]))
    def prism(self, c, r0, r1, y0, y1, n=6, col=WHITE, tile=PLAIN, cap=True, rot=0.0, capcol=None):
        """trụ/nón cụt n cạnh quanh trục đứng tại c=(x,z)"""
        a=rot+np.arange(n+1)*2*np.pi/n; cs=np.cos(a); sn=np.sin(a)
        for k in range(n):
            p0=(c[0]+r0*cs[k],y0,c[1]+r0*sn[k]); p1=(c[0]+r0*cs[k+1],y0,c[1]+r0*sn[k+1]); p2=(c[0]+r1*cs[k+1],y1,c[1]+r1*sn[k+1]); p3=(c[0]+r1*cs[k],y1,c[1]+r1*sn[k])
            am=(a[k]+a[k+1])/2; nh=np.array([np.cos(am),0.35*np.sign(r0-r1) if r0!=r1 else 0,np.sin(am)])
            if r1<1e-6: self.tri([p0,p1,p2],[tile_uv(tile,0,1),tile_uv(tile,1,1),tile_uv(tile,.5,0)],col,nh)
            elif r0<1e-6: self.tri([p0,p2,p3],[tile_uv(tile,.5,1),tile_uv(tile,1,0),tile_uv(tile,0,0)],col,nh)
            else: self.quad([p0,p1,p2,p3],tile,col,nh)
        if cap and r1>1e-6:
            pts=[(c[0]+r1*cs[k],y1,c[1]+r1*sn[k]) for k in range(n)]
            self.poly(pts,tile,capcol if capcol is not None else col,np.array([0,1.0,0]))
    def arrays(self):
        return np.array(self.P),np.array(self.N),np.array(self.UV),np.array(self.C)
def write_glb(path, P, N, UV, C3, I, jpeg, extra_nodes=None):
    P=np.asarray(P,float); mn=P.min(0); mx=P.max(0); ctr=(mn+mx)/2; sc=float(((mx-mn)/2).max())
    q=np.round((P-ctr)/sc*32767).astype(np.int16)
    nq=np.round(np.clip(N,-1,1)*127).astype(np.int8)
    uq=np.round(np.clip(UV,0,1)*65535).astype(np.uint16)
    cq=np.concatenate([np.round(np.clip(C3,0,1)*255).astype(np.uint8),np.full((len(P),1),255,np.uint8)],1)
    V=np.zeros(len(P),dtype=[('p','<i2',3),('pad','<i2'),('n','i1',3),('pad2','i1'),('uv','<u2',2),('c','u1',4)])
    V['p']=q; V['n']=nq; V['uv']=uq; V['c']=cq
    raw=np.frombuffer(V.tobytes(),dtype=np.dtype((np.void,20)))
    uniq,inv=np.unique(raw,return_inverse=True)
    I2=inv.ravel()[np.asarray(I).ravel()].astype('<u4')
    vb=uniq.tobytes(); ib=I2.tobytes(); nv=len(uniq)
    Vq=np.frombuffer(vb,dtype=V.dtype)
    def pad4(b,c=b'\0'): return b+c*((4-len(b)%4)%4)
    ib_p=pad4(ib); vb_p=pad4(vb); img_p=pad4(jpeg)
    bin_=ib_p+vb_p+img_p
    j={"asset":{"generator":"dalatevent-map-build","version":"2.0"},
       "accessors":[{"type":"SCALAR","componentType":5125,"count":int(len(I2)),"bufferView":1,"byteOffset":0},
                    {"type":"VEC3","componentType":5122,"count":nv,"max":[int(v) for v in Vq['p'].max(0)],"min":[int(v) for v in Vq['p'].min(0)],"normalized":True,"bufferView":2,"byteOffset":0},
                    {"type":"VEC3","componentType":5120,"count":nv,"normalized":True,"bufferView":2,"byteOffset":8},
                    {"type":"VEC2","componentType":5123,"count":nv,"normalized":True,"bufferView":2,"byteOffset":12},
                    {"type":"VEC4","componentType":5121,"count":nv,"normalized":True,"bufferView":2,"byteOffset":16}],
       "bufferViews":[{"buffer":0,"byteOffset":len(ib_p)+len(vb_p),"byteLength":len(jpeg)},
                      {"buffer":0,"byteOffset":0,"byteLength":len(ib),"target":34963},
                      {"buffer":0,"byteOffset":len(ib_p),"byteLength":len(vb),"byteStride":20,"target":34962}],
       "samplers":[{"magFilter":9729,"minFilter":9987,"wrapS":10497,"wrapT":10497}],
       "textures":[{"source":0,"sampler":0}],"images":[{"name":"atlas","mimeType":"image/jpeg","bufferView":0}],
       "buffers":[{"byteLength":len(bin_)}],
       "materials":[{"name":"atlas","doubleSided":True,"pbrMetallicRoughness":{"roughnessFactor":0.9,"metallicFactor":0,"baseColorTexture":{"index":0}}}],
       "meshes":[{"name":"buildings","primitives":[{"attributes":{"POSITION":1,"NORMAL":2,"TEXCOORD_0":3,"COLOR_0":4},"mode":4,"material":0,"indices":0}]}],
       "nodes":[{"name":"buildings","translation":[float(v) for v in ctr],"scale":[sc,sc,sc],"mesh":0}],
       "scenes":[{"name":"Scene","nodes":[0]}],"scene":0,"extensionsUsed":["KHR_mesh_quantization"],"extensionsRequired":["KHR_mesh_quantization"]}
    js=pad4(json.dumps(j,separators=(',',':')).encode(),b' ')
    total=12+8+len(js)+8+len(bin_)
    with open(path,'wb') as f:
        f.write(struct.pack('<III',0x46546C67,2,total)); f.write(struct.pack('<II',len(js),0x4E4F534A)); f.write(js); f.write(struct.pack('<II',len(bin_),0x004E4942)); f.write(bin_)
    return nv,len(I2)//3,total
