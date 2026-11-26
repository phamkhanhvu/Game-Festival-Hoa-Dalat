# Không khí Festival Hoa cho bản đồ Chợ Đà Lạt và Khu Hòa Bình: điền cây, chậu hoa, thảm hoa vào world_cho.js.
# Game đã biết vẽ các danh sách này (WORLD.trees, WORLD.pots, WORLD.flowers), trước đây để trống ở bản đồ Chợ.
#   - dọc mép vỉa hè các tuyến đường: xen mai anh đào, phượng tím và chậu hoa
#   - sát chân tường ở chỗ vỉa rộng: chậu hoa
#   - sân rộng (Khu Hòa Bình, trước chợ...): thảm hoa tròn nhiều vòng màu, chậu hoa ở giữa
#   - các bậc cỏ: rải hoa
# Chạy: python3 festival.py world_cho.js world_cho.js   (chạy lại được: mỗi lần ghi đè các danh sách)
import sys, json, math, numpy as np
import worldio
from scipy import ndimage
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
from shapely import contains_xy
src, dst = sys.argv[1:3]
j, h, top, k, pre, post = worldio.load(src); nx, nz, x0, z0, st = j['nx'], j['nz'], j['x0'], j['z0'], j['step']
X, Z = np.meshgrid(x0 + np.arange(nx) * st, z0 + np.arange(nz) * st); rng = np.random.default_rng(2026)
opn = h != -32768; H = np.where(opn, h / 100.0, np.nan)
roads = unary_union([LineString([(p[0], p[1]) for p in r['pts']] + ([(r['pts'][0][0], r['pts'][0][1])] if r.get('loop') else [])) for r in j['routes']])
road = contains_xy(roads.buffer(4.5), X.ravel(), Z.ravel()).reshape(X.shape)
dB = ndimage.distance_transform_edt(opn) * st                      # cách ô bị chặn (tường, kè)
dR = ndimage.distance_transform_edt(~road) * st                    # cách mép đường
gz, gx = np.gradient(np.nan_to_num(H, nan=0.0)); flat = (np.hypot(gx, gz) / st < 0.12) & (ndimage.binary_erosion(opn, np.ones((3, 3))))
grass = (k == 1) & opn
# các điểm phải tránh
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
stg = j['stage']; dS = np.hypot(X - stg['x'], Z - stg['z'])
def pick(mask, spacing, limit, taken):
    """chọn tham lam các ô trong mask, cách nhau và cách các điểm đã chọn ít nhất spacing"""
    jj, ii = np.where(mask); o = rng.permutation(len(jj)); out = []
    for t in o:
        x, z = x0 + ii[t] * st, z0 + jj[t] * st
        if all((x - a) ** 2 + (z - b) ** 2 >= s2 for a, b, s2 in taken): out.append((x, z, float(H[jj[t], ii[t]]))); taken.append((x, z, spacing ** 2))
        if len(out) >= limit: break
    return out
taken = []; trees = []; pots = []; dots = {c: [] for c in ('dot_pink', 'dot_yellow', 'dot_violet', 'dot_red', 'dot_white', 'dot_orange')}; DK = list(dots)
inner = (X > x0 + 6) & (X < x0 + nx * st - 6) & (Z > z0 + 6) & (Z < z0 + nz * st - 6)
base = opn & flat & ~road & ~dk & inner
# 1. thảm hoa ở sân rộng (ưu tiên sân Khu Hòa Bình quanh sân khấu)
wide = base & ~grass & (dB >= 4.2) & (dR >= 3.0) & (dA >= 6.5)
dM = np.hypot(X - 22.0, Z + 12.0)                                   # cách mặt tiền chợ
carpets = pick(wide & (dS < 60), 10.0, 16, taken) + pick(wide & (dM < 60), 11.0, 10, taken) + pick(wide, 20.0, 22, taken)
PAL = [('dot_pink', 'dot_white', 'dot_violet'), ('dot_yellow', 'dot_orange', 'dot_red'), ('dot_violet', 'dot_pink', 'dot_white'), ('dot_red', 'dot_yellow', 'dot_white'), ('dot_orange', 'dot_pink', 'dot_yellow')]
for n, (x, z, y) in enumerate(carpets):
    pal = PAL[n % len(PAL)]; pots.append(dict(x=round(x, 2), z=round(z, 2), y=round(y, 2)))
    for ring, (r, cnt) in enumerate(((1.0, 9), (1.65, 15), (2.3, 21))):
        for i in range(cnt):
            a = i / cnt * math.tau + ring * 0.3; fx, fz = x + math.cos(a) * r, z + math.sin(a) * r; ii, jj = int(round((fx - x0) / st)), int(round((fz - z0) / st))
            if 0 <= ii < nx and 0 <= jj < nz and opn[jj, ii]: dots[pal[ring]].append([round(fx, 2), round(float(H[jj, ii]), 2), round(fz, 2), round(float(rng.random() * 6.28), 2), round(0.5 + float(rng.random()) * 0.14, 2)])
# 2. dọc mép vỉa hè: cây hoa xen chậu hoa
kerb = base & ~grass & (dR >= 0.9) & (dR <= 1.5) & (dB >= 1.0) & (dA >= 3.0)
row = pick(kerb, 6.0, 520, taken); nt = 0
for n, (x, z, y) in enumerate(row):
    ii, jj = int(round((x - x0) / st)), int(round((z - z0) / st))
    if n % 3 == 0 and dB[jj, ii] >= 2.6 and dA[jj, ii] >= 5.0:
        kind = 'sakura' if (int(x // 60) + int(z // 60)) % 3 else 'jacaranda'; trees.append(dict(x=round(x, 2), z=round(z, 2), y=round(y, 2), a=round(float(rng.random() * 6.28), 2), k=kind, s=round(5.6 + float(rng.random()) * 1.8, 2))); nt += 1
    else: pots.append(dict(x=round(x, 2), z=round(z, 2), y=round(y, 2)))
# 3. sát chân tường ở chỗ vỉa rộng
room = ndimage.maximum_filter(dB, 13) >= 2.6
wallm = base & ~grass & (dB >= 0.9) & (dB <= 1.2) & (dR >= 2.5) & (dA >= 4.0) & room
for (x, z, y) in pick(wallm, 9.0, 90, taken): pots.append(dict(x=round(x, 2), z=round(z, 2), y=round(y, 2)))
# 4. cây hoa ở sân rộng còn trống
for (x, z, y) in pick(wide & (dB >= 5.0), 12.0, 40, taken):
    trees.append(dict(x=round(x, 2), z=round(z, 2), y=round(y, 2), a=round(float(rng.random() * 6.28), 2), k='sakura' if rng.random() < 0.7 else 'jacaranda', s=round(6.2 + float(rng.random()) * 2.0, 2)))
# 5. rải hoa trên các bậc cỏ, mọc thành đám
gm = grass & flat & (dB >= 0.7); jj, ii = np.where(gm); sel = rng.permutation(len(jj))[:170]
for t in sel:
    c = DK[int(rng.integers(0, 6))]
    for q in range(int(rng.integers(4, 8))):
        fx, fz = x0 + ii[t] * st + rng.normal(0, 0.7), z0 + jj[t] * st + rng.normal(0, 0.7); a, b = int(round((fx - x0) / st)), int(round((fz - z0) / st))
        if 0 <= a < nx and 0 <= b < nz and gm[b, a]: dots[c].append([round(float(fx), 2), round(float(H[b, a]), 2), round(float(fz), 2), round(float(rng.random() * 6.28), 2), round(0.4 + float(rng.random()) * 0.14, 2)])
# kiểm tra: vật cản mới không cắt đứt lối đi
def reach(extra):
    ok = opn & ~extra; s = (int(round((j['spawn']['z'] - z0) / st)), int(round((j['spawn']['x'] - x0) / st))); R = np.zeros_like(ok); R[s] = True; hh = h.astype(np.int32)
    while True:
        n0 = R.sum()
        for _ in range(80):
            for dj, di in ((0, 1), (0, -1), (1, 0), (-1, 0)): R |= np.roll(R, (dj, di), (0, 1)) & ok & (np.abs(hh - np.roll(hh, (dj, di), (0, 1))) <= 52)
        if R.sum() == n0: return R
blk = np.zeros(X.shape, bool)
for o, r in [(p, 1.0) for p in pots] + [(t, 0.85) for t in trees]: blk |= (X - o['x']) ** 2 + (Z - o['z']) ** 2 <= r * r          # bán kính va chạm cộng bán kính người chơi
r0, r1 = reach(np.zeros(X.shape, bool)), reach(blk); lost = int((r0 & ~r1 & ~blk).sum())
print('thảm hoa %d, cây %d (dọc đường %d), chậu hoa %d, bông hoa %d' % (len(carpets), len(trees), nt, len(pots), sum(len(v) for v in dots.values())))
print('ô đi tới được: trước %d, sau %d, mất ngoài chỗ đặt vật: %d' % (r0.sum(), r1.sum(), lost))
j['trees'] = trees; j['pots'] = pots; j['flowers'] = dots; worldio.save(dst, j, h, top, k, pre, post)
if len(sys.argv) > 3:
    from PIL import Image
    img = np.zeros(X.shape + (3,), np.uint8); img[opn] = (190, 186, 176); img[road & opn] = (90, 90, 96); img[grass] = (110, 170, 90)
    for c, col in zip(DK, ((255, 120, 180), (255, 220, 60), (170, 110, 240), (230, 60, 50), (255, 255, 255), (255, 150, 50))):
        for d in dots[c]: img[int(round((d[2] - z0) / st)), int(round((d[0] - x0) / st))] = col
    im = Image.fromarray(img).resize((nx * 2, nz * 2), Image.NEAREST); from PIL import ImageDraw; dr = ImageDraw.Draw(im)
    for p in pots: dr.ellipse([(p['x'] - x0) * 4 - 3, (p['z'] - z0) * 4 - 3, (p['x'] - x0) * 4 + 3, (p['z'] - z0) * 4 + 3], fill=(255, 0, 0))
    for t in trees: dr.ellipse([(t['x'] - x0) * 4 - 7, (t['z'] - z0) * 4 - 7, (t['x'] - x0) * 4 + 7, (t['z'] - z0) * 4 + 7], outline=(255, 90, 200) if t['k'] == 'sakura' else (150, 90, 255), width=3)
    im.save(sys.argv[3])
