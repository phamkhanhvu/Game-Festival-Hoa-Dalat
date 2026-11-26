# Các vế bậc thang nâu ở bậc thềm hai bên cầu thang lớn chỉ có 7 đến 11 bậc rồi đụng tường đá, không lên tới tầng trên.
# Tệp này tính vế bậc mới đủ cao (phủ lên vế cũ, lưng tựa đúng mặt tường cũ, mọc thêm ra phía trước), ghi vào world.js:
#   WORLD.steps = [[x, z, góc, dài, sâu bậc, số bậc, cao độ nền dưới, cao độ tầng trên], ...]  (x, z: giữa mép sau của vế bậc)
# và sửa lưới đi lại thành dốc đều từ nền dưới lên tầng trên. Game dựng các bậc này lúc chạy (buildSteps trong index.html).
# Chạy: blender/bpy: python3 exp_tris.py model.glb tris.npz ; rồi python3 steps.py tris.npz world.js world.js
import sys, math, numpy as np
from flights import find, worldio
fl, (j, h, top, k, pre, post) = find(sys.argv[1], sys.argv[2])
if 'steps' in j: sys.exit('world.js đã có WORLD.steps: chạy trên bản world.js gốc')
X, Z = np.meshgrid(j['x0'] + np.arange(j['nx']) * j['step'], j['z0'] + np.arange(j['nz']) * j['step']); S = []
for f in sorted(fl, key=lambda f: f['c'][0]):
    if f['tgt'] is None or f['base'] is None or f['tgt'] - f['lv'].max() < 0.3 or len(f['lv']) > 12: continue
    base, tgt, dp = f['base'], f['tgt'], f['dp']; nr = max(2, int(round((tgt - base) / f['rise']))); n = nr - 1; c, u, v = f['c'], f['u'], f['v']
    p = c + u * (f['u0'] + f['u1']) / 2 + v * f['v1']; ln = f['u1'] - f['u0']
    S.append([round(float(p[0]), 2), round(float(p[1]), 2), round(math.atan2(-u[1], u[0]), 4), round(float(ln), 2), round(float(dp), 3), n, round(base, 2), round(tgt, 2)])
    su = (X - p[0]) * u[0] + (Z - p[1]) * u[1]; sv = (X - p[0]) * v[0] + (Z - p[1]) * v[1]; m = (np.abs(su) <= ln / 2) & (sv <= 0.3) & (sv >= -(n * dp + 0.25))
    r = (tgt - base) / nr; hh = np.clip(tgt - r * (-sv[m] / dp + 0.5), base, tgt); h[m] = np.round(hh * 100).astype(int); top[m] = h[m]; k[m] = 0
    print('vế bậc tại (%.0f, %.0f): dài %.1f m, %d bậc thay cho %d, cao %.2f -> %.2f, ra thêm %.1f m' % (p[0], p[1], ln, n, len(f['lv']), base, tgt, n * dp - (f['v1'] - f['v0'])))
j['steps'] = S; worldio.save(sys.argv[3], j, h, top, k, pre, post); print('đã ghi', len(S), 'vế bậc vào', sys.argv[3])
