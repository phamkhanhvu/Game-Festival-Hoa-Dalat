import json, struct, numpy as np
def load(path):
    d=open(path,'rb').read()
    clen,_=struct.unpack('<II',d[12:20]); j=json.loads(d[20:20+clen])
    b0=20+clen; blen,_=struct.unpack('<II',d[b0:b0+8]); bin_=d[b0+8:b0+8+blen]
    bv=j['bufferViews']; acc=j['accessors']
    prim=j['meshes'][0]['primitives'][0]
    def get(ai):
        a=acc[ai]; v=bv[a['bufferView']]
        ct={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}[a['componentType']]
        n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        off=v.get('byteOffset',0)+a.get('byteOffset',0); stride=v.get('byteStride',0)
        isz=np.dtype(ct).itemsize*n
        if stride and stride!=isz:
            raw=np.frombuffer(bin_,dtype=np.uint8,count=stride*(a['count']-1)+isz,offset=off)
            idx=(np.arange(a['count'])[:,None]*stride+np.arange(isz)[None,:]).ravel()
            arr=np.frombuffer(raw[idx].tobytes(),dtype=ct).reshape(a['count'],n)
        else:
            arr=np.frombuffer(bin_,dtype=ct,count=a['count']*n,offset=off).reshape(a['count'],n)
        arr=arr.astype(np.float64)
        if a.get('normalized'):
            m={5120:127.,5121:255.,5122:32767.,5123:65535.}[a['componentType']]
            arr=np.maximum(arr/m,-1.0) if a['componentType'] in (5120,5122) else arr/m
        return arr
    node=j['nodes'][0]
    P=get(prim['attributes']['POSITION'])*np.array(node.get('scale',[1,1,1]))+np.array(node.get('translation',[0,0,0]))
    N=get(prim['attributes']['NORMAL']); N/=np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-9)
    UV=get(prim['attributes']['TEXCOORD_0'])
    C=get(prim['attributes']['COLOR_0']) if 'COLOR_0' in prim['attributes'] else np.ones((len(P),4))
    I=get(prim['indices']).astype(np.int64).reshape(-1,3)
    iv=bv[j['images'][0]['bufferView']]
    img=bin_[iv.get('byteOffset',0):iv.get('byteOffset',0)+iv['byteLength']]
    return dict(P=P,N=N,UV=UV,C=C,I=I,img=img,json=j)
if __name__=='__main__':
    m=load('/home/claude/phamkhanhvu/game-festival-hoa-dalat/market.glb')
    P=m['P']; print(P.min(0),P.max(0)); print(len(m['I']),'tris')
    print('uv',m['UV'].min(0),m['UV'].max(0)); print('col',m['C'].min(0),m['C'].max(0), np.unique((m['C']*255).round().astype(int),axis=0)[:20], len(np.unique((m['C']*255).round().astype(int),axis=0)))
    open('atlas.jpg','wb').write(m['img'])
    np.savez('market_dec.npz',P=P,N=m['N'],UV=m['UV'],C=m['C'],I=m['I'])
