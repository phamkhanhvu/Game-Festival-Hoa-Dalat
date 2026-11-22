import numpy as np
def raster(tris, x0, z0, step, nx, nz, out=None, mode='max'):
    """tris: (n,3,3) xyz. Returns grid (nz,nx) of y at cell centers (x0+i*step, z0+j*step), nan where empty."""
    if out is None: out=np.full((nz,nx),np.nan)
    for t in tris:
        xs=t[:,0]; zs=t[:,2]
        i0=max(0,int(np.ceil((xs.min()-x0)/step-1e-9))); i1=min(nx-1,int(np.floor((xs.max()-x0)/step+1e-9)))
        j0=max(0,int(np.ceil((zs.min()-z0)/step-1e-9))); j1=min(nz-1,int(np.floor((zs.max()-z0)/step+1e-9)))
        if i1<i0 or j1<j0: continue
        X,Z=np.meshgrid(x0+np.arange(i0,i1+1)*step, z0+np.arange(j0,j1+1)*step)
        d=(zs[1]-zs[2])*(xs[0]-xs[2])+(xs[2]-xs[1])*(zs[0]-zs[2])
        if abs(d)<1e-12: continue
        a=((zs[1]-zs[2])*(X-xs[2])+(xs[2]-xs[1])*(Z-zs[2]))/d
        b=((zs[2]-zs[0])*(X-xs[2])+(xs[0]-xs[2])*(Z-zs[2]))/d
        c=1-a-b
        m=(a>=-1e-6)&(b>=-1e-6)&(c>=-1e-6)
        if not m.any(): continue
        y=a*t[0,1]+b*t[1,1]+c*t[2,1]
        sub=out[j0:j1+1,i0:i1+1]
        if mode=='max': upd=m&(np.isnan(sub)|(y>sub))
        else: upd=m&(np.isnan(sub)|(y<sub))
        sub[upd]=y[upd]
    return out
