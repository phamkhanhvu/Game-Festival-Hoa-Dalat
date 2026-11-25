# ================= 6b. các khối đất dốc: chia bậc phẳng, có kè đá bao quanh =================
# Nguyên tắc: không để đất dốc tràn ra đường hay ăn vào chân nhà. Mọi chênh cao được giải quyết bằng kè đứng;
# mặt bậc phẳng (cỏ, cây), cầu thang khoét vào bậc; sát đường và sát nhà là vỉa lát đi theo mặt đường.
#  - khối 1: sườn đồi phía đông cầu đi bộ (giữa Khu Hòa Bình cao 15 m và đường sau chợ cao 5 đến 6 m)
#  - các khối còn lại: mọi bãi cỏ dốc khác của bản đồ (lấy từ lưới loại nền), xử lý cùng một cách
from scipy.ndimage import gaussian_filter, label as _label
from shapely.ops import unary_union
import shapely as _sh
STONE_T, GRASS_T = (6, 5), (1, 7); KEC, CAPC, GRC, SC = lin('#b9b2a2'), lin('#d6d0c2'), lin('#86b86a'), lin('#cfc9bb')
gnx, gnz, ggx0, ggz0, ggst = wj['nx'], wj['nz'], wj['x0'], wj['z0'], wj['step']
def polys(gm): return [p_ for p_ in ([gm] if gm.geom_type == 'Polygon' else getattr(gm, 'geoms', [])) if p_.geom_type == 'Polygon' and p_.area > 0.3]
def cells_poly(mk, grow=0.0):
    jj, ii = np.where(mk)
    if not len(jj): return Polygon()
    xs = ggx0 + ii * ggst; zs = ggz0 + jj * ggst; return unary_union(_sh.box(xs - ggst / 2 - grow, zs - ggst / 2 - grow, xs + ggst / 2 + grow, zs + ggst / 2 + grow))
ALLROADS = unary_union([LineString([(p_[0], p_[1]) for p_ in r_['pts']] + ([(r_['pts'][0][0], r_['pts'][0][1])] if r_.get('loop') else [])).buffer(4.3) for r_ in wj['routes']])
TKALL = []; TERR = []; STAIRS = []; BLOCKS = []; TREES = []; rngT = np.random.default_rng(11)
def old_h(x, z):
    i_ = int(round((x - ggx0) / ggst)); j_ = int(round((z - ggz0) / ggst))
    if not (0 <= i_ < gnx and 0 <= j_ < gnz) or wh[j_, i_] == -32768: return None
    return wh[j_, i_] / 100.0
def out_h(x, z):
    """cao độ mặt đi lại tại một điểm ngoài bậc đang xét: bậc khác, nền lát mới, hoặc nền cũ còn đi được; None nếu không đi được"""
    pt = Point(x, z)
    for TK_, LV_ in TKALL:
        for k_ in range(len(LV_)):
            for p_ in TK_[k_]:
                if p_.contains(pt): return LV_[k_]
    for hill_, pave_ in BLOCKS:
        if pave_.contains(pt): return gh(x, z) + 0.06
        if hill_.contains(pt): return None
    if FOOT.contains(pt): return gh(x, z) + 0.06
    if PLAT.contains(pt): return PY
    if FACE.contains(pt): return None
    return old_h(x, z)
def seg_iter(ring, step=1.6):
    co = np.array(ring.coords)
    for a_, b_ in zip(co[:-1], co[1:]):
        ln = np.hypot(*(b_ - a_)); n_ = max(1, int(math.ceil(ln / step)))
        for i_ in range(n_): yield a_ + (b_ - a_) * i_ / n_, a_ + (b_ - a_) * (i_ + 1) / n_
def terrace_block(name, HILL, PAVEH, LV, avoid=None, bridge=False, pink=0.0, tree_per=75.0):
    avoid = avoid if avoid is not None else Polygon()
    BLOCKS.append((HILL, PAVEH))
    for gp in polys(PAVEH): drape(gp, PLAIN, PAVE, 0.06)
    hx0, hz0, hx1, hz1 = HILL.bounds; cs = 0.5; gxs = np.arange(hx0, hx1, cs) + cs / 2; gzs = np.arange(hz0, hz1, cs) + cs / 2; GX, GZ = np.meshgrid(gxs, gzs)
    gsm = gaussian_filter(GR.at(GX, GZ), 4.0); inh = contains_xy(HILL, GX.ravel(), GZ.ravel()).reshape(GX.shape)
    lev = np.clip(np.searchsorted(LV, gsm - 0.3), 0, len(LV) - 1)
    if bridge:                                               # dưới gầm cầu đi bộ: hạ bậc cho khỏi chạm đáy cầu
        deckY = np.clip(9.8373 - 0.04538 * GX - 0.05654 * GZ, 12.8, 15.7); underb = contains_xy(BRIDGE.buffer(0.6), GX.ravel(), GZ.ravel()).reshape(GX.shape)
        capi = np.clip(np.searchsorted(LV, deckY - 2.3, 'right') - 1, 0, len(LV) - 1); lev = np.where(underb, np.minimum(lev, capi), lev)
    U = [HILL]
    for k_ in range(1, len(LV)):
        q_ = inh & (lev >= k_)
        if not q_.any(): U.append(Polygon()); continue
        u_ = unary_union(_sh.box(GX[q_] - cs / 2, GZ[q_] - cs / 2, GX[q_] + cs / 2, GZ[q_] + cs / 2)).buffer(1.5).buffer(-3.0).buffer(1.5).simplify(0.4).intersection(U[-1]).buffer(0)
        u_ = unary_union([p_ for p_ in polys(u_) if p_.area > 14]) if not u_.is_empty else Polygon()
        U.append(u_ if not u_.is_empty else Polygon())
    TK = [polys(U[k_].difference(U[k_ + 1]) if k_ + 1 < len(LV) else U[k_]) for k_ in range(len(LV))]
    TKALL.append((TK, LV)); my_st = []; NOTCH = []; AV = avoid.buffer(1.2) if not avoid.is_empty else avoid; BRB = BRIDGE.buffer(0.5) if bridge else Polygon()
    for k_ in range(len(LV)):
        for p_ in list(TK[k_]):
            if p_.area < 20: continue
            ring = p_.exterior; nS = int(ring.length / 0.5); cand = []
            for i_ in range(nS):
                a_ = ring.interpolate(i_ * 0.5); b_ = ring.interpolate(i_ * 0.5 + 0.25); pp = np.array([a_.x, a_.y]); tt = np.array([b_.x - a_.x, b_.y - a_.y]); ln = np.hypot(*tt)
                if ln < 1e-6: cand.append(None); continue
                tt /= ln; nn = np.array([tt[1], -tt[0]])
                if p_.contains(Point(*(pp + nn * 0.3))): nn = -nn
                hs_ = [out_h(*(pp + nn * 0.9 + tt * o_)) for o_ in (-1.0, 0.0, 1.0)]
                if any(v is None for v in hs_): cand.append(None); continue
                hlo = max(hs_); drop = LV[k_] - hlo
                if not (0.4 <= drop <= 2.3) or max(hs_) - min(hs_) > 0.25: cand.append(None); continue
                run = max(0.3 * math.ceil(drop / 0.18), 0.9)
                rect = Polygon([tuple(pp + tt * 1.1 - nn * 0.3), tuple(pp - tt * 1.1 - nn * 0.3), tuple(pp - tt * 1.1 - nn * (run + 1.6)), tuple(pp + tt * 1.1 - nn * (run + 1.6))])
                land = Polygon([tuple(pp + tt * 1.1 + nn * 0.2), tuple(pp - tt * 1.1 + nn * 0.2), tuple(pp - tt * 1.1 + nn * 1.6), tuple(pp + tt * 1.1 + nn * 1.6)])
                if not p_.contains(rect) or rect.intersects(AV) or land.intersects(AV) or rect.intersects(BRB) or land.intersects(ALLROADS): cand.append(None); continue
                cand.append((pp, nn, tt, run, hlo))
            runs = []; st_ = None
            for i_, c_ in enumerate(cand + [None]):
                if c_ is not None and st_ is None: st_ = i_
                if c_ is None and st_ is not None: runs.append((i_ - st_, (st_ + i_ - 1) // 2)); st_ = None
            runs.sort(reverse=True); chosen = []
            for ln_, mid in runs:
                c_ = cand[mid]
                if all(np.hypot(*(c_[0] - o_[0])) > 16 for o_ in chosen): chosen.append(c_)
                if len(chosen) >= (3 if ring.length > 150 else 2 if ring.length > 70 else 1): break
            for (pp, nn, tt, run, hlo) in chosen:
                my_st.append((pp, nn, tt, run, hlo, LV[k_])); NOTCH.append((k_, Polygon([tuple(pp + tt * 1.1 + nn * 0.5), tuple(pp - tt * 1.1 + nn * 0.5), tuple(pp - tt * 1.1 - nn * run), tuple(pp + tt * 1.1 - nn * run)])))
            if not chosen: print('   (bậc cao %.1f, %.0f m2 ở %s: không có chỗ đặt cầu thang, để làm bồn cây)' % (LV[k_], p_.area, name))
    for k_ in range(len(LV)):
        cs_ = [r_ for kk_, r_ in NOTCH if kk_ == k_]
        if cs_: TK[k_] = [q_ for p_ in TK[k_] for q_ in polys(p_.difference(unary_union(cs_)))]
    terr = [(p_, LV[k_]) for k_ in range(len(LV)) for p_ in TK[k_]]; TERR.extend(terr); STAIRS.extend(my_st)
    for (pp, nn, tt, run, hlo, lvl) in my_st:
        ns_ = max(2, math.ceil((lvl - hlo) / 0.18)); rz = (lvl - hlo) / ns_; tr_ = run / ns_; yb_ = min(hlo, g(*pp)) - 0.6
        for i_ in range(ns_): B.obox(pp - nn * (tr_ * (i_ + 0.5)), tt, nn, 1.1, tr_ / 2, yb_, hlo + rz * (i_ + 1), SC)
        B.obox(pp + nn * 0.25, tt, nn, 1.1, 0.25, yb_, hlo + 0.02, SC)
    nwall = 0
    for p_, lvl in terr:
        sheet(p_, lambda x, z, lvl=lvl: lvl, GRASS_T, GRC)
        for ring in [p_.exterior] + list(p_.interiors):
            for a_, b_ in seg_iter(ring):
                d_ = b_ - a_; ln = np.hypot(*d_)
                if ln < 1e-4: continue
                d_ = d_ / ln; nn = np.array([d_[1], -d_[0]]); mid = (a_ + b_) / 2
                if p_.contains(Point(*(mid + nn * 0.15))): nn = -nn
                ho = out_h(*(mid + nn * 0.45)); go = gh(*(mid + nn * 0.45)); nh3 = np.array([nn[0], 0, nn[1]])
                ya = min(g(*a_), gh(*a_)) - 0.5; yb = min(g(*b_), gh(*b_)) - 0.5; lowout = ho if ho is not None else go
                if lvl - lowout > 0.3:
                    top_ = lvl + (0.28 if not any(np.hypot(*(mid - s_[0])) < 1.5 for s_ in my_st) else 0.0)
                    B.wall(a_, b_, min(ya, lvl - 0.3), top_, STONE_T, KEC, None, nh3, None, min(yb, lvl - 0.3), top_); nwall += 1
                    if top_ > lvl:
                        ai, bi = a_ - nn * 0.3, b_ - nn * 0.3; B.wall(ai, bi, lvl, top_, PLAIN, CAPC, None, -nh3); B.quad([(a_[0], top_, a_[1]), (b_[0], top_, b_[1]), (bi[0], top_, bi[1]), (ai[0], top_, ai[1])], PLAIN, CAPC, UP)
                else:
                    B.wall(a_, b_, min(ya, lvl - 0.3), lvl, PLAIN, KEC, None, nh3, None, min(yb, lvl - 0.3), lvl)
                    if lowout > lvl + 0.12: B.wall(a_, b_, lvl - 0.2, lowout + 0.08, STONE_T, KEC, None, -nh3)          # đất ngoài cao hơn bậc: kè quay mặt vào trong
    BRW = BRIDGE.buffer(2.2) if bridge else Polygon(); nt = 0
    for p_, lvl in terr:
        inner = p_.buffer(-2.0)
        if inner.is_empty: continue
        x0_, z0_, x1_, z1_ = inner.bounds; want = int(p_.area / tree_per) + (1 if p_.area > 40 else 0); tries = 0; got = 0
        while got < want and tries < 500:
            tries += 1; c_ = np.array([rngT.uniform(x0_, x1_), rngT.uniform(z0_, z1_)])
            if not inner.contains(Point(*c_)) or BRW.contains(Point(*c_)) or any(np.hypot(*(c_ - t_)) < 4.6 for t_ in TREES) or any(np.hypot(*(c_ - s_[0])) < 4.0 for s_ in my_st): continue
            r_ = rngT.random()
            if r_ < pink: tree(c_, 5.0 + rngT.random() * 1.5, 2.0 + rngT.random() * 0.6, 'round', col=lin('#f2a7c3'), y0=lvl)
            else: tree(c_, 6.0 + rngT.random() * 2.5, 1.9 + rngT.random() * 0.8, 'pine' if r_ > 0.6 else 'round', y0=lvl)
            TREES.append(c_); BLOCK.append((Point(*c_).buffer(0.05), lvl + 6)); got += 1; nt += 1
    print('khối %s: %d mảnh bậc, cao độ %s, %d cầu thang, %d đoạn kè, %d cây' % (name, len(terr), sorted(set(round(l_, 1) for _p, l_ in terr)), len(my_st), nwall, nt))

# ---- khối 1: sườn đồi phía đông cầu ----
SIDEW = 2.6; tf = lambda s: 18.5 + (s - 39.5) / 17.5 * 2.5
HPOLY = unary_union([Polygon(WL([(s0, tf(s0)), (s1, tf(s1)), (s1, 36.0), (s0, 36.0)])) for s0, s1, _n, _c, _w in HOUSES])
P0 = Polygon([(-21.0, -87.5), (-9.0, -96.5), (12.0, -99.5), (30.0, -101.5), (38.5, -102.8), (46.9, -103.0), (54.5, -90.0), (62.0, -80.0), (22.0, -44.0), (2.0, -52.0), (-2.5, -61.5), (-4.0, -66.0), (-9.9, -73.4), (-16.2, -81.2)])
P0 = P0.difference(LOOPP.buffer(0.5)).buffer(0)                      # chỉ phía đồi của đường sau chợ
EXC = unary_union([FACE, PLAT, FOOT.buffer(0.05)]); RDW = ROAD.buffer(4.3 + SIDEW); RD = ROAD.buffer(4.3)
FRONT = Polygon(WL([(38.0, tf(38.0) - 9.0), (58.5, tf(58.5) - 9.0), (58.5, tf(58.5)), (38.0, tf(38.0))])).intersection(P0).difference(RD).difference(HPOLY).buffer(0)
WALK = P0.intersection(RDW).difference(RD).difference(EXC).difference(HPOLY).buffer(0)
PAVE1 = unary_union([WALK, FRONT]).buffer(0)
HILL1 = P0.difference(RDW).difference(EXC).difference(HPOLY.buffer(0.02)).difference(FRONT).buffer(0); HILL1 = unary_union([q_ for q_ in polys(HILL1) if q_.area > 8])
nH = kill_whole(HILL1.difference(BRIDGE.buffer(1.5))) + kill(HILL1.difference(BRIDGE.buffer(0.6))); OPEN.append(unary_union([HILL1, PAVE1]))
terrace_block('đồi phía đông cầu', HILL1, PAVE1, [6.6, 8.4, 10.2, 12.0, 13.8, 15.5], avoid=HPOLY, bridge=True)

# ---- các bãi cỏ dốc khác ----
glab, gn = _label(wk == 1); blab, bn = _label(wh == -32768); bsz = np.bincount(blab.ravel()); DONE1 = unary_union([HILL1, PAVE1, FACE, PLAT, FOOT, APR]).buffer(2.0); ZONES = []
for gi in range(1, gn + 1):
    gm = glab == gi
    if gm.sum() * ggst * ggst < 30: continue
    G_ = cells_poly(gm, 0.02).buffer(1.2).buffer(-1.2).simplify(0.5).buffer(0)
    if G_.intersects(DONE1): continue
    jj, ii = np.where(gm); j0, j1, i0, i1 = max(0, jj.min() - 16), min(gnz, jj.max() + 17), max(0, ii.min() - 16), min(gnx, ii.max() + 17)
    sub = blab[j0:j1, i0:i1]; ids = [b_ for b_ in np.unique(sub) if b_ > 0 and bsz[b_] >= 20]                 # nhà, sạp: mảng chặn từ 5 m2 (cây thì nhỏ hơn)
    BLD = cells_poly(np.isin(blab, ids) & (np.indices(blab.shape)[0] >= j0) & (np.indices(blab.shape)[0] < j1) & (np.indices(blab.shape)[1] >= i0) & (np.indices(blab.shape)[1] < i1), 0.05).buffer(0.3).buffer(0) if ids else Polygon()
    hv = wh[gm]; hv = hv[hv != -32768] / 100.0; lo, hi = float(np.percentile(hv, 2)), float(np.percentile(hv, 98)); small = G_.area < 400
    bstrip, rstrip = (0.0, 0.0) if small else (2.4, 1.8)
    core = G_.difference(ALLROADS.buffer(rstrip)).difference(BLD.buffer(bstrip)).buffer(-0.6).buffer(0.6).buffer(0)
    core = unary_union([q_ for q_ in polys(core) if q_.area > 12]) if not core.is_empty else Polygon()
    if core.is_empty: continue
    pave_ = G_.difference(core).difference(ALLROADS).difference(BLD).buffer(-0.05).buffer(0)
    LVb = [round(lo + 0.5 + 1.8 * k_, 2) for k_ in range(int(max(0.0, hi - lo - 0.5) / 1.8) + 2)]
    nk = kill_whole(core, frac=0.6, reach=6.0); OPEN.append(unary_union([core, pave_]))
    terrace_block('bãi cỏ (%d, %d)' % (core.centroid.x, core.centroid.y), core, pave_, LVb, avoid=BLD, pink=0.3, tree_per=140.0 if not small else 60.0)
    ZONES.append(unary_union([core, pave_]))
HILL = unary_union([b_[0] for b_ in BLOCKS]).buffer(0); PAVEH = unary_union([b_[1] for b_ in BLOCKS]).buffer(0); park = unary_union([HILL, PAVEH]).buffer(0)
