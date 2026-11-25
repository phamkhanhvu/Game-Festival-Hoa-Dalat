# Dựng lại khu sau lưng Chợ Đà Lạt theo ảnh chụp từ trên cao (2026-11):
#  cánh đông bắc của chợ cũ (băng cửa kính, mái tôn xanh dọc mép sau, tháp thang lam đứng, dãy nhà phụ thấp có sạp và mái hiên),
#  khối B mái đỏ, mặt sau khối trước (băng cửa kính, mái đón, mái tôn xanh trên sân thượng), taluy bê tông ô vuông và dãy ki-ốt phía trên,
#  vườn cây bên phải cầu đi bộ, dãy nhà phố, khu sạp mái tôn bên kia đường phía đông nam.
# Chạy: python3 rear.py <market.glb vào> <world_cho.js vào> <market.glb ra> <world_cho.js ra>
from common import *
from plan import *
import tiles
from tiles import CORR, RIBW, FINS, TALUY, RUST, KSK, AWN, SHUT
src, wsrc, dst, wdst = sys.argv[1:5]
m = glbio.load(src); P, N, UV, C, I = m['P'], m['N'], m['UV'], m['C'][:, :3], m['I']
wj, wh, wtop, wk, wpre, wpost = worldio.load(wsrc)
GR = Ground(ground_raster(P, I)); g = lambda x, z: float(GR.at(x, z)); gh = lambda x, z: float(GR.at(x, z, hi=True))
cen = P[I].mean(1); cg = GR.at(cen[:, 0], cen[:, 2], smooth=False); above = cen[:, 1] > cg + 0.45
LOOP = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loop.npy'))[:, :2]; LOOPP = Polygon(LOOP); ROAD = LineString(list(LOOP) + [LOOP[0]])
dead = np.zeros(len(I), bool); BLOCK = []; OPEN = []            # BLOCK: mặt bằng chặn trong lưới đi lại (đa giác, cao độ mái); OPEN: vùng mở lại
def kill(poly, extra=None, lift=None):
    q = contains_xy(poly, cen[:, 0], cen[:, 2]) & (above if lift is None else (cen[:, 1] > cg + lift))
    if extra is not None: q &= extra
    dead[q] = True; return int(q.sum())
B = Builder(); UP = np.array([0, 1.0, 0])
WH, WH2, GREY, DGREY = lin('#f1eee4'), lin('#e2ddd0'), lin('#b9b7b0'), lin('#77777a')
BLUE, BLUE2, GREEN, TEAL, RUSTC, REDR = lin('#3f86c9'), lin('#2f6fb0'), lin('#4f9a6a'), lin('#3d9c94'), lin('#b0603a'), lin('#b8463a')
WIN, ORG, STALL, GLASS, ROOFT, PANEL, SHOP, STONE = (7, 4), (4, 5), (5, 5), (2, 4), (3, 1), (5, 1), (0, 1), (3, 7)
WL = lambda pts: [tuple(L(s, t)) for s, t in pts]
def road_t(s, east):            # toạ độ t của tim đường quanh chợ tại s
    ls, lt = toL(LOOP[:, 0], LOOP[:, 1]); q = (lt < -15) if east else (lt > 0); o = np.argsort(ls[q]); return float(np.interp(s, ls[q][o], lt[q][o]))

# ================= 1. dọn phần trong vòng đường phía đông bắc khối trước =================
INNER = LOOPP.buffer(-4.3); zs, zt = toL(cen[:, 0], cen[:, 2])
n1 = kill(INNER, extra=(zs > 36.2) | ((zs > 30) & (zt < -19.5)))
print('trong vòng đường: bỏ', n1, 'tam giác')
APR = INNER.intersection(Polygon(WL([(31, -45), (150, -45), (150, 40), (36.3, 40), (36.3, -0.4), (31, -19.5)])))
# nền lát quanh chợ (cao hơn mặt đường 12 cm)
PAVE = lin('#b9b4a8'); st = 2.0
for x0 in np.arange(BX0, BX1, st):
    for z0 in np.arange(BZ0, BZ1, st):
        cell = Polygon([(x0, z0), (x0 + st, z0), (x0 + st, z0 + st), (x0, z0 + st)])
        if not APR.intersects(cell): continue
        pc = cell.intersection(APR)
        for gpoly in ([pc] if pc.geom_type == 'Polygon' else list(getattr(pc, 'geoms', []))):
            if gpoly.geom_type != 'Polygon' or gpoly.area < 0.02: continue
            co = list(gpoly.exterior.coords)[:-1]; c0 = np.mean(co, 0)
            pts = [(x, gh(x, z) + 0.06, z) for x, z in co]
            for k in range(1, len(pts) - 1): B.tri([pts[0], pts[k], pts[k + 1]], [tile_uv(PLAIN, .5, .5)] * 3, PAVE, UP)
edge = APR.exterior
for k in range(int(edge.length / 1.5)):
    a = edge.interpolate(k * 1.5); b = edge.interpolate(min((k + 1) * 1.5, edge.length)); B.quad([(a.x, g(a.x, a.y) - 0.7, a.y), (b.x, g(b.x, b.y) - 0.7, b.y), (b.x, gh(b.x, b.y) + 0.06, b.y), (a.x, gh(a.x, a.y) + 0.06, a.y)], PLAIN, PAVE * 0.8)
OPEN.append(APR)

# ================= 2. cánh đông bắc chợ cũ =================
Y0 = 4.2; F1, F2, F3, PAR = 8.6, 12.3, 15.9, 16.7            # sàn tầng 2, tầng 3, mái, đỉnh tường mái
def band(a, b, y0, y1, tile, col=WH, seg=4.0, nh=None): B.wall(L(*a), L(*b), y0, y1, tile, col, seg, None if nh is None else np.array([nh[0], 0, nh[1]]))
NW, SE, NE, SW = Nn, -Nn, A, -A
wing = WL(WING); BLOCK.append((Polygon(wing), PAR))
# mặt sau (tây bắc): tầng trệt sạp hàng, mái đón, hai băng cửa kính, tường mái
band((35.8, -0.5), (78, -0.5), Y0, F1 - 0.5, STALL, WH, 4.2, NW); band((35.8, -0.5), (78, -0.5), F1 - 0.5, F1 + 0.35, PLAIN, WH, None, NW)
band((35.8, -0.5), (78, -0.5), F1 + 0.35, F2 + 0.15, RIBW, WH, 4.2, NW); band((35.8, -0.5), (78, -0.5), F2 + 0.15, F3 - 0.1, RIBW, WH, 4.2, NW); band((35.8, -0.5), (78, -0.5), F3 - 0.1, PAR, PLAIN, WH, None, NW)
B.slab(WL([(36.5, -0.5), (77.5, -0.5), (77.5, 2.2), (36.5, 2.2)]), F1 - 0.05, F1 + 0.22, WH, topcol=GREY)                       # mái đón bê tông
for s in np.arange(38.5, 77, 6.0): B.obox(L(s, 2.0), A, Nn, 0.16, 0.16, g(*L(s, 2.0)) + 0.1, F1 - 0.05, WH2, top=False)
for k, s in enumerate(np.arange(37.5, 76, 4.2)):                                                                                # mái bạt sạp dưới mái đón
    c_ = [BLUE, lin('#d8d2c2'), GREEN, lin('#c9503f'), lin('#e0b04a')][k % 5]
    B.quad([(*L(s, 2.2)[:1], F1 - 1.0, L(s, 2.2)[1]), (*L(s + 3.8, 2.2)[:1], F1 - 1.0, L(s + 3.8, 2.2)[1]), (*L(s + 3.8, 4.4)[:1], F1 - 1.9, L(s + 3.8, 4.4)[1]), (*L(s, 4.4)[:1], F1 - 1.9, L(s, 4.4)[1])][::-1], AWN, c_, UP)
# mặt đông nam: phía trên nhà phụ có băng cửa, dưới bị nhà phụ che
band((78, -19), (30.0, -19), F2 - 0.6, F3 - 0.1, WIN, WH, 4.0, SE); band((78, -19), (30.0, -19), F3 - 0.1, PAR, PLAIN, WH, None, SE); band((78, -19), (30.0, -19), Y0, F2 - 0.6, PLAIN, WH2, None, SE)
# đầu hồi
band((78, -0.5), (78, -19), Y0, PAR, PLAIN, WH, None, NE); band((30.0, -19), (35.8, -0.5), Y0, PAR, PLAIN, WH, None, None)
# mái bằng xám, tường mái, phần mái tôn xanh dọc mép sau
B.flat(wing, F3 + 0.3, PLAIN, lin('#a9a8a3'))
B.patch([(*L(40, -8.5)[:1], F3 + 0.32, L(40, -8.5)[1]), (*L(77, -8.5)[:1], F3 + 0.32, L(77, -8.5)[1]), (*L(77, -18)[:1], F3 + 0.32, L(77, -18)[1]), (*L(40, -18)[:1], F3 + 0.32, L(40, -18)[1])][::-1], PANEL, lin('#bdbcb6'), 6, 2, UP)
def shed(s0, s1, t0, t1, ye, yr, col, wallc=WH, tile=CORR, per=4.0, back=True):
    """mái tôn một dốc: mép thấp ở t0 (cao ye), mép cao ở t1 (cao yr)"""
    n = max(1, int(round(abs(s1 - s0) / per))); p = lambda s, t, y: (L(s, t)[0], y, L(s, t)[1])
    for k in range(n):
        a = s0 + (s1 - s0) * k / n; b = s0 + (s1 - s0) * (k + 1) / n; B.quad([p(a, t0, ye), p(b, t0, ye), p(b, t1, yr), p(a, t1, yr)], tile, col, UP, None, [(0, 1), (1, 1), (1, 0), (0, 0)])
    if back: B.quad([p(s0, t1, ye - 0.3), p(s1, t1, ye - 0.3), p(s1, t1, yr), p(s0, t1, yr)], PLAIN, wallc); B.tri([p(s0, t0, ye), p(s0, t1, ye), p(s0, t1, yr)], [tile_uv(PLAIN, .5, .5)] * 3, wallc); B.tri([p(s1, t0, ye), p(s1, t1, ye), p(s1, t1, yr)], [tile_uv(PLAIN, .5, .5)] * 3, wallc)
def gable(s0, s1, t0, t1, ye, yr, col, tile=CORR, per=4.0, wallc=WH):
    tm = (t0 + t1) / 2; shed(s0, s1, t0, tm, ye, yr, col, wallc, tile, per, back=False); shed(s0, s1, t1, tm, ye, yr, col, wallc, tile, per, back=False)
    p = lambda s, t, y: (L(s, t)[0], y, L(s, t)[1])
    for s in (s0, s1): B.tri([p(s, t0, ye), p(s, t1, ye), p(s, tm, yr)], [tile_uv(PLAIN, .5, .5)] * 3, wallc)
gable(37.5, 77.5, -7.6, 0.6, PAR + 0.25, PAR + 1.75, BLUE)                                                                  # dải mái tôn xanh dài
B.ring(WL([(37.5, -7.4), (77.5, -7.4), (77.5, 0.4), (37.5, 0.4)]), F3 + 0.3, PAR + 0.3, PLAIN, WH)
B.ring(wing, F3 + 0.3, PAR, PLAIN, WH)                                                                                    # mặt trong tường mái
for (s, t, w, d, hh) in ((45, -13, 2.2, 1.6, 2.4), (63, -14.5, 3.0, 2.0, 2.2), (72, -12, 1.4, 1.4, 1.5)): B.obox(L(s, t), A, Nn, w, d, F3 + 0.3, F3 + 0.3 + hh, WH2, topcol=GREY)   # buồng thang, bồn nước
# nhà phụ thấp phía đông nam: sạp dưới, băng gạch nung trên, mái bằng, mái hiên ngói nâu
annex = WL(ANNEX); YA = 11.4; BLOCK.append((Polygon(annex), YA))
B.wall(L(36.5, -31.0), L(78, -24.3), Y0, 7.9, STALL, WH, 4.2, np.array([SE[0], 0, SE[1]])); B.wall(L(36.5, -31.0), L(78, -24.3), 7.9, 8.4, PLAIN, WH, None, np.array([SE[0], 0, SE[1]]))
B.wall(L(36.5, -31.0), L(78, -24.3), 8.4, 10.6, ORG, lin('#c98a6a'), 4.2, np.array([SE[0], 0, SE[1]])); B.wall(L(36.5, -31.0), L(78, -24.3), 10.6, YA + 0.5, PLAIN, WH, None, np.array([SE[0], 0, SE[1]]))
B.wall(L(36.5, -19), L(36.5, -31.0), Y0, YA + 0.5, PLAIN, WH, None, np.array([SW[0], 0, SW[1]])); B.wall(L(78, -24.3), L(78, -19), Y0, YA + 0.5, PLAIN, WH)
B.flat(annex, YA, PLAIN, lin('#aeada8'))
_d = (np.array(L(78, -24.3)) - np.array(L(36.5, -31.0))); _d /= np.hypot(*_d); _o = np.array([_d[1], -_d[0]]); _o = _o if np.dot(_o, SE) > 0 else -_o
for k in range(10):                                                                                                       # mái hiên dốc trên sạp
    a = np.array(L(36.5, -31.0)) + _d * (k * 4.2 + 0.2); b = a + _d * 3.9; c_ = [TEAL, TEAL, GREEN, lin('#d9d4c6'), TEAL][k % 5]
    B.quad([(a[0] + _o[0] * 2.4, 6.6, a[1] + _o[1] * 2.4), (b[0] + _o[0] * 2.4, 6.6, b[1] + _o[1] * 2.4), (b[0], 7.7, b[1]), (a[0], 7.7, a[1])], AWN, c_, UP)
# tháp thang lam đứng đầu đông bắc và khối thấp cạnh tháp
tw = WL(TOWER); YT = 21.6; BLOCK.append((Polygon(tw), YT)); B.ring(tw, Y0, YT - 0.5, FINS, WH, 3.2); B.ring(tw, YT - 0.5, YT, PLAIN, WH); B.flat(tw, YT, PLAIN, GREY)
B.ring([tuple(L(s, t)) for s, t in ((77.7, -1.7), (84.8, -1.7), (84.8, -10.8), (77.7, -10.8))], YT, YT + 0.3, PLAIN, WH); B.flat([tuple(L(s, t)) for s, t in ((77.7, -1.7), (84.8, -1.7), (84.8, -10.8), (77.7, -10.8))], YT + 0.3, PLAIN, WH)
we = WL(WEND); YE = 12.4; BLOCK.append((Polygon(we), YE)); B.ring(we, Y0, 8.4, STALL, WH, 4.0); B.ring(we, 8.4, YE - 0.4, WIN, WH, 4.0); B.ring(we, YE - 0.4, YE + 0.4, PLAIN, WH); B.flat(we, YE, PLAIN, lin('#aeada8'))

# ================= 3. khối B mái đỏ =================
bb = WL(BLKB); YB0 = 4.6; E1, E2, E3 = 9.2, 12.8, 16.3; BLOCK.append((Polygon(bb), E3 + 2.5))
B.ring(bb, YB0, E1 - 0.6, STALL, WH, 4.2); B.ring(bb, E1 - 0.6, E1 + 0.3, PLAIN, lin('#d9d2c0')); B.ring(bb, E1 + 0.3, E2, WIN, WH, 4.2); B.ring(bb, E2, E3 - 0.3, WIN, WH, 4.2); B.ring(bb, E3 - 0.3, E3 + 0.2, PLAIN, WH)
can = WL([(89, 14.6), (133, 14.6), (133, -12.6), (89, -12.6)]); B.ring(can, E1 - 0.35, E1 - 0.1, PLAIN, WH); B.flat(can, E1 - 0.1, PLAIN, GREY); B.flat(can, E1 - 0.35, PLAIN, WH2, up=False)
eave = [(89.2, 14.3), (132.8, 14.3), (132.8, -12.3), (89.2, -12.3)]; ridge = [(101.5, 1.0), (120.5, 1.0)]; YRG = E3 + 5.2
p3 = lambda s, t, y: (L(s, t)[0], y, L(s, t)[1])
def roofq(a, b, c_, d_, nu):    # mảng mái ngói: a,b mép dưới; c_,d_ mép trên
    B.patch([p3(*a, E3 + 0.2), p3(*b, E3 + 0.2), p3(*c_, YRG), p3(*d_, YRG)], ROOFT, REDR, nu, 3, UP)
roofq(eave[0], eave[1], ridge[1], ridge[0], 10); roofq(eave[2], eave[3], ridge[0], ridge[1], 10)
B.patch([p3(*eave[1], E3 + 0.2), p3(*eave[2], E3 + 0.2), p3(*ridge[1], YRG), p3(*ridge[1], YRG)], ROOFT, REDR * 0.9, 6, 3, UP); B.patch([p3(*eave[3], E3 + 0.2), p3(*eave[0], E3 + 0.2), p3(*ridge[0], YRG), p3(*ridge[0], YRG)], ROOFT, REDR * 0.9, 6, 3, UP)
B.flat(WL(eave), E3 + 0.15, PLAIN, WH2, up=False)
for _f in ('rearB.py', 'rear2.py'): exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), _f)).read())
