# Sửa cầu đi bộ vào chợ: các bước dựng khu sau chợ (rear/) đã xoá nhầm một đoạn mặt cầu lát gạch ở đầu cầu
# và toàn bộ lan can, bồn cây, cột đèn phía taluy. Tệp này lấy lại đúng các phần đó từ bản market.glb trước khi làm khu sau chợ.
#   python3 bridgefix.py <market.glb hiện tại> <market.glb trước khu sau chợ> <market.glb ra>
import sys, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import glbio
from mb import write_glb

A0 = np.array([-22.13, -94.9]); B0 = np.array([7.29, -58.24]); U = (B0 - A0) / np.linalg.norm(B0 - A0); NR = np.array([U[1], -U[0]])
S0, S1 = 4.5, 14.6            # đoạn mặt cầu bị thủng (tính theo mét dọc tim cầu từ mốc đầu cầu)
PARTS = [(1.0, 0.98, 0.92), (0.02, 0.02, 0.02), (1.0, 0.95, 0.8), (0.78, 0.75, 0.69), (0.85, 0.84, 0.79), (0.91, 0.9, 0.85), (0.92, 0.91, 0.87)]   # lan can, cột đèn, chao đèn, tường chắn

def load(path):
    M = glbio.load(path); P, N, UV, C, I = M['P'], M['N'], M['UV'], M['C'][:, :3], M['I']
    T = P[I]; cen = T.mean(1); s = (cen[:, [0, 2]] - A0) @ U; w = (cen[:, [0, 2]] - A0) @ NR
    tile = np.floor(UV[I[:, 0]] * 8).astype(int); col = C[I[:, 0]]
    nrm = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); flat = np.abs(nrm[:, 1]) > 0.9 * (np.linalg.norm(nrm, axis=1) + 1e-12)
    return dict(M=M, P=P, N=N, UV=UV, C=C, I=I, T=T, cen=cen, s=s, w=w, tile=tile, col=col, flat=flat)

def main(cur_path, old_path, out_path):
    c = load(cur_path); o = load(old_path)
    deck = lambda d: d['flat'] & (d['tile'][:, 0] == 0) & (d['tile'][:, 1] == 2) & (d['s'] >= S0) & (d['s'] < S1) & (np.abs(d['w']) < 3.2) & (d['cen'][:, 1] > 14.8) & (d['cen'][:, 1] < 15.9)
    drop = deck(c); add = deck(o)
    # các phần khác của cầu có trong bản cũ mà bản hiện tại không còn (so đúng từng tam giác)
    key = lambda T: [tuple(np.round(np.sort(t.reshape(-1)), 2)) for t in T]
    cor = lambda d: (d['s'] > -3) & (d['s'] < 50) & (np.abs(d['w']) < 4.0) & (d['cen'][:, 1] > 12.9) & (d['cen'][:, 1] < 20.5)
    have = set(key(c['T'][cor(c)]))
    part = np.zeros(len(o['I']), bool)
    for pc in PARTS: part |= np.abs(o['col'] - np.array(pc)).max(1) < 0.012
    part |= (o['tile'][:, 0] == 3) & (o['tile'][:, 1] == 2)        # hàng rào cây cắt tỉa
    part |= (o['tile'][:, 0] == 6) & (o['tile'][:, 1] == 1)        # bồn cây
    cand = np.where(cor(o) & part & ~add)[0]
    miss = np.array([i for i, k in zip(cand, key(o['T'][cand])) if k not in have], int)
    sel = np.zeros(len(o['I']), bool); sel[miss] = True; sel |= add
    keep = ~drop
    io = o['I'][sel]; nb = len(c['P'])
    P = np.concatenate([c['P'], o['P'][io].reshape(-1, 3)]); N = np.concatenate([c['N'], o['N'][io].reshape(-1, 3)])
    UV = np.concatenate([c['UV'], o['UV'][io].reshape(-1, 2)]); C = np.concatenate([c['C'], o['C'][io].reshape(-1, 3)])
    I = np.concatenate([c['I'][keep], (nb + np.arange(len(io) * 3)).reshape(-1, 3)])
    # kè đá của bậc cỏ chạy ngang dưới đầu cầu đang nhô lên khỏi mặt cầu 8 cm: hạ các đỉnh nằm trong lòng cầu xuống dưới mặt cầu
    T = P[I]; tl = np.floor(UV[I[:, 0]] * 8).astype(int); sv = (T[:, :, [0, 2]] - A0) @ U; wv = (T[:, :, [0, 2]] - A0) @ NR
    dk = np.clip(9.8373 - 0.04538 * T[:, :, 0] - 0.05654 * T[:, :, 2], 12.8, 15.7)
    ke = (tl[:, 0] == 6) & (tl[:, 1] == 5) & (sv.min(1) > 4.0) & (sv.max(1) < 24) & (np.abs(wv).min(1) < 3.05)
    hit = ke[:, None] & (np.abs(wv) < 3.1) & (T[:, :, 1] > dk - 0.06)
    P = P.copy(); P[I[hit]] = np.column_stack([T[hit][:, 0], (dk - 0.06)[hit], T[hit][:, 2]])
    nv, nt, size = write_glb(out_path, P, N, UV, C, I, c['M']['img']); print('kè dưới đầu cầu: hạ', int(hit.sum()), 'đỉnh')
    print(f'mặt cầu: bỏ {int(drop.sum())} mảnh còn sót, lấy lại {int(add.sum())} tam giác; lan can, bồn cây, cột đèn lấy lại: {len(miss)} tam giác; glb {nt} tam giác, {size/1e6:.2f} MB')

if __name__ == '__main__':
    main(*sys.argv[1:4])
