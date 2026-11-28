# Không khí Festival Hoa cho bản đồ Chợ Đà Lạt và Khu Hòa Bình: điền cây, chậu hoa, bồn hoa vào world_cho.js.
# Game đã biết vẽ các danh sách này (WORLD.trees, WORLD.pots, WORLD.flowers).
#
# Quy tắc (anh Vũ, 28.11.2026): cây và bồn hoa trang trí nằm SÁT CÔNG TRÌNH, không tràn ra đường.
#   - mặt nhựa (đường, sân nhựa, bãi xe) lấy từ market.glb (surface.py), không đoán theo tuyến xe;
#   - cây không bao giờ đứng trên mặt nhựa; chậu và hoa chỉ được nằm trên mặt nhựa khi tựa sát chân tường công trình
#     (chậu không quá 1,5 m, bồn hoa lớn không quá 2,6 m tính từ tường) và cách tim tuyến xe chạy đủ xa (luống 4 m, chậu 5 m, bồn lớn 8,5 m);
#   - mọi thứ bám chân tường công trình:
#       luống hoa   : dải bông hoa ngay chân tường (vỉa hẹp cũng đặt được, không cản lối đi)
#       chậu hoa    : cách tường khoảng 1 m, khi vỉa đủ rộng cho cả chậu
#       bồn hoa lớn : nửa hình tròn tựa vào tường, ba vòng màu, chậu ở giữa, khi nền lát trước tường sâu từ 2,75 m
#       cây hoa     : gốc cách tường 3 đến 3,8 m trên nền lát rộng, cây thấp hơn trước (4,4 đến 5,2 m) để tán không trùm ra đường và không đâm vào tường
#   - riêng bờ hồ: một hàng cây trên dải đất ven nước (không có công trình, nhưng không nằm trên đường);
#   - bậc cỏ: rải hoa thành đám như cũ.
# Chạy: python3 festival.py <world_cho.js vào> <world_cho.js ra> <market.glb> [ảnh_mặt_bằng.png]
#   (chạy lại được: mỗi lần ghi đè ba danh sách; cao độ lấy theo lưới h hiện có nên chạy sau kerbs.py)
import sys, json, math, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import worldio, surface
from scipy import ndimage
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
from shapely import contains_xy
src, dst, glb = sys.argv[1:4]
j, h, top, k, pre, post = worldio.load(src); nx, nz, x0, z0, st = j['nx'], j['nz'], j['x0'], j['z0'], j['step']
X, Z = np.meshgrid(x0 + np.arange(nx) * st, z0 + np.arange(nz) * st); rng = np.random.default_rng(2026)
opn = h != -32768; H = np.where(opn, h / 100.0, np.nan); grass = (k == 1) & opn
asph, roof = surface.compute(glb); asph = asph[:nz, :nx]; roof = np.nan_to_num(roof[:nz, :nx], nan=0.0)

# ---- công trình: ô bị chặn có mái cao từ 3 m, khối từ 30 m2 (bỏ kè, cột, gốc cây)
tall = ndimage.binary_closing((~opn) & (roof >= 3.0), iterations=2) & ~opn
lab, n = ndimage.label(tall, structure=np.ones((3, 3))); bld = (np.bincount(lab.ravel()) * st * st >= 30)[lab]; bld[lab == 0] = False
dB = ndimage.distance_transform_edt(~bld) * st                     # cách chân công trình
dK = ndimage.distance_transform_edt(opn) * st                      # cách ô bị chặn bất kỳ (tường, kè, cột)
dAs = ndimage.distance_transform_edt(~asph) * st                   # cách mặt nhựa
_, (fj, fi) = ndimage.distance_transform_edt(~opn, return_indices=True); Hf = np.nan_to_num(H, nan=0.0)[fj, fi]     # ô bị chặn lấy cao độ ô đi được gần nhất, để ô sát tường không bị coi là dốc
gz, gx = np.gradient(Hf); flat = (np.hypot(gx, gz) / st < 0.35) & opn       # bỏ taluy, bậc thang; gờ bó vỉa 10-20 cm không tính là dốc
sm = ndimage.gaussian_filter(np.minimum(dB, 8.0), 1.6); nzv, nxv = np.gradient(sm); nl = np.hypot(nxv, nzv) + 1e-9; nxv /= nl; nzv /= nl   # hướng từ tường ra ngoài

# ---- chỗ phải tránh
roads = unary_union([LineString([(p[0], p[1]) for p in r['pts']] + ([(r['pts'][0][0], r['pts'][0][1])] if r.get('loop') else [])) for r in j['routes']])
lane = contains_xy(roads.buffer(3.0), X.ravel(), Z.ravel()).reshape(X.shape)          # làn xe chạy
dR = ndimage.distance_transform_edt(~contains_xy(roads.buffer(0.5), X.ravel(), Z.ravel()).reshape(X.shape)) * st
avoid = []
def walk(o):
    if isinstance(o, dict):
        if 'x' in o and 'z' in o and isinstance(o['x'], (int, float)): avoid.append((o['x'], o['z']))
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
for key in ('booths', 'stalls', 'kiosks', 'checkins', 'stamps', 'audience', 'stage', 'gate', 'man', 'balloon', 'portal', 'spawn', 'explore', 'doors', 'deckProps'): walk(j.get(key))
avoid = np.array(avoid); am = np.zeros(X.shape, bool); am[np.clip(np.round((avoid[:, 1] - z0) / st).astype(int), 0, nz - 1), np.clip(np.round((avoid[:, 0] - x0) / st).astype(int), 0, nx - 1)] = True
dA = ndimage.distance_transform_edt(~am) * st
decks = unary_union([Polygon([(p[0], p[1]) for p in d['p']]) for d in j.get('decks', [])]) if j.get('decks') else Polygon()
dk = contains_xy(decks.buffer(3.0), X.ravel(), Z.ravel()).reshape(X.shape) if not decks.is_empty else np.zeros(X.shape, bool)
inner = (X > x0 + 6) & (X < x0 + nx * st - 6) & (Z > z0 + 6) & (Z < z0 + nz * st - 6)
okany = opn & flat & ~lane & ~dk & inner                           # nền đi được, phẳng, ngoài làn xe
ok = okany & ~asph                                                 # ... và KHÔNG phải mặt nhựa
stg = j['stage']; dS = np.hypot(X - stg['x'], Z - stg['z']); dM = np.hypot(X - 22.0, Z + 12.0)   # cách sân khấu, cách mặt tiền chợ

def cell(x, z): return int(round((z - z0) / st)), int(round((x - x0) / st))
def good(x, z, y=None, lim=0.3, far=None):
    """điểm đặt được: nền không nhựa; hoặc (khi cho far) nền nhựa nhưng cách tim tuyến xe ít nhất far mét"""
    jj, ii = cell(x, z)
    if not (0 <= ii < nx and 0 <= jj < nz) or not okany[jj, ii] or (y is not None and abs(H[jj, ii] - y) >= lim): return False
    return (not asph[jj, ii]) or (far is not None and dR[jj, ii] >= far)
def depth(x, z, y, ux, uz, far=None):
    """nền đặt được, cùng cao độ kéo dài bao xa tính từ chân tường (m), đo dọc hướng ra ngoài"""
    d = 0.25
    for m in range(0, 11):
        if not good(x + ux * 0.5 * m, z + uz * 0.5 * m, y, far=far): break
        d = 0.5 + 0.5 * m + 0.25
    return d
class Spacer:
    """giữ khoảng cách tối thiểu giữa các điểm đã chọn"""
    def __init__(self): self.pts = []
    def free(self, x, z, s): return all((x - a) ** 2 + (z - b) ** 2 >= min(s, t) ** 2 for a, b, t in self.pts)   # hai điểm cách nhau ít nhất bằng khoảng cách nhỏ hơn trong hai yêu cầu
    def add(self, x, z, s): self.pts.append((x, z, s))
def order(mask):
    jj, ii = np.where(mask); o = rng.permutation(len(jj)); return jj[o], ii[o]

trees = []; pots = []; dots = {c: [] for c in ('dot_pink', 'dot_yellow', 'dot_violet', 'dot_red', 'dot_white', 'dot_orange')}; DK = list(dots)
PAL = [('dot_pink', 'dot_white', 'dot_violet'), ('dot_yellow', 'dot_orange', 'dot_red'), ('dot_violet', 'dot_pink', 'dot_white'), ('dot_red', 'dot_yellow', 'dot_white'), ('dot_orange', 'dot_pink', 'dot_yellow')]
def R2(v): return round(float(v) + 1e-4, 2)                        # làm tròn 2 số lẻ, tránh giá trị nằm đúng ranh giới ô
def dot(c, x, z, y, lo=0.42, hi=0.56, far=None):
    x, z = R2(x), R2(z)
    if not good(x, z, far=far): return False                         # kiểm tra lại trên toạ độ sẽ ghi ra
    jj, ii = cell(x, z)
    dots[c].append([x, round(float(H[jj, ii]), 2), z, round(float(rng.random() * 6.28), 2), round(lo + float(rng.random()) * (hi - lo), 2)]); return True
def tree(x, z, y, lo, hi, kind=None):
    kind = kind or ('sakura' if (int(x // 60) + int(z // 60)) % 3 else 'jacaranda')
    trees.append(dict(x=R2(x), z=R2(z), y=round(float(y), 2), a=round(float(rng.random() * 6.28), 2), k=kind, s=round(lo + float(rng.random()) * (hi - lo), 2)))

# ---- 1. dọc chân tường công trình: luống hoa, chậu hoa, bồn hoa lớn
F_STRIP, F_POT, F_BED = 4.0, 5.0, 8.5                              # trên mặt nhựa: cách tim tuyến xe tối thiểu cho luống, chậu, bồn hoa lớn
edge = okany & ~grass & (dB <= 0.75) & (dK >= 0.45) & (dA >= 3.2) & (~asph | (dR >= F_STRIP))   # ô đi được nằm ngay sát tường
room = ndimage.maximum_filter(dK, 9) >= 2.4                       # gần đó còn khoảng trống rộng: chậu không bít lối
focus = (dS < 75) | (dM < 75)
sp = Spacer(); big = Spacer(); nbed = npot = nstrip = 0
for npass, (mask, gap) in enumerate(((edge & focus, 5.5), (edge & (dR <= 16), 7.5), (edge, 20.0))):   # quanh sân khấu và mặt tiền chợ dày nhất, rồi dọc các tuyến đường, còn lại thưa
    for jj, ii in zip(*order(mask)):
        x, z, y = x0 + ii * st, z0 + jj * st, float(H[jj, ii])
        if not sp.free(x, z, gap): continue
        ux, uz = float(nxv[jj, ii]), float(nzv[jj, ii]); tx, tz = -uz, ux
        pal = PAL[(nbed + npot + nstrip) % len(PAL)]
        px, pz = x + ux * 0.55, z + uz * 0.55                       # tâm chậu: cách tường khoảng 1 m
        can_pot = depth(x, z, y, ux, uz, F_POT) >= 1.6 and good(px, pz, y, far=F_POT) and room[jj, ii] and dK[cell(px, pz)] >= 0.9
        if can_pot and npass < 2 and depth(x, z, y, ux, uz, F_BED) >= 2.75 and big.free(x, z, 20.0):
            # bồn hoa lớn: nửa hình tròn tựa vào tường
            pts = []
            for ring, (r, cnt) in enumerate(((0.95, 4), (1.5, 6), (2.05, 8))):      # mỗi bông hoa là một cụm rộng gần 1 m
                for i in range(cnt):
                    a = (-80 + 160 * i / (cnt - 1)) * math.pi / 180; fx = x + (math.cos(a) * ux + math.sin(a) * tx) * r; fz = z + (math.cos(a) * uz + math.sin(a) * tz) * r
                    if (fx - px) ** 2 + (fz - pz) ** 2 < 0.55 ** 2: continue
                    pts.append((ring, fx, fz, good(R2(fx), R2(fz), y, far=F_BED)))
            if sum(p[3] for p in pts) >= 0.9 * len(pts):
                for ring, fx, fz, g in pts:
                    if g: dot(pal[ring], fx, fz, y, 0.48, 0.62, far=F_BED)
                pots.append(dict(x=R2(px), z=R2(pz), y=round(y, 2))); sp.add(x, z, gap); big.add(x, z, 20.0); nbed += 1; continue
        # luống hoa chân tường, hai màu xen kẽ; có chậu ở giữa nếu đủ chỗ
        us = (-1.7, -0.85, 0.85, 1.7) if can_pot else (-1.35, -0.45, 0.45, 1.35)
        row = [(x + tx * u, z + tz * u) for u in us]; row = [(fx, fz) for fx, fz in row if good(R2(fx), R2(fz), y, far=F_STRIP) and dB[cell(fx, fz)] <= 1.0]
        if len(row) < 3: continue
        for q, (fx, fz) in enumerate(row): dot(pal[q % 2], fx, fz, y, far=F_STRIP)
        if can_pot: pots.append(dict(x=R2(px), z=R2(pz), y=round(y, 2))); npot += 1
        else: nstrip += 1
        sp.add(x, z, gap)

# ---- 2. cây hoa: gốc trên nền lát rộng, cách tường 3 đến 3,8 m, cách mặt nhựa ít nhất 1 m
tm = ok & ~grass & (dB >= 3.0) & (dB <= 3.8) & (dAs >= 1.0) & (dK >= 1.6) & (dA >= 5.0)
ts = Spacer(); ntw = 0
for p in pots: ts.add(p['x'], p['z'], 2.2)
for mask, gap in ((tm & focus, 9.0), (tm & (dR <= 18), 11.0), (tm, 16.0)):
    for jj, ii in zip(*order(mask)):
        x, z, y = x0 + ii * st, z0 + jj * st, float(H[jj, ii])
        if not ts.free(x, z, gap): continue
        ux, uz = float(nxv[jj, ii]), float(nzv[jj, ii])
        if not all(good(x + ux * d, z + uz * d, y, 0.4) for d in (-1.5, -0.75, 0.75, 1.5)): continue   # nền lát liền từ tường ra quá gốc cây
        tree(x, z, y, 4.4, 5.2); ts.add(x, z, gap); ntw += 1
        if ntw >= 130: break
    if ntw >= 130: break

# ---- 3. bờ hồ: một hàng cây trên dải đất ven nước
LAKE = (185.0, 245.0)                                              # một điểm giữa mặt hồ Xuân Hương (góc đông nam bản đồ)
lab2, n2 = ndimage.label((~opn) & ~bld, structure=np.ones((3, 3))); lk = lab2[cell(*LAKE)]; nlk = 0
if lk:
    dL = ndimage.distance_transform_edt(lab2 != lk) * st
    lm = ok & (dL >= 2.0) & (dL <= 4.5) & (dAs >= 1.5) & (dA >= 5.0)
    for jj, ii in zip(*order(lm)):
        x, z = x0 + ii * st, z0 + jj * st
        if ts.free(x, z, 9.0): tree(x, z, float(H[jj, ii]), 5.4, 6.8, 'jacaranda' if nlk % 2 else 'sakura'); ts.add(x, z, 9.0); nlk += 1

# ---- 4. rải hoa trên các bậc cỏ, mọc thành đám
gm = grass & flat & (dK >= 0.7) & ~asph; jj, ii = np.where(gm); sel = rng.permutation(len(jj))[:170]
for t in sel:
    c = DK[int(rng.integers(0, 6))]
    for q in range(int(rng.integers(4, 8))):
        fx, fz = x0 + ii[t] * st + rng.normal(0, 0.7), z0 + jj[t] * st + rng.normal(0, 0.7); b, a = cell(fx, fz)
        if 0 <= a < nx and 0 <= b < nz and gm[b, a]: dot(c, fx, fz, None, 0.4, 0.54)

# ---- kiểm tra: vật cản mới không cắt đứt lối đi (nếu có thì gỡ vật gây ra)
def reach(extra):
    okc = opn & ~extra; s = cell(j['spawn']['x'], j['spawn']['z']); R = np.zeros_like(okc); R[s] = True; hh = h.astype(np.int32)
    while True:
        n0 = R.sum()
        for _ in range(80):
            for dj, di in ((0, 1), (0, -1), (1, 0), (-1, 0)): R |= np.roll(R, (dj, di), (0, 1)) & okc & (np.abs(hh - np.roll(hh, (dj, di), (0, 1))) <= 52)
        if R.sum() == n0: return R
def blocked():
    b = np.zeros(X.shape, bool)
    for o, r in [(p, 1.0) for p in pots] + [(t, 0.85) for t in trees]: b |= (X - o['x']) ** 2 + (Z - o['z']) ** 2 <= r * r   # bán kính va chạm cộng bán kính người chơi
    return b
r0 = reach(np.zeros(X.shape, bool)); removed = 0
for _ in range(6):
    blk = blocked(); r1 = reach(blk); lostm = r0 & ~r1 & ~blk
    if not lostm.any(): break
    dl = ndimage.distance_transform_edt(~lostm) * st
    keep = lambda o: dl[cell(o['x'], o['z'])] > 2.5
    n_before = len(pots) + len(trees); pots = [p for p in pots if keep(p)]; trees = [t for t in trees if keep(t)]; removed += n_before - len(pots) - len(trees)
blk = blocked(); r1 = reach(blk); lost = int((r0 & ~r1 & ~blk).sum())

# ---- số đo kiểm tra quy tắc
allp = [(p['x'], p['z']) for p in pots]; allt = [(t['x'], t['z']) for t in trees]; alld = [(f[0], f[2]) for v in dots.values() for f in v]
def st_(pts):
    c = [cell(*p) for p in pts]; a = np.array([asph[q] for q in c], bool); b = np.array([dB[q] for q in c]); r = np.array([dR[q] for q in c])
    return a, b, r
ap, bp, rp = st_(allp); at, bt, rt = st_(allt); ad, bd, rd = st_(alld); gd = np.array([grass[cell(*p)] for p in alld], bool)
print('bồn hoa lớn %d, chậu kèm luống %d, luống hoa %d, cây sát công trình %d, cây bờ hồ %d; tổng: chậu %d, cây %d, bông hoa %d' % (nbed, npot, nstrip, ntw, nlk, len(allp), len(allt), len(alld)))
print('cây trên mặt nhựa: %d (phải bằng 0)' % int(at.sum()))
print('chậu: xa tường nhất %.1f m; trên mặt nhựa %d, các chậu đó xa tường nhất %.1f m, gần tim tuyến xe nhất %.1f m' % (bp.max(), int(ap.sum()), bp[ap].max() if ap.any() else 0, rp[ap].min() if ap.any() else 0))
print('bông hoa ngoài bậc cỏ: xa tường nhất %.1f m; trên mặt nhựa %d, các bông đó xa tường nhất %.1f m, gần tim tuyến xe nhất %.1f m' % (bd[~gd].max(), int(ad.sum()), bd[ad].max() if ad.any() else 0, rd[ad].min() if ad.any() else 0))
print('cây: cách công trình quá 4 m (chỉ hàng bờ hồ): %d' % int((bt > 4.0).sum()))
print('ô đi tới được: trước %d, sau %d, mất ngoài chỗ đặt vật: %d (đã gỡ %d vật gây bít lối)' % (r0.sum(), r1.sum(), lost, removed))
j['trees'] = trees; j['pots'] = pots; j['flowers'] = dots; worldio.save(dst, j, h, top, k, pre, post)
if len(sys.argv) > 4:
    from PIL import Image, ImageDraw
    img = np.zeros(X.shape + (3,), np.uint8); img[:] = (20, 20, 24); img[opn & ~asph] = (205, 200, 188); img[asph & opn] = (92, 92, 100); img[grass] = (120, 175, 95); img[bld] = (150, 95, 60); img[(~opn) & ~bld] = (40, 40, 48)
    K = 2; im = Image.fromarray(img).resize((nx * K, nz * K), Image.NEAREST); dr = ImageDraw.Draw(im); s = K / st
    for c, col in zip(DK, ((255, 120, 180), (255, 220, 60), (170, 110, 240), (230, 60, 50), (255, 255, 255), (255, 150, 50))):
        for d in dots[c]: dr.point(((d[0] - x0) * s, (d[2] - z0) * s), fill=col)
    for p in pots: dr.ellipse([(p['x'] - x0) * s - 2, (p['z'] - z0) * s - 2, (p['x'] - x0) * s + 2, (p['z'] - z0) * s + 2], fill=(255, 0, 0))
    for t in trees: dr.ellipse([(t['x'] - x0) * s - 5, (t['z'] - z0) * s - 5, (t['x'] - x0) * s + 5, (t['z'] - z0) * s + 5], outline=(255, 60, 200) if t['k'] == 'sakura' else (120, 60, 255), width=2)
    im.save(sys.argv[4])
