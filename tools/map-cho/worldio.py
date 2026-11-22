import json, base64, numpy as np
PATH='/home/claude/phamkhanhvu/game-festival-hoa-dalat/world_cho.js'
def load(path=PATH):
    s=open(path).read(); a=s.index('{'); b=s.rindex('}')+1
    j=json.loads(s[a:b]); pre=s[:a]; post=s[b:]
    nx,nz=j['nx'],j['nz']
    h=np.frombuffer(base64.b64decode(j['h']),dtype='<i2').reshape(nz,nx).copy()
    top=np.frombuffer(base64.b64decode(j['top']),dtype='<i2').reshape(nz,nx).copy()
    k=np.frombuffer(base64.b64decode(j['k']),dtype=np.uint8).reshape(nz,nx).copy()
    return j,h,top,k,pre,post
def save(path,j,h,top,k,pre,post):
    j=dict(j); j['h']=base64.b64encode(h.astype('<i2').tobytes()).decode(); j['top']=base64.b64encode(top.astype('<i2').tobytes()).decode(); j['k']=base64.b64encode(k.astype(np.uint8).tobytes()).decode()
    open(path,'w').write(pre+json.dumps(j,ensure_ascii=False,separators=(',',':'))+post)
