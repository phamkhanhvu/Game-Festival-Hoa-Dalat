# Bó vỉa toàn bản đồ Chợ: lề và vỉa lát NHÌN THẤY ĐƯỢC, nằm sát mặt đường nhựa, có mép cao hơn mặt đường KERB (10 cm) và có mặt đứng bó vỉa.
#   python3 kerbs.py <market.glb vào> <world_cho.js vào> <market.glb ra> <world_cho.js ra>
# Chạy sau curbs.py / rear/rear.py / bridgefix.py / festival.py. Nguyên tắc (rút từ lần làm hỏng ngày 28.11.2026):
#   - chỉ đụng tới tấm lát thật: gạch kem (ô 2,2) hoặc lát xám đều màu ở cả ba đỉnh. Ô địa hình 2,5 m có màu pha giữa đất và nhựa KHÔNG phải lề;
#   - không đụng tới mảng bị mặt đường phủ lên (nằm dưới đường), không đụng tới cụm lát nhỏ hơn MINA m2;
#   - chỉ nâng, không hạ; mép đã cao từ 10 cm trở lên thì giữ nguyên, chỉ thêm mặt đứng;
#   - chia tấm theo cạnh (hai tam giác chung cạnh luôn chia giống nhau) nên không sinh khe hở; mọi cạnh biên bị nâng đều có mặt đứng che xuống vị trí cũ.
import sys, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import glbio, worldio
from mb import lin, tile_uv, PLAIN, write_glb
from rast import raster
from scipy import ndimage
from collections import defaultdict

KERB = 0.10        # mép lề cao hơn mặt đường (m)
NEAR = 1.0         # trong khoảng này tính từ mép đường, mặt lề đặt ở mặt đường + KERB
FADE = 2.5         # từ NEAR đến FADE mét, mặt lề trở dần về cao độ cũ
RREF = 0.5         # bán kính tìm dải đường chính quanh mỗi ô mặt nhựa (m)
SLOPE = 0.06       # độ dốc lớn nhất của đoạn trở về cao độ cũ
LOWMAX = 0.26      # tấm lát thấp hơn mặt đường tới mức này vẫn được kéo lên (vỉa quanh chợ đang thấp hơn mặt đường 12-20 cm)
SPLIT = 1.0        # cạnh ngắn hơn mức này thì không chia nữa
TOL = 0.012        # sai lệch cho phép giữa mặt lề mới và tấm phẳng (m)
MINA = 12.0        # cụm lát nhỏ hơn mức này (m2) để nguyên
PAVEC = lin('#b9b4a8'); FACEC = lin('#a9a397'); YARDC = lin('#7b7c82')
X0, Z0, S, NX, NZ = -130.0, -165.0, 0.25, 1321, 1721

def classify(P, UV, C, I):
    tri = P[I]; cen = tri.mean(1); c3 = C[I][:, :, :3]; cm = c3.mean(1)
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); nl = np.linalg.norm(nrm, axis=1) + 1e-12
    flat = np.abs(nrm[:, 1]) / nl > 0.95
    tile = np.floor(UV[I[:, 0]] * 8).astype(int)
    inb = (cen[:, 0] > X0) & (cen[:, 0] < X0 + S * NX) & (cen[:, 2] > Z0) & (cen[:, 2] < Z0 + S * NZ)
    green = (cm[:, 1] > cm[:, 0] * 1.2) & (cm[:, 1] > cm[:, 2] * 1.2)
    G = raster(tri[flat & inb], X0, Z0, S, NX, NZ, mode='min')
    ci = np.clip(np.round((cen[:, 0] - X0) / S).astype(int), 0, NX - 1); cj = np.clip(np.round((cen[:, 2] - Z0) / S).astype(int), 0, NZ - 1)
    low = (cen[:, 1] - np.nan_to_num(G[cj, ci], nan=-1e9)) < 0.6            # mặt sát đất (không lấy sàn cầu, sân thượng)
    base = flat & inb & low
    uni = np.abs(c3 - c3[:, :1]).max((1, 2)) < 0.012                         # ba đỉnh cùng một màu
    yard = uni & (np.abs(c3[:, 0] - YARDC).max(1) < 0.012)                   # sân nhựa trên của dãy ki-ốt (khu sau chợ): là sân có bờ riêng, không phải mặt đường
    road = base & (cm.max(1) < 0.3) & ~green & ~yard
    brick = base & (cm.max(1) >= 0.3) & (tile[:, 0] == 2) & (tile[:, 1] == 2)
    pave = base & uni & (np.abs(c3[:, 0] - PAVEC).max(1) < 0.012) & (tile[:, 0] == PLAIN[0]) & (tile[:, 1] == PLAIN[1]) & ~brick
    return tri, base, road, brick, pave

def tri_cells(t):
    """các ô lưới có tâm nằm trong tam giác t (3x3 xyz): trả về j, i, y tại tâm ô"""
    xs = t[:, 0]; zs = t[:, 2]; e = np.zeros(0, int)
    i0 = max(0, int(np.ceil((xs.min() - X0) / S - 1e-9))); i1 = min(NX - 1, int(np.floor((xs.max() - X0) / S + 1e-9)))
    j0 = max(0, int(np.ceil((zs.min() - Z0) / S - 1e-9))); j1 = min(NZ - 1, int(np.floor((zs.max() - Z0) / S + 1e-9)))
    if i1 < i0 or j1 < j0: return e, e, np.zeros(0)
    X, Z = np.meshgrid(X0 + np.arange(i0, i1 + 1) * S, Z0 + np.arange(j0, j1 + 1) * S)
    d = (zs[1] - zs[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (zs[0] - zs[2])
    if abs(d) < 1e-12: return e, e, np.zeros(0)
    a = ((zs[1] - zs[2]) * (X - xs[2]) + (xs[2] - xs[1]) * (Z - zs[2])) / d; b = ((zs[2] - zs[0]) * (X - xs[2]) + (xs[0] - xs[2]) * (Z - zs[2])) / d; c = 1 - a - b
    m = (a >= -1e-6) & (b >= -1e-6) & (c >= -1e-6); jj, ii = np.nonzero(m)
    return jj + j0, ii + i0, (a * t[0, 1] + b * t[1, 1] + c * t[2, 1])[m]

def bil(A, x, z):
    fx = np.clip((np.asarray(x, float) - X0) / S, 0, NX - 1.001); fz = np.clip((np.asarray(z, float) - Z0) / S, 0, NZ - 1.001)
    i = fx.astype(int); j = fz.astype(int); a = fx - i; b = fz - j
    return A[j, i] * (1 - a) * (1 - b) + A[j, i + 1] * a * (1 - b) + A[j + 1, i] * (1 - a) * b + A[j + 1, i + 1] * a * b

def cell(x, z):
    return (np.clip(np.round((np.asarray(x, float) - X0) / S).astype(int), 0, NX - 1), np.clip(np.round((np.asarray(z, float) - Z0) / S).astype(int), 0, NZ - 1))

def select(tri, base, road, pv, walk):
    """tấm lát nhìn thấy được và thuộc cụm đủ lớn; mặt đường lộ thiên"""
    top = raster(tri[base], X0, Z0, S, NX, NZ)                               # mặt trên cùng của mọi lớp nền
    topo = np.nan_to_num(raster(tri[road], X0, Z0, S, NX, NZ), nan=-1e9)      # chỉ mặt đường nhựa phủ lên mới tính là "bị che" (hai tấm lát chồng nhau thì cùng được xử lý)
    vis = np.zeros(len(tri), bool); cover = np.zeros((NZ, NX), bool); cells = {}
    for t in np.where(pv)[0]:
        jj, ii, y = tri_cells(tri[t]); cells[t] = (jj, ii)
        if len(y) == 0:
            i, j = cell(tri[t][:, 0].mean(), tri[t][:, 2].mean()); vis[t] = not (topo[j, i] > tri[t][:, 1].mean() + 0.02); continue
        ok = y >= topo[jj, ii] - 0.002
        vis[t] = ok.mean() >= 0.5
        if vis[t]: cover[jj[ok], ii[ok]] = True
    lab, n = ndimage.label(ndimage.binary_closing(cover, iterations=1) | cover, structure=np.ones((3, 3)))
    area = np.bincount(lab.ravel(), minlength=n + 1) * S * S; big = area >= MINA; big[0] = False
    labd = ndimage.maximum_filter(lab, size=5)                               # tam giác quá nhỏ (không chứa tâm ô nào) lấy nhãn của cụm sát bên
    sel = np.zeros(len(tri), bool)
    for t in np.where(vis)[0]:
        jj, ii = cells[t]
        if len(jj):
            l = lab[jj, ii]; l = l[l > 0]
            if len(l) == 0: l = labd[jj, ii]; l = l[l > 0]
            sel[t] = len(l) > 0 and bool(big[np.bincount(l).argmax()])
        else:
            i, j = cell(tri[t][:, 0].mean(), tri[t][:, 2].mean()); sel[t] = bool(big[labd[j, i]])
    for _ in range(3):                                                       # mảnh nhỏ dính sát cụm đã chọn cũng đi theo (nếu không sẽ thành hố)
        near = ndimage.binary_dilation(~np.isnan(raster(tri[sel], X0, Z0, S, NX, NZ)), iterations=2); add = 0
        for t in np.where(vis & ~sel)[0]:
            jj, ii = cells[t]
            if len(jj) == 0: i, j = cell(tri[t][:, 0].mean(), tri[t][:, 2].mean()); jj, ii = np.array([j]), np.array([i])
            if near[jj, ii].any(): sel[t] = True; add += 1
        if not add: break
    R = raster(tri[road], X0, Z0, S, NX, NZ); covsel = raster(tri[sel], X0, Z0, S, NX, NZ)
    exposed = ~np.isnan(R) & (R >= top - 0.03) & ~(covsel >= R - 0.002) & walk   # mặt đường là lớp trên cùng (cho phép vạch sơn nằm trên), không bị tấm lát phủ, không nằm trong chân công trình
    return sel, vis, R, exposed

def cut_under_road(P, N, UV, C, I):
    """Tấm lát quanh chợ được trải cả xuống dưới dải đường (thấp hơn mặt đường 13-19 cm). Nếu nâng nguyên tấm thì lề trùm lên đường,
    nếu bỏ qua tam giác bị che một phần thì lề có hố. Vì vậy cắt các tam giác đó đúng theo mép dải đường: phần lộ ra giữ lại, phần nằm dưới đường bỏ đi."""
    import shapely
    from shapely.geometry import Polygon
    from shapely.strtree import STRtree
    from shapely.ops import unary_union
    tri, base, road, brick, pave = classify(P, UV, C, I); pv = brick | pave
    part = np.where(pv)[0]                                                   # xét mọi tam giác lát (so hình học chính xác, không dựa vào lưới)
    rid = np.where(road)[0]; rp = [Polygon(tri[t][:, [0, 2]]) for t in rid]; tree = STRtree(rp)
    def plane(T):
        n = np.cross(T[1] - T[0], T[2] - T[0]); return n, float(n @ T[0])
    def yat(pl, x, z): n, d = pl; return (d - n[0] * x - n[2] * z) / n[1]
    drop = np.zeros(len(I), bool); Pn, Nn, Un, Cn = [], [], [], []; ncut = 0; acut = 0.0
    for t in part:
        T = tri[t]; A = Polygon(T[:, [0, 2]])
        if not A.is_valid or A.area < 1e-4: continue
        pa = plane(T)
        if abs(pa[0][1]) < 1e-9: continue
        cov = []
        for k in tree.query(A):
            B = rp[k]
            if not B.is_valid: continue
            X = A.intersection(B)
            if X.is_empty or X.area < 1e-4: continue
            c = X.representative_point(); pb = plane(tri[rid[k]])
            if abs(pb[0][1]) < 1e-9: continue
            if yat(pb, c.x, c.y) > yat(pa, c.x, c.y) + 0.002: cov.append(X)
        if not cov: continue
        U = unary_union(cov).buffer(0.002, join_style=2).simplify(0.001); V = A.difference(U)
        if U.intersection(A).area < 0.01 or V.area < 0.004: continue         # gần như không bị che, hoặc bị che gần hết: để nguyên
        drop[t] = True; ncut += 1; acut += A.area - V.area
        for g in getattr(V, 'geoms', [V]):
            if g.geom_type != 'Polygon' or g.area < 0.004: continue
            for q in shapely.constrained_delaunay_triangles(g).geoms:
                xy = np.array(q.exterior.coords)[:3]
                if abs((xy[1, 0] - xy[0, 0]) * (xy[2, 1] - xy[0, 1]) - (xy[1, 1] - xy[0, 1]) * (xy[2, 0] - xy[0, 0])) < 2e-5: continue
                # toạ độ trọng tâm trong tam giác gốc để nội suy cao độ, UV, màu
                d = (T[1, 2] - T[2, 2]) * (T[0, 0] - T[2, 0]) + (T[2, 0] - T[1, 0]) * (T[0, 2] - T[2, 2])
                a_ = ((T[1, 2] - T[2, 2]) * (xy[:, 0] - T[2, 0]) + (T[2, 0] - T[1, 0]) * (xy[:, 1] - T[2, 2])) / d
                b_ = ((T[2, 2] - T[0, 2]) * (xy[:, 0] - T[2, 0]) + (T[0, 0] - T[2, 0]) * (xy[:, 1] - T[2, 2])) / d
                w = np.stack([a_, b_, 1 - a_ - b_], 1)
                pts = w @ T; pts[:, 0] = xy[:, 0]; pts[:, 2] = xy[:, 1]
                if np.cross(pts[1] - pts[0], pts[2] - pts[0])[1] * pa[0][1] < 0: pts = pts[::-1]; w = w[::-1]
                Pn.append(pts); Nn.append(w @ N[I[t]]); Un.append(w @ UV[I[t]]); Cn.append(w @ C[I[t]])
    if not Pn: return P, N, UV, C, I, 0, 0.0
    nb = len(P); k = len(Pn) * 3
    P2 = np.concatenate([P, np.concatenate(Pn)]); N2 = np.concatenate([N, np.concatenate(Nn)]); U2 = np.concatenate([UV, np.concatenate(Un)]); C2 = np.concatenate([C, np.concatenate(Cn)])
    I2 = np.concatenate([I[~drop], (nb + np.arange(k)).reshape(-1, 3)])
    return P2, N2, U2, C2, I2, ncut, acut

def weld_t(Tq, Nq, Uq, Cq, isb):
    """Vá mối nối chữ T: đỉnh của tam giác này nằm giữa cạnh của tam giác kia thì chia tam giác kia tại đúng điểm đó (nếu không, sau khi nâng sẽ hở khe)."""
    tot = 0
    for _ in range(8):
        keyv = {}
        V = Tq.reshape(-1, 3)
        for v in V:
            kx = (int(round(v[0] * 1000)), int(round(v[2] * 1000)))
            if kx not in keyv: keyv[kx] = v
        grid = defaultdict(list)
        for kx, v in keyv.items(): grid[(int(np.floor(v[0])), int(np.floor(v[2])))].append((kx, v))
        hit = {}
        for t in range(len(Tq)):
            for a in range(3):
                b = (a + 1) % 3; A = Tq[t, a]; B = Tq[t, b]; dx = B[0] - A[0]; dz = B[2] - A[2]; L2 = dx * dx + dz * dz
                if L2 < 1e-6: continue
                ka = (int(round(A[0] * 1000)), int(round(A[2] * 1000))); kb = (int(round(B[0] * 1000)), int(round(B[2] * 1000)))
                best = None
                for gx in range(int(np.floor(min(A[0], B[0]))), int(np.floor(max(A[0], B[0]))) + 1):
                    for gz in range(int(np.floor(min(A[2], B[2]))), int(np.floor(max(A[2], B[2]))) + 1):
                        for kx, v in grid.get((gx, gz), ()):
                            if kx == ka or kx == kb: continue
                            u = ((v[0] - A[0]) * dx + (v[2] - A[2]) * dz) / L2
                            if u <= 0.0 or u >= 1.0: continue
                            if abs((v[0] - A[0]) * dz - (v[2] - A[2]) * dx) / np.sqrt(L2) > 0.0015: continue
                            if abs(A[1] + (B[1] - A[1]) * u - v[1]) > 0.02: continue          # cùng một tấm (cùng cao độ)
                            if best is None or abs(u - 0.5) < abs(best[1] - 0.5): best = (a, u, v)
                if best is not None: hit[t] = best; break
        if not hit: break
        tot += len(hit); keep = np.ones(len(Tq), bool); addT, addN, addU, addC, addB = [], [], [], [], []
        for t, (a, u, v) in hit.items():
            b = (a + 1) % 3; c = (a + 2) % 3; keep[t] = False
            def mid(X): return X[t, a] + (X[t, b] - X[t, a]) * u
            m = mid(Tq); m[0] = v[0]; m[2] = v[2]; m[1] = v[1]; mn, mu, mc = mid(Nq), mid(Uq), mid(Cq)
            for (p0, p1, p2), (n0, n1, n2), (u0, u1, u2), (c0, c1, c2) in (((Tq[t, a], m, Tq[t, c]), (Nq[t, a], mn, Nq[t, c]), (Uq[t, a], mu, Uq[t, c]), (Cq[t, a], mc, Cq[t, c])),
                                                                           ((m, Tq[t, b], Tq[t, c]), (mn, Nq[t, b], Nq[t, c]), (mu, Uq[t, b], Uq[t, c]), (mc, Cq[t, b], Cq[t, c]))):
                addT.append(np.stack([p0, p1, p2])); addN.append(np.stack([n0, n1, n2])); addU.append(np.stack([u0, u1, u2])); addC.append(np.stack([c0, c1, c2])); addB.append(isb[t])
        Tq = np.concatenate([Tq[keep], np.array(addT)]); Nq = np.concatenate([Nq[keep], np.array(addN)]); Uq = np.concatenate([Uq[keep], np.array(addU)]); Cq = np.concatenate([Cq[keep], np.array(addC)]); isb = np.concatenate([isb[keep], np.array(addB)])
    return Tq, Nq, Uq, Cq, isb, tot

def road_field(R, exposed):
    """Cao độ mặt đường tham chiếu cho mọi điểm = cao độ ô mặt đường lộ thiên gần nhất, rồi làm trơn trên cả mặt bằng.
    Bản đồ có hai lớp nhựa (dải đường chính cao hơn lớp nhựa nền hai bên khoảng 19 cm), nên nếu không làm trơn thì mép lề nhấp nhô theo từng đoạn.
    Sau khi làm trơn, giá trị không được lệch quá 12 cm so với giá trị gốc: hai con đường khác cao trình (cách nhau một bờ kè) không bị pha vào nhau."""
    d, (jj, ii) = ndimage.distance_transform_edt(~exposed, return_indices=True)
    r = int(round(RREF / S)); yy, xx = np.ogrid[-r:r + 1, -r:r + 1]; disk = (xx * xx + yy * yy) <= r * r
    R0 = np.where(exposed, R, -1e9); Rm = ndimage.maximum_filter(R0, footprint=disk); Rm = np.where(Rm - R0 > 0.30, R0, Rm)   # rãnh nhựa hẹp sát dải đường chính: lấy theo dải đường chính
    Rn = Rm[jj, ii]
    Rs = ndimage.gaussian_filter(Rn, 1.5 / S, mode='nearest')
    return np.clip(Rs, Rn - 0.12, Rn + 0.12), d * S

def split(A, sp):
    """chia tam giác theo cờ từng cạnh sp (n,3): cạnh k nối đỉnh k và k+1. Giữ chiều quay."""
    m = [(A[:, k] + A[:, (k + 1) % 3]) / 2 for k in range(3)]; cnt = sp.sum(1); out = [A[cnt == 0]]
    q = cnt == 3
    if q.any():
        a, b, c = A[q, 0], A[q, 1], A[q, 2]; m0, m1, m2 = m[0][q], m[1][q], m[2][q]
        out += [np.stack([a, m0, m2], 1), np.stack([m0, b, m1], 1), np.stack([m2, m1, c], 1), np.stack([m0, m1, m2], 1)]
    for k in range(3):
        k1, k2 = (k + 1) % 3, (k + 2) % 3
        q = (cnt == 1) & sp[:, k]
        if q.any():
            v0, v1, v2, mk = A[q, k], A[q, k1], A[q, k2], m[k][q]; out += [np.stack([v0, mk, v2], 1), np.stack([mk, v1, v2], 1)]
        q = (cnt == 2) & sp[:, k] & sp[:, k1]
        if q.any():
            v0, v1, v2, mk, ml = A[q, k], A[q, k1], A[q, k2], m[k][q], m[k1][q]; out += [np.stack([mk, v1, ml], 1), np.stack([v0, mk, ml], 1), np.stack([v0, ml, v2], 1)]
    return np.concatenate(out)

def build(P, N, UV, C, I, walk):
    tri, base, road, brick, pave = classify(P, UV, C, I); pv = brick | pave
    sel, vis, R, exposed = select(tri, base, road, pv, walk)
    Rn, dist = road_field(R, exposed)
    def target(x, y, z):
        rn = bil(Rn, x, z); dd = bil(dist, x, z); gap = rn + KERB - y
        F = np.maximum(FADE - NEAR, gap / SLOPE)                             # nâng càng nhiều thì trở về cao độ cũ càng thoải (dốc không quá SLOPE)
        w = np.clip((NEAR + F - dd) / F, 0, 1) * np.clip((y - rn + LOWMAX + 0.06) / 0.06, 0, 1)   # tấm thấp hơn đường quá LOWMAX là một cao trình khác: không kéo lên
        return y + np.where(gap > 0, w * gap, 0.0)
    Tq = P[I[sel]].copy(); Nq = N[I[sel]]; Uq = UV[I[sel]]; Cq = C[I[sel]]; isb = np.repeat(brick[sel][:, None], 3, 1).astype(float)
    Tq, Nq, Uq, Cq, isb, nweld = weld_t(Tq, Nq, Uq, Cq, isb)
    for _ in range(9):
        V = Tq; W = np.roll(V, -1, axis=1); y0 = V[..., 1]; y1 = W[..., 1]; ym = (y0 + y1) / 2
        tv = target(V[..., 0], y0, V[..., 2]); tw = np.roll(tv, -1, axis=1)
        M = (V + W) / 2; Q1 = (V + M) / 2; Q3 = (M + W) / 2
        dm = np.abs(target(M[..., 0], ym, M[..., 2]) - (tv + tw) / 2)
        d1 = np.abs(target(Q1[..., 0], (y0 + ym) / 2, Q1[..., 2]) - (tv * 3 + tw) / 4); d3 = np.abs(target(Q3[..., 0], (ym + y1) / 2, Q3[..., 2]) - (tw * 3 + tv) / 4)
        dev = np.maximum(dm, np.maximum(d1, d3))                             # đối xứng giữa hai tam giác chung cạnh: cả hai cùng chia hoặc cùng không
        L = np.hypot(V[..., 0] - W[..., 0], V[..., 2] - W[..., 2])
        sp = (dev > TOL) & (L > SPLIT)
        if not sp.any(): break
        Tq, Nq, Uq, Cq, isb = split(Tq, sp), split(Nq, sp), split(Uq, sp), split(Cq, sp), split(isb[..., None], sp)[..., 0]
    Told = Tq.copy(); Ynew = target(Tq[..., 0], Tq[..., 1], Tq[..., 2]); moved = Ynew - Told[..., 1]; Tq = Tq.copy(); Tq[..., 1] = Ynew
    # lớp nền khác (không đổi) và mặt lề mới: để biết bên ngoài mỗi cạnh biên là gì
    other = raster(tri[base & ~sel], X0, Z0, S, NX, NZ); newpv = raster(Tq, X0, Z0, S, NX, NZ); oldpv = raster(tri[sel], X0, Z0, S, NX, NZ)
    after = np.fmax(other, newpv)
    key = lambda p: (int(round(p[0] * 200)), int(round(p[2] * 200)))
    E = defaultdict(list)
    for t in range(len(Tq)):
        ks = [key(Tq[t, a]) for a in range(3)]
        for a in range(3):
            b = (a + 1) % 3; E[(ks[a], ks[b]) if ks[a] < ks[b] else (ks[b], ks[a])].append((t, a, b))
    Pf, Nf, UVf, Cf = [], [], [], []; nface = 0; flen = 0.0; kerbh = []; kerbl = []
    for e, lst in E.items():
        if len(lst) != 1: continue
        t, a, b = lst[0]; A, B = Tq[t, a], Tq[t, b]; third = Tq[t, 3 - a - b]
        L = float(np.hypot(B[0] - A[0], B[2] - A[2]))
        if L < 0.03: continue
        d2 = np.array([B[0] - A[0], B[2] - A[2]]) / L; n2 = np.array([d2[1], -d2[0]])
        if np.dot(n2, [third[0] - A[0], third[2] - A[2]]) > 0: n2 = -n2       # hướng ra ngoài tấm
        ns = max(1, int(np.ceil(L / 2.5))); f = np.linspace(0, 1, ns + 1)
        pts = A[None] + (B - A)[None] * f[:, None]; old = Told[t, a, 1] + (Told[t, b, 1] - Told[t, a, 1]) * f; mv = pts[:, 1] - old
        qi, qj = cell(pts[:, 0] + n2[0] * 0.3, pts[:, 2] + n2[1] * 0.3)
        ho = after[qj, qi]; ex = exposed[qj, qi]; drop = pts[:, 1] - ho
        if ex.any(): kerbh += list((pts[:, 1] - R[qj, qi])[ex]); kerbl += [L / len(f)] * int(ex.sum())
        need = (mv > 0.004) | (ex & (drop > 0.03) & (drop < 0.45))
        if not need.any(): continue
        bot = np.where(~np.isnan(ho) & (drop > 0) & (drop < 0.6), np.minimum(ho, old), old) - 0.08
        col = FACEC if isb[t, 0] > 0.5 else Cq[t, a] * 0.85                   # lề gạch: màu đá bó vỉa; vỉa lát xám: cùng màu mép cũ
        n3 = np.array([n2[0], 0.0, n2[1]])
        for k in range(ns):
            if not (need[k] or need[k + 1]): continue
            p0, p1 = pts[k], pts[k + 1]; q0 = np.array([p0[0], bot[k], p0[2]]); q1 = np.array([p1[0], bot[k + 1], p1[2]])
            quad = (p0, p1, q1, q0) if np.cross(p1 - p0, q0 - p0) @ n3 > 0 else (p1, p0, q0, q1)
            for tr in ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])):
                for p in tr: Pf.append(p); Nf.append(n3); UVf.append(tile_uv(PLAIN, .5, .5)); Cf.append(col)
        nface += 1; flen += L
    keep = ~sel; nb = len(P)
    P2 = np.concatenate([P, Tq.reshape(-1, 3), np.array(Pf).reshape(-1, 3)]); N2 = np.concatenate([N, Nq.reshape(-1, 3), np.array(Nf).reshape(-1, 3)])
    UV2 = np.concatenate([UV, Uq.reshape(-1, 2), np.array(UVf).reshape(-1, 2)]); C2 = np.concatenate([C, Cq.reshape(-1, 3), np.array(Cf).reshape(-1, 3)])
    I2 = np.concatenate([I[keep], (nb + np.arange(len(Tq) * 3 + len(Pf))).reshape(-1, 3)])
    kerbh = np.array(kerbh); kerbl = np.array(kerbl)
    hist = [float(kerbl[(kerbh >= lo) & (kerbh < hi)].sum()) for lo, hi in ((-9, 0.06), (0.06, 0.095), (0.095, 0.145), (0.145, 0.2), (0.2, 9))] if len(kerbh) else []
    newcov = exposed & (newpv > R + 0.002) & ~(oldpv > R + 0.002)             # mặt đường lộ thiên bị tấm lát mới trồi lên che
    st = dict(sel=int(sel.sum()), pv=int(pv.sum()), buried=int((pv & ~vis).sum()), small=int((vis & ~sel).sum()), tris=len(Tq), moved=int((moved > 0.004).sum()), maxup=float(moved.max()) if len(Tq) else 0.0,
              nface=nface, flen=flen, kerb=hist, newcov=float(newcov.sum() * S * S), nweld=nweld, holes=float((~np.isnan(oldpv) & np.isnan(newpv)).sum() * S * S))
    return P2, N2, UV2, C2, I2, oldpv, newpv, st, dict(exposed=exposed, R=R, newcov=newcov, sel=sel, moved=moved, Tq=Tq, Told=Told, vis=vis, pv=pv, tri=tri)

def main(gin, win, gout, wout):
    M = glbio.load(gin); P, N, UV, C, I = M['P'], M['N'], M['UV'], M['C'][:, :3], M['I']
    j_, h, top, kk, pre, post = worldio.load(win); h0 = h.copy(); h = h.copy()
    walk = np.zeros((NZ, NX), bool); w2 = np.repeat(np.repeat(h > -32768, 2, 0), 2, 1); walk[:min(NZ, w2.shape[0]), :min(NX, w2.shape[1])] = w2[:NZ, :NX]
    P, N, UV, C, I, ncut, acut = cut_under_road(P, N, UV, C, I)
    P2, N2, UV2, C2, I2, oldpv, newpv, st, dbg = build(P, N, UV, C, I, walk)
    ob = oldpv[::2, ::2][:h.shape[0], :h.shape[1]]; na = newpv[::2, ::2][:h.shape[0], :h.shape[1]]
    hm = h / 100.0                                                           # ô đang đi trên tấm lát (hoặc trên mặt đường phủ ngay trên mép tấm) thì đi theo mặt lát mới
    m = ~np.isnan(ob) & ~np.isnan(na) & (h > -32768) & (hm - ob > -0.06) & (hm - ob < 0.30) & (na - hm > 0.004)
    h[m] = np.round(na[m] * 100).astype(h.dtype)
    # vật đặt trên nền (gian, sạp, ki-ốt, cây, chậu, hoa, mốc check-in...) đi theo mặt nền mới
    def dh(x, z, y):
        i = int(round((x - X0) / 0.5)); jj = int(round((z - Z0) / 0.5))
        if 0 <= i < h.shape[1] and 0 <= jj < h.shape[0] and h0[jj, i] > -32768 and h[jj, i] != h0[jj, i] and abs(y - h0[jj, i] / 100.0) < 0.3: return (int(h[jj, i]) - int(h0[jj, i])) / 100.0
        return 0.0
    nobj = 0
    def fix(o):
        nonlocal nobj
        if isinstance(o, dict):
            if all(k in o and isinstance(o[k], (int, float)) for k in ('x', 'z', 'y')):
                d = dh(o['x'], o['z'], o['y'])
                if d: o['y'] = round(o['y'] + d, 3); nobj += 1
            for v in o.values(): fix(v)
        elif isinstance(o, list):
            for v in o: fix(v)
    for k_, v in j_.items():
        if k_ in ('routes', 'decks', 'deckPath', 'deckProps', 'h', 'top', 'k', 'map'): continue
        if k_ == 'flowers':
            for arr in v.values():
                for f in arr:
                    d = dh(f[0], f[2], f[1])
                    if d: f[1] = round(f[1] + d, 3); nobj += 1
        else: fix(v)
    nv, nt, size = write_glb(gout, P2, N2, UV2, C2, I2, M['img'])
    worldio.save(wout, j_, h, top, kk, pre, post)
    print(f"cắt theo mép dải đường: {ncut} tam giác, bỏ {acut:.0f} m2 nằm dưới đường; vá mối nối chữ T: {st['nweld']}; lỗ hổng sau khi chia: {st['holes']:.2f} m2")
    print(f"tấm lát: {st['pv']} tam giác; bị đường phủ (để nguyên) {st['buried']}; cụm nhỏ (để nguyên) {st['small']}; xử lý {st['sel']} -> {st['tris']} sau khi chia")
    print(f"đỉnh được nâng: {st['moved']} (nhiều nhất {st['maxup']*100:.0f} cm); mặt đứng: {st['nface']} cạnh, {st['flen']:.0f} m; mặt đường bị lề mới trồi lên che: {st['newcov']:.1f} m2")
    print("mép lề giáp đường, số mét theo độ cao so với mặt đường [<6, 6-9.5, 9.5-14.5, 14.5-20, >20 cm]:", [round(v) for v in st['kerb']])
    print(f"ô lưới đi lại cập nhật: {int(m.sum())}; vật dời theo nền: {nobj}; glb {nt} tam giác, {size/1e6:.2f} MB")
    return dbg

if __name__ == '__main__':
    main(*sys.argv[1:5])
