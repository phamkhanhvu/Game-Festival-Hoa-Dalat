# Mặt bằng lớp phủ của bản đồ Chợ, tính từ market.glb, trên lưới đi lại 0,5 m của world_cho.js:
#   asphalt[j,i]  : mặt trên cùng tại ô là nhựa đường (kể cả sân nhựa, kể cả chỗ có vạch sơn nằm trên)
#   roof[j,i]     : chiều cao (m) của phần công trình cao nhất phía trên ô, tính từ mặt đất (nan nếu không có gì)
# Dùng cho festival.py để không đặt cây, chậu, hoa lên mặt đường và để biết đâu là chân công trình.
#   python3 surface.py market.glb out.npz
import sys, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import glbio, kerbs
from rast import raster

def compute(glb):
    X0, Z0, S, NX, NZ = kerbs.X0, kerbs.Z0, kerbs.S, kerbs.NX, kerbs.NZ
    M = glbio.load(glb); P, UV, C, I = M['P'], M['UV'], M['C'][:, :3], M['I']
    tri, base, road, brick, pave = kerbs.classify(P, UV, C, I)
    cm = C[I].mean(1); green = (cm[:, 1] > cm[:, 0] * 1.2) & (cm[:, 1] > cm[:, 2] * 1.2)
    dark = base & (cm.max(1) < 0.3) & ~green                                # mọi mặt nhựa, kể cả sân nhựa của dãy ki-ốt
    top = raster(tri[base], X0, Z0, S, NX, NZ); R = raster(tri[dark], X0, Z0, S, NX, NZ)
    asph = ~np.isnan(R) & (R >= top - 0.03)                                 # nhựa là lớp trên cùng (vạch sơn nằm trên 1-2 cm vẫn tính là mặt đường)
    cen = tri.mean(1); inb = (cen[:, 0] > X0 - 5) & (cen[:, 0] < X0 + S * NX + 5) & (cen[:, 2] > Z0 - 5) & (cen[:, 2] < Z0 + S * NZ + 5)
    allmax = raster(tri[inb], X0, Z0, S, NX, NZ); gmin = raster(tri[base], X0, Z0, S, NX, NZ, mode='min')
    roof = allmax - gmin
    # về lưới 0,5 m: một ô là nhựa nếu bất kỳ điểm 0,25 m nào trong ô là nhựa; mái lấy giá trị lớn nhất
    def down(A, f):
        n2, m2 = (NZ // 2) * 2, (NX // 2) * 2; B = A[:n2, :m2].reshape(n2 // 2, 2, m2 // 2, 2); return f(f(B, axis=3), axis=1)
    a2 = np.zeros(((NZ + 1) // 2, (NX + 1) // 2), bool); r2 = np.full(a2.shape, np.nan)
    pa = np.zeros((a2.shape[0] * 2, a2.shape[1] * 2), bool); pa[:NZ, :NX] = asph; pr = np.full(pa.shape, np.nan); pr[:NZ, :NX] = roof
    a2 = pa.reshape(a2.shape[0], 2, a2.shape[1], 2).any((1, 3))
    with np.errstate(all='ignore'): r2 = np.nanmax(pr.reshape(a2.shape[0], 2, a2.shape[1], 2), axis=(1, 3))
    return a2, r2

if __name__ == '__main__':
    a, r = compute(sys.argv[1]); np.savez_compressed(sys.argv[2], asphalt=a, roof=r); print(a.shape, 'nhựa %.0f m2' % (a.sum() * 0.25), 'ô có mái > 3 m: %d' % (np.nan_to_num(r) > 3).sum())
