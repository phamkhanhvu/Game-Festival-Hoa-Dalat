# Làm kỹ lại mặt tiền Chợ Đà Lạt và tượng đài ở bùng binh theo ảnh thực tế (2026-11):
#  mặt tiền cong ôm bùng binh, từ dưới lên: sạp hàng và mái tôn che, dải bảng quảng cáo treo mép mái đón (giữa là bảng LED), mái đón bê tông dày,
#  lan can bông gió zíc zắc, hành lang hở có cột, khối trên nhô ra gồm băng gạch cam đất, lam ngang trắng và dãy cửa kính, tường mái trắng mang chữ đỏ CHỢ ĐÀ LẠT;
#  đầu tây là khối cao ốp gạch trắng có ô cửa vuông nhỏ; sân thượng có hàng cây bách, cột cờ, dù trắng, khinh khí cầu trang trí;
#  tượng đài: bệ đá, nhóm tượng người quanh thân cây, tán cây nhiều tầng hình nấm.
# Bảng quảng cáo dùng nội dung chung (đặc sản, hoa, dâu...), không dựng thương hiệu thật. Lưới đi lại không đổi (không thêm vật cản dưới đất).
# Chạy: python3 cho.py <market.glb vào> <world_cho.js> <market.glb ra>
import sys, os, io, math, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glbio, mb, worldio
from mb import lin, tile_uv
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon
from shapely import contains_xy
src, wsrc, dst = sys.argv[1], sys.argv[2], sys.argv[3]
m = glbio.load(src); P, N, UV, C, I = m['P'], m['N'], m['UV'], m['C'][:, :3], m['I']
wj, wh, _, _, _, _ = worldio.load(wsrc)
def terr(x, z):
    i = np.clip(np.round((np.asarray(x) - wj['x0']) / wj['step']).astype(int), 0, wj['nx'] - 1); j = np.clip(np.round((np.asarray(z) - wj['z0']) / wj['step']).astype(int), 0, wj['nz'] - 1)
    v = wh[j, i] / 100.0; return np.where(v < -50, 4.4, v)
# ---------- cung mặt tiền (giống gen.py): d = khoảng lùi theo bán kính tính từ mép mái đón; d = 4.8 là chân tường ----------
_w, _e = np.array([4.0, -15.0]), np.array([51.0, -29.0]); _c = np.hypot(*(_e - _w)) / 2; _sag = 7.0; R = (_c * _c + _sag * _sag) / (2 * _sag)
_n = np.array([(_e - _w)[1], -(_e - _w)[0]]) / (2 * _c); _n = _n if _n[1] < 0 else -_n; AC = (_w + _e) / 2 + _n * _sag - _n * R
A0, A1 = math.atan2(*(_w - AC)[::-1]), math.atan2(*(_e - AC)[::-1]); LARC = R * (A1 - A0)
def Wp(t, d): th = A0 + (A1 - A0) * t; return AC + (R + d) * np.array([math.cos(th), math.sin(th)])
def rad(t): th = A0 + (A1 - A0) * t; return np.array([math.cos(th), math.sin(th)])
def tan(t): th = A0 + (A1 - A0) * t; return np.array([-math.sin(th), math.cos(th)])
def G(t): return 4.55 + (3.65 - 4.55) * min(max(t, 0), 1)          # cao độ mặt đất dọc mặt tiền
Y0 = 4.5; YBB0, YBB1, YS0, YS1, YZ1, YG1, YO1, YW1, YR, YP = 7.6, 9.45, 9.5, 10.1, 11.7, 12.5, 13.7, 16.7, 16.8, 18.7
TB0 = 0.24                                                          # khối cao đầu tây chiếm phần t < TB0
# ---------- bỏ mặt tiền cũ, tháp cũ và tượng đài cũ ----------
cen = P[I].mean(1); ny = N[I[:, 0], 1]; r = np.hypot(cen[:, 0] - AC[0], cen[:, 2] - AC[1]); th = np.arctan2(cen[:, 2] - AC[1], cen[:, 0] - AC[0]); tg = terr(cen[:, 0], cen[:, 2])
zone = (r > R - 0.7) & (r < R + 7.0) & (th > A0 - 0.03) & (th < A1 + 0.03) & (cen[:, 1] > tg + 0.3)
roofkeep = (ny > 0.9) & (cen[:, 1] > 16.4) & (r > R + 4.8)
TWR = Polygon([(2.5, -37), (2.5, -26), (10.5, -27), (10.5, -40)]).buffer(0.6); tower = contains_xy(TWR, cen[:, 0], cen[:, 2]) & (cen[:, 1] > 16.9)
MC = np.array([31.5, 11.5]); mon = (np.hypot(cen[:, 0] - MC[0], cen[:, 2] - MC[1]) < 3.3) & (cen[:, 1] > 3.97)
old = (zone & ~roofkeep) | tower | mon; I = I[~old]; print('bỏ', int(old.sum()), 'tam giác cũ (mặt tiền', int((zone & ~roofkeep).sum()), ', tháp', int(tower.sum()), ', tượng', int(mon.sum()), ')')
# ---------- ô vân mới ----------
ZIG, AD1, AD2, LED, SIGN, WT, WSQ, WIN, ORG, STALL, STONE = (4, 3), (5, 3), (6, 3), (7, 3), (4, 4), (5, 4), (6, 4), (7, 4), (4, 5), (5, 5), (6, 5)
FB, FS = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
def fit(d, text, box, fill, font=FB, maxsize=90):
    x0, y0, x1, y1 = box; s = maxsize
    while s > 6:
        f = ImageFont.truetype(font, s); bb = d.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= x1 - x0 and bb[3] - bb[1] <= y1 - y0: break
        s -= 1
    d.text((x0 + (x1 - x0 - (bb[2] - bb[0])) / 2 - bb[0], y0 + (y1 - y0 - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=fill)
def noisy(img, amt, seed):
    a = np.array(img).astype(np.float32); a += np.random.default_rng(seed).normal(0, amt, a.shape[:2])[:, :, None]; return Image.fromarray(a.clip(0, 255).astype(np.uint8))
def patch_atlas(jpeg):
    A = Image.open(io.BytesIO(jpeg)).convert('RGB'); put = lambda tile, im: A.paste(im, (tile[0] * 256, tile[1] * 256))
    t = Image.new('RGB', (256, 256), (66, 70, 78)); d = ImageDraw.Draw(t)                       # bông gió zíc zắc
    for row in range(3):
        yb = 40 + row * 70
        pts = [(x, yb + (0 if (x // 32) % 2 == 0 else 50)) for x in range(0, 257, 32)]; d.line(pts, fill=(250, 250, 246), width=13, joint='curve')
    d.rectangle([0, 0, 255, 15], fill=(250, 250, 246)); d.rectangle([0, 240, 255, 255], fill=(250, 250, 246)); d.rectangle([0, 0, 9, 255], fill=(250, 250, 246)); d.rectangle([246, 0, 255, 255], fill=(250, 250, 246)); put(ZIG, t)
    def ads(specs):
        t = Image.new('RGB', (256, 256)); d = ImageDraw.Draw(t)
        for k, (bg, fg, big, small, acc) in enumerate(specs):
            y = k * 128; d.rectangle([0, y, 255, y + 127], fill=bg); d.rectangle([0, y, 255, y + 127], outline=(250, 250, 250), width=4)
            d.ellipse([14, y + 30, 82, y + 98], fill=acc); d.ellipse([34, y + 46, 62, y + 74], fill=(255, 255, 255))
            fit(d, big, (92, y + 22, 246, y + 76), fg, maxsize=40); fit(d, small, (92, y + 80, 246, y + 108), fg, maxsize=18)
        return t
    put(AD1, ads([((38, 132, 84), (255, 255, 255), 'ĐẶC SẢN', 'MỨT · TRÀ · CÀ PHÊ', (250, 204, 60)), ((232, 120, 46), (255, 255, 255), 'DÂU TÂY', 'HÁI TẠI VƯỜN', (214, 40, 60))]))
    put(AD2, ads([((244, 240, 228), (40, 110, 70), 'HOA ĐÀ LẠT', 'TƯƠI MỖI SÁNG', (236, 110, 170)), ((36, 104, 176), (255, 255, 255), 'RAU CỦ', 'SẠCH · NGON', (120, 196, 90))]))
    t = Image.new('RGB', (256, 256), (16, 14, 14)); d = ImageDraw.Draw(t); d.rectangle([0, 0, 255, 127], outline=(120, 30, 30), width=4)           # bảng LED
    fit(d, 'CHÀO MỪNG ĐẾN', (12, 14, 244, 56), (255, 60, 50), maxsize=34); fit(d, 'CHỢ ĐÀ LẠT', (12, 60, 244, 116), (255, 80, 60), maxsize=44)
    for x in range(0, 256, 4): d.line([(x, 0), (x, 127)], fill=(16, 14, 14), width=1)
    for k in range(4): x = k * 64; d.rectangle([x, 128, x + 63, 255], fill=[(250, 226, 110), (120, 190, 110)][k % 2]); d.rectangle([x, 128, x + 63, 255], outline=(60, 110, 60), width=3); fit(d, ['QUÀ', 'HOA', 'MỨT', 'TRÀ'][k], (x + 6, 160, x + 58, 224), (30, 90, 50), maxsize=30)
    put(LED, t)
    s = Image.new('RGB', (1024, 87), (250, 250, 246)); fit(ImageDraw.Draw(s), 'CHỢ ĐÀ LẠT', (20, 4, 1004, 83), (206, 36, 40), font=FS, maxsize=86); s = s.resize((1024, 64), Image.LANCZOS)
    t = Image.new('RGB', (256, 256), (250, 250, 246)); [t.paste(s.crop((k * 256, 0, k * 256 + 256, 64)), (0, k * 64)) for k in range(4)]; put(SIGN, t)
    def wtile():
        t = Image.new('RGB', (256, 256), (246, 246, 242)); d = ImageDraw.Draw(t)
        for k in range(0, 256, 32): d.line([(k, 0), (k, 255)], fill=(226, 228, 226), width=2); d.line([(0, k), (255, k)], fill=(226, 228, 226), width=2)
        return t
    put(WT, noisy(wtile(), 2.5, 1)); t = wtile(); d = ImageDraw.Draw(t); d.rectangle([78, 70, 178, 170], fill=(236, 236, 232)); d.rectangle([88, 80, 168, 160], fill=(58, 72, 84)); d.line([(128, 80), (128, 160)], fill=(236, 236, 232), width=5); d.rectangle([78, 170, 178, 178], fill=(200, 202, 200)); put(WSQ, noisy(t, 2.5, 2))
    t = Image.new('RGB', (256, 256), (248, 248, 244)); d = ImageDraw.Draw(t)                                                                   # cửa kính trên, lam ngang dưới
    for k in range(2): x = k * 128; d.rectangle([x + 8, 10, x + 120, 100], fill=(52, 70, 86)); d.rectangle([x + 8, 10, x + 120, 40], fill=(74, 98, 118))
    for k in range(5): y = 112 + k * 28; d.rectangle([0, y + 18, 255, y + 26], fill=(150, 156, 160)); d.rectangle([0, y, 255, y + 17], fill=(250, 250, 248))
    d.rectangle([0, 0, 5, 255], fill=(248, 248, 244)); d.rectangle([124, 104, 131, 255], fill=(240, 240, 236)); put(WIN, t)
    t = Image.new('RGB', (256, 256), (198, 122, 88)); d = ImageDraw.Draw(t)
    for k in range(0, 256, 16): d.line([(k, 0), (k, 255)], fill=(178, 106, 76), width=1); d.line([(0, k), (255, k)], fill=(178, 106, 76), width=1)
    put(ORG, noisy(t, 6, 3))
    t = Image.new('RGB', (256, 256), (46, 40, 36)); d = ImageDraw.Draw(t); rng = np.random.default_rng(5)                                       # sạp hàng
    d.rectangle([0, 0, 255, 38], fill=(244, 222, 96)); d.rectangle([0, 0, 255, 38], outline=(70, 130, 70), width=3); fit(d, 'ĐẶC SẢN · HOA · MỨT', (10, 6, 246, 32), (36, 100, 56), maxsize=22)
    for row in range(3):
        y = 52 + row * 46; d.rectangle([10, y + 34, 246, y + 39], fill=(190, 170, 140))
        for k in range(13): c = [(214, 60, 60), (240, 190, 60), (250, 250, 240), (120, 180, 90), (236, 130, 60), (150, 90, 160)][int(rng.integers(6))]; d.rectangle([14 + k * 18, y + 8 + int(rng.integers(8)), 28 + k * 18, y + 33], fill=c)
    d.rectangle([0, 190, 255, 255], fill=(60, 110, 62))
    for k in range(60): x, y = int(rng.integers(6, 250)), int(rng.integers(192, 250)); c = [(236, 80, 110), (250, 214, 70), (250, 250, 250), (240, 140, 60), (190, 110, 220)][int(rng.integers(5))]; d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=c)
    d.rectangle([0, 0, 6, 255], fill=(236, 236, 230)); d.rectangle([249, 0, 255, 255], fill=(236, 236, 230)); put(STALL, t)
    put(STONE, noisy(Image.new('RGB', (256, 256), (160, 164, 166)), 14, 7))
    out = io.BytesIO(); A.save(out, 'JPEG', quality=90, optimize=True); return out.getvalue()
# ---------- dựng ----------
B = mb.MB(); UP = np.array([0, 1.0, 0]); DN = -UP; WH = lin('#f6f5f0'); WH2 = lin('#e4e2da'); PL = mb.PLAIN; FULL = lin('#ffffff')
def p3(q, y): return (float(q[0]), float(y), float(q[1]))
def nh2(v): return np.array([v[0], 0, v[1]])
def vq(t0, t1, d, y0, y1, tile=PL, col=WH, sub=None, back=False):
    B.quad([p3(Wp(t0, d), y0), p3(Wp(t1, d), y0), p3(Wp(t1, d), y1), p3(Wp(t0, d), y1)], tile, col, nh2(rad((t0 + t1) / 2) * (1 if back else -1)), sub)
def band(tA, tB, d, y0, y1, tile=PL, col=WH, tw=None, sub=None, back=False):          # dải mặt đứng theo cung; tw: bề rộng một ô vân (m), None = màu trơn
    n = max(1, int(round((tB - tA) * LARC / tw))) if tw else 1; m_ = max(1, int(math.ceil(((tB - tA) * LARC / n) / 1.15))); s0, v0, s1, v1 = sub or (0, 0, 1, 1)
    for k in range(n):
        for j in range(m_):
            ta = tA + (tB - tA) * (k + j / m_) / n; tb = tA + (tB - tA) * (k + (j + 1) / m_) / n
            vq(ta, tb, d, y0, y1, tile, col, (s0 + (s1 - s0) * j / m_, v0, s0 + (s1 - s0) * (j + 1) / m_, v1) if tw else None, back)
def hq(tA, tB, d0, d1, y, col=WH, up=True, tile=PL):
    n = max(1, int(math.ceil((tB - tA) * LARC / 1.15)))
    for k in range(n):
        ta, tb = tA + (tB - tA) * k / n, tA + (tB - tA) * (k + 1) / n; B.quad([p3(Wp(ta, d0), y), p3(Wp(tb, d0), y), p3(Wp(tb, d1), y), p3(Wp(ta, d1), y)], tile, col, UP if up else DN)
def wall(a, b, y0, y1, tile=PL, col=WH, out=None, tw=None, thh=None, sub=None):         # tường phẳng giữa hai điểm (x, z), chia ô tw x thh
    a = np.asarray(a, float); b = np.asarray(b, float); L = np.hypot(*(b - a)); nx_ = max(1, int(round(L / tw))) if tw else 1; nyy = max(1, int(round((y1 - y0) / thh))) if thh else 1
    for i in range(nx_):
        for j in range(nyy):
            q0, q1 = a + (b - a) * i / nx_, a + (b - a) * (i + 1) / nx_; z0, z1 = y0 + (y1 - y0) * j / nyy, y0 + (y1 - y0) * (j + 1) / nyy
            B.quad([p3(q0, z0), p3(q1, z0), p3(q1, z1), p3(q0, z1)], tile, col, nh2(out), sub)
# tầng trệt: tường sạp hàng, mái tôn che, bảng tên sạp
band(-0.01, 1.01, 4.8, 2.8, YS0, PL, lin('#d8d4ca'))
NST = 15
for k in range(NST):
    ta, tb = k / NST, (k + 1) / NST; g = G((ta + tb) / 2); band(ta, tb, 4.72, g, g + 3.0, STALL, FULL, tw=(tb - ta) * LARC)
    ac = [lin('#7a3b34'), lin('#f1efe8'), lin('#2f6f52'), lin('#f1efe8'), lin('#8a4a2a')][k % 5]; n = 3
    for j in range(n):
        t0_, t1_ = ta + (tb - ta) * j / n, ta + (tb - ta) * (j + 1) / n - 0.0015
        B.quad([p3(Wp(t0_, 0.6), g + 3.25), p3(Wp(t1_, 0.6), g + 3.25), p3(Wp(t1_, -2.3), g + 2.75), p3(Wp(t0_, -2.3), g + 2.75)], PL, ac * (0.92 if j % 2 else 1.0), UP)
        B.quad([p3(Wp(t0_, -2.3), g + 2.75), p3(Wp(t1_, -2.3), g + 2.75), p3(Wp(t1_, -2.3), g + 2.55), p3(Wp(t0_, -2.3), g + 2.55)], PL, ac * 0.8, nh2(-rad(ta)))
    if k % 2 == 0: q = Wp((ta + tb) / 2, -2.2); B.prism((q[0], q[1]), 0.045, 0.045, g, g + 2.6, 4, lin('#70747a'), cap=False)
# dải bảng quảng cáo treo mép mái đón, giữa là bảng LED
NB = 12; tb0, tb1 = 0.03, 0.97; cell = (tb1 - tb0) / NB; specs = [(AD1, 0), (AD2, 0), (AD1, 1), (AD2, 1)]
for k in range(NB):
    ta, tb = tb0 + cell * k + 0.002, tb0 + cell * (k + 1) - 0.002
    if k in (5, 6):
        if k == 5: band(tb0 + cell * 5 + 0.002, tb0 + cell * 7 - 0.002, 0.12, YBB0, YBB1, LED, FULL, tw=2 * cell * LARC, sub=(0, 0, 1, 0.5))
    else: tl, row = specs[k % 4]; band(ta, tb, 0.12, YBB0, YBB1, tl, FULL, tw=cell * LARC, sub=(0, row * 0.5, 1, row * 0.5 + 0.5))
band(tb0, tb1, 0.2, YBB0, YBB1, PL, lin('#3c4046'), back=True)
# mái đón bê tông dày, mép lượn
hq(-0.02, 1.02, -0.45, 4.8, YS1, WH); hq(-0.02, 1.02, -0.3, 4.8, YS0, WH2, up=False); band(-0.02, 1.02, -0.45, YS0 + 0.22, YS1, PL, WH); band(-0.02, 1.02, -0.3, YS0, YS0 + 0.22, PL, WH2)
for te, sg in ((-0.02, -1), (1.02, 1)): wall(Wp(te, -0.45), Wp(te, 4.8), YS0, YS1, PL, WH, out=tan(te) * sg)
# lan can bông gió zíc zắc và hành lang hở
band(0.0, 1.0, 3.9, YS1, YZ1, ZIG, FULL, tw=2.15); band(0.0, 1.0, 3.98, YS1, YZ1, PL, lin('#565a62'), back=True); hq(0.0, 1.0, 3.86, 4.02, YZ1 + 0.01, WH)
band(TB0, 1.0, 4.8, YS1, YG1, PL, lin('#34373e'))
NCOL = 13
for k in range(NCOL + 1):
    t = TB0 + (1 - TB0) * k / NCOL; q = Wp(t, 3.95); B.obox(q, tan(t), rad(t), 0.2, 0.2, YZ1, YG1, WH, top=False)
# khối trên nhô ra: băng gạch cam đất, lam ngang và cửa kính, mặt đáy, tường mái
DB = 3.2
band(TB0, 1.0, DB, YG1, YO1, ORG, FULL, tw=2.2); band(TB0, 1.0, DB, YO1, YW1, WIN, FULL, tw=2.2); band(TB0, 1.0, DB, YW1, YR + 0.02, PL, WH)
hq(TB0, 1.0, DB, 4.8, YG1, WH2, up=False); wall(Wp(TB0, DB), Wp(TB0, 4.8), YG1, YR, ORG, FULL * 0.9, out=-tan(TB0))
band(TB0, 1.0, DB, YR, YP, PL, WH); band(TB0, 1.0, DB + 0.3, YR, YP, PL, WH2, back=True); hq(TB0, 1.0, DB, DB + 0.3, YP, WH); hq(TB0, 1.0, DB + 0.3, 4.9, YR + 0.02, lin('#cfa98c'), tile=PL)
# đầu đông: khối trên quành theo hông chợ
EA = Wp(1.0, DB); Eb = np.array([49.8, -47.0]); ed = (Eb - Wp(1.0, 4.8)); ed /= np.hypot(*ed); eo = np.array([-ed[1], ed[0]]); eo = eo if eo[0] > 0 else -eo; E1 = Wp(1.0, 4.8) + eo * 0.4; E2 = Eb + eo * 0.4
for a_, b_ in ((EA, E1), (E1, E2)):
    o_ = np.array([-(b_ - a_)[1], (b_ - a_)[0]]); o_ = o_ if np.dot(o_, eo) > 0 else -o_; o_ /= np.hypot(*o_)
    wall(a_, b_, YG1, YO1, ORG, FULL, out=o_, tw=2.2); wall(a_, b_, YO1, YW1, WIN, FULL, out=o_, tw=2.2); wall(a_, b_, YW1, YP, PL, WH, out=o_); wall(a_, b_, YS1, YG1, PL, lin('#34373e'), out=o_)
    wall(a_, b_, YS1, YZ1, ZIG, FULL, out=o_, tw=2.15) if a_ is E1 else None
# chữ đỏ CHỢ ĐÀ LẠT trên tường mái trắng
SW = 17.0; tc = 0.62; dt = SW / LARC; NPC = 16
for k in range(NPC):
    u0, u1 = k / NPC, (k + 1) / NPC; s = int(u0 * 4 + 1e-6); vq(tc - dt / 2 + dt * u0, tc - dt / 2 + dt * u1, DB - 0.06, YR + 0.25, YR + 1.7, SIGN, FULL, (u0 * 4 - s, s * 0.25, u1 * 4 - s, s * 0.25 + 0.25))
# khối cao ốp gạch trắng đầu tây
TBP = [Wp(0.0, 4.8), Wp(TB0, 4.8), np.array([10.3, -39.2]), np.array([3.2, -36.6])]; YT = 22.0; tcen = np.mean(TBP, 0)
band(0.0, TB0, 4.78, YS1, YT, WT, FULL, tw=2.4); n_ = int(round((YT - YS1) / 2.4))
for a_, b_, tile_, ylo in ((TBP[3] , TBP[0], WSQ, None), (TBP[1], TBP[2], WT, YR), (TBP[2], TBP[3], WT, YR)):
    o_ = np.array([-(b_ - a_)[1], (b_ - a_)[0]]); o_ /= np.hypot(*o_); mid = (a_ + b_) / 2; o_ = o_ if np.dot(o_, mid - tcen) > 0 else -o_; a2, b2 = a_ + o_ * 0.25, b_ + o_ * 0.25
    if ylo is None: wall(a2, b2, 2.8, YS1, WT, FULL, out=o_, tw=2.4, thh=2.4); wall(a2, b2, YS1, YT, WSQ, FULL, out=o_, tw=2.4, thh=2.4)
    else: wall(a2, b2, ylo, YT, tile_, FULL, out=o_, tw=2.4, thh=2.4)
B.poly([p3(q, YT) for q in TBP], PL, lin('#cfd0cc'), UP)
for a_, b_ in zip(TBP, TBP[1:] + TBP[:1]): o_ = np.array([-(b_ - a_)[1], (b_ - a_)[0]]); o_ /= np.hypot(*o_); o_ = o_ if np.dot(o_, (a_ + b_) / 2 - tcen) > 0 else -o_; wall(a_ + o_ * 0.27, b_ + o_ * 0.27, YT - 0.05, YT + 0.8, PL, WH, out=o_)
B.obox(tcen, np.array([1.0, 0]), np.array([0, 1.0]), 2.4, 1.8, YT, YT + 2.6, WH2, topcol=lin('#b9bbb6'))
# sân thượng: hàng cây bách, dù trắng, cột cờ, khinh khí cầu trang trí
CYP = lin('#2f5f3a')
for k, t in enumerate((0.27, 0.33, 0.47, 0.52, 0.66, 0.70, 0.86, 0.95)):
    q = Wp(t, 5.6 + (k % 2) * 0.8); B.prism((q[0], q[1]), 0.4, 0.4, YR, YR + 0.5, 6, lin('#e6e2d8')); B.prism((q[0], q[1]), 0.5, 0.05, YR + 0.5, YR + 3.6 + (k % 3) * 0.5, 7, CYP, cap=False)
for t in (0.30, 0.38, 0.44, 0.78, 0.82):
    q = Wp(t, 6.4); B.prism((q[0], q[1]), 0.04, 0.04, YR, YR + 2.2, 4, lin('#888c90'), cap=False); B.prism((q[0], q[1]), 1.25, 0.0, YR + 2.0, YR + 2.6, 8, WH, cap=False)
fq = Wp(0.57, 7.2); B.prism((fq[0], fq[1]), 0.06, 0.05, YR, YR + 6.6, 5, lin('#c9ccd0'), cap=False); ft = tan(0.57); f0 = fq + ft * 0.06
RED, YEL = lin('#da251d'), lin('#ffeb3b'); fy0, fy1 = YR + 5.2, YR + 6.5; B.quad([p3(f0, fy0), p3(f0 + ft * 1.95, fy0), p3(f0 + ft * 1.95, fy1), p3(f0, fy1)], PL, RED, nh2(-rad(0.57)))
sc_ = f0 + ft * 0.975; sy = (fy0 + fy1) / 2; sp = [(sc_ + ft * math.sin(a) * (0.36 if i % 2 == 0 else 0.15) - rad(0.57) * 0.02, sy + math.cos(a) * (0.36 if i % 2 == 0 else 0.15)) for i, a in enumerate(np.arange(10) * math.pi / 5)]
for i in range(10): B.tri([p3(sc_ - rad(0.57) * 0.02, sy), p3(sp[i][0], sp[i][1]), p3(sp[(i + 1) % 10][0], sp[(i + 1) % 10][1])], [tile_uv(PL, .5, .5)] * 3, YEL, nh2(-rad(0.57)))
bq = Wp(0.50, 8.4); by = YR + 5.2
for (r0, r1, ya, yb) in ((0.25, 0.9, 0, 0.7), (0.9, 1.3, 0.7, 1.5), (1.3, 1.3, 1.5, 2.2), (1.3, 0.8, 2.2, 3.0), (0.8, 0.0, 3.0, 3.4)): B.prism((bq[0], bq[1]), r0, r1, by + ya, by + yb, 10, lin('#f1ede2') if int(ya * 2) % 2 else lin('#d9d2c2'), cap=False)
B.prism((bq[0], bq[1]), 0.05, 0.05, YR, by, 4, lin('#a9a9a9'), cap=False); B.prism((bq[0], bq[1]), 0.3, 0.3, by - 0.7, by - 0.25, 6, lin('#a0744a'))
# ---------- tượng đài ở bùng binh ----------
SG = lin('#f4f4f2'); SD = lin('#d2d4d6'); mx_, mz_ = MC; yb_ = 3.95
B.prism((mx_, mz_), 3.0, 2.9, yb_ - 0.3, yb_ + 0.1, 12, lin('#c9c2b4'), tile=STONE); B.prism((mx_, mz_), 2.05, 1.5, yb_ + 0.1, yb_ + 2.6, 7, SD, tile=STONE, rot=0.3); B.prism((mx_, mz_), 1.5, 1.15, yb_ + 2.6, yb_ + 3.0, 7, SG, tile=STONE, rot=0.75)
yf = yb_ + 3.0
for k in range(4):
    a = 0.4 + k * math.pi / 2; fx, fz = mx_ + math.cos(a) * 0.62, mz_ + math.sin(a) * 0.62; hh = 2.5 - (k % 2) * 0.25
    B.prism((fx, fz), 0.46, 0.27, yf, yf + hh * 0.62, 6, SG, tile=STONE, cap=False, rot=a); B.prism((fx, fz), 0.27, 0.33, yf + hh * 0.62, yf + hh * 0.86, 6, SG, tile=STONE, cap=False, rot=a); B.prism((fx, fz), 0.33, 0.12, yf + hh * 0.86, yf + hh * 0.93, 6, SG, tile=STONE, cap=False, rot=a)
    B.prism((fx, fz), 0.1, 0.19, yf + hh * 0.93, yf + hh * 1.02, 6, SG, tile=STONE, cap=False); B.prism((fx, fz), 0.19, 0.08, yf + hh * 1.02, yf + hh * 1.12, 6, SG, tile=STONE)
B.prism((mx_ + 0.35, mz_ + 0.5), 0.2, 0.13, yf + 2.7, yf + 3.5, 5, SG, tile=STONE, cap=False); B.prism((mx_ + 0.35, mz_ + 0.5), 0.09, 0.14, yf + 3.5, yf + 3.75, 5, SG, tile=STONE)
B.prism((mx_, mz_), 0.36, 0.24, yf, yf + 6.6, 7, SD, tile=STONE, cap=False)
for (dx, dz, yy, rr) in ((0.55, 0.2, 3.5, 1.45), (-0.6, 0.35, 4.2, 1.7), (0.2, -0.55, 4.9, 1.9), (0.6, 0.4, 5.6, 1.5), (-0.35, -0.2, 6.2, 1.35), (0.05, 0.05, 6.8, 0.95)):
    c_ = (mx_ + dx, mz_ + dz); B.prism(c_, 0.25, rr, yf + yy, yf + yy + 0.22, 9, SD, tile=STONE, cap=False, rot=yy); B.prism(c_, rr, rr * 0.8, yf + yy + 0.22, yf + yy + 0.42, 9, SG, tile=STONE, cap=False, rot=yy); B.prism(c_, rr * 0.8, 0.0, yf + yy + 0.42, yf + yy + 0.66, 9, SG, tile=STONE, cap=False, rot=yy)
Pn, Nn, UVn, Cn = B.arrays(); In = np.arange(len(Pn)).reshape(-1, 3) + len(P)
nv, nt, size = mb.write_glb(dst, np.concatenate([P, Pn]), np.concatenate([N, Nn]), np.concatenate([UV, UVn]), np.concatenate([C, Cn]), np.concatenate([I, In]), patch_atlas(m['img']))
print('thêm', len(In), 'tam giác; tệp mới', nt, 'tam giác', size, 'byte')
