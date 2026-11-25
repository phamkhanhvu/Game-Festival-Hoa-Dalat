# ================= ghi market.glb =================
keep = ~dead; I2 = I[keep]
Pn, Nn_, UVn, Cn = B.arrays()
if XP: Pn = np.concatenate([Pn, np.concatenate(XP)]); Nn_ = np.concatenate([Nn_, np.concatenate(XN)]); UVn = np.concatenate([UVn, np.concatenate(XUV)]); Cn = np.concatenate([Cn, np.concatenate(XC)])
In = np.arange(len(Pn)).reshape(-1, 3) + len(P)
nv, nt, size = mb.write_glb(dst, np.concatenate([P, Pn]), np.concatenate([N, Nn_]), np.concatenate([UV, UVn]), np.concatenate([C, Cn]), np.concatenate([I2, In]), tiles.patch_atlas(m['img']))
print('bỏ', int(dead.sum()), 'thêm', len(In), 'tam giác; tệp mới', nt, 'tam giác', size, 'byte')
# ================= lưới đi lại, lưới mái, loại nền, bản đồ nhỏ =================
import base64
from PIL import Image
nx, nz, gx0, gz0, gst = wj['nx'], wj['nz'], wj['x0'], wj['z0'], wj['step']; h, top, kk = wh.copy(), wtop.copy(), wk.copy()
X, Z = np.meshgrid(gx0 + np.arange(nx) * gst, gz0 + np.arange(nz) * gst)
def mask(poly):
    x0b, z0b, x1b, z1b = poly.bounds; i0, i1 = max(0, int((x0b - gx0) / gst) - 1), min(nx, int((x1b - gx0) / gst) + 3); j0, j1 = max(0, int((z0b - gz0) / gst) - 1), min(nz, int((z1b - gz0) / gst) + 3)
    mk = np.zeros((nz, nx), bool); mk[j0:j1, i0:i1] = contains_xy(poly, X[j0:j1, i0:i1].ravel(), Z[j0:j1, i0:i1].ravel()).reshape(j1 - j0, i1 - i0); return mk
inb = (X > BX0 + 2) & (X < BX1 - 2) & (Z > BZ0 + 2) & (Z < BZ1 - 2); GH = np.zeros((nz, nx)); GH[inb] = GR.at(X[inb], Z[inb]); GHI = np.zeros((nz, nx)); GHI[inb] = GR.at(X[inb], Z[inb], hi=True)
touched = np.zeros((nz, nx), bool); n_open = 0
for poly in OPEN:                                                      # mở lại chỗ công trình cũ đã bỏ
    mk = mask(poly) & inb; q = mk & (h == -32768); h[q] = np.round(GH[q] * 100).astype(int); n_open += int(q.sum()); touched |= mk; kk[mk & (kk == 1)] = 0
def setflat(poly, yfn, kval=None):
    mk = mask(poly) & inb & (h != -32768); h[mk] = np.round(yfn(mk) * 100).astype(int); touched[mk] = True
    if kval is not None: kk[mask(poly) & inb] = kval
    return mk
mAPR = setflat(APR, lambda mk: GHI[mk] + 0.06); mPLAT = setflat(PLAT.buffer(0.3), lambda mk: np.full(int(mk.sum()), PY)); mPARK = setflat(park, lambda mk: GHI[mk] + 0.06, 1)
for gp in ([FOOT] if FOOT.geom_type == 'Polygon' else list(FOOT.geoms)): setflat(gp, lambda mk: GHI[mk] + 0.06)
for gp in FILLS:
    mk = mask(gp) & inb; q = mk & (h == -32768) & ~mask(BRIDGE.buffer(1.0)); h[q] = np.round(GHI[q] * 100).astype(int); touched |= mk; setflat(gp, lambda mk: GHI[mk] + 0.06)
mFACE = mask(FACE.buffer(0.25)) & ~mask(PLAT.buffer(-0.4)); h[mFACE] = -32768; top[mFACE] = np.round(np.maximum(GH[mFACE], 5) * 100).astype(int); touched |= mFACE
mRAIL = mask(LineString(RAIL).buffer(0.35)); h[mRAIL] = -32768; top[mRAIL] = int(PY * 100 + 105); touched |= mRAIL
n_blk = 0
for poly, ytop in BLOCK + [(BLOCKR, ROOFY + 3.7)]:
    if poly is BLOCKR: continue                                        # quán sân thượng nằm trên mái, không thuộc lưới mặt đất
    mk = mask(poly.buffer(0.3)); n_blk += int((mk & (h != -32768)).sum()); h[mk] = -32768; top[mk] = int(round(ytop * 100)); touched |= mk
opn = h != -32768; top[opn & touched] = h[opn & touched]
print('lưới đi lại: mở lại', n_open, 'ô, chặn mới', n_blk, 'ô')
# vật đặt sẵn trên nền đã nâng: chỉnh cao độ theo lưới mới
def fix(o):
    if isinstance(o, dict):
        if 'x' in o and 'z' in o and 'y' in o:
            i = int(round((o['x'] - gx0) / gst)); j = int(round((o['z'] - gz0) / gst))
            if 0 <= i < nx and 0 <= j < nz and touched[j, i] and h[j, i] != -32768 and abs(h[j, i] / 100 - o['y']) > 0.02 and abs(h[j, i] / 100 - o['y']) < 1.0: print('  chỉnh cao độ', round(o['x'], 1), round(o['z'], 1), o['y'], '->', h[j, i] / 100); o['y'] = round(h[j, i] / 100, 2)
            if 0 <= i < nx and 0 <= j < nz and touched[j, i] and h[j, i] == -32768: print('  !!! vật nằm trong ô bị chặn:', {a: b for a, b in o.items() if a in ('x', 'z', 'y', 'id')})
        for v in o.values(): fix(v)
    elif isinstance(o, list):
        for v in o: fix(v)
for key in ('stalls', 'booths', 'kiosks', 'checkins', 'stamps', 'audience', 'stage', 'gate', 'man', 'balloon'): fix(wj.get(key))
for r in wj['routes']:
    for p in r['pts']:
        i = int(round((p[0] - gx0) / gst)); j = int(round((p[1] - gz0) / gst))
        if touched[j, i]: print('  !!! tuyến xe đi qua ô đã đổi', p)
# bản đồ nhỏ: 1 điểm ảnh = 1 m
b = base64.b64decode(wj['map'].split(',')[1]); mm = np.asarray(Image.open(io.BytesIO(b)).convert('RGB')).copy()
BLc, ASc, GRc, TAc = (120, 112, 104), (120, 122, 128), (126, 168, 98), (200, 188, 165)
for pz in range(mm.shape[0]):
    for px in range(mm.shape[1]):
        gi, gj = px * 2, pz * 2
        if gi >= nx or gj >= nz or not touched[gj, gi]: continue
        was_b = tuple(mm[pz, px]) == BLc
        if mFACE[gj, gi]: mm[pz, px] = TAc
        elif h[gj, gi] == -32768: mm[pz, px] = BLc
        elif kk[gj, gi] == 1: mm[pz, px] = GRc
        elif mPLAT[gj, gi]: mm[pz, px] = ASc
        elif was_b or mAPR[gj, gi] or tuple(mm[pz, px]) == GRc: v = int(round(186 + 2.13 * h[gj, gi] / 100.0)); mm[pz, px] = (v, v - 6, v - 16)
buf = io.BytesIO(); Image.fromarray(mm).save(buf, format='PNG', optimize=True); wj['map'] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(); Image.fromarray(mm).resize((mm.shape[1] * 2, mm.shape[0] * 2), Image.NEAREST).save('/tmp/minimap_new.png')
worldio.save(wdst, wj, h, top, kk, wpre, wpost); print('đã ghi', wdst)
