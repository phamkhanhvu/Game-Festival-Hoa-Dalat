# Phần dùng chung cho rear.py: nạp lưới, mặt đất thấp nhất, hàm xoá theo vùng, hàm dựng tường/mái theo ô vân
import sys, os, io, math, numpy as np
_here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_here)); sys.path.insert(0, _here)
import glbio, mb, worldio
from mb import lin, tile_uv, PLAIN
from scipy import ndimage
from shapely.geometry import Polygon, LineString, Point
from shapely import contains_xy
from fr import *
BX0, BX1, BZ0, BZ1, GS = -75.0, 170.0, -160.0, 25.0, 0.5
def ground_raster(P, I):
    """mặt thấp nhất mỗi ô 0,5 m trong khung làm việc (mặt đất, kể cả dưới gầm cầu); ô không có mặt thì lấy ô gần nhất"""
    cen = P[I].mean(1); sel = (cen[:, 0] > BX0 - 10) & (cen[:, 0] < BX1 + 10) & (cen[:, 2] > BZ0 - 10) & (cen[:, 2] < BZ1 + 10); T = I[sel]
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]; ar = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2; n = np.clip((ar * 14).astype(int) + 3, 3, 80000)
    rng = np.random.default_rng(1); idx = np.repeat(np.arange(len(T)), n); u = rng.random(len(idx)); v = rng.random(len(idx)); f = u + v > 1; u[f] = 1 - u[f]; v[f] = 1 - v[f]
    pts = a[idx] + (b[idx] - a[idx]) * u[:, None] + (c[idx] - a[idx]) * v[:, None]
    W = int((BX1 - BX0) / GS); H = int((BZ1 - BZ0) / GS); px = ((pts[:, 0] - BX0) / GS).astype(int); pz = ((pts[:, 2] - BZ0) / GS).astype(int); ok = (px >= 0) & (px < W) & (pz >= 0) & (pz < H)
    px, pz, y = px[ok], pz[ok], pts[ok, 1]; o = np.argsort(-y); G = np.full((H, W), np.nan); G[pz[o], px[o]] = y[o]
    bad = np.isnan(G); ind = ndimage.distance_transform_edt(bad, return_distances=False, return_indices=True); G = G[tuple(ind)]
    return G
class Ground:
    def __init__(self, G): self.G = G; self.Gs = ndimage.uniform_filter(ndimage.median_filter(G, 5), 5); self.Gh = ndimage.uniform_filter(ndimage.maximum_filter(ndimage.median_filter(G, 3), 7), 5)
    def at(self, x, z, smooth=True, hi=False):
        G = self.Gh if hi else (self.Gs if smooth else self.G); fx = np.clip((np.asarray(x, float) - BX0) / GS - 0.5, 0, G.shape[1] - 1.001); fz = np.clip((np.asarray(z, float) - BZ0) / GS - 0.5, 0, G.shape[0] - 1.001)
        i = np.floor(fx).astype(int); j = np.floor(fz).astype(int); a = fx - i; b = fz - j
        return (G[j, i] * (1 - a) + G[j, i + 1] * a) * (1 - b) + (G[j + 1, i] * (1 - a) + G[j + 1, i + 1] * a) * b
class Builder(mb.MB):
    """thêm các hàm dựng theo ô vân: tường chia đoạn (mỗi đoạn một ô), mái dốc, hộp theo đa giác"""
    def wall(self, a, b, y0, y1, tile=PLAIN, col=mb.WHITE, seg=None, nh=None, sub=None, y0b=None, y1b=None):
        a = np.asarray(a, float); b = np.asarray(b, float); Ln = np.hypot(*(b - a)); n = 1 if not seg else max(1, int(round(Ln / seg)))
        if nh is None: d = (b - a) / max(Ln, 1e-9); nh = np.array([d[1], 0, -d[0]])
        y0b = y0 if y0b is None else y0b; y1b = y1 if y1b is None else y1b
        if (b[0] - a[0]) * nh[2] - (b[1] - a[1]) * nh[0] < 0: a, b = b, a; y0, y0b = y0b, y0; y1, y1b = y1b, y1      # a -> b luôn từ trái sang phải khi nhìn từ ngoài vào (chữ trên ô vân không bị ngược)
        for k in range(n):
            f0, f1 = k / n, (k + 1) / n; p = a + (b - a) * f0; q = a + (b - a) * f1
            self.quad([(p[0], y0 + (y0b - y0) * f0, p[1]), (q[0], y0 + (y0b - y0) * f1, q[1]), (q[0], y1 + (y1b - y1) * f1, q[1]), (p[0], y1 + (y1b - y1) * f0, p[1])], tile, col, np.asarray(nh, float), sub)
    def ring(self, poly, y0, y1, tile=PLAIN, col=mb.WHITE, seg=None, skip=(), sub=None):
        """tường quanh đa giác (x,z), pháp tuyến quay ra ngoài"""
        pg = Polygon(poly); c = np.array(pg.centroid.coords[0]); n = len(poly)
        for k in range(n):
            if k in skip: continue
            a = np.asarray(poly[k], float); b = np.asarray(poly[(k + 1) % n], float); d = (b - a) / max(np.hypot(*(b - a)), 1e-9); nn = np.array([d[1], -d[0]])
            if np.dot(nn, (a + b) / 2 - c) < 0: nn = -nn
            self.wall(a, b, y0, y1, tile, col, seg, np.array([nn[0], 0, nn[1]]), sub)
    def flat(self, poly, y, tile=PLAIN, col=mb.WHITE, up=True, uv=None):
        pts = [(x, y, z) for x, z in poly]; self.poly(pts, tile, col, np.array([0, 1.0 if up else -1.0, 0]), uv)
    def slab(self, poly, y0, y1, col=mb.WHITE, tile=PLAIN, topcol=None, bottom=True):
        self.ring(poly, y0, y1, PLAIN, col); self.flat(poly, y1, tile, topcol if topcol is not None else col)
        if bottom: self.flat(poly, y0, PLAIN, col * 0.8, up=False)
    def patch(self, p4, tile, col, nu=1, nv=1, nh=None):
        """mảng tứ giác chia nu x nv ô vân; p4: dưới-trái, dưới-phải, trên-phải, trên-trái"""
        p = np.asarray(p4, float)
        for i in range(nu):
            for j in range(nv):
                def at(u, v): return (p[0] * (1 - u) + p[1] * u) * (1 - v) + (p[3] * (1 - u) + p[2] * u) * v
                self.quad([at(i / nu, j / nv), at((i + 1) / nu, j / nv), at((i + 1) / nu, (j + 1) / nv), at(i / nu, (j + 1) / nv)], tile, col, nh)
