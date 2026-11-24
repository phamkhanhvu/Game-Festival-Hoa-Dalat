# Làm kỹ góc quán cà phê trên khối thấp đầu cong cạnh cầu thang chợ (theo 6 ảnh thực tế):
# sân quán mở trên mái khối thấp, cột mảnh màu cam, lan can nan gỗ, bồn cây rủ viền mép sân, vách kính lùi vào trong,
# băng lam trang trí xám xanh nẹp vàng chạy quanh: cao ở hai bên, hạ thấp bằng đường cong chữ S khi ôm mũi cong;
# phía dưới thêm băng xanh dương trên dãy cửa hàng tầng trệt và đường chỉ vàng trên mảng tường trắng.
# Không dựng logo hay chữ thương hiệu thật. Chạy: python3 galaxy.py <market.glb vào> <market.glb ra>
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glbio, mb
from mb import lin, tile_uv
from design import *
FINS, WILL, GLASS, PLAIN, PAVE = (7, 0), (1, 7), (2, 4), (3, 0), (0, 2)
src, dst = sys.argv[1], sys.argv[2]
m = glbio.load(src); P, N, UV, C, I = m['P'], m['N'], m['UV'], m['C'][:, :3], m['I']
yB = WB['roof']; yg = Q + 4.2; v0 = WB['v0']; v1 = WB['v1'] - 0.03; vc = (WB['v0'] + WB['v1']) / 2; R = WB['R']; uc = WB['uc']
# bỏ lan can kính, bể nước và chậu cây cũ trên mái khối thấp (giữ sàn mái và vách kính của khối cao ở u = 12.5)
cen = P[I].mean(1); cu, cv = w2l(cen[:, 0], cen[:, 2])
inb = (cu > 12.8) & (((cu <= uc) & (cv > v0 - 0.15) & (cv < v1 + 0.15)) | ((cu > uc) & ((cu - uc) ** 2 + (cv - vc) ** 2 < (R + 0.15) ** 2)))
old = inb & (cen[:, 1] > yB + 0.02) & (cen[:, 1] < yB + 6); I = I[~old]; print('bỏ', int(old.sum()), 'tam giác cũ trên mái khối thấp')
B = mb.MB(); UPV = np.array([0, 1.0, 0])
# đường bao mép sân, chia mịn: từ góc tây nam (sát cầu thang), qua mũi cong, tới góc tây bắc
pts = [(u, v1) for u in np.linspace(WB['u0'], uc, 7)] + [(uc + R * np.cos(a), vc + (R - 0.03) * np.sin(a)) for a in np.linspace(np.pi / 2, -np.pi / 2, 37)[1:-1]] + [(u, v0) for u in np.linspace(uc, WB['u0'], 7)]
W = np.array([l2w(u, v) for u, v in pts], float); n = len(W)
seg = np.linalg.norm(np.diff(W, axis=0), axis=1); S = np.concatenate([[0], np.cumsum(seg)]); TOT = S[-1]
def outn(k):
    a = W[max(k - 1, 0)]; b = W[min(k + 1, n - 1)]; r = b - a; r /= np.linalg.norm(r); return np.array([-r[1], r[0]])
ON = np.array([outn(k) for k in range(n)])
if np.dot(ON[n // 2], W[n // 2] - W.mean(0)) < 0: ON = -ON
off = lambda d: W + ON * d
def p3(q, y): return (float(q[0]), float(y), float(q[1]))
def strip(A_, B_, ya0, ya1, yb0, yb1, tile, col, k, sub=None):       # mặt đứng giữa hai điểm liên tiếp, mặt ngoài theo ON
    nh = np.array([ON[k][0], 0, ON[k][1]]); B.quad([p3(A_, ya0), p3(B_, yb0), p3(B_, yb1), p3(A_, ya1)], tile, col, nh, sub)
smooth = lambda t: (lambda x: x * x * (3 - 2 * x))(np.clip(t, 0, 1))
FLOOR = yB; CEIL = yB + 3.3; LOW = yB + 5.9; TALL = yB + 8.5
def top(s):                                                            # mép trên băng lam: cao ở hai bên, thấp quanh mũi
    d = min(s, TOT - s); return LOW + (TALL - LOW) * (1 - smooth((d - 8.5) / 5.5))
TEAL, GOLD, ORANGE, WH, WH2, GREEN, BLUE = lin('#b4dde6'), lin('#d9a441'), lin('#e8963c'), lin('#f3f2ed'), lin('#e2dfd6'), lin('#9fd08a'), lin('#1f5fae')
E0, E1 = off(1.0), off(0.75)                                           # mép ngoài băng lam, mép trong
for k in range(n - 1):
    ta, tb = top(S[k]), top(S[k + 1])
    strip(E0[k], E0[k + 1], CEIL, ta, CEIL, tb, FINS, TEAL, k, (0.02, 0.05, 0.36, 0.95))             # băng lam: mỗi nhịp một tấm xám xanh kèm hai nẹp vàng
    strip(E0[k] + ON[k] * 0.03, E0[k + 1] + ON[k + 1] * 0.03, CEIL - 0.16, CEIL + 0.05, CEIL - 0.16, CEIL + 0.05, PLAIN, GOLD, k)     # nẹp vàng dưới
    strip(E0[k] + ON[k] * 0.03, E0[k + 1] + ON[k + 1] * 0.03, ta - 0.14, ta + 0.06, tb - 0.14, tb + 0.06, PLAIN, GOLD, k)             # nẹp vàng trên
    B.quad([p3(E1[k], ta), p3(E1[k + 1], tb), p3(E1[k + 1], CEIL), p3(E1[k], CEIL)], PLAIN, lin('#cfd6d2'), -np.array([ON[k][0], 0, ON[k][1]]))   # mặt trong
    B.quad([p3(E0[k], ta + 0.06), p3(E0[k + 1], tb + 0.06), p3(E1[k + 1], tb + 0.06), p3(E1[k], ta + 0.06)], PLAIN, GOLD, UPV)                   # mũ trên
# trần và mái quán (quạt từ tâm), mái nằm ở cao độ băng thấp
ctr = np.array(l2w(uc - 2.0, vc), float)
for k in range(n - 1):
    B.tri([p3(ctr, CEIL), p3(E0[k + 1], CEIL), p3(E0[k], CEIL)], [tile_uv(PLAIN, .5, .5)] * 3, lin('#efe9dc'), -UPV)
    B.tri([p3(ctr, LOW - 0.25), p3(E1[k], LOW - 0.25), p3(E1[k + 1], LOW - 0.25)], [tile_uv(PLAIN, .5, .5)] * 3, lin('#b9bdb8'), UPV)
for a, b in ((E0[-1], E0[0]),): B.tri([p3(ctr, CEIL), p3(a, CEIL), p3(b, CEIL)], [tile_uv(PLAIN, .5, .5)] * 3, lin('#efe9dc'), -UPV); B.tri([p3(ctr, LOW - 0.25), p3(a, LOW - 0.25), p3(b, LOW - 0.25)], [tile_uv(PLAIN, .5, .5)] * 3, lin('#b9bdb8'), UPV)
# lan can nan gỗ, bồn cây rủ, cột cam mảnh
PL0, PL1 = off(0.05), off(0.85)
for k in range(n - 1):
    strip(W[k], W[k + 1], FLOOR, FLOOR + 1.0, FLOOR, FLOOR + 1.0, FINS, ORANGE, k)
    strip(PL1[k], PL1[k + 1], FLOOR - 0.45, FLOOR + 0.3, FLOOR - 0.45, FLOOR + 0.3, PLAIN, WH, k)                      # thành bồn
    B.quad([p3(PL0[k], FLOOR + 0.34), p3(PL1[k], FLOOR + 0.34), p3(PL1[k + 1], FLOOR + 0.34), p3(PL0[k + 1], FLOOR + 0.34)], WILL, GREEN, UPV)
    strip(PL1[k] + ON[k] * 0.05, PL1[k + 1] + ON[k + 1] * 0.05, FLOOR - 0.5 - 0.25 * (k % 3 == 1), FLOOR + 0.42, FLOOR - 0.5 - 0.25 * (k % 3 == 0), FLOOR + 0.42, WILL, GREEN, k)   # dây rủ
    B.quad([p3(W[k], FLOOR - 0.45), p3(W[k + 1], FLOOR - 0.45), p3(PL1[k + 1], FLOOR - 0.45), p3(PL1[k], FLOOR - 0.45)], PLAIN, WH2, -UPV)
for k in range(1, n - 1, 3):
    q = W[k] + ON[k] * 0.35; t = np.array([-ON[k][1], ON[k][0]]); B.obox(q, t, ON[k], 0.07, 0.07, FLOOR, CEIL, ORANGE, top=False)
# vách kính của quán lùi vào trong, trụ trắng lớn hai bên
IN = off(-3.4)
for k in range(n - 1): strip(IN[k], IN[k + 1], FLOOR, CEIL, FLOOR, CEIL, GLASS, lin('#8fa3a8'), k)
for k in (8, n - 9): q = W[k] - ON[k] * 0.7; t = np.array([-ON[k][1], ON[k][0]]); B.obox(q, t, ON[k], 0.55, 0.55, FLOOR, CEIL, WH, top=False)
# bàn ghế trên sân quán
for k in range(4, n - 4, 5):
    q = W[k] - ON[k] * 1.7; B.prism((q[0], q[1]), 0.45, 0.45, FLOOR + 0.70, FLOOR + 0.76, 6, lin('#c9a273')); B.prism((q[0], q[1]), 0.05, 0.05, FLOOR, FLOOR + 0.7, 4, lin('#5a5148'), cap=False)
# tầng dưới: băng xanh dương trên dãy cửa hàng, chỉ vàng trên mảng tường trắng
F0, F1 = off(0.95), off(0.04)
for k in range(5, n - 6):
    strip(F0[k], F0[k + 1], yg - 1.15, yg - 0.03, yg - 1.15, yg - 0.03, PLAIN, BLUE, k); strip(F0[k], F0[k + 1], yg - 1.3, yg - 1.15, yg - 1.3, yg - 1.15, PLAIN, lin('#3aa655'), k)
    B.quad([p3(W[k], yg - 1.3), p3(W[k + 1], yg - 1.3), p3(F0[k + 1], yg - 1.3), p3(F0[k], yg - 1.3)], PLAIN, WH2, -UPV)
for k in range(n - 1):
    yl = yg + (FLOOR - 0.5 - yg) * (0.45 + 0.2 * np.sin(S[k] / TOT * np.pi * 3)); yr = yg + (FLOOR - 0.5 - yg) * (0.45 + 0.2 * np.sin(S[k + 1] / TOT * np.pi * 3))
    strip(F1[k], F1[k + 1], yl, yl + 0.16, yr, yr + 0.16, PLAIN, lin('#e3c24a'), k)
Pn, Nn, UVn, Cn = B.arrays(); In = np.arange(len(Pn)).reshape(-1, 3) + len(P)
nv, nt, size = mb.write_glb(dst, np.concatenate([P, Pn]), np.concatenate([N, Nn]), np.concatenate([UV, UVn]), np.concatenate([C, Cn]), np.concatenate([I, In]), m['img'])
print('thêm', len(In), 'tam giác; tệp mới', nt, 'tam giác', size, 'byte')
