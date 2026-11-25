import numpy as np, math
TH=math.radians(-30.2); A=np.array([math.cos(TH),math.sin(TH)]); Nn=np.array([A[1],-A[0]]); 
if Nn[1]>0: Nn=-Nn
S0=np.array([15.81,-43.23])
def L(s,t): return S0+A*s+Nn*t
def toL(x,z): d=np.stack([np.asarray(x)-S0[0],np.asarray(z)-S0[1]],-1); return d@A, d@Nn
