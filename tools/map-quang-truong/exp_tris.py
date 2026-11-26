import bpy, sys, numpy as np
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=sys.argv[1])
out = {}
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    me = o.data; me.calc_loop_triangles(); mw = np.array(o.matrix_world)
    v = np.array([x.co[:] for x in me.vertices]); v = v @ mw[:3, :3].T + mw[:3, 3]; v = np.stack([v[:, 0], v[:, 2], -v[:, 1]], 1)
    t = np.array([lt.vertices[:] for lt in me.loop_triangles])
    if len(t): out[(me.materials[0].name if me.materials and me.materials[0] else 'none') + '|' + o.name] = v[t].astype(np.float32)
np.savez_compressed(sys.argv[2], **out); print('saved', len(out))
