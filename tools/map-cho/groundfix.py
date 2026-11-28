# Dọn nền bản đồ Chợ (chạy trước kerbs.py):
#   1. bỏ các mảng lát nhỏ nằm trơ trọi giữa mặt nhựa, ngang mặt nhựa (mảng sót lại từ các lần sửa trước, trông như miếng vá sáng trên đường);
#   2. đổi màu các đỉnh địa hình sáng lọt giữa vùng nhựa sang màu nhựa (xoá các vệt, nêm sáng trên sân nhựa).
#   python3 groundfix.py <market.glb vào> <market.glb ra>
import sys, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import glbio, kerbs
from mb import write_glb, PLAIN
from rast import raster
from scipy import ndimage
X0, Z0, S, NX, NZ = kerbs.X0, kerbs.Z0, kerbs.S, kerbs.NX, kerbs.NZ
ASPH = np.array([0.106, 0.114, 0.125])
RAD = 7.0          # bán kính xét vùng xung quanh một đỉnh sáng (m)
DARKF = 0.80       # tỉ lệ mặt nhựa tối thiểu quanh đỉnh để coi là "lọt giữa vùng nhựa"

def main(gin, gout):
    M = glbio.load(gin); P, N, UV, C, I = M['P'], M['N'], M['UV'], M['C'][:, :3].copy(), M['I']
    P, N, UV, C, I, ncut, acut = kerbs.cut_under_road(P, N, UV, C, I); C = C.copy()   # tấm lát bị mặt nhựa phủ một phần: cắt theo mép, để các mảnh lộ ra thành tam giác riêng
    tri, base, road, brick, pave = kerbs.classify(P, UV, C, I); pv = brick | pave
    top = raster(tri[base], X0, Z0, S, NX, NZ); R = raster(tri[road], X0, Z0, S, NX, NZ)
    roadtop = ~np.isnan(R) & (R >= top - 0.03)
    # ---- 1. mảng lát nhỏ trơ trọi giữa mặt nhựa
    cover = np.zeros((NZ, NX), bool); cells = {}
    for t in np.where(pv)[0]:
        jj, ii, y = kerbs.tri_cells(tri[t]); cells[t] = (jj, ii)
        if len(y) == 0: continue
        ok = y >= top[jj, ii] - 0.002; cover[jj[ok], ii[ok]] = True
    lab, n = ndimage.label(cover, structure=np.ones((3, 3))); area = np.bincount(lab.ravel(), minlength=n + 1) * S * S
    kill = np.zeros(n + 1, bool); where = []
    for l in range(1, n + 1):
        if not (0.3 <= area[l] < 12): continue
        m = lab == l; ring = ndimage.binary_dilation(m, iterations=4) & ~m
        if roadtop[ring].mean() < 0.85 or (~np.isnan(R[m])).mean() < 0.95: continue
        if np.nanmedian(top[m] - R[m]) > 0.03: continue                      # mảng cao hơn mặt nhựa là đảo, bồn: giữ
        kill[l] = True; jj, ii = np.nonzero(m); where.append((round(float(area[l]), 1), round(float(X0 + ii.mean() * S), 1), round(float(Z0 + jj.mean() * S), 1)))
    drop = np.zeros(len(I), bool)
    for t in np.where(pv)[0]:
        jj, ii = cells[t]
        if len(jj) == 0: i, j = kerbs.cell(tri[t][:, 0].mean(), tri[t][:, 2].mean()); jj, ii = np.array([j]), np.array([i])
        l = lab[jj, ii]; l = l[l > 0]
        if len(l) and kill[np.bincount(l).argmax()] and kill[l].all(): drop[t] = True
    # ---- 2. đỉnh địa hình sáng lọt giữa vùng nhựa
    r = int(round(RAD / S)); frac = ndimage.uniform_filter(roadtop.astype(float), size=2 * r + 1, mode='nearest')
    c3 = C[I]; spread = np.abs(c3 - c3.mean(1, keepdims=True)).max((1, 2)); tile = np.floor(UV[I[:, 0]] * 8).astype(int)
    terr = base & (tile[:, 0] == PLAIN[0]) & (tile[:, 1] == PLAIN[1]) & (spread > 0.03) & ~pv   # tam giác địa hình có màu chuyển dần
    notterr = np.ones(len(P), bool); isterr = np.zeros(len(P), bool)
    isterr[I[terr].ravel()] = True
    other = ~terr; notterr[:] = False; notterr[I[other].ravel()] = True                       # đỉnh còn thuộc tam giác khác (tấm lát, vạch sơn...) thì không đụng
    v = np.where(isterr & ~notterr)[0]
    mx = C[v].max(1); sat = C[v].max(1) - C[v].min(1)
    vi, vj = kerbs.cell(P[v, 0], P[v, 2])
    q = (mx > 0.16) & (mx < 0.58) & (sat < 0.14) & (frac[vj, vi] >= DARKF)
    C[v[q]] = ASPH
    keep = ~drop
    nv, nt, size = write_glb(gout, P, N, UV, C, I[keep], M['img'])
    print(f'cắt {ncut} tam giác lát theo mép mặt nhựa (bỏ {acut:.0f} m2 nằm dưới); bỏ {int(drop.sum())} tam giác lát trơ trọi giữa mặt nhựa ({len(where)} mảng: {where}); đổi màu {int(q.sum())} đỉnh địa hình sáng lọt giữa vùng nhựa; glb {nt} tam giác, {size/1e6:.2f} MB')

if __name__ == '__main__':
    main(*sys.argv[1:3])
