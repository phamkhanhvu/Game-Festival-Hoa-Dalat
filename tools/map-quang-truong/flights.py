# Tìm các vế bậc thang nâu (vật liệu FUEGO) của mô hình quảng trường không lên tới tầng trên, và tính vế bậc mới đủ cao
import sys, json, numpy as np
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'map-cho')); import worldio
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import contains_xy
def find(tris_npz, world_js):
    d = np.load(tris_npz); T = np.concatenate([d[k] for k in d.files if 'FUEGO' in k]); n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); a = np.linalg.norm(n, axis=1) / 2
    H = T[np.abs(n[:, 1]) / np.maximum(2 * a, 1e-9) > 0.9]; cen = H.mean(1)
    U = unary_union([Polygon(t[:, [0, 2]]).buffer(0.12) for t in H if Polygon(t[:, [0, 2]]).area > 1e-4]); gs = list(U.geoms)
    j, h, top, k, pre, post = worldio.load(world_js)
    def hat(x, z):
        i = int(round((x - j['x0']) / j['step'])); jj = int(round((z - j['z0']) / j['step']))
        return None if not (0 <= i < j['nx'] and 0 <= jj < j['nz']) or h[jj, i] == -32768 else h[jj, i] / 100.0
    out = []
    for g in gs:
        q = contains_xy(g, cen[:, 0], cen[:, 2]); P = H[q].reshape(-1, 3); lv = np.unique(np.round(cen[q, 1], 2))
        if len(lv) < 4: continue
        xz = P[:, [0, 2]]; c = xz.mean(0); w, V = np.linalg.eigh(np.cov((xz - c).T)); u = V[:, 1]; v = V[:, 0]
        # hướng lên: v tăng theo cao độ
        if np.corrcoef((xz - c) @ v, P[:, 1])[0, 1] < 0: v = -v
        if abs(np.corrcoef((xz - c) @ v, P[:, 1])[0, 1]) < 0.9: u, v = v, u; v = v if np.corrcoef((xz - c) @ v, P[:, 1])[0, 1] > 0 else -v
        su = (xz - c) @ u; sv = (xz - c) @ v; u0, u1, v0, v1 = su.min(), su.max(), sv.min(), sv.max(); rise = float(np.median(np.diff(lv))); dp = (v1 - v0) / len(lv)
        def med(vv):
            vals = [hat(*(c + u * uu + v * vv)) for uu in np.linspace(u0 + 0.5, u1 - 0.5, 9)]; vals = [x for x in vals if x is not None]; return float(np.median(vals)) if vals else None
        tgt = med(v1 + 1.0); base = med(v0 - 0.8)
        out.append(dict(c=c, u=u, v=v, u0=u0, u1=u1, v0=v0, v1=v1, lv=lv, rise=rise, dp=dp, tgt=tgt, base=base, area=g.area))
    return out, (j, h, top, k, pre, post)
if __name__ == '__main__':
    fl, _ = find(sys.argv[1], sys.argv[2])
    for f in sorted(fl, key=lambda f: f['c'][0]):
        gap = None if f['tgt'] is None else f['tgt'] - f['lv'].max()
        print('tâm (%.0f, %.0f) dài %.1f rộng %.1f  %d bậc %.2f..%.2f  bậc cao %.2f sâu %.2f  nền dưới %s  tầng trên %s  hụt %s' % (f['c'][0], f['c'][1], f['u1'] - f['u0'], f['v1'] - f['v0'], len(f['lv']), f['lv'].min(), f['lv'].max(), f['rise'], f['dp'], f['base'], f['tgt'], None if gap is None else round(gap, 2)))
