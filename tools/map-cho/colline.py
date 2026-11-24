# Dựng lại Dalat Center và khách sạn Colline trong market.glb: đế ba tầng ốp gỗ nâu có băng trắng,
# trên là hai khối cao bảy tầng lam nâu sẫm đặt lùi vào trong, cách nhau một khe (Dalat Center phía bắc, Colline phía nam).
# Chỉ thay hình khối trong phạm vi nền công trình cũ; mặt đất, đường và lưới đi lại trong world_cho.js giữ nguyên.
# Chạy: python3 colline.py <market.glb vào> <market.glb ra>     (cần numpy, shapely)
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glbio, mb
from shapely.geometry import Polygon
from shapely import contains_xy, constrained_delaunay_triangles
from shapely.geometry.polygon import orient
src, dst = sys.argv[1], sys.argv[2]
m = glbio.load(src); P, N, UV, C, I = m['P'], m['N'], m['UV'], m['C'][:, :3], m['I']
FOOT = Polygon([(189, -110), (160, -89), (123, -138), (140, -151), (119, -179), (153, -178), (163, -174), (167, -171), (173, -158), (160, -148)])     # nền công trình (x, z)
cen = P[I].mean(1); ins = contains_xy(FOOT.buffer(0.6), cen[:, 0], cen[:, 2]); ny = np.abs(N[I[:, 0], 1]); ymax = P[I][:, :, 1].max(1)
old = ins & ((ny < 0.9) | (ymax > 12.5)); I = I[~old]; print('bỏ', int(old.sum()), 'tam giác của khối cũ')
B = mb.MB(); UP = np.array([0, 1.0, 0])
WOOD, DARK, DARK2, WHITE, CONC, ROOF, TERR = mb.lin('#b47a50'), mb.lin('#7a5743'), mb.lin('#5a4232'), mb.lin('#f8f6f0'), mb.lin('#aaa69e'), mb.lin('#969c8c'), mb.lin('#b9b4a6')
SHOP, LOUV, PLAIN, FLAT = (0, 1), (0, 3), (3, 0), (0, 2)
def wall(a, b, y0, y1, tile, col, out, bay=None, floors=1):
    a = np.asarray(a, float); b = np.asarray(b, float); L = np.hypot(*(b - a)); nb = max(1, int(round(L / bay))) if bay else 1; nh = np.array([out[0], 0, out[1]])
    for k in range(nb):
        p0, p1 = a + (b - a) * k / nb, a + (b - a) * (k + 1) / nb
        for f in range(floors):
            z0, z1 = y0 + (y1 - y0) * f / floors, y0 + (y1 - y0) * (f + 1) / floors
            B.quad([(p0[0], z0, p0[1]), (p1[0], z0, p1[1]), (p1[0], z1, p1[1]), (p0[0], z1, p0[1])], tile, col, nh)
def ring(pts, y0, y1, tile, col, bay=None, floors=1):
    q = list(orient(Polygon(pts), 1.0).exterior.coords[:-1])
    for a, b in zip(q, q[1:] + q[:1]): d = np.array(b) - np.array(a); wall(a, b, y0, y1, tile, col, (d[1], -d[0]) / np.hypot(*d), bay, floors)
def roof(pts, y, tile, col):
    for t in constrained_delaunay_triangles(Polygon(pts)).geoms:
        c = list(t.exterior.coords[:-1]); B.tri([(x, y, z) for x, z in c], [mb.tile_uv(tile, 0.1, 0.9), mb.tile_uv(tile, 0.9, 0.9), mb.tile_uv(tile, 0.5, 0.1)], col, UP)
F0 = 10.3; G1 = F0 + 4.8; TM = G1 + 2 * 3.7; TH = 7 * 3.6            # cao độ nền, hết tầng trệt, mặt sân đế, chiều cao hai khối trên
fp = list(FOOT.exterior.coords[:-1])
ring(fp, 4.5, F0, PLAIN, CONC); ring(fp, F0, G1, SHOP, mb.lin('#f2ece2'), bay=4.2); ring(fp, G1, TM, LOUV, WOOD, bay=3.0, floors=2); ring(fp, TM, TM + 1.4, PLAIN, WHITE); roof(fp, TM, FLAT, TERR)
A_, B_, C_ = np.array([123.0, -138.0]), np.array([160.0, -89.0]), np.array([189.0, -110.0]); cu = (B_ - A_) / np.hypot(*(B_ - A_)); cv = (C_ - B_) / np.hypot(*(C_ - B_))
pt = lambda u, v: tuple(A_ + cu * u + cv * v)
for u0, u1 in ((2.0, 30.0), (33.5, 59.5)):
    v0, v1 = 9.0, 33.5; q = [pt(u0, v0), pt(u1, v0), pt(u1, v1), pt(u0, v1)]
    ring(q, TM, TM + TH, LOUV, DARK, bay=2.6, floors=7); ring(q, TM + TH, TM + TH + 1.4, PLAIN, DARK2); roof(q, TM + TH, FLAT, ROOF)
    r2 = [pt(u0 + 5, v0 + 6), pt(u1 - 5, v0 + 6), pt(u1 - 5, v1 - 6), pt(u0 + 5, v1 - 6)]; ring(r2, TM + TH, TM + TH + 3.2, PLAIN, DARK2); roof(r2, TM + TH + 3.2, FLAT, mb.lin('#96968f'))
Pn, Nn, UVn, Cn = B.arrays(); In = np.arange(len(Pn)).reshape(-1, 3) + len(P)
nv, nt, size = mb.write_glb(dst, np.concatenate([P, Pn]), np.concatenate([N, Nn]), np.concatenate([UV, UVn]), np.concatenate([C, Cn]), np.concatenate([I, In]), m['img'])
print('thêm', len(In), 'tam giác; tệp mới', nv, 'đỉnh', nt, 'tam giác', size, 'byte; đỉnh cao nhất khối mới', round(TM + TH + 3.2, 1))
