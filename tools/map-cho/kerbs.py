# Bó vỉa toàn bản đồ Chợ: mọi lề / vỉa lát giáp mặt đường nhựa được đặt cao hơn mặt đường KERB (10 cm) ở mép,
# rồi dựng mặt đứng bó vỉa từ mép lề xuống dưới mặt đường một chút để không còn khe hở hay "tấm lát lơ lửng".
#   python3 kerbs.py <market.glb vào> <world_cho.js vào> <market.glb ra> <world_cho.js ra>
# Chạy sau curbs.py / rear/rear.py (các bước đó dựng lại lề). Lưới đi lại h được cập nhật theo mặt lề mới.
import sys, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import glbio, worldio
from mb import lin, tile_uv, PLAIN, write_glb
from rast import raster
from scipy import ndimage
from collections import defaultdict

KERB = 0.10        # lề cao hơn mặt đường ở mép (m)
NEAR = 1.0         # trong khoảng này tính từ mép đường, mặt lề đặt đúng mặt đường + KERB
FADE = 2.5         # từ NEAR đến FADE mét, mặt lề trở dần về cao độ cũ
SPLIT = 1.0        # cạnh tấm lề dài nhất sau khi chia
FACE_D = 0.6       # cạnh biên của lề cách đường không quá FACE_D thì dựng mặt bó vỉa
FACEC = lin('#a9a397')
X0, Z0, S, NX, NZ = -130.0, -165.0, 0.25, 1321, 1721

def classify(P, UV, C, I):
    tri = P[I]; cen = tri.mean(1); col = C[I[:, 0]][:, :3]
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); nl = np.linalg.norm(nrm, axis=1) + 1e-12
    flat = np.abs(nrm[:, 1]) / nl > 0.95
    tile = np.floor(UV[I[:, 0]] * 8).astype(int)
    inb = (cen[:, 0] > X0) & (cen[:, 0] < X0 + S * NX) & (cen[:, 2] > Z0) & (cen[:, 2] < Z0 + S * NZ)
    dark = col.max(1) < 0.3; green = (col[:, 1] > col[:, 0] * 1.2) & (col[:, 1] > col[:, 2] * 1.2)
    G = raster(tri[flat & inb], X0, Z0, S, NX, NZ, mode='min')
    ci = np.clip(np.round((cen[:, 0] - X0) / S).astype(int), 0, NX - 1); cj = np.clip(np.round((cen[:, 2] - Z0) / S).astype(int), 0, NZ - 1)
    low = (cen[:, 1] - np.nan_to_num(G[cj, ci], nan=-1e9)) < 0.6           # mặt sát đất (không lấy sàn cầu, sân thượng)
    base = flat & inb & low
    road = base & dark & ~green
    brick = base & ~dark & (tile[:, 0] == 2) & (tile[:, 1] == 2)                                   # lề gạch và sân lát kem
    pave = base & ~dark & ~green & (np.abs(col - lin('#b9b4a8')).max(1) < 0.03) & ~brick        # vỉa lát xám quanh chợ, khu sau chợ, bậc cỏ
    return tri, road, brick | pave

def road_field(tri, road, cover):
    R = raster(tri[road], X0, Z0, S, NX, NZ)
    R[~np.isnan(cover) & (cover > R - 0.3)] = np.nan          # mặt đường nằm dưới tấm lát thì không tính là mặt đường hở
    m = ~np.isnan(R); d = ndimage.distance_transform_edt(~m) * S
    # mặt đường kéo dài ra hai bên một cách trơn (lọc Gauss có trọng số), để mép lề bám theo mà không gợn theo ô lưới
    sg = 0.75 / S; num = ndimage.gaussian_filter(np.where(m, R, 0.0), sg); den = ndimage.gaussian_filter(m.astype(float), sg)
    Rs = np.where(den > 1e-4, num / np.maximum(den, 1e-4), np.nan)
    for _ in range(3):                                            # vùng xa hơn: lan tiếp bằng lọc rộng hơn
        hole = np.isnan(Rs)
        if not hole.any(): break
        sg *= 3; mm = ~hole; num = ndimage.gaussian_filter(np.where(mm, Rs, 0.0), sg); den = ndimage.gaussian_filter(mm.astype(float), sg)
        Rs[hole] = (num / np.maximum(den, 1e-6))[hole]
    return R, np.nan_to_num(Rs), d

def bil(A, x, z):
    fx = np.clip((np.asarray(x) - X0) / S, 0, NX - 1.001); fz = np.clip((np.asarray(z) - Z0) / S, 0, NZ - 1.001)
    i = fx.astype(int); j = fz.astype(int); a = fx - i; b = fz - j
    return A[j, i] * (1 - a) * (1 - b) + A[j, i + 1] * a * (1 - b) + A[j + 1, i] * (1 - a) * b + A[j + 1, i + 1] * a * b

def cell(x, z):
    return (np.clip(np.round((np.asarray(x) - X0) / S).astype(int), 0, NX - 1),
            np.clip(np.round((np.asarray(z) - Z0) / S).astype(int), 0, NZ - 1))

def main(gin, win, gout, wout):
    M = glbio.load(gin); P, N, UV, C, I = M['P'].copy(), M['N'], M['UV'], M['C'][:, :3].copy(), M['I']
    tri, road, pv = classify(P, UV, C, I)
    before = raster(tri[pv], X0, Z0, S, NX, NZ)
    R, Rn, dist = road_field(tri, road, before)
    # 1) chia nhỏ các tấm lề gần đường (cạnh dài nhất <= SPLIT) để mặt lề bám theo mặt đường, rồi nâng / hạ đỉnh
    keep = ~pv; Tq = P[I[pv]]; Nq = N[I[pv]]; Uq = UV[I[pv]]; Cq = C[I[pv]]
    def target(x, y, z):
        rn = bil(Rn, x, z); dd = bil(dist, x, z)
        ok = (dd <= FADE) & (np.abs(y - rn) < 0.6); w = np.clip((FADE - dd) / (FADE - NEAR), 0, 1)
        return np.where(ok, y + w * (rn + KERB - y), y)
    for _ in range(7):
        # chỉ chia tấm nào mà mặt lề mới không còn phẳng trên tấm đó (sai lệch giữa cạnh hoặc tâm quá 1,5 cm) và cạnh còn dài hơn SPLIT
        V = Tq; tv = target(V[..., 0], V[..., 1], V[..., 2])
        M3 = (V + np.roll(V, -1, axis=1)) / 2; tm = target(M3[..., 0], M3[..., 1], M3[..., 2]); dev = np.abs(tm - (tv + np.roll(tv, -1, axis=1)) / 2).max(1)
        G3 = V.mean(1); dev = np.maximum(dev, np.abs(target(G3[:, 0], G3[:, 1], G3[:, 2]) - tv.mean(1)))
        e = np.max(np.linalg.norm(V - np.roll(V, 1, axis=1), axis=2), 1)
        sp = (dev > 0.03) & (e > SPLIT)
        if not sp.any(): break
        def four(A):
            a, b, c = A[sp, 0], A[sp, 1], A[sp, 2]; ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
            return np.concatenate([A[~sp], np.stack([a, ab, ca], 1), np.stack([ab, b, bc], 1), np.stack([ca, bc, c], 1), np.stack([ab, bc, ca], 1)])
        Tq, Nq, Uq, Cq = four(Tq), four(Nq), four(Uq), four(Cq)
    x, y, z = Tq[..., 0].ravel(), Tq[..., 1].ravel(), Tq[..., 2].ravel()
    ynew = target(x, y, z)
    moved = int((np.abs(ynew - y) > 0.005).sum()); Tq[..., 1] = ynew.reshape(-1, 3)
    nb = len(P); P = np.concatenate([P, Tq.reshape(-1, 3)]); N = np.concatenate([N, Nq.reshape(-1, 3)]); UV = np.concatenate([UV, Uq.reshape(-1, 2)]); C = np.concatenate([C, Cq.reshape(-1, 3)])
    I = np.concatenate([I[keep], (nb + np.arange(len(Tq) * 3)).reshape(-1, 3)]); pv = np.concatenate([np.zeros(int(keep.sum()), bool), np.ones(len(Tq), bool)])
    # 2) mặt đứng bó vỉa trên các cạnh biên của lề nằm sát đường
    key = lambda p: (int(round(p[0] * 50)), int(round(p[2] * 50)))
    E = defaultdict(list); T = P[I]
    for t in np.where(pv)[0]:
        for a, b in ((0, 1), (1, 2), (2, 0)):
            ka, kb = key(T[t, a]), key(T[t, b]); E[(ka, kb) if ka < kb else (kb, ka)].append((t, a, b))
    Pf, Nf, UVf, Cf = [], [], [], []
    def quad(p0, p1, q1, q0, n):
        for tr in ((p0, p1, q1), (p0, q1, q0)):
            for p in tr: Pf.append(p); Nf.append(n); UVf.append(tile_uv(PLAIN, .5, .5)); Cf.append(FACEC)
    nface = 0; flen = 0.0
    for e, lst in E.items():
        if len(lst) != 1: continue
        t, a, b = lst[0]; A, B = T[t, a], T[t, b]; c3 = T[t, 3 - a - b]
        L = np.hypot(*(B - A)[[0, 2]])
        if L < 0.05: continue
        nseg = max(1, int(np.ceil(L / 3.0))); pts = [A + (B - A) * k / nseg for k in range(nseg + 1)]
        ii_, jj_ = cell([p[0] for p in pts], [p[2] for p in pts])
        if (dist[jj_, ii_] > FACE_D).any(): continue
        mid = (A + B) / 2; d2 = (B - A)[[0, 2]] / L; nn = np.array([d2[1], -d2[0]])
        if np.dot(nn, (c3 - A)[[0, 2]]) > 0: nn = -nn
        qi, qj = cell([mid[0] + nn[0] * 0.3], [mid[2] + nn[1] * 0.3])
        if np.isnan(R[qj[0], qi[0]]) or not np.isnan(before[qj[0], qi[0]]): continue   # bên ngoài cạnh phải là mặt đường trống
        rb = bil(Rn, [p[0] for p in pts], [p[2] for p in pts])
        if ((np.array([p[1] for p in pts]) - rb) < 0.03).all(): continue
        d2 = (B - A)[[0, 2]] / L; n = np.array([d2[1], 0, -d2[0]])
        if np.dot(n[[0, 2]], (c3 - A)[[0, 2]]) > 0: n = -n                   # pháp tuyến quay ra phía đường
        for k in range(nseg):
            p0, p1 = pts[k], pts[k + 1]; q0 = np.array([p0[0], rb[k] - 0.08, p0[2]]); q1 = np.array([p1[0], rb[k + 1] - 0.08, p1[2]])
            if n[0] * (p1[2] - p0[2]) - n[2] * (p1[0] - p0[0]) > 0: quad(p0, p1, q1, q0, n)   # chiều cuộn sao cho mặt hướng ra đường
            else: quad(p1, p0, q0, q1, n)
        nface += 1; flen += L
    k0 = len(P)
    P2 = np.concatenate([P, np.array(Pf)]); N2 = np.concatenate([N, np.array(Nf)]); UV2 = np.concatenate([UV, np.array(UVf)]); C2 = np.concatenate([C, np.array(Cf)])
    I2 = np.concatenate([I, (k0 + np.arange(len(Pf))).reshape(-1, 3)])
    # 3) lưới đi lại: ô nào đang theo mặt lề cũ thì theo mặt lề mới
    after = raster(P2[I2[np.concatenate([pv, np.zeros(len(Pf) // 3, bool)])]], X0, Z0, S, NX, NZ)
    j_, h, top, kk, pre, post = worldio.load(win)
    ob = before[::2, ::2][:h.shape[0], :h.shape[1]]; na = after[::2, ::2][:h.shape[0], :h.shape[1]]
    m = ~np.isnan(ob) & ~np.isnan(na) & (h > -32768) & (np.abs(h / 100.0 - ob) < 0.06)
    h = h.copy(); h[m] = np.round(na[m] * 100).astype(h.dtype)
    nv, nt, size = write_glb(gout, P2, N2, UV2, C2, I2, M['img'])
    worldio.save(wout, j_, h, top, kk, pre, post)
    print(f'đỉnh lề dời: {moved}; mặt bó vỉa: {nface} cạnh, {flen:.0f} m; ô lưới đi lại cập nhật: {int(m.sum())}; glb {nt} tam giác, {size/1e6:.2f} MB')

if __name__ == '__main__':
    main(*sys.argv[1:5])
