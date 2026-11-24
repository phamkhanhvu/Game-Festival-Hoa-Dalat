# Ảnh phủ nhân vật bốn mặt (2048×1408): bốn ô 512 px theo thứ tự trước, sau, phải, trái.
# Mỗi tranh được tách nền, rồi co giãn từng hàng ngang cho viền hình trùng với viền của mô hình 3D nhìn từ đúng hướng đó
# (các tranh do AI vẽ nên dáng không khớp tuyệt đối với mô hình); vùng ngoài viền kéo màu mép ra để không lem nền.
# Chạy: python3 tex4.py <character.npz: P, I> <trước.png> <sau.png> <phải.png (mặt quay sang phải)> <trái.png> <character.jpg ra>
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
M = np.load(sys.argv[1]); P, I = M['P'], M['I']; PW, H = 512, 1408; X0, FW = 6, 500; Y0 = int(round(0.003 * H)); FH = int(round(0.994 * H))
mn, mx = P.min(0), P.max(0)
def mesh_extent(view):                # viền mô hình theo từng hàng của ô ảnh, tính bằng tỉ lệ 0..1 trong khung bao
    ax = 0 if view < 2 else 2; f = (P[:, ax] - mn[ax]) / (mx[ax] - mn[ax]); f = 1 - f if view in (1, 3) else f
    y = (1 - (P[:, 1] - mn[1]) / (mx[1] - mn[1])) * (FH - 1); im = Image.new('L', (FW, FH), 0); d = ImageDraw.Draw(im)
    for t in I: d.polygon([(f[k] * (FW - 1), y[k]) for k in t], fill=255)
    return np.array(im) > 0
def cut(path):                        # tách nền: nền trong suốt sẵn, hoặc nền xám liền với mép ảnh
    im = Image.open(path)
    if im.mode == 'RGBA': a = np.array(im); return a[:, :, :3].astype(np.float32), a[:, :, 3] > 100
    a = np.array(im.convert('RGB')).astype(np.float32); bg = np.median(np.concatenate([a[:8].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)]), 0)
    near = (np.abs(a - bg).max(2) < 15) & ((a.max(2) - a.min(2)) < 14); lab, n = ndi.label(near); edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    fg = ~np.isin(lab, edge[edge > 0]); fg = ndi.binary_opening(fg, iterations=2); l2, n2 = ndi.label(fg); big = np.argmax(ndi.sum(fg, l2, range(1, n2 + 1))) + 1
    holes = ndi.binary_fill_holes(l2 == big) & ~(l2 == big); hl, hn = ndi.label(holes); keep = np.zeros_like(holes)       # lỗ nhỏ trong hình (đốm sáng trên vải) thì lấp, khe hở lớn (giữa hai chân, giữa tay và thân) thì để là nền
    for k in range(1, hn + 1):
        if (hl == k).sum() < 250: keep |= hl == k
    return a, ndi.binary_erosion((l2 == big) | keep, iterations=2)
def rows(mask):                       # mép trái, phải của hình theo từng hàng (đã làm mượt), NaN ở hàng trống
    any_ = mask.any(1); lo = np.where(any_, mask.argmax(1), np.nan).astype(float); hi = np.where(any_, mask.shape[1] - 1 - mask[:, ::-1].argmax(1), np.nan).astype(float)
    ok = np.where(any_)[0]; idx = np.arange(len(lo)); lo = np.interp(idx, ok, lo[ok]); hi = np.interp(idx, ok, hi[ok])
    return ndi.uniform_filter1d(lo, 9), ndi.uniform_filter1d(hi, 9)
out = np.zeros((H, PW * 4, 3), np.float32)
for view in range(4):
    rgb, m = cut(sys.argv[2 + view]); ys, xs = np.where(m); rgb = rgb[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = FH / m.shape[0]; nw = max(8, int(round(m.shape[1] * sc)))
    rgb = np.array(Image.fromarray(rgb.astype(np.uint8)).resize((nw, FH), Image.LANCZOS)).astype(np.float32); m = np.array(Image.fromarray(m).resize((nw, FH), Image.NEAREST))
    idx = ndi.distance_transform_edt(~m, return_distances=False, return_indices=True); rgb = rgb[idx[0], idx[1]]             # tô nền bằng màu gần nhất của hình
    ilo, ihi = rows(m); mm = mesh_extent(view); mlo, mhi = rows(mm); xs_ = np.arange(FW, dtype=np.float32)
    if view == 0: ilo = np.zeros(FH); ihi = np.full(FH, nw - 1.0); mlo = np.zeros(FH); mhi = np.full(FH, FW - 1.0)      # mô hình dựng từ chính tranh mặt trước nên đã khớp: không co giãn, tránh lệch bàn tay và nét mặt
    panel = np.zeros((FH, FW, 3), np.float32)
    for r in range(FH):
        t = ((xs_ - mlo[r]) / max(mhi[r] - mlo[r], 1.0)).clip(0, 1); sx = ilo[r] + t * (ihi[r] - ilo[r]); x0 = np.clip(np.floor(sx).astype(int), 0, nw - 1); x1 = np.clip(x0 + 1, 0, nw - 1); fr = (sx - x0)[:, None]
        panel[r] = rgb[r, x0] * (1 - fr) + rgb[r, x1] * fr
    cv = np.zeros((H, PW, 3), np.float32); cv[Y0:Y0 + FH, X0:X0 + FW] = panel; k = np.zeros((H, PW), bool); k[Y0:Y0 + FH, X0:X0 + FW] = True
    idx = ndi.distance_transform_edt(~k, return_distances=False, return_indices=True); out[:, view * PW:(view + 1) * PW] = cv[idx[0], idx[1]]
    print('mặt', view, 'tranh', m.shape, 'độ rộng hình', round(float(np.nanmean(ihi - ilo))), '-> mô hình', round(float(np.mean(mhi - mlo))))
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(sys.argv[6], quality=90, optimize=True); print('ghi', sys.argv[6])
