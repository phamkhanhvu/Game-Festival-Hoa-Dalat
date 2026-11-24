# Làm kỹ góc quán cà phê trên khối thấp đầu cong cạnh cầu thang chợ (theo 6 ảnh thực tế):
# sân quán mở trên mái khối thấp, cột mảnh màu cam, lan can nan gỗ, bồn cây rủ viền mép sân, vách kính lùi vào trong,
# băng lam trang trí xám xanh nẹp vàng chạy quanh: cao ở hai bên, hạ thấp bằng đường cong chữ S khi ôm mũi cong;
# phía dưới thêm băng xanh dương trên dãy cửa hàng tầng trệt và đường chỉ vàng trên mảng tường trắng.
# Mặt bằng khối thấp là khung chữ nhật bo tròn hai góc phía bùng binh (không phải đầu bán nguyệt): tệp này dựng lại cả khối thấp theo mặt bằng đó
# và chặn thêm phần hai góc mới trong lưới đi lại của world_cho.js.
# Tầng trệt mặt nhìn ra bùng binh là nhà thuốc: thêm hai ô vân vào atlas (biển NHÀ THUỐC chữ thập xanh, mặt tiền quầy thuốc).
# Không dựng logo hay chữ thương hiệu thật. Chạy: python3 galaxy.py <market.glb vào> <market.glb ra> [<world_cho.js vào> <world_cho.js ra>]
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glbio, mb
from mb import lin, tile_uv
from design import *
FINS, WILL, GLASS, PLAIN, PAVE = (7, 0), (1, 7), (2, 4), (3, 0), (0, 2)
src, dst = sys.argv[1], sys.argv[2]
m = glbio.load(src); P, N, UV, C, I = m['P'], m['N'], m['UV'], m['C'][:, :3], m['I']
yB = WB['roof']; yg = Q + 4.2; v0 = WB['v0']; v1 = WB['v1'] - 0.03; vc = (WB['v0'] + WB['v1']) / 2; R = WB['R']; uc = WB['uc']
UE = uc + R; RC = 4.5                                                     # mép đông khối thấp và bán kính bo góc
arc = lambda cu_, cv_, a0, a1: [(cu_ + RC * np.cos(a), cv_ + RC * np.sin(a)) for a in np.linspace(a0, a1, 8)]
pts = [(u, v1) for u in np.linspace(WB['u0'], UE - RC, 12)[:-1]] + arc(UE - RC, v1 - RC, np.pi / 2, 0) + [(UE, v) for v in np.linspace(v1 - RC, v0 + RC, 12)[1:-1]] + arc(UE - RC, v0 + RC, 0, -np.pi / 2) + [(u, v0) for u in np.linspace(UE - RC, WB['u0'], 12)[1:]]
from shapely.geometry import Polygon
from shapely import contains_xy
FOOT = Polygon(pts + [(WB['u0'], v0)])
# bỏ toàn bộ khối thấp cũ (tường, mái đón, sàn mái, lan can, bể nước, chậu cây) và các vật nằm trong hai góc mới; giữ vách kính khối cao ở u = 12.5 và lan can cầu thang
cen = P[I].mean(1); cu, cv = w2l(cen[:, 0], cen[:, 2])
inb = (cu > 12.8) & (cv < v1 + 0.15) & contains_xy(FOOT.buffer(1.0), cu, cv)
old = inb & (cen[:, 1] > Q + 0.6) & (cen[:, 1] < yB + 6); I = I[~old]; print('bỏ', int(old.sum()), 'tam giác của khối thấp cũ')
B = mb.MB(); UPV = np.array([0, 1.0, 0])
# ----- hai ô vân mới cho nhà thuốc: (5,2) nửa trên là biển hiệu; (6,2) là mặt tiền quầy thuốc -----
import io
from PIL import Image, ImageDraw, ImageFont
PHSIGN, PHSHOP = (5, 2), (6, 2)
def patch_atlas(jpeg):
    A = Image.open(io.BytesIO(jpeg)).convert('RGB'); F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    t = Image.new('RGB', (256, 256), (31, 95, 174)); d = ImageDraw.Draw(t)
    d.rectangle([0, 0, 255, 127], fill=(31, 95, 174)); d.rectangle([0, 118, 255, 127], fill=(58, 166, 85))
    d.ellipse([10, 34, 62, 86], fill=(255, 255, 255)); d.rectangle([30, 42, 42, 78], fill=(40, 160, 80)); d.rectangle([18, 54, 54, 66], fill=(40, 160, 80))
    f = ImageFont.truetype(F, 26); d.text((72, 44), 'NHÀ THUỐC', font=f, fill=(255, 255, 255))
    d.rectangle([0, 128, 255, 255], fill=(240, 244, 246)); f2 = ImageFont.truetype(F, 20); d.text((14, 150), 'THUỐC TỐT · GIÁ TỐT', font=f2, fill=(31, 95, 174)); d.text((14, 190), 'MỞ CỬA MỖI NGÀY', font=f2, fill=(40, 140, 80))
    A.paste(t, (PHSIGN[0] * 256, PHSIGN[1] * 256))
    t = Image.new('RGB', (256, 256), (236, 240, 242)); d = ImageDraw.Draw(t)
    d.rectangle([6, 10, 249, 255], fill=(206, 226, 236)); d.rectangle([6, 10, 249, 16], fill=(120, 130, 138))
    for cx in (6, 126, 244): d.rectangle([cx, 10, cx + 5, 255], fill=(120, 130, 138))
    cols = [(255, 255, 255), (60, 140, 200), (240, 200, 70), (70, 170, 110), (230, 100, 90), (250, 250, 250)]
    for half, x0 in enumerate((16, 136)):
        for r in range(4):
            y = 40 + r * 52; d.rectangle([x0, y + 34, x0 + 102, y + 38], fill=(250, 250, 250))
            for c in range(6): d.rectangle([x0 + 2 + c * 17, y + 6 + (c * 7 + r * 3) % 9, x0 + 15 + c * 17, y + 33], fill=cols[(c + r + half) % 6])
    d.ellipse([196, 20, 236, 60], fill=(255, 255, 255)); d.rectangle([211, 26, 221, 54], fill=(40, 160, 80)); d.rectangle([202, 35, 230, 45], fill=(40, 160, 80))
    A.paste(t, (PHSHOP[0] * 256, PHSHOP[1] * 256)); out = io.BytesIO(); A.save(out, 'JPEG', quality=90, optimize=True); return out.getvalue()
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
EAST = [k for k in range(n - 1) if pts[k][0] > UE - 0.01 and pts[k + 1][0] > UE - 0.01]          # các nhịp của mặt phẳng phía bùng binh
# thân khối thấp: kính cửa hàng tầng trệt, tường trắng phía trên, sàn mái lát gạch
for k in range(n - 1):
    if k in EAST[:10]: e = EAST.index(k); strip(W[k], W[k + 1], Q - 0.5, yg - 1.3, Q - 0.5, yg - 1.3, PHSHOP, lin('#ffffff'), k, (0.5 * (e % 2), 0, 0.5 * (e % 2) + 0.5, 1)); strip(W[k], W[k + 1], yg - 1.3, yg, yg - 1.3, yg, PLAIN, WH, k)      # nhà thuốc ở mặt nhìn ra bùng binh
    else: strip(W[k], W[k + 1], Q - 0.5, yg, Q - 0.5, yg, GLASS, lin('#ffffff', 0.96), k)
    strip(W[k], W[k + 1], yg, FLOOR, yg, FLOOR, PLAIN, WH, k)
    B.tri([p3(ctr, FLOOR), p3(W[k], FLOOR), p3(W[k + 1], FLOOR)], [tile_uv(PAVE, .5, .5), tile_uv(PAVE, .1, .1), tile_uv(PAVE, .9, .1)], lin('#d9d6ce'), UPV)
B.tri([p3(ctr, FLOOR), p3(W[-1], FLOOR), p3(W[0], FLOOR)], [tile_uv(PLAIN, .5, .5)] * 3, lin('#d9d6ce'), UPV)
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
for k in (9, n - 10): q = W[k] - ON[k] * 0.7; t = np.array([-ON[k][1], ON[k][0]]); B.obox(q, t, ON[k], 0.55, 0.55, FLOOR, CEIL, WH, top=False)
# bàn ghế trên sân quán
for k in range(4, n - 4, 5):
    q = W[k] - ON[k] * 1.7; B.prism((q[0], q[1]), 0.45, 0.45, FLOOR + 0.70, FLOOR + 0.76, 6, lin('#c9a273')); B.prism((q[0], q[1]), 0.05, 0.05, FLOOR, FLOOR + 0.7, 4, lin('#5a5148'), cap=False)
# tầng dưới: băng xanh dương trên dãy cửa hàng, chỉ vàng trên mảng tường trắng
F0, F1 = off(0.95), off(0.04)
SG = EAST[len(EAST) // 2 - 3:len(EAST) // 2 + 3]
for e, k in enumerate(SG): strip(F0[k] + ON[k] * 0.03, F0[k + 1] + ON[k + 1] * 0.03, yg - 1.12, yg - 0.06, yg - 1.12, yg - 0.06, PHSIGN, lin('#ffffff'), k, (e / len(SG), 0, (e + 1) / len(SG), 0.5))     # biển NHÀ THUỐC trên băng xanh
for k in range(1, n - 2):
    B.quad([p3(W[k], yg + 0.16), p3(F0[k], yg + 0.16), p3(F0[k + 1], yg + 0.16), p3(W[k + 1], yg + 0.16)], PLAIN, WH, UPV); strip(F0[k], F0[k + 1], yg - 0.03, yg + 0.16, yg - 0.03, yg + 0.16, PLAIN, WH2, k)
    strip(F0[k], F0[k + 1], yg - 1.15, yg - 0.03, yg - 1.15, yg - 0.03, PLAIN, BLUE, k); strip(F0[k], F0[k + 1], yg - 1.3, yg - 1.15, yg - 1.3, yg - 1.15, PLAIN, lin('#3aa655'), k)
    B.quad([p3(W[k], yg - 1.3), p3(W[k + 1], yg - 1.3), p3(F0[k + 1], yg - 1.3), p3(F0[k], yg - 1.3)], PLAIN, WH2, -UPV)
for k in range(n - 1):
    yl = yg + (FLOOR - 0.5 - yg) * (0.45 + 0.2 * np.sin(S[k] / TOT * np.pi * 3)); yr = yg + (FLOOR - 0.5 - yg) * (0.45 + 0.2 * np.sin(S[k + 1] / TOT * np.pi * 3))
    strip(F1[k], F1[k + 1], yl, yl + 0.16, yr, yr + 0.16, PLAIN, lin('#e3c24a'), k)
Pn, Nn, UVn, Cn = B.arrays(); In = np.arange(len(Pn)).reshape(-1, 3) + len(P)
nv, nt, size = mb.write_glb(dst, np.concatenate([P, Pn]), np.concatenate([N, Nn]), np.concatenate([UV, UVn]), np.concatenate([C, Cn]), np.concatenate([I, In]), patch_atlas(m['img']))
print('thêm', len(In), 'tam giác; tệp mới', nt, 'tam giác', size, 'byte')
if len(sys.argv) > 4:                                                    # chặn phần mặt bằng mới trong lưới đi lại, bỏ đèn và chậu rơi vào trong nhà
    import worldio
    j, h, tp, kk, pre, post = worldio.load(sys.argv[3]); nx, nz, x0, z0, st = j['nx'], j['nz'], j['x0'], j['z0'], j['step']
    X, Z = np.meshgrid(x0 + np.arange(nx) * st, z0 + np.arange(nz) * st); gu, gv = w2l(X, Z); ins = contains_xy(FOOT.buffer(0.35), gu.ravel(), gv.ravel()).reshape(nz, nx) & (gu > WB['u0'])
    new = ins & (h > -30000); h[ins] = -32768; tp[ins] = int(round(yB * 100)); print('chặn thêm', int(new.sum()), 'ô lưới')
    for key in ('lamps', 'pots', 'trees', 'utrees', 'flowers', 'flags'):
        if isinstance(j.get(key), list) and j[key]:
            def inside(o):
                x, z = (o['x'], o['z']) if isinstance(o, dict) else (o[0], o[1]); u_, v_ = w2l(x, z); return bool(u_ > WB['u0']) and bool(contains_xy(FOOT.buffer(0.8), float(u_), float(v_)))
            keep = [o for o in j[key] if not inside(o)]
            if len(keep) != len(j[key]): print(key, 'bỏ', len(j[key]) - len(keep)); j[key] = keep
    worldio.save(sys.argv[4], j, h, tp, kk, pre, post)
