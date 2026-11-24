# Dựng lại ảnh phủ nhân vật character.jpg (1024×1408) từ tranh mặt trước của chủ dự án:
#  nửa trái: mặt trước, khớp theo khung bao của mô hình, viền ngoài kéo màu mép ra để không lem nền;
#  nửa phải: mặt sau dựng từ chính các điểm ảnh của tranh: gáy tóc, lưng áo đỏ có mũ trùm, ba lô vải ô liu có túi, nắp và dây, quần, gót giày.
# Chạy: python3 tex.py <tranh.png có nền trong suốt> <character.jpg ra>
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
src = Image.open(sys.argv[1]).convert('RGBA'); A = np.array(src); al = A[:, :, 3] > 60; ys, xs = np.where(al)
fig = src.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
W, H = 1024, 1408; X0, X1 = 0.006 * W, 0.494 * W; Y0, Y1 = (1 - 0.997) * H, (1 - 0.003) * H; fw, fh = int(round(X1 - X0)), int(round(Y1 - Y0))
fig = fig.resize((fw, fh), Image.LANCZOS); F = np.array(fig).astype(np.float32); rgb = F[:, :, :3]; m = F[:, :, 3] > 128
rng = np.random.default_rng(7)
def pad(rgb, m):                      # tô vùng ngoài hình bằng màu điểm ảnh gần nhất trong hình, rồi làm mềm riêng phần viền
    idx = ndi.distance_transform_edt(~m, return_distances=False, return_indices=True); out = rgb[idx[0], idx[1]]
    bl = np.stack([ndi.gaussian_filter(out[:, :, c], 2.5) for c in range(3)], 2); out[~m] = bl[~m]; return out
r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]; yy, xx = np.mgrid[0:fh, 0:fw]; fy = yy / fh; fx = xx / fw
red = (r > 85) & (g < 100) & (r > g * 1.55)
# ---------------- mặt sau ----------------
Bk = rgb.copy()
def tex_like(mask_src, shape, blur=1.2):   # vân vải lấy từ chính điểm ảnh: nhiễu quanh màu trung bình, giữ độ lệch chuẩn
    px = rgb[mask_src]; mu = px.mean(0); sd = px.std(0); n = ndi.gaussian_filter(rng.normal(size=shape), blur); n /= n.std() + 1e-6
    return mu[None, None, :] + n[:, :, None] * sd[None, None, :] * 0.55
# 1) đầu: thay mặt bằng tóc, giữ viền tóc và tai; gáy lộ một dải da cổ
head = m & (fy < 0.150); hair_px = head & (r < 75) & (g < 65); skin = head & (r > 150) & (g > 100)
hair = tex_like(hair_px, (fh, fw), 0.8); strand = ndi.gaussian_filter(rng.normal(size=(fh, fw)), (14, 1.6)); strand /= strand.std(); hair = hair * (1 + 0.07 * strand[:, :, None])
cxh = xs_mid = (np.where(head.any(0))[0].min() + np.where(head.any(0))[0].max()) / 2 / fw
inner = ndi.binary_erosion(head, iterations=7); face = inner & (((fx - cxh) / 0.172) ** 2 + ((fy - 0.074) / 0.074) ** 2 < 1)        # lòng đầu, chừa viền tóc thật và hai tai
shade = 0.82 + 0.3 * (1 - ((fx - cxh) / 0.13) ** 2).clip(0, 1) * (1 - (fy / 0.14)) ; soft = ndi.gaussian_filter(face.astype(np.float32), 4)[:, :, None]; Bk[:] = Bk * (1 - soft) + hair * shade[:, :, None] * soft
nape = m & (fy >= 0.134) & (fy < 0.152) & (np.abs(fx - cxh) < 0.07); sk = rgb[skin].mean(0); Bk[nape] = sk * 0.88
# 2) thân: lưng áo đỏ liền (bỏ sơ mi, khoá kéo, dây rút, quai ba lô phía trước)
torso = m & (fy > 0.150) & (fy < 0.492) & (fx > 0.20) & (fx < 0.80)
jk = tex_like(red & (fy > 0.3) & (fy < 0.45), (fh, fw), 1.0)
lum = ndi.gaussian_filter(np.where(red, rgb.mean(2), 0), 14) / (ndi.gaussian_filter(red.astype(np.float32), 14) + 1e-3); lum = lum / (rgb[red].mean() + 1e-6)
fillm = torso & ~red; Bk[fillm] = (jk * lum.clip(0.6, 1.35)[:, :, None])[fillm]
hem = m & (fy > 0.458) & (fy < 0.492) & (fx > 0.28) & (fx < 0.72)                                   # bo gấu áo chạy ngang lưng
rib = 0.86 + 0.14 * np.sign(np.sin(xx * 1.15)); Bk[hem & fillm] = (jk * 0.9 * rib[:, :, None])[hem & fillm]
tail = m & (fy >= 0.492) & (fy < 0.56) & (r > 150) & (g > 140) & (fx > 0.32) & (fx < 0.68)                                    # vạt sơ mi thò dưới gấu: đổi thành quần
pants_px = m & (fy > 0.6) & (fy < 0.85) & (r < 90); pt = tex_like(pants_px, (fh, fw), 0.9); Bk[tail] = pt[tail]
# 3) mũ trùm rủ sau gáy
img = Image.fromarray(pad(Bk, m).clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(img, 'RGBA'); jm = rgb[red].mean(0)
col = lambda k: tuple(int(v) for v in (jm * k).clip(0, 255))
cx = cxh * fw; hy0, hy1 = 0.150 * fh, 0.235 * fh
d.pieslice([cx - 0.17 * fw, hy0 - 0.03 * fh, cx + 0.17 * fw, hy1 + 0.045 * fh], 0, 180, fill=col(0.80) + (255,))
d.pieslice([cx - 0.14 * fw, hy0 - 0.045 * fh, cx + 0.14 * fw, hy1 + 0.012 * fh], 0, 180, fill=col(1.04) + (255,))
d.arc([cx - 0.17 * fw, hy0 - 0.03 * fh, cx + 0.17 * fw, hy1 + 0.045 * fh], 0, 180, fill=col(0.6) + (255,), width=3)
# 4) ba lô (trùng ô mà mã game dùng cho khối ba lô: fu 0.35..0.73, v 0.555..0.765)
om = np.array([136.0, 128.0, 84.0])                      # màu vải ô liu của ba lô, lấy theo quai và thân ba lô trong tranh
oc = lambda k: tuple(int(v) for v in (om * k).clip(0, 255))
bx0, bx1 = 0.33 * fw, 0.75 * fw; by0, by1 = (1 - 0.775 - 0.003) / 0.994 * fh, (1 - 0.545 - 0.003) / 0.994 * fh
d.rounded_rectangle([bx0 - 4, by0 - 4, bx1 + 4, by1 + 6], 30, fill=oc(0.55) + (255,))
d.rounded_rectangle([bx0, by0, bx1, by1], 28, fill=oc(1.0) + (255,))
d.rounded_rectangle([bx0 + 8, by0 + 6, bx1 - 8, by0 + (by1 - by0) * 0.34], 24, fill=oc(1.1) + (255,), outline=oc(0.62) + (255,), width=3)                  # nắp
d.rounded_rectangle([cx - 20, by0 - 12, cx + 20, by0 + 8], 8, fill=oc(0.8) + (255,), outline=oc(0.55) + (255,), width=2)                                   # quai xách
d.rounded_rectangle([bx0 + 22, by0 + (by1 - by0) * 0.47, bx1 - 22, by1 - 16], 18, fill=oc(0.9) + (255,), outline=oc(0.6) + (255,), width=3)               # túi trước
d.line([bx0 + 30, by0 + (by1 - by0) * 0.58, bx1 - 30, by0 + (by1 - by0) * 0.58], fill=oc(0.6) + (255,), width=3)
for sx in (bx0 + (bx1 - bx0) * 0.3, bx0 + (bx1 - bx0) * 0.7):                                                                                             # hai dây khoá nắp
    d.rectangle([sx - 7, by0 + (by1 - by0) * 0.2, sx + 7, by0 + (by1 - by0) * 0.5], fill=oc(0.72) + (255,)); d.rectangle([sx - 9, by0 + (by1 - by0) * 0.36, sx + 9, by0 + (by1 - by0) * 0.41], fill=(58, 60, 50, 255))
back = np.array(img).astype(np.float32)
bm = np.zeros((fh, fw), bool); bm[int(by0) - 12:int(by1) + 6, int(bx0) - 4:int(bx1) + 4] = True
fab = ndi.gaussian_filter(rng.normal(size=(fh, fw)), 0.8); back[bm] *= (1 + 0.05 * fab[bm])[:, None]
gx = (1 - 0.22 * (np.abs(xx - (bx0 + bx1) / 2) / ((bx1 - bx0) / 2)) ** 2.5).clip(0.7, 1); back[bm] *= gx[bm][:, None]
front = pad(rgb, m)
out = np.zeros((H, W, 3), np.float32); ox, oy = int(round(X0)), int(round(Y0))
for half, im in ((0, front), (W // 2, back)):
    canvas = np.zeros((H, W // 2, 3), np.float32); canvas[oy:oy + fh, ox:ox + fw] = im
    msk = np.zeros((H, W // 2), bool); msk[oy:oy + fh, ox:ox + fw] = True; idx = ndi.distance_transform_edt(~msk, return_distances=False, return_indices=True); canvas = canvas[idx[0], idx[1]]
    out[:, half:half + W // 2] = canvas
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(sys.argv[2], quality=92, optimize=True); print('ghi', sys.argv[2])
