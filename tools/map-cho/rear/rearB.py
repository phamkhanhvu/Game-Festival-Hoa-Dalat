# ================= 4. mặt sau và sân thượng khối trước =================
# bỏ nhà cửa vòm trên sân thượng (không có thật), thay bằng hai mái tôn xanh của quán sân thượng; lối đi trên mái giữ nguyên
ROOFY = 16.83
n4 = kill(Polygon(WL([(-2.5, -5.6), (30, -5.6), (30, -14.5), (-2.5, -14.5)])), extra=cen[:, 1] > ROOFY + 0.12)
# tường sau: thay hai đoạn không vướng cửa cầu và thang lên mái
REAR = [(-9.0, -1.2), (17.2, 35.8)]
for s0, s1 in REAR: kill(Polygon(WL([(s0, -1.15), (s1, -1.15), (s1, 0.75), (s0, 0.75)])), extra=(cen[:, 1] < 17.95))
print('khối trước: bỏ nhà sân thượng', n4)
# các dải ngang cũ (băng cam, băng tối...) là những tam giác dài suốt tường sau: bỏ, rồi dựng lại riêng cho đoạn giữa còn giữ
_s3, _t3 = toL(P[I][:, :, 0], P[I][:, :, 2]); _long = (np.ptp(_s3, axis=1) > 12) & (_t3.min(1) > -1.2) & (_t3.max(1) < 0.9) & (_s3.min(1) > -10.5) & (_s3.max(1) < 36.5) & (np.ptp(P[I][:, :, 1], axis=1) < 2.5) & (P[I][:, :, 1].max(1) < 17.95) & (P[I][:, :, 1].min(1) > 5.0) & ~dead
_fnl = np.cross(P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]]); _long &= np.abs(_fnl[:, 1]) < 0.3 * np.linalg.norm(_fnl, axis=1)
_grp = {}
for i_ in np.where(_long)[0]:
    key = (round(float(P[I[i_]][:, 1].min()), 1), round(float(P[I[i_]][:, 1].max()), 1)); _grp.setdefault(key, []).append(i_)
for (ya_, yb_), ids in _grp.items():
    cc = C[I[ids]].reshape(-1, 3).mean(0); tt = float(_t3[ids].mean()); uvm = UV[I[ids]].reshape(-1, 2)
    B.quad([p3(17.2, tt, ya_), p3(-1.2, tt, ya_), p3(-1.2, tt, yb_), p3(17.2, tt, yb_)], PLAIN, cc, np.array([NW[0], 0, NW[1]]))
dead[_long] = True; print('dải ngang cũ trên tường sau: bỏ', int(_long.sum()), 'tam giác,', len(_grp), 'dải dựng lại ở đoạn giữa', sorted(_grp))

YP1 = 17.9
for s0, s1 in REAR:
    a, b = (s0, -0.35), (s1, -0.35)
    band(a, b, 3.3, 8.15, STALL if s0 > 0 else SHUT, WH, 4.2, NW); band(a, b, 8.15, 8.95, PLAIN, WH, None, NW)
    band(a, b, 8.95, 12.55, RIBW, WH, 4.2, NW); band(a, b, 12.55, 16.1, RIBW, WH, 4.2, NW); band(a, b, 16.1, YP1, PLAIN, WH, None, NW)
    B.wall(L(s1, -0.75), L(s0, -0.75), ROOFY, YP1, PLAIN, WH, None, np.array([SE[0], 0, SE[1]])); B.flat(WL([(s0, -0.45), (s1, -0.45), (s1, -0.75), (s0, -0.75)]), YP1, PLAIN, WH)
    B.slab(WL([(s0 + 0.2, -0.45), (s1 - 0.2, -0.45), (s1 - 0.2, 1.9), (s0 + 0.2, 1.9)]), 8.35, 8.6, WH, topcol=GREY)                     # mái đón
    for k, s in enumerate(np.arange(s0 + 0.6, s1 - 3.5, 4.2)):
        c_ = [lin('#c9503f'), BLUE, lin('#d8d2c2'), GREEN][k % 4]
        B.quad([p3(s, 1.9, 7.6), p3(s + 3.8, 1.9, 7.6), p3(s + 3.8, 3.6, 6.9), p3(s, 3.6, 6.9)][::-1], AWN, c_, UP)
# quán sân thượng: mái tôn xanh trên cột, vách thấp phía sau
def cafe(s0, s1, t0, t1, col):
    for s in (s0 + 0.3, (s0 + s1) / 2, s1 - 0.3):
        for t in (t0 - 0.3, t1 + 0.3): B.obox(L(s, t), A, Nn, 0.09, 0.09, ROOFY, ROOFY + 2.75, lin('#dcdad2'), top=False)
    gable(s0, s1, t1, t0, ROOFY + 2.75, ROOFY + 3.7, col, wallc=lin('#dfe6ee'))
    B.wall(L(s0, t1 + 0.3), L(s1, t1 + 0.3), ROOFY, ROOFY + 1.0, PLAIN, WH, None, np.array([SE[0], 0, SE[1]])); B.wall(L(s1, t1 + 0.3), L(s0, t1 + 0.3), ROOFY, ROOFY + 1.0, PLAIN, WH, None, np.array([NW[0], 0, NW[1]]))
    for k, s in enumerate(np.arange(s0 + 1.6, s1 - 1.0, 2.6)): B.prism(L(s, (t0 + t1) / 2), 0.5, 0.5, ROOFY + 0.7, ROOFY + 0.76, 6, lin('#c9a273')); B.prism(L(s, (t0 + t1) / 2), 0.05, 0.05, ROOFY, ROOFY + 0.7, 4, DGREY, cap=False)
cafe(-1.0, 12.5, -6.2, -12.8, BLUE); cafe(14.5, 28.5, -6.2, -12.8, BLUE2)
BLOCKR = Polygon(WL([(-1.4, -5.9), (28.9, -5.9), (28.9, -13.2), (-1.4, -13.2)]))
# bảng hiệu quán trên mái, nhìn về bùng binh
B.quad([p3(21.5, -13.6, ROOFY + 3.9), p3(28.0, -13.6, ROOFY + 3.9), p3(28.0, -13.6, ROOFY + 6.3), p3(21.5, -13.6, ROOFY + 6.3)], (1, 6), mb.WHITE, np.array([SE[0], 0, SE[1]])); B.quad([p3(28.0, -13.5, ROOFY + 3.9), p3(21.5, -13.5, ROOFY + 3.9), p3(21.5, -13.5, ROOFY + 6.3), p3(28.0, -13.5, ROOFY + 6.3)], PLAIN, DGREY, np.array([NW[0], 0, NW[1]]))
for s in (22.0, 27.5): B.obox(L(s, -13.4), A, Nn, 0.08, 0.08, ROOFY + 2.9, ROOFY + 3.9, DGREY, top=False)

# ================= 5. taluy bê tông phía tây cầu, sân trên có dãy ki-ốt, sạp chân taluy =================
# sườn dốc thoải cũ (bãi lát ô cờ) được đắp thành sân phẳng phía trên và mái taluy dốc xuống đường sau chợ
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
def kill_whole(poly, frac=0.3, reach=25.0):
    """bỏ trọn các vật (cụm tam giác dính nhau) có từ frac số tam giác nằm trong vùng"""
    q = np.where(contains_xy(poly.buffer(reach), cen[:, 0], cen[:, 2]) & above & ~dead)[0]
    if not len(q): return 0
    V = np.round(P[I[q]].reshape(-1, 3), 2); _, inv = np.unique(V, axis=0, return_inverse=True); n = len(q)
    M = coo_matrix((np.ones(3 * n), (np.repeat(np.arange(n), 3), inv.ravel()))).tocsr(); nc, lab = connected_components(M @ M.T)
    ins = contains_xy(poly, cen[q, 0], cen[q, 2]); tot = np.bincount(lab, minlength=nc); inn = np.bincount(lab, weights=ins, minlength=nc)
    span = np.array([np.ptp(P[I[q[lab == c]]].reshape(-1, 3)[:, [0, 2]], axis=0).max() if tot[c] else 0 for c in range(nc)])
    ok = (inn >= frac * tot) & (span < 45); k = ok[lab]; dead[q[k]] = True; return int(k.sum())
PY = 15.15
WEDGE = [(-38.0, -30), (-39.7, -42), (-39.5, -52), (-38.5, -60), (-35.0, -70), (-30.0, -78.5), (-22.0, -87.0)]
CREST = [(-25.0, -30), (-24.0, -41), (-20.5, -52), (-16.0, -61), (-15.5, -70), (-18.0, -78), (-20.3, -85.5)]
TOE = [(-13.0, -30), (-11.5, -40), (-8.5, -47.5), (-3.5, -54), (-1.5, -61.5), (-3.0, -66.0), (-8.9, -73.4), (-15.2, -81.2), (-19.6, -86.0)]
BRIDGE = LineString([(-19, -91), (17.5, -45.5)]).buffer(3.3, cap_style=2)
PLAT = Polygon(WEDGE + CREST[::-1]); FACE = Polygon(CREST + TOE[::-1])
Z5 = Polygon(WEDGE + [(-20.5, -88.0), (-12.5, -80.5), (-6.0, -72.0), (1.5, -62.0)] + [(x + 10.0, z) for x, z in TOE[:5]][::-1]).buffer(0)
assert Z5.is_valid and PLAT.is_valid and FACE.is_valid
FOOT = Z5.intersection(Polygon([(-60, -62.5), (40, -62.5), (40, -20), (-60, -20)])).difference(ROAD.buffer(4.3)).difference(PLAT).difference(FACE).buffer(-0.05)      # nền lát chân taluy, chỉ đoạn gần ngang mặt đường
Z5 = Z5.buffer(0.8).difference(BRIDGE).difference(ROAD.buffer(4.4))
n5 = kill_whole(Z5) + kill(Z5); OPEN.append(Z5); print('taluy: bỏ', n5)
def sheet(poly, yfn, tile, col, st=2.0, per=4.0, lift=0.0):
    x0b, z0b, x1b, z1b = poly.bounds
    for x0 in np.arange(math.floor(x0b / per) * per, x1b, st):
        for z0 in np.arange(math.floor(z0b / per) * per, z1b, st):
            cell = Polygon([(x0, z0), (x0 + st, z0), (x0 + st, z0 + st), (x0, z0 + st)])
            if not poly.intersects(cell): continue
            pc = cell.intersection(poly)
            for gp in ([pc] if pc.geom_type == 'Polygon' else list(getattr(pc, 'geoms', []))):
                if gp.geom_type != 'Polygon' or gp.area < 0.02: continue
                co = list(gp.exterior.coords)[:-1]; pts = [(x, yfn(x, z) + lift, z) for x, z in co]
                uv = [tile_uv(tile, min(max((x - math.floor(x0 / per) * per) / per, 0), 1), min(max((z - math.floor(z0 / per) * per) / per, 0), 1)) for x, z in co]
                for k in range(1, len(pts) - 1): B.tri([pts[0], pts[k], pts[k + 1]], [uv[0], uv[k], uv[k + 1]], col, UP)
def drape(poly, tile, col, lift, st=2.0, per=4.0, skirt=True):
    sheet(poly, gh, tile, col, st, per, lift)
    if skirt:
        e = poly.exterior
        for k in range(int(e.length / 1.5) + 1):
            a = e.interpolate(k * 1.5); b = e.interpolate(min((k + 1) * 1.5, e.length))
            if a.distance(b) > 1e-6: B.quad([(a.x, g(a.x, a.y) - 0.7, a.y), (b.x, g(b.x, b.y) - 0.7, b.y), (b.x, gh(b.x, b.y) + lift, b.y), (a.x, gh(a.x, a.y) + lift, a.y)], PLAIN, col * 0.85)
def curtain(a, b, ya, yb, col, nh=None, step=1.5):
    """tường chắn từ mép trên (ya ở a, yb ở b) xuống tới mặt đất"""
    a = np.array(a, float); b = np.array(b, float); n = max(1, int(np.hypot(*(b - a)) / step))
    for k in range(n):
        p = a + (b - a) * k / n; q = a + (b - a) * (k + 1) / n; yp = ya + (yb - ya) * k / n; yq = ya + (yb - ya) * (k + 1) / n
        B.quad([(p[0], min(g(*p) - 0.2, yp), p[1]), (q[0], min(g(*q) - 0.2, yq), q[1]), (q[0], yq, q[1]), (p[0], yp, p[1])], PLAIN, col, nh)
ASPH = lin('#7b7c82'); sheet(PLAT, lambda x, z: PY, PLAIN, ASPH)
for gp in ([FOOT] if FOOT.geom_type == 'Polygon' else list(FOOT.geoms)):
    if gp.area > 1: sheet(gp, gh, PLAIN, PAVE, lift=0.06)
for k in range(9):                                                                     # vạch đỗ xe trên sân trên
    c_ = np.array([-31.0, -36.0 - k * 4.2]); B.quad([(c_[0] - 2.4, PY + 0.02, c_[1]), (c_[0] + 2.4, PY + 0.02, c_[1]), (c_[0] + 2.4, PY + 0.02, c_[1] + 0.14), (c_[0] - 2.4, PY + 0.02, c_[1] + 0.14)], PLAIN, WH, UP)
def resamp(pl, n):
    pl = np.array(pl, float); d = np.r_[0, np.cumsum(np.hypot(*np.diff(pl, axis=0).T))]; f = np.linspace(0, d[-1], n); return np.stack([np.interp(f, d, pl[:, 0]), np.interp(f, d, pl[:, 1])], 1)
NC = 37; NV = 4; CR = resamp(CREST, NC); TO = resamp(TOE, NC); TC = lin('#e6decd')
def fpt(k, j):
    f = j / NV; x, z = CR[k] * (1 - f) + TO[k] * f; y = PY * (1 - f) + (g(*TO[k]) + 0.05) * f; return (x, max(y, g(x, z) + (0.2 if 0 < j < NV else 0.0)), z)
for k in range(NC - 1):
    for j in range(NV):
        u0, u1 = (k % 3) / 3, (k % 3 + 1) / 3
        B.quad([fpt(k, j + 1), fpt(k + 1, j + 1), fpt(k + 1, j), fpt(k, j)], TALUY, TC, UP, None, [(u0, 1), (u1, 1), (u1, 0), (u0, 0)])
curtain(CREST[0], TOE[0], PY, g(*TOE[0]), TC * 0.9, np.array([0, 0, 1.0])); curtain(WEDGE[0], CREST[0], PY, PY, TC * 0.9, np.array([0, 0, 1.0]))
for a, b in zip(TOE[:-1], TOE[1:]): B.wall(b, a, g(*b) - 0.25, g(*b) + 0.3, PLAIN, lin('#cfc8b6'), None, None, None, g(*a) - 0.25, g(*a) + 0.3); B.wall(a, b, g(*a) - 0.25, g(*a) + 0.3, PLAIN, lin('#cfc8b6'), None, None, None, g(*b) - 0.25, g(*b) + 0.3)
# gờ bê tông và lan can trên đỉnh taluy và mép nam sân trên
RAIL = [WEDGE[0]] + CREST
for a, b in zip(RAIL[:-1], RAIL[1:]):
    a = np.array(a, float); b = np.array(b, float); d = (b - a) / np.hypot(*(b - a)); n_ = np.array([-d[1], d[0]])
    for (h0, h1, cc) in ((0.0, 0.45, lin('#d9d2c0')), (0.98, 1.06, WH)): B.wall(a, b, PY + h0, PY + h1, PLAIN, cc); B.wall(b, a, PY + h0, PY + h1, PLAIN, cc)
    for f in np.arange(0, 1.0001, 2.0 / np.hypot(*(b - a))): q = a + (b - a) * f; B.obox(q, d, n_, 0.05, 0.05, PY + 0.45, PY + 1.02, WH, top=False)
# dãy ki-ốt mái trắng dọc mép trên (mặt quay vào bãi), xen cây
crest = LineString(CREST); KIO = []; gP = lambda x, z: PY
STALL_LEN = np.array([wj['stalls']['c_len']['x'], wj['stalls']['c_len']['z']])
dist = 2.6
while dist < crest.length - 2.0:
    q = crest.interpolate(dist); q2 = crest.interpolate(dist + 0.5); d = np.array([q2.x - q.x, q2.y - q.y]); d /= np.hypot(*d); up_ = np.array([-d[1], d[0]])
    if FACE.contains(Point(q.x + up_[0] * 2, q.y + up_[1] * 2)): up_ = -up_
    c_ = np.array([q.x, q.y]) + up_ * 2.0
    if np.hypot(*(c_ - STALL_LEN)) > 6.5: KIO.append((c_, d, up_))
    dist += 5.0
for k, (c_, d, up_) in enumerate(KIO):
    y0 = PY; y1 = y0 + 2.75; hw = 1.35
    B.obox(c_, d, up_, hw, hw, y0, y1, WH, top=False)
    f0 = c_ + up_ * (hw + 0.02) - d * hw; f1 = c_ + up_ * (hw + 0.02) + d * hw; B.wall(f1, f0, y0 + 0.1, y1, KSK, mb.WHITE, None, np.array([up_[0], 0, up_[1]]))
    rc = [lin('#f4f2ec'), lin('#e6e9ee'), lin('#f0e8d8')][k % 3]
    cs = [c_ + d * sx * (hw + 0.45) + up_ * sz * (hw + 0.45) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for i in range(4): a_, b_ = cs[i], cs[(i + 1) % 4]; B.tri([(a_[0], y1, a_[1]), (b_[0], y1, b_[1]), (c_[0], y1 + 1.15, c_[1])], [tile_uv(CORR, 0, 1), tile_uv(CORR, 1, 1), tile_uv(CORR, .5, 0)], rc, UP)
    B.flat([tuple(q) for q in cs], y1 - 0.02, PLAIN, WH2, up=False)
    BLOCK.append((Polygon([tuple(c_ + d * sx * hw + up_ * sz * hw) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]), y1 + 1.0))
def tree(c_, h=6.0, r=1.9, kind='pine', col=None, y0=None):
    y0 = g(*c_) - 0.1 if y0 is None else y0
    if kind == 'pine':
        col = col if col is not None else lin('#2f6b45'); B.prism(c_, 0.16, 0.12, y0, y0 + h * 0.3, 5, lin('#6b4a32'), cap=False)
        for i in range(3): B.prism(c_, r * (1 - i * 0.25), r * (0.35 - i * 0.1), y0 + h * (0.22 + i * 0.24), y0 + h * (0.52 + i * 0.24), 7, col * (0.9 + 0.08 * i), tile=(0, 7), cap=(i == 2), rot=i * 0.5)
    else:
        col = col if col is not None else lin('#4f8f4a'); B.prism(c_, 0.2, 0.14, y0, y0 + h * 0.5, 5, lin('#6b4a32'), cap=False)
        B.prism(c_, r * 0.55, r, y0 + h * 0.42, y0 + h * 0.66, 7, col * 0.85, tile=(0, 7), cap=False); B.prism(c_, r, r * 0.8, y0 + h * 0.66, y0 + h * 0.86, 7, col, tile=(0, 7), cap=False, rot=0.3); B.prism(c_, r * 0.8, 0.0, y0 + h * 0.86, y0 + h, 7, col * 1.1, tile=(0, 7), cap=False, rot=0.3)
for k in range(len(KIO) - 1):
    c_ = (KIO[k][0] + KIO[k + 1][0]) / 2 + KIO[k][2] * 0.2
    if k % 2 == 0: tree(c_, 5.5 + (k % 3) * 0.8, 1.5, 'round', y0=PY)
# sạp mái tôn dưới chân taluy, sát lề đường
for k, (cx, cz, ang, col) in enumerate(((-10.9, -33.5, 1.47, BLUE), (-9.6, -40.5, 1.35, GREEN), (-6.6, -47.4, 1.05, BLUE2))):
    d = np.array([math.cos(ang), -math.sin(ang)]); n_ = np.array([d[1], -d[0]]); n_ = n_ if n_[0] > 0 else -n_; c_ = np.array([cx, cz]); y0 = g(*(c_ + n_ * 1.4)); hw, hd = 2.6, 1.5
    for sx in (-1, 1):
        for sz in (-1, 1): B.obox(c_ + d * sx * hw + n_ * sz * hd, d, n_, 0.07, 0.07, y0 - 0.6, y0 + (2.5 if sz > 0 else 3.0), DGREY, top=False)
    q = lambda sx, sz, y: ((c_ + d * sx * (hw + 0.3) + n_ * sz * (hd + 0.35))[0], y, (c_ + d * sx * (hw + 0.3) + n_ * sz * (hd + 0.35))[1])
    B.patch([q(-1, 1, y0 + 2.45), q(1, 1, y0 + 2.45), q(1, -1, y0 + 3.05), q(-1, -1, y0 + 3.05)], CORR, col, 2, 1, UP)
    B.obox(c_ + n_ * 0.2, d, n_, hw - 0.3, 0.45, y0 - 0.6, y0 + 0.95, lin('#c9a273'), tile=PLAIN); B.wall(c_ + n_ * 0.67 - d * (hw - 0.3), c_ + n_ * 0.67 + d * (hw - 0.3), y0 + 0.0, y0 + 0.95, STALL, mb.WHITE, 2.6, np.array([n_[0], 0, n_[1]]), (0, 0.45, 1, 1))
    BLOCK.append((Polygon([tuple(c_ + d * sx * hw + n_ * sz * hd) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]), y0 + 3.0))

# ================= 6. vườn cây bên phải cầu và dãy nhà phố =================
OLDROW = Polygon(WL([(7.3, 13.2), (59, 16.3), (59, 43.5), (7.3, 43.5)])); OLDAWN = Polygon(WL([(9.0, 8.5), (60, 12.0), (60, 17.0), (9.0, 14.0)]))
n6 = kill_whole(OLDROW.difference(BRIDGE.buffer(1.5)).difference(ROAD.buffer(4.4))) + kill(OLDROW) + kill(OLDAWN, extra=(cen[:, 1] > cg + 1.2) & (cen[:, 1] < cg + 6.0) & (np.ptp(P[I][:, :, 1], axis=1) < 1.6)); OPEN.append(OLDROW); print('dãy nhà cũ bên phải cầu: bỏ', n6)
# dãy nhà phố bốn căn nhìn ra đường sau chợ
SP = WL(SHOPS); HOUSES = [(39.5, 44.0, 4, lin('#f0e6cf'), (0, 0)), (44.0, 48.3, 3, lin('#dfe9ef'), (2, 1)), (48.3, 52.8, 4, lin('#f3ead8'), (1, 0)), (52.8, 57.0, 3, lin('#e9dccb'), (0, 0))]
for s0, s1, nf, col, wt in HOUSES:
    tf = lambda s: 18.5 + (s - 39.5) / 17.5 * 2.5; poly = WL([(s0, tf(s0)), (s1, tf(s1)), (s1, 36.0), (s0, 36.0)]); yb = min(g(*p) for p in poly) - 0.4; yg = g(*L((s0 + s1) / 2, tf((s0 + s1) / 2) - 0.5)) + 0.12
    top_ = yg + 3.9 + (nf - 1) * 3.4; BLOCK.append((Polygon(poly), top_ + 0.6))
    B.ring(poly, yb, top_ + 0.6, PLAIN, col); f0, f1 = np.array(poly[0]) + SE * 0.03, np.array(poly[1]) + SE * 0.03; nh = np.array([SE[0], 0, SE[1]])
    B.wall(f1, f0, yg, yg + 3.7, SHOP, mb.WHITE, None, nh)
    for k in range(nf - 1): B.wall(f1, f0, yg + 3.9 + k * 3.4, yg + 3.9 + (k + 1) * 3.4 - 0.2, wt, col, None, nh)
    b0, b1 = np.array(poly[3]) + NW * 0.03, np.array(poly[2]) + NW * 0.03
    for k in range(nf - 1): B.wall(b0, b1, yg + 3.9 + k * 3.4, yg + 3.9 + (k + 1) * 3.4 - 0.2, (0, 4), col, None, np.array([NW[0], 0, NW[1]]))
    B.flat(poly, top_, PLAIN, lin('#a8a6a0'))
    aw = [lin('#c9503f'), BLUE, GREEN, lin('#e0b04a')][int(s0) % 4]; B.quad([(*(f0 + SE * 1.5)[:1], yg + 2.9, (f0 + SE * 1.5)[1]), (*(f1 + SE * 1.5)[:1], yg + 2.9, (f1 + SE * 1.5)[1]), (f1[0], yg + 3.6, f1[1]), (f0[0], yg + 3.6, f0[1])][::-1], AWN, aw, UP)

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rearC.py')).read())

# ================= 7. dọn mảng cỏ, mảng lát cũ còn sót dưới chân taluy và dưới gầm cầu; bồn nước trên nhà góc bùng binh =================
RG = Polygon([(-15, -28), (-21, -88), (-10, -95), (12, -66), (16, -56), (19, -50), (9, -38), (-2, -28)])
from shapely.ops import unary_union
CLEAN = unary_union([RG, APR.buffer(1.0), OLDROW.buffer(1.5), OLDAWN.buffer(1.5), Z5])
_c = C[I].mean(1); _green = (_c[:, 1] > _c[:, 0] + 0.04) & (_c[:, 1] > _c[:, 2] + 0.04); _light = _c.min(1) > 0.42
q7 = contains_xy(CLEAN, cen[:, 0], cen[:, 2]) & (cen[:, 1] > cg + 0.03) & (cen[:, 1] < cg + 0.7) & (_green | _light) & ~dead
q7 &= ~contains_xy(BRIDGE.buffer(-0.6), cen[:, 0], cen[:, 2]) | (np.abs(np.cross(P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]])[:, 1]) > 0.9 * np.linalg.norm(np.cross(P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]]), axis=1))
dead[q7] = True; print('mảng cỏ, lề cũ còn sót: bỏ', int(q7.sum()))
TANK = lin('#2f74c0')
for (x, z) in ((67.5, -7.0), (69.9, -5.4), (68.4, -2.9)):
    B.obox((x, z), np.array([1.0, 0]), np.array([0, 1.0]), 0.9, 0.9, 21.4, 21.75, GREY); B.prism((x, z), 0.8, 0.8, 21.75, 23.4, 10, TANK); B.prism((x, z), 0.8, 0.25, 23.4, 23.65, 10, TANK * 0.9)
# mặt đất nền màu sáng hoặc xanh còn lộ ở lề đường dưới gầm cầu: đổi sang màu nhựa của đường (không phủ thêm lớp, vạch sơn giữ nguyên)
_near = np.array([ROAD.distance(Point(x, z)) < 2.0 for x, z in cen[:, [0, 2]][::1]]) if False else None
_rd = contains_xy(ROAD.buffer(2.0).intersection(RG.buffer(30)), cen[:, 0], cen[:, 2]) & (np.abs(cen[:, 1] - cg) < 0.05) & (_c.max(1) < 0.25); ASPHC = np.median(_c[_rd], axis=0) if _rd.sum() > 20 else lin('#55575c')
C = C.copy(); q8 = contains_xy(unary_union([RG, OLDAWN.buffer(1.5), OLDROW.buffer(1.5)]), cen[:, 0], cen[:, 2]) & (np.abs(cen[:, 1] - cg) <= 0.12) & (_green | _light) & ~dead & ~contains_xy(park, cen[:, 0], cen[:, 2])
C[I[q8].ravel()] = ASPHC; UV = UV.copy(); UV[I[q8].ravel()] = tile_uv(PLAIN, .5, .5); print('mặt nền đổi màu nhựa:', int(q8.sum()), 'tam giác, màu', np.round(ASPHC, 3))

# ================= 8. cắt bỏ mặt nền cũ bên dưới các tấm phủ mới =================
# nền cũ có nhiều lớp chồng nhau (lề, mảng lát, nền nhà cũ) cao thấp lệch tới 0,45 m nên đâm xuyên qua cỏ và nền lát mới.
# Mọi tam giác nền nằm trong vùng phủ bị cắt đúng theo mép vùng; phần nằm ngoài vùng giữ lại, nội suy cao độ, vân và màu.
import shapely
# nền lát quanh vườn cây và dãy nhà phố: dưới dãy nhà cũ đã bỏ, lưới nền gốc bị thủng nhiều chỗ
FILL = unary_union([OLDROW, OLDAWN]).buffer(3.5).difference(park).difference(ROAD.buffer(4.3)).difference(FOOT).difference(PLAT).difference(FACE).buffer(-0.01)
FILLS = [q_ for q_ in ([FILL] if FILL.geom_type == 'Polygon' else list(FILL.geoms)) if q_.area > 1]
for gp in FILLS: drape(gp, PLAIN, PAVE, 0.06)
CUT = unary_union([APR, park, FOOT, PLAT, FACE] + FILLS).buffer(0)
tri3 = P[I]; ymax = tri3[:, :, 1].max(1); glo = np.minimum(cg, GR.at(tri3[:, :, 0], tri3[:, :, 2], smooth=False).min(1))
gsv = GR.at(tri3[:, :, 0], tri3[:, :, 2]); nearg = (tri3[:, :, 1] <= np.maximum(gsv, GR.at(tri3[:, :, 0], tri3[:, :, 2], smooth=False)) + 0.6).all(1)      # mọi đỉnh nằm sát mặt nền (kể cả tam giác nền dốc)
_f3 = np.cross(tri3[:, 1] - tri3[:, 0], tri3[:, 2] - tri3[:, 0]); flat3 = np.abs(_f3[:, 1]) > 0.5 * np.maximum(np.linalg.norm(_f3, axis=1), 1e-9); gsc = GR.at(cen[:, 0], cen[:, 2])
nearg |= flat3 & (cen[:, 1] > gsc - 1.5) & (cen[:, 1] < gsc + 0.6)                      # mặt nền ở chỗ giật cấp (dưới gầm cầu): so với mặt tấm phủ
bx0, bz0, bx1, bz1 = CUT.bounds; cand = np.where(~dead & ((ymax <= np.maximum(cg, glo) + 0.5) | nearg) & (tri3[:, :, 0].max(1) > bx0) & (tri3[:, :, 0].min(1) < bx1) & (tri3[:, :, 2].max(1) > bz0) & (tri3[:, :, 2].min(1) < bz1))[0]
# lưới nền gốc tô màu theo đỉnh (cỏ, lề sáng, nhựa tối). Sát mép các vùng phủ còn sót những tam giác nửa sáng nửa tối, trông như mảnh vỡ:
# trong dải 5 m quanh vùng phủ, đỉnh sáng hoặc xanh của các tam giác chuyển màu được đổi theo màu các đỉnh tối cùng tam giác. Vạch sơn đường (mảnh nhỏ) không đụng tới.
def offc(cc): return (cc.min(-1) > 0.27) | ((cc[..., 1] > cc[..., 0] * 1.15) & (cc[..., 1] > cc[..., 2] * 1.15))
area3 = np.linalg.norm(np.cross(tri3[:, 1] - tri3[:, 0], tri3[:, 2] - tri3[:, 0]), axis=1) / 2; BAND = CUT.buffer(5.0); terr = ~dead & nearg & (area3 > 2.5) & contains_xy(BAND, cen[:, 0], cen[:, 2]); n9 = 0
for _it in range(3):
    oc = offc(C[I]); mix = np.where(terr & oc.any(1) & ~oc.all(1))[0]
    if not len(mix): break
    acc = np.zeros((len(C), 3)); cnt = np.zeros(len(C))
    for i_ in mix:
        v = I[i_]; dk = C[v][~oc[i_]].mean(0); vo = v[oc[i_]]; acc[vo] += dk; cnt[vo] += 1
    vv = np.where(cnt > 0)[0]; C[vv] = acc[vv] / cnt[vv][:, None]; n9 += len(vv)
# đỉnh còn màu cỏ của sườn dốc cũ trong dải này: lấy màu trung bình các đỉnh nền không xanh, không sáng trong bán kính 5 m
from scipy.spatial import cKDTree
tv = np.unique(I[terr].ravel()); cv = C[tv]; isg = (cv[:, 1] > cv[:, 0] * 1.15) & (cv[:, 1] > cv[:, 2] * 1.15); okv = ~offc(cv)
if isg.any() and okv.any():
    kd = cKDTree(P[tv][okv][:, [0, 2]]); dd, ix = kd.query(P[tv][isg][:, [0, 2]], k=6, distance_upper_bound=5.0); src = cv[okv]
    for a_, (d_, i_) in zip(tv[isg], zip(dd, ix)):
        m_ = np.isfinite(d_)
        if m_.any(): C[a_] = src[i_[m_]].mean(0); n9 += 1
print('mép vùng phủ: đổi màu', n9, 'đỉnh lưới nền')
shapely.prepare(CUT); XP, XN, XUV, XC, XSRC = [], [], [], [], []; ncut = nrem = 0
for i_ in cand:
    v = I[i_]; a2 = P[v][:, [0, 2]]; ar2 = 0.5 * ((a2[1, 0] - a2[0, 0]) * (a2[2, 1] - a2[0, 1]) - (a2[2, 0] - a2[0, 0]) * (a2[1, 1] - a2[0, 1]))
    if abs(ar2) < 1e-5:
        if CUT.contains(Point(*a2.mean(0))): dead[i_] = True; ncut += 1
        continue
    T_ = Polygon(a2)
    if not CUT.intersects(T_): continue
    if CUT.contains(T_): dead[i_] = True; ncut += 1; continue
    if T_.intersection(CUT).area < 1e-4: continue
    dead[i_] = True; ncut += 1; rem = T_.difference(CUT)
    if rem.is_empty or rem.area < 1e-4: continue
    M = np.array([[a2[1, 0] - a2[0, 0], a2[2, 0] - a2[0, 0]], [a2[1, 1] - a2[0, 1], a2[2, 1] - a2[0, 1]]]); Mi = np.linalg.inv(M)
    # lưới nền gốc tô màu theo đỉnh (cỏ, lề, nhựa): mảnh còn lại nằm ngoài vùng phủ nên chỉ lấy màu các đỉnh nằm ngoài vùng, không thì loang màu cỏ, màu lề ra mặt đường
    outv = ~contains_xy(CUT, a2[:, 0], a2[:, 1]); _ok = outv & ~offc(C[v]); ccol = C[v][_ok].mean(0) if _ok.any() else (C[v][outv].mean(0) if outv.any() else C[v][np.argmin(C[v].sum(1))])
    for gp in ([rem] if rem.geom_type == 'Polygon' else [q_ for q_ in rem.geoms if q_.geom_type == 'Polygon']):
        if gp.area < 1e-4: continue
        for t_ in shapely.constrained_delaunay_triangles(gp).geoms:
            co = np.array(t_.exterior.coords)[:3]; s2 = 0.5 * ((co[1, 0] - co[0, 0]) * (co[2, 1] - co[0, 1]) - (co[2, 0] - co[0, 0]) * (co[1, 1] - co[0, 1]))
            if abs(s2) < 1e-6: continue
            if (s2 > 0) != (ar2 > 0): co = co[::-1]
            bc = (Mi @ (co - a2[0]).T).T; w = np.stack([1 - bc[:, 0] - bc[:, 1], bc[:, 0], bc[:, 1]], 1)
            pp = w @ P[v]; pp[:, 0] = co[:, 0]; pp[:, 2] = co[:, 1]; XP.append(pp); XN.append(w @ N[v]); XUV.append(w @ UV[v]); XC.append(np.tile(ccol, (3, 1))); XSRC.append(i_); nrem += 1
print('cắt nền cũ dưới tấm phủ: bỏ', ncut, 'tam giác, giữ lại', nrem, 'mảnh ngoài vùng')

