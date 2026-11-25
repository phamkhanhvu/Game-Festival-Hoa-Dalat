# Ô vân mới cho khu sau chợ (dán vào các ô còn trống của atlas 8x8)
import io, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
CORR, RIBW, FINS, TALUY, RUST, KSK, AWN, SHUT = (4, 6), (5, 6), (6, 6), (7, 6), (4, 7), (5, 7), (6, 7), (7, 7)
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def noisy(img, amt, seed):
    a = np.array(img).astype(np.float32); a += np.random.default_rng(seed).normal(0, amt, a.shape[:2])[:, :, None]; return Image.fromarray(a.clip(0, 255).astype(np.uint8))
def patch_atlas(jpeg):
    A = Image.open(io.BytesIO(jpeg)).convert('RGB'); put = lambda tile, im: A.paste(im.convert('RGB'), (tile[0] * 256, tile[1] * 256))
    rng = np.random.default_rng(7)
    # tôn sóng (trắng xám, nhuộm bằng màu đỉnh): sóng dọc, vài đường nối ngang
    x = np.arange(256); w = 0.5 + 0.5 * np.cos(x / 256 * 2 * np.pi * 16); a = (198 + 52 * w)[None, :].repeat(256, 0)
    for y in (63, 127, 191): a[y:y + 2, :] *= 0.86
    put(CORR, noisy(Image.fromarray(np.stack([a] * 3, -1).astype(np.uint8)), 3, 1))
    # băng cửa kính khung trắng (mặt sau chợ): 4 cột x 3 hàng ô kính, mảng tường dưới
    t = Image.new('RGB', (256, 256), (238, 236, 228)); d = ImageDraw.Draw(t)
    for c in range(4):
        for r in range(3):
            x0 = 6 + c * 62; y0 = 18 + r * 56; g = [(96, 118, 138), (112, 134, 150), (84, 104, 124), (126, 146, 158)][(c * 3 + r * 5) % 4]
            if (c, r) in ((1, 2), (3, 0)): g = (214, 216, 210)
            d.rectangle([x0, y0, x0 + 56, y0 + 50], fill=g); d.line([x0 + 28, y0, x0 + 28, y0 + 50], fill=(236, 234, 226), width=3)
            d.polygon([(x0 + 2, y0 + 48), (x0 + 22, y0 + 2), (x0 + 30, y0 + 2), (x0 + 10, y0 + 48)], fill=tuple(min(255, v + 22) for v in g))
    d.rectangle([0, 190, 255, 255], fill=(232, 229, 219)); d.line([0, 190, 255, 190], fill=(190, 186, 176), width=2); d.rectangle([0, 0, 255, 10], fill=(244, 242, 236))
    put(RIBW, noisy(t, 3, 2))
    # lam đứng (tháp thang): thanh trắng, khe tối, đai ngang
    t = Image.new('RGB', (256, 256), (58, 64, 72)); d = ImageDraw.Draw(t)
    for k in range(8): d.rectangle([k * 32 + 4, 0, k * 32 + 23, 255], fill=(242, 240, 233)); d.line([k * 32 + 23, 0, k * 32 + 23, 255], fill=(196, 194, 186), width=2)
    for y in (0, 122, 246): d.rectangle([0, y, 255, y + 9], fill=(236, 234, 226))
    put(FINS, noisy(t, 3, 3))
    # taluy bê tông: mái nghiêng có khung dầm ô vuông, vết nước
    t = Image.new('RGB', (256, 256), (196, 184, 160)); d = ImageDraw.Draw(t)
    for k in range(60):
        xx = int(rng.integers(0, 256)); yy = int(rng.integers(0, 200)); d.line([xx, yy, xx + int(rng.integers(-3, 4)), yy + int(rng.integers(20, 70))], fill=(170, 158, 136), width=int(rng.integers(1, 4)))
    for k in range(5): d.rectangle([k * 64 - 5, 0, k * 64 + 5, 255], fill=(214, 204, 184)); d.rectangle([0, k * 64 - 5, 255, k * 64 + 5], fill=(214, 204, 184))
    for i in range(4):
        for j in range(4): d.ellipse([i * 64 + 29, j * 64 + 40, i * 64 + 35, j * 64 + 46], fill=(120, 108, 92))
    put(TALUY, noisy(t.filter(ImageFilter.GaussianBlur(0.6)), 5, 4))
    # mái tôn cũ chắp vá: mảng gỉ, xám, đỏ nhạt
    t = Image.new('RGB', (256, 256), (150, 120, 100)); d = ImageDraw.Draw(t); pal = [(146, 92, 62), (120, 78, 58), (168, 150, 138), (132, 126, 122), (172, 104, 78), (98, 88, 84), (186, 170, 150), (156, 74, 58)]
    for i in range(4):
        for j in range(4):
            c = pal[int(rng.integers(0, len(pal)))]; d.rectangle([i * 64, j * 64, i * 64 + 63, j * 64 + 63], fill=c)
            if rng.random() < 0.5: c2 = pal[int(rng.integers(0, len(pal)))]; d.rectangle([i * 64 + int(rng.integers(0, 30)), j * 64, i * 64 + 63, j * 64 + int(rng.integers(20, 63))], fill=c2)
    a = np.array(t).astype(np.float32) * (0.86 + 0.14 * np.cos(np.arange(256) / 256 * 2 * np.pi * 24))[None, :, None]
    put(RUST, noisy(Image.fromarray(a.clip(0, 255).astype(np.uint8)), 6, 5))
    # mặt ki-ốt: tường trắng, ô cửa bán hàng có hàng hoá, mái hiên nhỏ
    t = Image.new('RGB', (256, 256), (240, 238, 230)); d = ImageDraw.Draw(t); d.rectangle([28, 70, 228, 190], fill=(52, 46, 44))
    cols = [(214, 70, 60), (240, 190, 70), (90, 160, 90), (70, 120, 190), (230, 130, 60), (200, 90, 150)]
    for r in range(3):
        for c in range(9): d.rectangle([36 + c * 21, 80 + r * 36, 36 + c * 21 + 15, 80 + r * 36 + 24], fill=cols[(r * 2 + c) % 6])
        d.rectangle([28, 106 + r * 36, 228, 110 + r * 36], fill=(190, 160, 120))
    d.rectangle([20, 190, 236, 204], fill=(206, 200, 188)); d.rectangle([0, 0, 255, 40], fill=(36, 98, 160))
    f = ImageFont.truetype(FB, 24); d.text((128, 20), 'KI-ỐT', font=f, fill=(255, 255, 255), anchor='mm')
    put(KSK, noisy(t, 3, 6))
    # bạt sọc (trắng và xám nhạt, nhuộm bằng màu đỉnh)
    a = np.where((np.arange(256) // 32) % 2 == 0, 250, 176)[None, :].repeat(256, 0).astype(np.uint8); put(AWN, noisy(Image.fromarray(np.stack([a] * 3, -1)), 2, 7))
    # cửa cuốn, cửa sắt kéo của sạp đóng
    t = Image.new('RGB', (256, 256), (150, 154, 158)); d = ImageDraw.Draw(t)
    for y in range(0, 256, 10): d.line([0, y, 255, y], fill=(118, 122, 128), width=2)
    for xx in (0, 127, 250): d.rectangle([xx, 0, xx + 5, 255], fill=(226, 224, 216))
    d.rectangle([0, 0, 255, 22], fill=(226, 224, 216)); put(SHUT, noisy(t, 3, 8))
    b = io.BytesIO(); A.save(b, 'JPEG', quality=90); return b.getvalue()
